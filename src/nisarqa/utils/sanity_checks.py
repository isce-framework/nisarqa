from __future__ import annotations

from collections.abc import Container
from typing import Any, TypeVar

import h5py
import numpy as np
from numpy.typing import ArrayLike

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)

T = TypeVar("T")


def dataset_sanity_checks(product: nisarqa.NisarProduct) -> None:
    """
    Perform a series of verification checks on the input product's datasets.

    Parameters
    ----------
    product : nisarqa.NisarProduct
        Instance of the input product.
    """
    with h5py.File(product.filepath, "r") as f:

        identification_sanity_checks(
            id_group=f[product.identification_path],
            product_type=product.product_type,
        )


def identification_sanity_checks(
    id_group: h5py.Group, product_type: str
) -> None:
    """
    Perform sanity checks on Datasets in input product's identification group.

    Parameters
    ----------
    id_group : h5py.Group
        Handle to the `identification` group in the input product.
    product_type : str
        One of: 'rslc', 'gslc', 'gcov', 'rifg', 'runw', 'gunw', 'roff', 'goff',
        or their uppercase variants. (The NISAR convention is for the
        identification group's `productType` Dataset to be all uppercase.)
    """

    log = nisarqa.get_logger()

    def _full_path(ds_name: str) -> str:
        return f"{id_group.name}/{ds_name}"

    def _dataset_exists(ds_name: str) -> bool:
        if ds_name not in id_group:
            log.error(f"Missing dataset: {_full_path(ds_name)}")
            return False
        return True

    def _get_dataset(ds_name: str) -> np.ndarray | np.bytes_:
        return id_group[ds_name][()]

    def _get_integer_dataset(ds_name: str) -> int | None:
        data = _get_dataset(ds_name=ds_name)
        if np.issubdtype(data.dtype, np.integer):
            return data
        else:
            log.error(
                f"Dataset has dtype `{data.dtype}`, must be an integer type."
                f" Dataset: {_full_path(ds_name)}"
            )
            return None

    def _get_string_dataset(ds_name: str) -> str | None:
        data = _get_dataset(ds_name=ds_name)
        if nisarqa.verify_str_meets_isce3_conventions(ds=id_group[ds_name]):
            return nisarqa.byte_string_to_python_str(data)
        else:
            return None

    def _verify_greater_than_zero(value: int | None, ds_name: str) -> bool:
        if (value is None) or (value <= 0):
            log.error(
                f"Dataset value is {value}, must be greater than zero."
                f" Dataset: {_full_path(ds_name)}"
            )
            return False
        return True

    def _verify_data_is_in_list(
        value: T | None, valid_options: Container[T], ds_name: str
    ) -> bool:
        if (value is None) or (value not in valid_options):
            log.error(
                f"Dataset value is {value!r}, must be one of "
                f" {valid_options}. Dataset: {_full_path(ds_name)}"
            )
            return False
        return True

    passes = True

    # Track all of the Datasets that this function explicitly checks.
    # That way, if/when ISCE3 adds new Datasets to the`identification` Group,
    # we can log that they were not manually verified by this function.
    ds_checked = set()

    # absolute orbit number
    if product_type.lower() in nisarqa.LIST_OF_INSAR_PRODUCTS:
        ds_names = [
            "referenceAbsoluteOrbitNumber",
            "secondaryAbsoluteOrbitNumber",
        ]
    else:
        ds_names = ["absoluteOrbitNumber"]
    for ds_name in ds_names:
        ds_checked.add(ds_name)
        if _dataset_exists(ds_name):
            data = _get_integer_dataset(ds_name=ds_name)
            passes &= _verify_greater_than_zero(value=data, ds_name=ds_name)

    ds_name = "trackNumber"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_integer_dataset(ds_name=ds_name)
        passes &= _verify_greater_than_zero(value=data, ds_name=ds_name)
        if (data is None) or (data > nisarqa.NUM_TRACKS):
            log.error(
                f"Dataset value is {data}, must be less than or equal to"
                f" total number of tracks, which is {nisarqa.NUM_TRACKS}."
                f" Dataset: {_full_path(ds_name)}"
            )
            passes = False

    ds_name = "frameNumber"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_integer_dataset(ds_name=ds_name)
        passes &= _verify_greater_than_zero(value=data, ds_name=ds_name)
        if (data is None) or (data > nisarqa.NUM_FRAMES):
            log.error(
                f"Dataset value is {data}, must be less than or equal to"
                f" total number of frames, which is {nisarqa.NUM_FRAMES}."
                f" Dataset: {_full_path(ds_name)}"
            )
            passes = False

    ds_name = "diagnosticModeFlag"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_integer_dataset(ds_name=ds_name)
        passes &= _verify_data_is_in_list(
            value=data, valid_options=(0, 1, 2), ds_name=ds_name
        )

    ds_name = "productType"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_string_dataset(ds_name=ds_name)
        if (data is None) or (data != product_type.upper()):
            log.error(
                f"Dataset value is {data}, must match the specified"
                f" product type of {product_type.upper()}."
                f" Dataset: {_full_path(ds_name)}"
            )
            passes = False

    ds_name = "lookDirection"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_string_dataset(ds_name=ds_name)
        passes &= _verify_data_is_in_list(
            value=data, valid_options=("Left", "Right"), ds_name=ds_name
        )

    ds_name = "productLevel"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_string_dataset(ds_name=ds_name)
        passes &= _verify_data_is_in_list(
            value=data,
            valid_options=("L0A", "L0B", "L1", "L2"),
            ds_name=ds_name,
        )

    ds_name = "radarBand"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_string_dataset(ds_name=ds_name)
        passes &= _verify_data_is_in_list(
            value=data, valid_options=("L", "S"), ds_name=ds_name
        )

    ds_name = "orbitPassDirection"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_string_dataset(ds_name=ds_name)
        passes &= _verify_data_is_in_list(
            value=data,
            valid_options=("Ascending", "Descending"),
            ds_name=ds_name,
        )

    ds_name = "processingType"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_string_dataset(ds_name=ds_name)
        passes &= _verify_data_is_in_list(
            value=data,
            valid_options=("Nominal", "Urgent", "Custom", "Undefined"),
            ds_name=ds_name,
        )

    # Verify Boolean Datasets
    bool_datasets = [
        "isDithered",
        "isGeocoded",
        "isMixedMode",
        "isUrgentObservation",
        "isFullFrame",
    ]

    if product_type.lower() in nisarqa.LIST_OF_INSAR_PRODUCTS:
        bool_datasets += [
            "referenceIsJointObservation",
            "secondaryIsJointObservation",
        ]
    else:
        bool_datasets += ["isJointObservation"]

    for ds_name in bool_datasets:
        ds_checked.add(ds_name)
        if _dataset_exists(ds_name):
            data = _get_string_dataset(ds_name=ds_name)
            if data is not None:
                passes &= nisarqa.verify_isce3_boolean(ds=id_group[ds_name])
            else:
                passes = False

    # Verify "Version" Datasets (major, minor, patch)
    for ds_name in (
        "productVersion",
        "productSpecificationVersion",
    ):
        ds_checked.add(ds_name)
        if _dataset_exists(ds_name):
            data = _get_string_dataset(ds_name=ds_name)
            if data is not None:
                try:
                    nisarqa.Version.from_string(version_str=data)
                except ValueError:
                    log.error(
                        f"Dataset value is {data}, must follow version format"
                        f" MAJOR.MINOR.PATCH. Dataset: {_full_path(ds_name)}"
                    )
                    passes = False
            else:
                passes = False

    # Verify datetime Datasets
    ds_name = "processingDateTime"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_string_dataset(ds_name=ds_name)
        if data is not None:
            passes &= nisarqa.verify_nisar_datetime_string_format(
                datetime_str=data,
                dataset_name=_full_path(ds_name),
                precision="seconds",
            )
        else:
            passes = False

    if product_type.lower() in nisarqa.LIST_OF_INSAR_PRODUCTS:
        dt_datasets = (
            "referenceZeroDopplerStartTime",
            "secondaryZeroDopplerStartTime",
            "referenceZeroDopplerEndTime",
            "secondaryZeroDopplerEndTime",
        )
    else:
        dt_datasets = (
            "zeroDopplerStartTime",
            "zeroDopplerEndTime",
        )

    for ds_name in dt_datasets:
        ds_checked.add(ds_name)
        if _dataset_exists(ds_name):
            data = _get_string_dataset(ds_name=ds_name)
            if data is not None:
                passes &= nisarqa.verify_nisar_datetime_string_format(
                    datetime_str=data,
                    dataset_name=_full_path(ds_name),
                    precision="nanoseconds",
                )
            else:
                passes = False

    # These are datasets which need more-robust pattern-matching checks.
    # For now, just check that they are being populated with a non-dummy value.
    for ds_name in (
        "compositeReleaseId",
        "granuleId",
        "missionId",
        "plannedObservationId",
        "processingCenter",
        "listOfFrequencies",
        "boundingPolygon",
        "instrumentName",
        "plannedDatatakeId",
        "productDoi",
    ):
        ds_checked.add(ds_name)
        if _dataset_exists(ds_name):
            data = _get_string_dataset(ds_name=ds_name)
            if data is not None:
                # TODO: Use a regex for more flexible pattern matching.
                if data in ("", "0", "['0']", "['']", "['' '' '' '' '']"):
                    log.error(
                        f"Dataset value is {data!r}, which is not a valid value."
                        f" Dataset: {_full_path(ds_name)}"
                    )
                    passes = False
                else:
                    log.warning(
                        f"Dataset value is {data!r}, but it has not be automatically"
                        f" verified during checks. Dataset: {_full_path(ds_name)}"
                    )
            else:
                passes = False

    # Log if any Datasets were not verified
    keys_in_product = set(id_group.keys())
    difference = keys_in_product - ds_checked
    if len(difference) > 0:
        log.warning(
            "Datasets found in product's `identification` group but not"
            f" verified: {difference}"
        )

    summary = nisarqa.get_summary()
    if passes:
        summary.check_identification_group(result="PASS")
    else:
        summary.check_identification_group(result="FAIL")


__all__ = nisarqa.get_all(__name__, objects_to_skip)
