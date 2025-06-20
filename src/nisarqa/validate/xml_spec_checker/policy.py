from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import TypeVar

# List of objects from the import statements that
# should not be included when importing this module
import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)

VersionT = TypeVar("VersionT", bound="Version")


@dataclass(order=True)
class Version:
    """
    A product version.

    Supports rich comparison operators with other `Version` objects.

    Attributes
    ----------
    major, minor, patch : int
        The major, minor, and patch version numbers.
    """

    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls: type[VersionT], version_str: str) -> VersionT:
        """
        Create a Version object from a version string.

        Parameters
        ----------
        version_str : str
            The version string. Must be a period-delineated string of three
            integers.

        Returns
        -------
        Version
            A Version object based on the given string.

        Raises
        ------
        ValueError
            If version_str cannot be parsed into a Version object.
        """

        version_list = version_str.split(".")
        if len(version_list) != 3:
            raise ValueError(
                f"{version_str} is not a recognized version number."
            )
        try:
            int_map = map(int, version_list)
        except Exception as err:
            raise ValueError(
                f"{version_str} is not a recognized version number."
            ) from err

        major, minor, patch = int_map
        return cls(major, minor, patch)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def get_supported_xml_spec_versions() -> list[Version]:
    """
    Return an ordered list of all supported XML product versions in QA. This
    is achieved by finding all directory names in the product specs
    directory and converting them to Version objects, and then returning
    them in a sorted list.

    Returns
    -------
    list[Version]
        All XML product specs supported by QA, in earliest-to-latest order.
    """
    log = nisarqa.get_logger()

    # This will be achieved by finding and sorting the names of all
    # subdirectories in the product specs base path.
    # First, get the product specs directory path.
    specs_dir = nisarqa.PRODUCT_SPECS_PATH
    # Get all files and directories under the specifications directory.
    # This is not recursive - it only lists first-level children of
    # the directory.
    children = os.listdir(specs_dir)
    # Filter only subdirectories.
    dirs = list(filter(lambda name: os.path.isdir(specs_dir / name), children))

    versions: list[Version] = []
    for dir in dirs:
        try:
            ver = Version.from_string(dir)
            versions.append(ver)
        except ValueError:
            log.debug(
                f'XML product specification directory "{dir}" cannot be'
                " parsed as a version number. This directory will be"
                " ignored when selecting XML specifications."
            )

    # Return the sorted list of version directory names.
    return sorted(versions)


def get_xml_version_to_compare_against(version: Version) -> Version:
    """
    Check an HDF5 product spec version against the set of supported
    XML product spec versions and return one to use.

    Products with a version greater than the greatest supported version
    will be checked against the greatest version.
    Products with a version lesser than the minimum supported version
    will be checked against the minimum version.
    Products with a version that is between the greatest and minimum
    versions, but not matching any version in the set of supported versions,
    will be checked against the next greater supported version.

    Parameters
    ----------
    version : Version
        The HDF5 product version being checked.

    Returns
    -------
    Version
        The XML spec version available in QA which most closely matches the
        given version.
    """
    log = nisarqa.get_logger()

    all_versions = get_supported_xml_spec_versions()

    latest_version = all_versions[-1]
    minimum_version = all_versions[0]

    if version == latest_version:
        # The nominal case. Just return the same version.
        return latest_version
    if version in all_versions:
        # The version being requested is of a supported version
        # that is lesser than the greatest supported version.
        # This is not necessarily an error but is a warning case.
        # Notify the user and continue.
        log.warning(
            f"Input HDF5 file's product is {version}, which is less than the"
            f" latest XML version available in QA: {latest_version}."
        )
        return version
    if version > latest_version:
        # A version is being requested that is greater than the greatest
        # supported version.
        # Default to the greatest supported version.
        log.error(
            f"Input HDF5 file's product is {version}, which is greater than"
            f" the the latest XML version available in QA: {latest_version}."
            f" Defaulting to latest supported version {latest_version}. "
        )
        return str(latest_version)
    if version < minimum_version:
        # A version is being requested that is lesser than the minimum
        # supported version.
        # Default to the minimum supported version.
        log.error(
            f"Input HDF5 file's product is {version}, which is less than"
            f" the the earliest XML version available in QA: {minimum_version}."
            f" Defaulting to earliest supported version {minimum_version}."
            " The input HDF5 will be compared to this higher version,"
            " likely resulting in many false-positives of validation errors."
        )
        return minimum_version
    # At this juncture it has been established that the version parameter
    # given is between the minimum and maximum supported versions, but is
    # not itself supported. Default to the version that is the next higher
    # than the given version.
    for supported_ver in all_versions:
        if supported_ver > version:
            return supported_ver

    # The code should never reach this point. Raise a critical error.
    raise ValueError(
        "check_version_number was unable to find a supported XML product"
        f" spec version number for HDF5 product with spec version {version}."
        " This is a bug."
    )


def ignored_xml_annotation_attributes() -> set[str]:
    """
    A set of XML annotation attributes that are not expected to appear in
    products and therefore should not be checked against.

    Returns
    -------
    set[str]
        The set of ignored attributes.
    """
    return {"lang", "app"}


def numeric_dtype_should_not_have_units() -> set[str]:
    """
    Set of Dataset basenames that are numeric but should not have units.

    Returns
    -------
    basenames : set of str
        The set dataset basenames that have numeric dtype but should NOT
        have a units attribute.
    """
    return {
        "epsg",
        "projection",
        "diagnosticModeFlag",
        "absoluteOrbitNumber",
        "referenceAbsoluteOrbitNumber",
        "secondaryAbsoluteOrbitNumber",
        "frameNumber",
        "trackNumber",
        "mask",
        "validSamplesSubSwath1",
        "validSamplesSubSwath2",
        "validSamplesSubSwath3",
        "validSamplesSubSwath4",
        "validSamplesSubSwath5",
    }


def ignore_annotation(app: str) -> bool:
    """
    Determine if an annotation should be ignored when an XML dataset is
    checked against HDF5.

    Parameters
    ----------
    annotation : DataAnnotation
        The annotation to determine policy on.

    Returns
    -------
    bool
        True if ignore; False otherwise.
    """
    # Annotations whose "app" attribute is "io" describe, at most, some aspect
    # of the data. They are not generally checkable against HDF5 because they
    # do not reflect any particular change in the HDF5 file.
    if app in ["io"]:
        return True
    return False


def rule_excepted_paths(product_type: str) -> list[Template]:
    """
    Given a product type, return all ignored regular expression path templates
    associated with that product type, i.e. a "rule excepted path".

    Rule excepted paths are paths that ignore inclusion rules that might cause
    a dataset to be expected or not expected for a given product.
    For instance, RSLC calibration info is frequency dependent, but for each
    frequency in the product, all linear polarizations will be represented,
    even if they are not all valid in other places in the product. This is
    where such edge cases can be handled.
    The templates returned by this function are regular expressions which
    will be processed by `nisarqa.process_excepted_paths()`

    Parameters
    ----------
    product_type : str
        One of: 'rslc', 'gslc', 'gcov', 'rifg', 'runw', 'gunw', 'roff', 'goff'.

    Returns
    -------
    list[string.Template]
        All ignored regexp path templates associated with the given product
        type.
    """
    calibration_info_formats = [
        ".*/metadata/calibrationInformation/$freq/$lin_pol/differentialDelay",
        ".*/metadata/calibrationInformation/$freq/$lin_pol/differentialPhase",
        ".*/metadata/calibrationInformation/$freq/$lin_pol/scaleFactor",
        ".*/metadata/calibrationInformation/$freq/$lin_pol/scaleFactorSlope",
    ]

    if product_type in ["rslc", "gslc", "gcov"]:
        return [Template(format) for format in calibration_info_formats]
    return []


def pol_options(include_quad: bool = True) -> list[str]:
    """
    Return the list of all polarizations considered valid by this system.

    Parameters
    ----------
    include_quad : bool, optional
        Whether or not to include quad-polarizations. Defaults to True

    Returns
    -------
    list[str]
        The polarizations.
    """
    return linear_pols(include_quad) + circular_pols(include_quad)


def linear_pols(include_quad: bool = False) -> list[str]:
    """
    Return the list of all lateral polarizations considered valid by this
    system.

    Parameters
    ----------
    include_quad : bool, optional
        Whether or not to include quad-polarizations. Defaults to False

    Returns
    -------
    list[str]
        The polarizations.
    """
    pols = ["HH", "HV", "VH", "VV"]
    if include_quad:
        quad_pols = []
        for sub_pol_1 in pols:
            for sub_pol_2 in pols:
                quad_pols.append(sub_pol_1 + sub_pol_2)
        pols += quad_pols
    return pols


def circular_pols(include_quad: bool = False) -> list[str]:
    """
    Return the list of all circular polarizations considered valid by this
    system.

    Parameters
    ----------
    include_quad : bool, optional
        Whether or not to include quad-polarizations. Defaults to False

    Returns
    -------
    list[str]
        The polarizations.
    """
    pols = ["RH", "RV"]
    if include_quad:
        pols += ["RHRH", "RHRV", "RVRH", "RVRV"]
    return pols


def subswaths_options() -> list[str]:
    """
    Return the list of all subswath segments considered valid by this system.
    """
    return [
        "validSamplesSubSwath1",
        "validSamplesSubSwath2",
        "validSamplesSubSwath3",
        "validSamplesSubSwath4",
        "validSamplesSubSwath5",
    ]


def locate_spec_xml_file(product_type: str, version: Version) -> Path | None:
    """
    Given a version number and product name, find the specs XML file.

    Parameters
    ----------
    product_type : str
        One of: 'rslc', 'gslc', 'gcov', 'rifg', 'runw', 'gunw', 'roff', 'goff'.
    version : Version
        The XML product spec version.

    Returns
    -------
    Path
        The path to the XML file for that product and version.

    Raises
    ------
    FileNotFoundError
        If the XML file for the requested product and version was not found.
    """
    log = nisarqa.get_logger()

    filename = _get_spec_xml_filename(product_type=product_type)
    base_path = nisarqa.PRODUCT_SPECS_PATH

    full_path = base_path / str(version) / filename
    log.info(f"Using XML spec file: {full_path}")
    if not full_path.exists():
        raise FileNotFoundError(
            f"Product spec XML file not found for {product_type}"
            f" version {version} at path: {full_path}."
        )
    return full_path


def _get_spec_xml_filename(product_type: str) -> str:
    """Given a product name, return its' expected spec XML filename."""
    if product_type == "rifg":
        return "nisar_L1_RIFG.xml"
    if product_type == "roff":
        return "nisar_L1_ROFF.xml"
    if product_type == "rslc":
        return "nisar_L1_RSLC.xml"
    if product_type == "runw":
        return "nisar_L1_RUNW.xml"
    if product_type == "gcov":
        return "nisar_L2_GCOV.xml"
    if product_type == "goff":
        return "nisar_L2_GOFF.xml"
    if product_type == "gslc":
        return "nisar_L2_GSLC.xml"
    if product_type == "gunw":
        return "nisar_L2_GUNW.xml"
    raise ValueError(f"Product type {product_type} not recognized.")


__all__ = nisarqa.get_all(__name__, objects_to_skip)
