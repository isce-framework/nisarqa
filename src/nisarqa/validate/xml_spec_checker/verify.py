from __future__ import annotations

import os
from collections.abc import Mapping, Iterable
from typing import Optional

import nisarqa

# List of objects from the import statements that
# should not be included when importing this module
objects_to_skip = nisarqa.get_all(name=__name__)


def verify_file_against_xml(
    input_file: str | os.PathLike,
    product_type: str,
    product_spec_version: str,
    freq_pols: Mapping[str, Iterable[str]],
    layer_groups: Iterable[str] | None = None,
) -> None:
    """
    Verify input HDF5 file meets the XML product specifications document.

    Parameters
    ----------
    input_file : path-like
        Filepath to the input product.
    product_type : str
        One of: 'rslc', 'gslc', 'gcov', 'rifg', 'runw', 'gunw', 'roff', 'goff'.
    product_spec_version : str
        Contents of `../identification/productSpecificationVersion` from input
        file. Examples: "0.0.9", "1.1.0"
    freq_pols : Mapping[str, Iterable[str]]
        Dict of the expected frequency + polarization combinations that the
        input NISAR product says it contains.
            Example: { "A" : ["HH", "HV], "B" : ["VV", "VH"] }
    valid_layers : Iterable[str] or None, optional
        ROFF and GOFF products contain HDF5 datasets referred to as "layer number
        datasets" (e.g. `../layer1/..`, `../layer3/..`).
        This parameter should be a set of all valid layer groups for this product,
        e.g., {'layer1', 'layer2', 'layer3'}, or None.
        If None, layer datasets will not be checked. Defaults to None.
    """
    log = nisarqa.get_logger()

    # Validate inputs
    if product_type.lower() not in nisarqa.LIST_OF_NISAR_PRODUCTS:
        raise ValueError(
            f"`{product_type=}`; must one of: {nisarqa.LIST_OF_NISAR_PRODUCTS}"
        )

    if product_type in ("roff", "goff"):
        if layer_groups is None:
            raise ValueError(
                f"{product_type=}, so `layer_numbers` cannot be None."
            )
        elif not isinstance(layer_groups, Iterable):
            msg = (
                f"`{layer_groups=}` and has type `{type(layer_groups)}`,"
                " but must be an iterable."
            )
            raise TypeError(msg)
        elif not all(isinstance(n, str) for n in layer_groups):
            msg = (
                f"`{layer_groups=}`, but must be an iterable of strings"
                " for ROFF and GOFF products."
            )
            raise ValueError(msg)
        elif not all(n.startswith("layer") for n in layer_groups):
            msg = (
                f"`{layer_groups=}`, but all layer group must all start"
                " with 'layer'."
            )
            raise ValueError(msg)
        elif not all(
            ((int(n[5:]) > 0) and (int(n[5:]) < 9)) for n in layer_groups
        ):
            msg = (
                f"`{layer_groups=}`, but the layer groups' numbers must"
                " all be within range [1, 8]."
            )
            raise ValueError(msg)
    else:
        if layer_groups is not None:
            raise ValueError(
                f"`{product_type=}` which should not have layer number groups,"
                f" but input parameter `{layer_groups=}`. `layer_numbers` is"
                " only used in the case of ROFF and GOFF products. Please"
                " check that this is intended; if not, set `layer_numbers` to"
                " None."
            )

    if product_type in ("roff", "goff"):
        log.info(
            f"Verification of HDF5 against XML will check for these numbered"
            f" layer groups: {layer_groups}"
        )

    log.info(f"Checking product version against supported versions.")
    xml_version = nisarqa.get_xml_version_to_compare_against(
        nisarqa.Version.from_string(product_spec_version)
    )

    xml_filepath = nisarqa.locate_spec_xml_file(
        product_type=product_type,
        version=xml_version,
    )
    log.debug(
        "Validating input HDF5 product against XML spec located at:"
        f" {xml_filepath}"
    )

    nisarqa.check_hdf5_against_xml(
        product_type=product_type,
        xml_file=xml_filepath,
        hdf5_file=input_file,
        valid_freq_pols=freq_pols,
        valid_layers=layer_groups,
        valid_subswaths=[],
    )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
