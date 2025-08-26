from __future__ import annotations

import re
from collections.abc import Container

import h5py
import numpy as np

import nisarqa
from nisarqa.utils.typing import T

objects_to_skip = nisarqa.get_all(name=__name__)


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

    def _get_string_dataset(ds_name: str) -> str | list[str] | None:
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
        value: T | None,
        valid_options: Container[T],
        ds_name: str,
    ) -> bool:
        if (value is None) or (value not in valid_options):
            log.error(
                f"Dataset value is {value!r}, must be one of"
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
            # Only support "Nominal", "Urgent", and "Custom" values.
            # As of product specs v1.3.0, "Undefined" was removed,
            # so all products generated via nominal NISAR mission operations
            # should not have "Undefined".
            # Very few (if any) older test datasets used "Undefined", so it is
            # not worth the added code complexity to handle older test datasets.
            # Simply let it be logged as a false-negative.
            valid_options=("Nominal", "Urgent", "Custom"),
            ds_name=ds_name,
        )

    ds_name = "compositeReleaseId"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_string_dataset(ds_name=ds_name)
        if data is not None:
            passes &= _is_valid_crid(data, path_in_h5=_full_path(ds_name))
        else:
            passes = False

    for ds_name in ("missionId", "platformName"):
        ds_checked.add(ds_name)
        if _dataset_exists(ds_name):
            data = _get_string_dataset(ds_name=ds_name)
            if data is not None:
                if data != "NISAR":
                    log.error(
                        f"Dataset value is {data!r} but should be 'NISAR' for nominal"
                        " NISAR mission operations. (Ignore if data"
                        " is from a different mission, e.g. ALOS or UAVSAR.)"
                        f" Dataset: {_full_path(ds_name)}"
                    )
                    passes = False
            else:
                passes = False

    ds_name = "processingCenter"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_string_dataset(ds_name=ds_name)
        passes &= _verify_data_is_in_list(
            value=data,
            valid_options=("JPL", "ISRO"),
            ds_name=ds_name,
        )

    ds_name = "instrumentName"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_string_dataset(ds_name=ds_name)
        passes &= _verify_data_is_in_list(
            value=data,
            valid_options=("L-SAR", "S-SAR"),
            ds_name=ds_name,
        )

    ds_name = "productDoi"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_string_dataset(ds_name=ds_name)
        if data is not None:
            passes &= _is_valid_nisar_doi(
                doi=data,
                product_type=product_type,
                path_in_h5=_full_path(ds_name),
            )
        else:
            passes = False

    if product_type.lower() in nisarqa.LIST_OF_INSAR_PRODUCTS:
        obs_modes = [
            "referenceListOfObservationModes",
            "secondaryListOfObservationModes",
        ]
    else:
        obs_modes = ["listOfObservationModes"]
    for ds_name in obs_modes:
        ds_checked.add(ds_name)
        if _dataset_exists(ds_name):
            data = _get_string_dataset(ds_name=ds_name)
            if data is not None:
                if isinstance(data, str):
                    log.error(
                        f"Dataset is a scalar, but should be a list."
                        f" Dataset: {_full_path(ds_name)}"
                    )
                    passes = False
                    data = [data]
                for obs_mode in data:
                    passes &= _is_valid_observation_mode(
                        obs_mode, path_in_h5=_full_path(ds_name)
                    )
            else:
                passes = False

    ds_name = "listOfFrequencies"
    ds_checked.add(ds_name)
    if _dataset_exists(ds_name):
        data = _get_string_dataset(ds_name=ds_name)
        if data is not None:
            if isinstance(data, str):
                log.error(
                    f"`{ds_name}` is the scalar {data!r}, but should be a list."
                    f" Dataset: {_full_path(ds_name)}"
                )
                passes = False
                data = [data]
            if not set(data).issubset({"A", "B"}):
                log.error(
                    f"Dataset contains {data}, must be a subset of"
                    f" {{'A', 'B'}}. Dataset: {_full_path(ds_name)}"
                )
                passes = False
            if nisarqa.contains_duplicates(data):
                log.error(
                    f"Dataset contains duplicate values: {data}."
                    f" Dataset: {_full_path(ds_name)}"
                )
                passes = False
        else:
            passes = False

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
    misc_ds = [
        "granuleId",
        "boundingPolygon",
    ]
    if product_type.lower() in nisarqa.LIST_OF_INSAR_PRODUCTS:
        misc_ds += [
            "referencePlannedDatatakeId",
            "secondaryPlannedDatatakeId",
            "referencePlannedObservationId",
            "secondaryPlannedObservationId",
        ]
    else:
        misc_ds += [
            "plannedDatatakeId",
            "plannedObservationId",
        ]

    for ds_name in misc_ds:
        ds_checked.add(ds_name)
        if _dataset_exists(ds_name):
            data = _get_string_dataset(ds_name=ds_name)
            if data is not None:
                # TODO: Use a regex for more flexible pattern matching.
                if data in (
                    "",
                    "0",
                    "['0']",
                    "['']",
                    "['' '' '' '' '']",
                    "None",
                    "(NOT SPECIFIED)",
                ):
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


def _is_valid_crid(crid: str, path_in_h5: str) -> bool:
    """
    True if Composite Release ID (CRID) is in the correct format; False o/w.

    Parameters
    ----------
    crid : str
        The composite release ID, per specification in docstring Notes section.
    path_in_h5 : str
        Full path in the HDF5 for the composite release ID. (Used for logging.)

    Returns
    -------
    passes : bool
        True if `crid` is in the correct format.

    Notes
    -----
    As of July 2025, CRID convention for R5 and later (corresponds to product
    specification version 1.3.0 or later):

        EMMmmp
            Environment
                A = ADT
                D = Development
                T = Test
                P = Prod
                S = Science Ondemand
                E or Q = Engineering or Quick-turnaround (TBD)
            Major has 2 numerical digits
            minor has 2 numerical digits
            patch has 1 numerical digit
        Example: P05000 for R05.00.0

    CRID convention for R4.0.8 or earlier:

        ESMMmp
            Environment
                A = ADT
                D = Development
                T = Test
                P = Prod
                S = Science Ondemand
            Spare has 1 numerical digit (was previously used to denote
                0 = prelaunch, 1 = launch, but decided that it was unnecessary
                and was changed to spare)
            Major has 2 numerical digits
            minor has 1 numerical digits
            patch has 1 numerical digit
        Example: P00408 for R4.0.8

    Source: https://wiki.jpl.nasa.gov/display/NISARSDS/CRID+release+notification+process
    """
    pattern = r"^[ADTPSEQ]\d{5}$"
    correct = re.fullmatch(pattern, crid) is not None
    if not correct:
        nisarqa.get_logger().error(
            f"Dataset value is {crid}, which does not match a pattern like"
            f" e.g. 'P05000' or 'P00408'. Dataset: {path_in_h5}"
        )

    return correct


def _is_valid_observation_mode(obs_mode: list[str], path_in_h5: str) -> bool:
    """
    True if `obs_mode` follows the expected pattern; False otherwise.

    Parameters
    ----------
    obs_mode : str
        A single observation mode string, per specification in docstring
        Notes section.
    path_in_h5 : str
        Full path in the HDF5 to the dataset containing the observation mode.
        (Used for logging.)

    Returns
    -------
    passes : bool
        True if `obs_mode` is in the correct format.

    Notes
    -----
    As of Aug 2025, there are different string format conventions for
    L-band only, S-band only, and joint L- and S-band observations.

    L-band only:
        Examples:
            L:SCI:DH:40M+05N:FS:B4:D02
            L:ENG:NO:77M+---:HS:B16:F10

        Format:
            <band>:<phase>:<mode>:<main><pulse>+<side><pulse>:<swath>:<bits>:<prf>

        <band> : L for L-band
        <phase> : SCI (Science)
                  ENG (Engineering)
                  PST (Post Take)
                  PRE (PRE take)
                  DM1 (Diagnostic Mode 1)
                  DM2 (Diagnostic Mode 2)
                  CAN (Super Canned)
                  TST (Test mode)
        <mode> : SH (Single Pol HH)
                 SV (Single Pol VV)
                 DH (Dual Pol H-transmit)
                 DV (Dual Pol HH/HV)
                 QP (Quad Pol)
                 CP (Compact Pol)
                 QQ (Quasi Quad)
                 QD (Quasi Dual HH/VV)
                 NO (Rx Only H, Rx Only V, or Qx Only HV)
        <main> : Main band's range bandwidth. One of: 05, 40, 20, 77
        <pulse> : Pulse width of main band.
                  One of: N (Narrow), M (Medium), or W (Wide), or F (???)
                  Example: L:CAN:DH:77F+---:FS:B4:D01
        <side> : Side band's range bandwidth.
                 One of: 05, 20, or -- (not acquired)
        <pulse> : Pulse width of side band
                  One of: N (Narrow), M (Medium), W (Wide), - (not acquired)
        <swath> : FS (Full Swath) or HS (Half Swath)
        <bits> : Bits per sample. One of: B3, B4, B8, B12, B16
        <prf> : PRF with version
                First character is one of: F (Fixed) or D (Dithered)
                Second two characters XX denote the version of Fixed or
                Dithered PRF. (Both Fixed and Dithered have different versions
                such as PRF and Dithered sequence.)
                Example: D02 denotes "Dithered PRF Sequence number 2"

    S-band only:
        Examples:
            S:DB:DH:10W:B4:F04
            S:--:DX:75W:B8:F06
            S:NR:DH:10N:B4:F05

        Format:
            <band>:<tbd>:<mode>:<bandwidth><pulse>:<bits>:<prf>

        <band> : S for S-band
        <tbd> : One of: DB, NR, DR, --,
        <mode> : SH, SV, DH, DV, DX, QQ, CP, FP
        <main> : Range bandwidth. One of: 10, 25, 37, 75
        <pulse> : Pulse width. One of: N (Narrow) or W (Wide)
        <bits> : Bits per sample. One of: B4, B3, B8
        <prf> : PRF with version
                First character is one of: F (Fixed) or D (Dithered)
                Second two characters XX denote the version of Fixed or
                Dithered PRF. (Both Fixed and Dithered have different versions
                such as PRF and Dithered sequence.)
                Example: D02 denotes "Dithered PRF Sequence number 2"

    Joint L- and S-band:
        Examples:
            L:SCI:DV:05W+---:FS:B4:F04  S:DB:CP:25W:B4
            L:PST:CP:77M+---:FS:B4:F04  S:--:DX:75W:B8

        Format:
            <L-band observation mode>  <S-band observation mode>

        Where <L-band observation mode> is formatted per the conventions above.
        and <S-band observation mode> is formatted per the conventions above
        but without the <prf> ending.
    """
    # ----- L-band only -----
    l_band_pattern = re.compile(
        r"^L:"  # startswith L:
        r"(SCI|ENG|PST|PRE|DM1|DM2|CAN|TST):"  # phase
        r"(SH|SV|DH|DV|QP|CP|QQ|QD|NO):"  # mode
        r"(05|20|40|77)(N|M|W|F)\+"  # main bandwidth + pulse
        r"(05|20|--)(N|M|W|-):"  # side bandwidth + pulse
        r"(FS|HS):"  # swath
        r"(B3|B4|B8|B12|B16):"  # bits
        r"(F|D)\d{2}$"  # endswith PRF
    )

    # ----- S-band only -----
    s_band_pattern = re.compile(
        r"^S:"  # startswith S:
        r"(DB|NR|DR|--):"  # ???
        r"(SH|SV|DH|DV|DX|QQ|FP|CP):"  # mode
        r"(10|25|37|75)(N|W):"  # bandwidth + pulse
        r"(B3|B4|B8):"  # bits
        r"(F|D)\d{2}$"  # endswith PRF
    )

    # ----- Joint L- and S-band -----
    # (L-band regex + whitespace + S-band regex without PRF)
    joint_pattern = re.compile(
        l_band_pattern.pattern[:-1]  # L-band without endswith "$"
        + r"\s+"  # whitespace
        + s_band_pattern.pattern[1:-12]  # S-band regex without "^" and "<prf>$"
        + r"$"  # re-append the endswith "$"
    )

    # check against all three
    correct = (
        l_band_pattern.match(obs_mode) is not None
        or s_band_pattern.match(obs_mode) is not None
        or joint_pattern.match(obs_mode) is not None
    )
    if not correct:
        nisarqa.get_logger().error(
            f"Dataset contains value {obs_mode}, which does not match"
            " a pattern like e.g. `L:SCI:DH:40M+05N:FS:B4:D02`."
            f" Dataset: {path_in_h5}"
        )

    return correct


def _is_valid_nisar_doi(
    *, doi: str, product_type: str, path_in_h5: str
) -> bool:
    """
    True if `doi` follows NISAR DOI format for L1/L2 products; False otherwise.

    Parameters
    ----------
    doi : str
        A DOI string in NISAR DOI format for L1/L2 products (see Notes).
    product_type : str
        One of: 'rslc', 'gslc', 'gcov', 'rifg', 'runw', 'gunw', 'roff', 'goff',
        or their uppercase variants.
    path_in_h5 : str
        Full path in the HDF5 to the DOI's Dataset. (Used for logging.)

    Returns
    -------
    passes : bool
        True if `doi` follows the NISAR conventions for L1/L2 DOIs;
        False otherwise.

    Notes
    -----
    NISAR L1/L2 products follow the following conventions for DOI:

        10.5067/NI<level><product>-<maturity><version>

    where:
        <level> is either "L1" (level-1 products) or "L2" (level-2 products)
        <product> is the 4-character product type in all caps
        <maturity> is either "B" (Beta), "P" (Provisional), or "V" (Version)
        <version> is a single character, starting with 1

    Example L1: RIFG
    DOI                   CMR Short Name
    10.5067/NIL1RIFG-B1   NISAR_L1_RIFG_BETA_V1
    10.5067/NIL1RIFG-P1   NISAR_L1_RIFG_PROVISIONAL_V1
    10.5067/NIL1RIFG-V1   NISAR_L1_RIFG_V1

    Example L2: GCOV
    DOI                   CMR Short Name
    10.5067/NIL2GCOV-B1   NISAR_L2_GCOV_BETA_V1
    10.5067/NIL2GCOV-P1   NISAR_L2_GCOV_PROVISIONAL_V1
    10.5067/NIL2GCOV-V1   NISAR_L2_GCOV_V1
    Source: https://wiki.jpl.nasa.gov/display/NISARSDS/Digital+Object+Identifiers+DOIs
    """

    # Build regex dynamically based on product types
    pattern = (
        rf"^10\.5067/NI"  # DOI prefix
        rf"(L1|L2)"  # Level
        rf"{product_type.upper()}"  # Product type
        rf"-"
        rf"(B|P|V)"  # Maturity
        rf"[1-9]$"  # Version (1–9)
    )

    correct = re.fullmatch(pattern, doi) is not None

    if not correct:
        nisarqa.get_logger().error(
            f"Dataset contains value {doi!r}, but must follow NISAR"
            " conventions for L1/L2 DOIs, e.g. '10.5067/NIL2GCOV-V1'."
            f" Dataset: {path_in_h5}"
        )

    return correct


__all__ = nisarqa.get_all(__name__, objects_to_skip)
