from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Tuple

import numpy as np
from numpy.typing import DTypeLike

import nisarqa

from .data_annotation import DataAnnotation, XMLAnnotation
from .dataset import DataShape, HDF5Dataset, XMLDataset

objects_to_skip = nisarqa.get_all(name=__name__)


def check_xml_for_unused_shape_elements(
    shape_names: Iterable[str],
    shapes: Iterable[DataShape],
    xml_datasets: Iterable[XMLDataset],
):
    """
    Check the given XML shapes against other shapes and Datasets, and log
    any shapes that are not in use by any Dataset or other shape.

    Parameters
    ----------
    shape_names: Iterable[str]
        A set of shape names to check for.
    shapes : Iterable[DataShape]
        A set of Shape objects to check against.
    xml_datasets : Iterable[XMLDataset]
        A set of XML datasets to check against.
    """
    log = nisarqa.get_logger()

    shape_set = set(shape_names)

    used_shapes: set[str] = set()

    # DataShapes sometimes hold other shape names in their dimensions. Check all
    # dimensions for shape names and add them to the used shapes. It doesn't matter if
    # the dimensions have non-shape names, as these will be discarded when a difference
    # is taken later.
    for shape in shapes:
        for dimension in shape.dimensions:
            if dimension.name in shape_set:
                used_shapes.add(dimension.name)

    # All datasets either have an DataShape or None in their shape field. If there is an
    # DataShape, add its' name to the used shapes set.
    for dataset in xml_datasets:
        if dataset.shape is not None:
            used_shapes.add(dataset.shape.name)

    # The set of unused shapes is the difference between the set of all shapes and
    # the set of used shapes.
    unused_shapes = shape_set - used_shapes

    # Log the number of unused shapes, and then log their names, if any.
    log.info(f"\tUNUSED XML SHAPES: {len(unused_shapes)}")
    if len(unused_shapes) > 0:
        for shape_name in sorted(unused_shapes):
            log.warning(f"\t\tXML UNUSED SHAPE: {shape_name}")


def compare_dataset_lists(
    product_type: str,
    *,
    xml_datasets: Iterable[str],
    hdf5_datasets: Iterable[str],
    valid_freq_pols: Mapping[str, Iterable[str]],
    valid_layers: Iterable[str] | None = None,
    valid_subswaths: Iterable[str] | None = None,
) -> Tuple[set[str], set[str], set[str]]:
    """
    Calculate the sets of datasets in common between XML and HDF5, as well as
    those unique to each. Log the results.

    Parameters
    ----------
    product_type : str
        One of: 'rslc', 'gslc', 'gcov', 'rifg', 'runw', 'gunw', 'roff', 'goff'.
    xml_datasets : Iterable[str]
        A set of dataset names in the XML file.
    hdf5_datasets : Iterable[str]
        A set of dataset names in the HDF5 file.
    valid_freq_pols : Mapping[str, Iterable[str]]
        Dict of the expected frequency + polarization combinations that the
        input NISAR product says it contains.
            Example: { "A" : ["HH", "HV], "B" : ["VV", "VH"] }
    valid_layers : Iterable[str] or None, optional
        ROFF and GOFF products contain HDF5 datasets referred to as "layer number
        datasets" (e.g. `../layer1/..`, `../layer3/..`).
        This parameter should be a set of all valid layer groups for this product,
        e.g., {'layer1', 'layer2', 'layer3'}, or None.
        If None, layer datasets will not be checked. Defaults to None.
    valid_subswaths : Iterable[str] | None, optional
        Some products contain a number of subswaths - if the product has
        subswath information, this should be a set of subswaths expected
        in the product. If not, it should be None. Defaults to None.

    Returns
    -------
    common_dataset_names: set[str]:
        The names of all datasets in common between XML and HDF5.
    unique_xml_dataset_names: set[str]:
        The names of all datasets in the XML that are not in HDF5.
    unique_hdf5_dataset_names: set[str]:
        The names of all datasets in the HDF5 that are not in the XML.
    """
    log = nisarqa.get_logger()

    # Make these into sets so their results will also be sets.
    xml_datasets = set(xml_datasets)
    hdf5_datasets = set(hdf5_datasets)

    all_pols = list(nisarqa.get_possible_pols(product_type=product_type))

    if product_type == "gcov":
        # For GCOV, the Dataset paths can use either the four-character
        # covariance terms or the two-character polarizations (or neither).
        # Append the two-character pols from RSLC to create the full GCOV list.
        all_pols += list(nisarqa.get_possible_pols(product_type="rslc"))

    excepted_paths = nisarqa.rule_excepted_paths(product_type=product_type)

    # The shared datasets are all those in the intersect between the two
    # input sets.
    shared_dataset_names = xml_datasets.intersection(hdf5_datasets)
    exp_shared, unexp_shared = nisarqa.check_paths(
        paths=shared_dataset_names,
        valid_freq_pols=valid_freq_pols,
        valid_layers=valid_layers,
        valid_subswaths=valid_subswaths,
        rule_exceptions=excepted_paths,
        all_pols=all_pols,
    )
    log.info(
        "\tTOTAL NUMBER OF DATASETS IN INTERSECTION OF XML AND HDF5:"
        f" {len(shared_dataset_names)}"
    )
    log.info(f"\t\tCORRECTLY INCLUDED IN HDF5: {len(exp_shared)}")
    for name in sorted(exp_shared):
        log.info(f"\t\t\tCORRECTLY INCLUDED DATASET: {name}")
    log.info(f"\t\tUNEXPECTED INCLUSIONS: {len(unexp_shared)}")
    for name in sorted(unexp_shared):
        log.error(f"\t\t\tUNEXPECTED XML DATASET PRESENT IN HDF5: {name}")

    # The XML unique datasets are all those in the difference between the XML
    # datasets and the common set.
    xml_only_dataset_names = xml_datasets.difference(shared_dataset_names)
    exp_xml, unexp_xml = nisarqa.check_paths(
        paths=xml_only_dataset_names,
        valid_freq_pols=valid_freq_pols,
        valid_layers=valid_layers,
        valid_subswaths=valid_subswaths,
        rule_exceptions=excepted_paths,
        all_pols=all_pols,
    )
    log.info(f"\tXML UNIQUE NODES: {len(xml_only_dataset_names)}")
    log.info(f"\t\tMISSING FROM HDF5: {len(exp_xml)}")
    for name in sorted(exp_xml):
        log.error(f"\t\t\tDATASET MISSING FROM HDF5: {name}")
    log.info(f"\t\tCORRECTLY OMITTED FROM HDF5: {len(unexp_xml)}")

    # The HDF5 unique datasets are all those in the difference between the HDF5
    # datasets and the common set.
    hdf5_only_dataset_names = hdf5_datasets.difference(shared_dataset_names)
    log.info(f"\tHDF5 UNIQUE NODES: {len(hdf5_only_dataset_names)}")
    for name in sorted(hdf5_only_dataset_names):
        log.error(f"\t\tHDF5 DATASET NOT IN XML: {name}")

    return (
        shared_dataset_names,
        xml_only_dataset_names,
        hdf5_only_dataset_names,
    )


@dataclass
class SingleAspectSingleInstanceFlags:
    """
    Flags for if a single metadata aspect of a single HDF5 Dataset matches XML.

    Example: The `zeroDopplerTime` Dataset has a "units" Attribute. Create
    an instance of this class to capture if the "units" Attribute is:
        1) found in the HDF5 but missing from the XML
        2) found in the XML but missing from the HDF5
        3) found in both HDF5 and XML, but inconsistent between them.

    Examples of Dataset metadata: an Attribute, the dtype,
    the description, the 'units' Attribute.

    Parameters
    ----------
    missing_in_xml : bool
        True if metadata aspect is found in the HDF5 but missing from the XML.
        False otherwise.
    missing_in_hdf5 : bool
        True if metadata aspect is found in the XML but missing from the HDF5.
        False otherwise.
    hdf5_inconsistent_with_xml : bool
        True if the metadata aspect is found in both the HDF5 and the XML,
        but is inconsistent. False otherwise.

    See Also
    --------
    SingleAspectMultipleInstancesAccumulator :
        Class to accumulate instances of SingleAspectSingleInstanceFlags.
    """

    missing_in_xml: bool = False
    missing_in_hdf5: bool = False
    hdf5_inconsistent_with_xml: bool = False

    @property
    def hdf5_and_xml_match(self):
        """True if HDF5 Dataset's metadata aspect matches exactly the XML."""
        return not (
            self.missing_in_xml
            | self.missing_in_hdf5
            | self.hdf5_inconsistent_with_xml
        )


@dataclass(frozen=True)
class SingleAspectMultipleInstancesAccumulator:
    """
    Accumulator for correctness of a single aspect across multiple instances.

    Examples of a Dataset's metadata aspect: an Attribute, the dtype,
    the description, the 'units' Attribute.

    "Multiple Instances" refers to the number of instances of that aspect
    which have been accumulated. For example, say a GCOV product contains
    103 Datasets with a 'units' Attribute. This means that there are 103
    instances of the 'units' aspect to have their stats accumulated into
    an instance of this Class. Note that a single Dataset may have zero
    or multiple instances of a given metadata aspect.

    Parameters
    ----------
    name_of_metadata_aspect : str
        Name of the metadata aspect whose stats are being tallied here.
        Ex: "Attribute name", "units", "dtype", "description"
    total_num_aspects_checked : int
        Total number of instances of `name_of_metadata_aspect` found in
        either HDF5 or XML.
    num_missing_in_xml : int
        Number of instances of `name_of_metadata_aspect` found in HDF5
        but missing from the XML.
    num_missing_from_hdf5 : int
        Number of instances of `name_of_metadata_aspect` found in XML
        but missing from the HDF5.
    num_inconsistent_hdf5_vs_xml : int
        Number of instances of `name_of_metadata_aspect` found in both XML
        and HDF5 but are inconsistent. This includes issues like datetime
        descriptions that include microseconds, or variable length strings
        when fixed-length were expected.
    num_hdf5_and_xml_match : int
        Total number of instances of `name_of_metadata_aspect` that
        are consistent between the HDF5 and the XML.
    """

    name_of_metadata_aspect: str
    total_num_aspects_checked: int = 0
    num_missing_in_xml: int = 0
    num_missing_from_hdf5: int = 0
    num_inconsistent_hdf5_vs_xml: int = 0
    num_hdf5_and_xml_match: int = 0

    def __add__(
        self,
        other: (
            SingleAspectMultipleInstancesAccumulator
            | SingleAspectSingleInstanceFlags
        ),
        /,
    ) -> SingleAspectMultipleInstancesAccumulator:

        if isinstance(other, SingleAspectMultipleInstancesAccumulator):
            if self.name_of_metadata_aspect != other.name_of_metadata_aspect:
                raise ValueError(
                    f"`{self.name_of_metadata_aspect=}` but"
                    f" `{other.name_of_metadata_aspect=}`; they must be identical."
                )
            other_total_num_attrs = other.total_num_aspects_checked
            other_missing_in_xml = other.num_missing_in_xml
            other_missing_in_hdf5 = other.num_missing_from_hdf5
            other_differ = other.num_inconsistent_hdf5_vs_xml
            other_both_pass_checks = other.num_hdf5_and_xml_match
        elif isinstance(other, SingleAspectSingleInstanceFlags):
            other_total_num_attrs = 1

            # `True` and `False` become `1` and `0` when used for addition
            other_missing_in_xml = other.missing_in_xml
            other_missing_in_hdf5 = other.missing_in_hdf5
            other_differ = other.hdf5_inconsistent_with_xml
            other_both_pass_checks = other.hdf5_and_xml_match
        else:
            raise TypeError(
                f"The second addend has type `{type(other)}`,"
                " but only SingleAspectMultipleInstancesAccumulator or SingleAspectSingleInstanceFlags"
                " are supported."
            )

        return SingleAspectMultipleInstancesAccumulator(
            name_of_metadata_aspect=self.name_of_metadata_aspect,
            total_num_aspects_checked=self.total_num_aspects_checked
            + other_total_num_attrs,
            num_missing_in_xml=self.num_missing_in_xml + other_missing_in_xml,
            num_missing_from_hdf5=self.num_missing_from_hdf5
            + other_missing_in_hdf5,
            num_inconsistent_hdf5_vs_xml=self.num_inconsistent_hdf5_vs_xml
            + other_differ,
            num_hdf5_and_xml_match=self.num_hdf5_and_xml_match
            + other_both_pass_checks,
        )

    def print_to_log(self) -> None:
        """Record the current status of this instance in the log file."""
        log = nisarqa.get_logger()
        name = self.name_of_metadata_aspect
        fmt_frac = lambda x: f"{x} ({100 * x / total:.1f} %)"

        log.info(f"Comparing HDF5 Dataset {name} vs. XML spec {name}:")

        total = self.total_num_aspects_checked
        log.info(
            f"\t{name}: Total number of instances in union of HDF5 and XML:"
            f" {total}"
        )
        miss_xml = self.num_missing_in_xml
        log.info(
            f"\t{name}: Number of instances in HDF5 but missing from XML:"
            f" {fmt_frac(miss_xml)}"
        )
        miss_hdf5 = self.num_missing_from_hdf5
        log.info(
            f"\t{name}: Number of instances in XML but missing from HDF5:"
            f" {fmt_frac(miss_hdf5)}"
        )
        num_diff = self.num_inconsistent_hdf5_vs_xml
        log.info(
            f"\t{name}: Number of instances in HDF5 that are inconsistent"
            f" with XML spec: {fmt_frac(num_diff)}"
        )

        correct = self.num_hdf5_and_xml_match
        log.info(
            f"\t{name}: Number of instances that are consistent between"
            f" the HDF5 and XML: {fmt_frac(correct)}"
        )


@dataclass(frozen=True)
class MultipleAspectsMultipleInstancesSummary:
    """
    Class to hold stats on all metadata aspects across all Datasets.

    Examples of a Dataset's metadata aspect: an Attribute, the dtype,
    datetime formats, the description, the 'units' Attribute.

    Parameters
    ----------
    attr_names_stats : SingleAspectMultipleInstancesAccumulator
        Stats on the "Attribute name" metadata aspect.
    dtype_stats : SingleAspectMultipleInstancesAccumulator
        Stats on the "dtype" metadata aspect.
    datetime_stats : SingleAspectMultipleInstancesAccumulator
        Stats on the format of Datasets whose contents are datetime strings. (Does not
        include stats on datetime strings found in units nor descriptions.)
    description_stats : SingleAspectMultipleInstancesAccumulator
        Stats on the "description" metadata aspect.
    units_stats : SingleAspectMultipleInstancesAccumulator
        Stats on the "units" metadata aspect.
    """

    attr_names_stats: SingleAspectMultipleInstancesAccumulator = (
        SingleAspectMultipleInstancesAccumulator(
            name_of_metadata_aspect="Attribute names"
        )
    )
    dtype_stats: SingleAspectMultipleInstancesAccumulator = (
        SingleAspectMultipleInstancesAccumulator(
            name_of_metadata_aspect="dtype"
        )
    )
    datetime_stats: SingleAspectMultipleInstancesAccumulator = (
        SingleAspectMultipleInstancesAccumulator(
            name_of_metadata_aspect="datetime Dataset format"
        )
    )
    description_stats: SingleAspectMultipleInstancesAccumulator = (
        SingleAspectMultipleInstancesAccumulator(
            name_of_metadata_aspect="description"
        )
    )
    units_stats: SingleAspectMultipleInstancesAccumulator = (
        SingleAspectMultipleInstancesAccumulator(
            name_of_metadata_aspect="units"
        )
    )

    def __add__(
        self, other: MultipleAspectsMultipleInstancesSummary, /
    ) -> MultipleAspectsMultipleInstancesSummary:
        return MultipleAspectsMultipleInstancesSummary(
            attr_names_stats=self.attr_names_stats + other.attr_names_stats,
            dtype_stats=self.dtype_stats + other.dtype_stats,
            datetime_stats=self.datetime_stats + other.datetime_stats,
            description_stats=self.description_stats + other.description_stats,
            units_stats=self.units_stats + other.units_stats,
        )

    def print_to_log(self) -> None:
        """Record the current status of this instance in the log file."""
        self.attr_names_stats.print_to_log()
        self.dtype_stats.print_to_log()
        self.datetime_stats.print_to_log()
        self.description_stats.print_to_log()
        self.units_stats.print_to_log()


def compare_hdf5_dataset_to_xml(
    xml_dataset: XMLDataset,
    hdf5_dataset: HDF5Dataset,
) -> MultipleAspectsMultipleInstancesSummary:
    """
    Perform checks that compare an HDF5 dataset against the XML spec.

    Parameters
    ----------
    xml_dataset : nisarqa.XMLDataset
        The XML dataset.
    hdf5_dataset : nisarqa.HDF5Dataset
        The HDF5 dataset.

    Returns
    -------
    stats : nisarqa.MultipleAspectsMultipleInstancesSummary
        Metrics for attributes and aspects of `xml_dataset` and `hdf5_dataset`.
    """
    # This section should not be reached. Error if the given datasets have
    # different names.
    if not xml_dataset.name == hdf5_dataset.name:
        raise ValueError(
            f"Dataset names differ: XML:{xml_dataset.name},"
            f" HDF5:{hdf5_dataset.name}"
        )

    dtype_stats = SingleAspectMultipleInstancesAccumulator(
        name_of_metadata_aspect="dtype"
    )
    dtype_stats += compare_dtypes_xml_hdf5(xml_dataset, hdf5_dataset)

    datetime_stats = SingleAspectMultipleInstancesAccumulator(
        name_of_metadata_aspect="datetime Dataset format"
    )
    datetime_stats += compare_datetime_hdf5_to_xml(xml_dataset, hdf5_dataset)

    name_of_attr_name_aspect = "Attribute names"
    attr_names_stats = SingleAspectMultipleInstancesAccumulator(
        name_of_metadata_aspect=name_of_attr_name_aspect
    )
    descr_stats = SingleAspectMultipleInstancesAccumulator(
        name_of_metadata_aspect="description"
    )
    units_stats = SingleAspectMultipleInstancesAccumulator(
        name_of_metadata_aspect="units"
    )

    for annotation in xml_dataset.annotations:
        if annotation.attributes["app"] == "io":
            continue

        attr_names_stats += attribute_names_check(
            xml_annotation=annotation,
            hdf5_annotation=hdf5_dataset.annotation,
            dataset_name=hdf5_dataset.name,
            name_of_metadata_aspect=name_of_attr_name_aspect,
        )

        descr_stats += attribute_description_check(
            xml_annotation=annotation,
            hdf5_annotation=hdf5_dataset.annotation,
            dataset_name=hdf5_dataset.name,
        )

        units_stats += attribute_units_check(
            xml_annotation=annotation,
            hdf5_annotation=hdf5_dataset.annotation,
            dataset_name=hdf5_dataset.name,
        )

    return MultipleAspectsMultipleInstancesSummary(
        attr_names_stats=attr_names_stats,
        dtype_stats=dtype_stats,
        datetime_stats=datetime_stats,
        description_stats=descr_stats,
        units_stats=units_stats,
    )


def stringify_dtype(dtype: DTypeLike) -> str:
    """
    Get the name of a datatype as a concise, human-readable string.

    Parameters
    ----------
    dtype : data-type
        The input datatype.

    Returns
    -------
    name : str
        The datatype name, such as 'int32' or 'float64'. If `dtype` was
        `nisarqa.complex32`, returns 'complex32'.
    """
    dtype = np.dtype(dtype)
    return "complex32" if (dtype == nisarqa.complex32) else str(dtype)


def compare_dtypes_xml_hdf5(
    xml_dataset: XMLDataset, hdf5_dataset: HDF5Dataset
) -> SingleAspectSingleInstanceFlags:
    """
    Compare dtypes of an XML dataset and an HDF5 dataset; log any discrepancies.

    Parameters
    ----------
    xml_dataset : nisarqa.XMLDataset
        The XML dataset to compare.
    hdf5_dataset : nisarqa.HDF5Dataset
        The HDF5 dataset to compare.

    Returns
    -------
    flags : nisarqa.SingleAspectSingleInstanceFlags
        Metrics for dtypes in `xml_dataset` and `hdf5_dataset`.
    """
    log = nisarqa.get_logger()
    xml_dtype = xml_dataset.dtype
    hdf5_dtype = hdf5_dataset.dtype

    flags = SingleAspectSingleInstanceFlags()

    # If either dtype is None (more likely to be for an XML, but check for both)
    # means the dtype could not be determined. Print error and return.
    if xml_dtype is None:
        log.error(
            f"XML dataset dtype could not be determined: {xml_dataset.name}"
        )
        flags.missing_in_xml = True
    if hdf5_dtype is None:
        log.error(
            f"HDF5 dataset dtype could not be determined: {hdf5_dataset.name}"
        )
        flags.missing_in_hdf5 = True

    # Strings are a special case. When the XML requests a string, the HDF5
    # Dataset should be a byte string with a length specified by the XML file,
    # or an arbitrary length if the XML length is "0".
    if xml_dtype == str:
        if not np.issubdtype(hdf5_dtype, np.bytes_):
            log.error(
                f"XML expects string. HDF5 has type `{hdf5_dtype}`, but"
                f" should be a NumPy byte string. Dataset {hdf5_dataset.name}"
            )
            flags.hdf5_inconsistent_with_xml = True
        else:
            # NumPy byte string, or a list of numpy bytes strings. Perfect!
            xml_stated_length = xml_dataset.length

            # All strings should have a length in their properties.
            if xml_stated_length is None:
                log.error(
                    f"String given without length: XML dataset {xml_dataset.name}"
                )
                flags.missing_in_xml = True

            # If the length is 0, there is no expected length. Return successfully.
            elif xml_stated_length == 0:
                pass

            else:
                # The length of the string in the HDF5 dataset is its itemsize.
                # If this is different from the length value, then the actual string
                # length differs from the expected one.
                hdf5_dataset_length = hdf5_dtype.itemsize
                if xml_stated_length != hdf5_dataset_length:
                    log.error(
                        "Unequal string lengths. XML expects length"
                        f" {xml_stated_length}, HDF5 dataset byte string length is"
                        f" {hdf5_dataset_length}: Dataset {xml_dataset.name}"
                    )
                    flags.hdf5_inconsistent_with_xml = True

    elif xml_dtype != hdf5_dtype:
        # For non-string types, perform a simple type check.
        log.error(
            f"dtypes differ. XML: {stringify_dtype(xml_dtype)}, "
            f"HDF5: {stringify_dtype(hdf5_dtype)} - Dataset {xml_dataset.name}"
        )
        flags.hdf5_inconsistent_with_xml = True

    return flags


def compare_datetime_hdf5_to_xml(
    xml_dataset: XMLDataset, hdf5_dataset: HDF5Dataset
) -> SingleAspectSingleInstanceFlags:
    """
    Compare datetime string in HDF5 datasets vs. XML spec; log discrepancies.

    This function only compares the dataset values to the description provided
    in the XML; it does not check datetime strings in the "units" Attributes.

    Parameters
    ----------
    xml_dataset : nisarqa.XMLDataset
        The XML dataset to compare.
    hdf5_dataset : nisarqa.HDF5Dataset
        The HDF5 dataset to compare.

    Returns
    -------
    flags : nisarqa.SingleAspectSingleInstanceFlags
        Metrics for datetime strings in `xml_dataset` and `hdf5_dataset`.

    Raises
    ------
    NotImplementedError
        If the HDF5 Dataset is an array of byte strings, where at least
        one of those strings contains a datetime string.
        As of June 2025, NISAR product specs contain no Datasets like this;
        handling these edge cases would cause unnecessary code complexity.
    """
    log = nisarqa.get_logger()
    flags = SingleAspectSingleInstanceFlags()

    # The XML dataset type is considered "truth" in the QA XML Checker.
    # Only datasets with a string dtype contain datetime strings, so if a
    # dataset has a different type (e.g. integer) we know that there are
    # no datetimes to verify. (And thus, no inconsistent datetimes to log.)
    if xml_dataset.dtype != str:
        return flags

    # Now, check that the HDF5's corresponding Dataset is also a (byte) string.
    # If not, then the Dataset was incorrectly formed; however, another
    # function in the XML Checker is responsible for checking+logging that
    # the HDF5 datatype must be np.bytes_ if the XML datatype is str,
    # so we do not need to log that issue again here. Instead, return early.
    # (Once the user fixes the dtype issue and reruns QA, then this datetime
    # string check will run to completion and log any datetime string issues.)
    h5_string = hdf5_dataset.dataset[...]
    if not np.issubdtype(h5_string.dtype, np.bytes_):
        return flags

    # Convert to a Python Unicode string. If Dataset is an array of byte
    # strings, this will return a list of Python strings.
    # (Note: Arrays of byte strings also have a dtype of `numpy.bytes_`)
    h5_ds_val = nisarqa.byte_string_to_python_str(h5_string)

    if isinstance(h5_ds_val, list):
        # Array of byte strings.
        # As of June 2025, there are no known Datasets in NISAR L1/L2 products
        # that are arrays of strings which should contain datetime strings.
        # Let's add a quick check in case this changes.
        for s in h5_ds_val:
            if nisarqa.contains_datetime_value_substring(s):
                raise NotImplementedError(
                    "Dataset contains an array of byte strings, in which"
                    " at least one byte string contains a datetime."
                    f" Please update QA check. Dataset: {hdf5_dataset.name}"
                )
        # The array of byte strings contained no datetime strings. Great!
        return flags

    # Check if the HDF5 Dataset contains a datetime value
    h5_name = hdf5_dataset.dataset.name

    if nisarqa.contains_datetime_value_substring(input_str=h5_ds_val):
        try:
            h5_dt_str = nisarqa.extract_datetime_value_substring(
                input_str=h5_ds_val, dataset_name=h5_name
            )
        except ValueError:
            if "runConfigurationContents" in h5_name:
                # Known edge case which contains multiple datetime strings.
                # In this edge case, we do not need verify against the XML.
                h5_dt_str = None
            else:
                raise

    else:
        h5_dt_str = None

    # Check if the XML description contains a datetime value
    for ann in xml_dataset.annotations:
        if nisarqa.contains_datetime_template_substring(
            input_str=ann.description
        ):
            xml_dt_str = nisarqa.extract_datetime_template_substring(
                input_str=ann.description, dataset_name=h5_name
            )
            break
    else:
        xml_dt_str = None

    if (h5_dt_str is None) and (xml_dt_str is None):
        # neither contain a datetime string. Great!
        pass
    elif (h5_dt_str is None) and (xml_dt_str is not None):
        log.error(
            f"XML contains the datetime template string '{xml_dt_str}'"
            " in its description Attribute, but the HDF5 Dataset does not"
            f" contain a datetime string. Dataset: {h5_name}"
        )
        flags.missing_in_hdf5 = True
    elif (h5_dt_str is not None) and (xml_dt_str is None):
        log.error(
            f"HDF5 dataset contains a datetime string: '{h5_dt_str}',"
            f" but the XML does not provide a datetime template format"
            f" in the description. Dataset: {h5_name}"
        )
        flags.missing_in_xml = True
    else:
        if not nisarqa.verify_datetime_string_matches_template(
            dt_value_str=h5_dt_str,
            dt_template_str=xml_dt_str,
            dataset_name=h5_name,
        ):
            flags.hdf5_inconsistent_with_xml = True

    return flags


def attribute_names_check(
    xml_annotation: XMLAnnotation,
    hdf5_annotation: DataAnnotation,
    dataset_name: str,
    name_of_metadata_aspect: str,
) -> nisarqa.SingleAspectMultipleInstancesAccumulator:
    """
    Compare attribute names for a single Dataset between XML and HDF5.

    Parameters
    ----------
    xml_annotation : nisarqa.XMLAnnotation
        An XML annotation to compare.
    hdf5_annotation : nisarqa.DataAnnotation
        An HDF5 annotation to compare.
    dataset_name : str
        The name of the dataset on which both annotations exist.
    name_of_metadata_aspect : str
        Name for this attribute aspect, which will be used when constructing
        the returned `stats` object. Example: "Attribute names".

    Returns
    -------
    stats : nisarqa.SingleAspectMultipleInstancesAccumulator
        Metrics for attribute names in `xml_annotation` and `hdf5_annotation`.
    """
    log = nisarqa.get_logger()

    # Ignore certain attributes present in the XML, such as "lang" and "app"
    ignored_xml_attributes = nisarqa.ignored_xml_annotation_attributes()
    xml_attributes = xml_annotation.attribute_names - ignored_xml_attributes

    hdf5_attrs = hdf5_annotation.attribute_names

    total_num = len(hdf5_attrs | xml_attributes)

    # Attributes that exist only in XML but not HDF5.
    xml_unique_attribs = xml_attributes - hdf5_attrs
    num_only_in_xml = len(xml_unique_attribs)
    if num_only_in_xml > 0:
        log.error(
            f"Attributes found in XML but not HDF5: {xml_unique_attribs} -"
            f" Dataset {dataset_name}"
        )

    # Attributes that exist only in HDF5 but not XML.
    hdf5_unique_attribs = hdf5_attrs - xml_attributes
    num_only_in_hdf5 = len(hdf5_unique_attribs)
    if num_only_in_hdf5 > 0:
        log.error(
            f"Attributes found in HDF5 but not XML: {hdf5_unique_attribs} -"
            f" Dataset {dataset_name}"
        )

    num_in_common = len(hdf5_attrs & xml_attributes)

    # Here, `num_inconsistent_hdf5_vs_xml` should be zero because attribute
    # names can only be identical in the HDF5 & XML or missing from one
    # or the other.
    num_inconsistent_hdf5_vs_xml = 0

    return SingleAspectMultipleInstancesAccumulator(
        name_of_metadata_aspect=name_of_metadata_aspect,
        total_num_aspects_checked=total_num,
        num_missing_in_xml=num_only_in_xml,
        num_missing_from_hdf5=num_only_in_hdf5,
        num_inconsistent_hdf5_vs_xml=num_inconsistent_hdf5_vs_xml,
        num_hdf5_and_xml_match=num_in_common,
    )


def attribute_units_check(
    xml_annotation: XMLAnnotation,
    hdf5_annotation: DataAnnotation,
    dataset_name: str,
) -> SingleAspectSingleInstanceFlags:
    """
    Check the units Attribute of an HDF5 dataset against the XML spec.

    Parameters
    ----------
    xml_annotation : nisarqa.XMLAnnotation
        An XML annotation to check.
    hdf5_annotation : nisarqa.DataAnnotation
        An HDF5 annotation to check.
    dataset_name : str
        The dataset being checked, for logging.

    Returns
    -------
    flags : nisarqa.SingleAspectSingleInstanceFlags
        Metrics for units attributes in `xml_annotation` and `hdf5_annotation`.
    """

    log = nisarqa.get_logger()

    flags = SingleAspectSingleInstanceFlags()
    xml_dt_template_string = ""
    hdf5_dt_string = ""

    # Get value of 'units'; perform basic checks
    if "units" in xml_annotation.attributes:
        # `element_to_annotation()` in `xml_parser.py` already validated the XML.
        # Here, simply use those validated results.
        xml_units = str(xml_annotation.attributes["units"])

        # if available, extract the datetime string
        if nisarqa.contains_datetime_template_substring(input_str=xml_units):
            xml_dt_template_string = (
                nisarqa.extract_datetime_template_substring(
                    input_str=xml_units, dataset_name=dataset_name
                )
            )

    else:
        xml_units = None

    if "units" in hdf5_annotation.attributes:
        hdf5_units = str(hdf5_annotation.attributes["units"])

        if hdf5_units == "":
            # Log an error but don't flag the attribute as "missing".
            # If the XML units string is non-empty, this will be treated
            # as an inconsistency and we don't want to double-count.
            log.error(
                f'Empty "units" attribute in HDF5: Dataset {dataset_name}'
            )

        # if available, extract the datetime string
        if nisarqa.contains_datetime_value_substring(input_str=hdf5_units):
            hdf5_dt_string = nisarqa.extract_datetime_value_substring(
                input_str=hdf5_units, dataset_name=dataset_name
            )
    else:
        hdf5_units = None

    log_err = lambda: log.error(
        f"Differing `units` attributes detected for datasets. XML: "
        f"{xml_units!r}, HDF5: {hdf5_units!r}: Dataset {dataset_name}"
    )

    if (xml_units is None) and (hdf5_units is not None):
        flags.missing_in_xml = True
        log_err()

    elif (xml_units is not None) and (hdf5_units is None):
        flags.missing_in_hdf5 = True
        log_err()
    elif xml_dt_template_string or hdf5_dt_string:
        # "units" exists in both XML and HDF5, and one or both of the "units"
        # contains a datetime string.
        # This is an edge case that we need to handle separately.
        if (
            xml_dt_template_string and hdf5_dt_string
        ) and nisarqa.verify_datetime_matches_template_with_addl_text(
            dt_value_str=hdf5_units,
            dt_template_str=xml_units,
            dataset_name=dataset_name,
        ):
            pass
        else:
            log.error(
                f"Differing format of `units` attributes detected for datasets;"
                f" inconsistent datetime formats and/or text. XML: "
                f'"{xml_units}", HDF5: "{hdf5_units}": Dataset {dataset_name}'
            )
            flags.hdf5_inconsistent_with_xml = True

    elif xml_units != hdf5_units:
        # "units" exists in both XML and HDF5, but they are inconsistent.
        # (The datetime edge case was handled above.)
        flags.hdf5_inconsistent_with_xml = True
        log_err()

    return flags


def attribute_description_check(
    xml_annotation: XMLAnnotation,
    hdf5_annotation: DataAnnotation,
    dataset_name: str,
) -> SingleAspectSingleInstanceFlags:
    """
    Check the descriptions listed on XML and HDF5 attributes against each other.

    Parameters
    ----------
    xml_annotation : nisarqa.XMLAnnotation
        An XML annotation to check.
    hdf5_annotation : nisarqa.DataAnnotation
        An HDF5 annotation to check.
    dataset_name : str
        The dataset being checked, for logging.

    Returns
    -------
    flags : nisarqa.SingleAspectSingleInstanceFlags
        Metrics for description attributes in `xml_annotation` and
        `hdf5_annotation`.
    """
    log = nisarqa.get_logger()
    flags = SingleAspectSingleInstanceFlags()

    xml_desc = str(xml_annotation.description)
    hdf5_desc = str(hdf5_annotation.description)

    if xml_desc == "":
        log.error(f"Empty description on XML: Dataset {dataset_name}")
        flags.missing_in_xml = True

    if hdf5_desc == "":
        log.error(
            f"Empty description attribute on HDF5: Dataset {dataset_name}"
        )
        flags.missing_in_hdf5 = True

    if xml_desc != hdf5_desc:
        log.error(
            f'Differing descriptions detected: XML: "{xml_desc}",'
            f' HDF5: "{hdf5_desc}": Dataset {dataset_name}'
        )
        flags.hdf5_inconsistent_with_xml = True

    return flags


__all__ = nisarqa.get_all(__name__, objects_to_skip)
