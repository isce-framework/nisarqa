#!/usr/bin/env python

import argparse
import os
import warnings
from collections.abc import Iterable

import h5py
import numpy as np

import nisarqa


def _doc_order(prod_type: str) -> str:
    """
    Return the document order code corresponding to a given product type.

    Parameters
    ----------
    prod_type : str
        Product type name. Supported values are:
        "RSLC", "GSLC", "GCOV", "RIFG", "RUNW", "GUNW", "ROFF", "GOFF".

    Returns
    -------
    str
        A single-letter code ("a"-"h") representing the order for the
        product type's HDF5 Markdown spec to appear in the directory.
        Example: RSLC should appear first, so it is assigned the letter "a".
    """

    prod_type = prod_type.lower()
    if prod_type == "rslc":
        return "a"
    elif prod_type == "gslc":
        return "b"
    elif prod_type == "gcov":
        return "c"
    elif prod_type == "rifg":
        return "d"
    elif prod_type == "runw":
        return "e"
    elif prod_type == "gunw":
        return "f"
    elif prod_type == "roff":
        return "g"
    elif prod_type == "goff":
        return "h"
    else:
        raise ValueError("Unsupported product type.")


def _freqs(prod_type: str) -> list[str]:
    """
    Return the list of possible frequency group names for the product type.

    Parameters
    ----------
    prod_type : str
        Product type name. Supported values are:
        "RSLC", "GSLC", "GCOV", "RIFG", "RUNW", "GUNW", "ROFF", "GOFF".

    Returns
    -------
    list of str
        List of frequency group names, e.g. ["frequencyA", "frequencyB"].
    """
    prod_type = prod_type.lower()
    if prod_type in ("rslc", "gslc", "gcov"):
        freqs = nisarqa.NISAR_FREQS
    elif prod_type in nisarqa.LIST_OF_INSAR_PRODUCTS:
        freqs = ["A"]
    else:
        raise ValueError("Unsupported product type.")

    return [f"frequency{f}" for f in freqs]


def _pols(prod_type: str) -> list[str]:
    """
    Return the list of possible polarization group names for the product type.

    Parameters
    ----------
    prod_type : str
        Product type name. Supported values are:
        "RSLC", "GSLC", "GCOV", "RIFG", "RUNW", "GUNW", "ROFF", "GOFF".

    Returns
    -------
    list of str
        List of polarization (or term) group names.
        For non-GCOV, this will be e.g. ["HH", "HV"].
        For GCOV, this will be e.g. ["HHHH", "HVHV"].
    """
    prod_type = prod_type.lower()
    return list(nisarqa.get_possible_pols(prod_type))


def _layers(prod_type: str) -> list[str]:
    """
    Return the list of possible layer group names for the product type.

    Parameters
    ----------
    prod_type : str
        Product type name. Supported values are: "ROFF", "GOFF".

    Returns
    -------
    list of str
        List of frequency group names, e.g. ["layer1", "layer2"].
    """
    prod_type = prod_type.lower()
    if prod_type not in ("roff", "goff"):
        raise ValueError(f"{prod_type=}, must be either ROFF or GOFF.")

    layers = list(nisarqa.NISAR_LAYERS)
    # Assert that the formatting of nisarqa.NISAR_LAYERS is as expected
    assert "layer1" in layers
    return layers


def _reformat(names: Iterable[str]) -> str:
    """
    Format sequence of names as a comma-separated string, enclosed in backticks.

    Parameters
    ----------
    names : Iterable of str
        Sequence of names to format. Example: ["HH", "HV"].

    Returns
    -------
    str
        A single string with each name enclosed in backticks and separated
        by commas. Example: "`HH`, `HV`".
    """
    reformatted = [f"`{n}`" for n in names]

    return ", ".join(reformatted)


def get_header(product_type: str) -> str:
    """
    Generate a formatted header for the Markdown file to detail the QA HDF5.

    Parameters
    ----------
    product_type : str
        Product type name. Supported values include:
        "RSLC", "GSLC", "GCOV", "RIFG", "RUNW", "GUNW", "ROFF", "GOFF".

    Returns
    -------
    str
        A formatted Markdown string describing the possible groups
        and data structures that may appear in the QA HDF5 file for
        the specified product type.

    Notes
    -----
    The generated header includes sections for:
        - Frequency groups (based on available bands)
        - Polarization or covariance term groups
        - Calibration tool groups (for RSLC and GSLC)
        - Layer groups (for ROFF and GOFF)
    """
    product_type = product_type.lower()

    header = (
        f"\n## {product_type.upper()} QA HDF5 Contents"
        f"\n\nEach QA HDF5 file includes a subset of the available options"
        " below, which will correspond to the available frequencies,"
        f" polarizations, etc. in the input {product_type.upper()} granule."
        f"\n\n* Possible Frequency groups: {_reformat(_freqs(product_type))}"
    )

    if product_type == "gcov":
        header += (
            "\n\n* Possible On- and Off-diagonal Covariance Term groups:"
            f" {_reformat(_pols(product_type))}"
        )

        pols = [p[:2] for p in _pols(product_type) if p[:2] == p[:-2]]
        header += (
            "\n\n* Possible Polarization groups (for e.g. calibration"
            f" information): {_reformat(pols)}"
        )

    else:
        header += (
            "\n\n* Possible Polarization groups:"
            f" {_reformat(_pols(product_type))}"
        )

    if product_type in ("rslc", "gslc"):
        grps = ("`pointTargetAnalyzer`",)
        abscal = ""
        if product_type == "rslc":
            grps += (
                "`absoluteRadiometricCalibration`",
                "`noiseEquivalentBackscatter`",
            )
            abscal = "and AbsCal "

        header += (
            f"\n\n* Possible CalTools groups: {', '.join(grps)}"
            f"\n   - Note: PTA {abscal}results only possible for granules"
            " over designated calibration sites."
        )

    if product_type in ("roff", "goff"):
        header += (
            f"\n\n* Possible layer groups: {_reformat(_layers(product_type))}"
        )

    header += "\n\n"

    return header


def get_spec_table(input_file: str, product_type: str) -> str:
    """
    Generate a Markdown-formatted table with the contents of a NISAR QA HDF5.

    This function inspects the structure and attributes of an input QA HDF5
    file and produces a formatted Markdown table summarizing datasets,
    attributes, and metadata.

    It is used to create detailed documentation tables for QA product
    specifications.

    Parameters
    ----------
    input_file : str
        Path to the input QA HDF5 file.
    product_type : str
        Product type name. Supported values include:
        "RSLC", "GSLC", "GCOV", "RIFG", "RUNW", "GUNW", "ROFF", "GOFF".

    Returns
    -------
    str
        Markdown-formatted specification table describing the datasets
        contained within the input QA HDF5 file, including their
        attributes and metadata.

    Notes
    -----
    The output Markdown includes:
        - Global (root-level) attributes
        - Dataset paths, dimensions, and data types
        - Dataset-specific attributes
        - Selective filtering to include only one representative
          frequency, polarization, or layer group.
    """

    def _get_string_rep(val: np.bytes_) -> str:
        """
        Convert a Fixed-length byte-string to a standard Python string object.
        """
        if np.issubdtype(val.dtype, np.bytes_):
            return nisarqa.byte_string_to_python_str(val)
        else:
            raise TypeError("NOT A STRING! OH NO! ", val)

    with h5py.File(input_file, "r") as in_f:

        # Table header for Markdown file
        spec = [
            (
                f"\n|     | {product_type.upper()} QA HDF5 Datasets,"
                " Attributes, and Additional Metadata |"
                "\n| :---: | --------------------------------------- |"
            )
        ]

        # Add Global Attributes section
        spec.append(f"\n| Path | **`/` _(Root Group - Global Attributes)_** |")
        obj = in_f["/"]
        for key, val in obj.attrs.items():
            spec.append(f"\n|    | _{key}:_ {_get_string_rep(val)} |")
        spec.append("\n|     |     |    |")

        # Add datasets and their attributes

        # Lists to track which datasets must be included or excluded.
        must_include = []
        do_not_include = []
        prod_type = product_type.upper()

        # Identify mandatory dataset paths based on product type.
        if prod_type == "RSLC":
            must_include += [
                "/absoluteRadiometricCalibration/data/",
                "/noiseEquivalentBackscatter/data/",
            ]
        if prod_type in ("RSLC", "GSLC"):
            must_include += ["/pointTargetAnalyzer/data/"]

        def _include(grp_to_display: str, all_grps: list[str]) -> None:
            """
            Mark one group for inclusion and exclude all others.

            Parameters
            ----------
            grp_to_display : str
                The name of the group to which is required to be included
                in the specification.
            all_grps : list of str
                List of all possible group names, including `grp_to_display`.
                The `grp_to_display` will be added to `must_include`,
                and all others to `do_not_include`.
            """
            nonlocal must_include, do_not_include
            if grp_to_display not in all_grps:
                raise ValueError(f"{grp_to_display=}, must be in {all_grps=}")
            must_include += [f"/{grp_to_display}/"]
            # Make a shallow copy to avoid mutating the input list.
            dup = list(all_grps)
            dup.remove(grp_to_display)
            do_not_include += [f"/{d}/" for d in dup]

        # Include only one representative frequency, polarization, and layer
        # group for brevity in the generated documentation.
        _include(grp_to_display="frequencyA", all_grps=_freqs(prod_type))

        # QA HDF5 for all product types have "HH" polarization groups.
        # (Even though GCOV uses terms (e.g. "HHHH") for its image layers,
        # its RFI group contains pols, e.g. ../frequencyA/HH/rfiLikelihood.)
        if prod_type == "GCOV":
            pols = [p[:2] for p in _pols(prod_type) if p[:2] == p[:-2]]
        else:
            pols = _pols(prod_type)
        _include(grp_to_display="HH", all_grps=pols)

        if prod_type == "GCOV":
            _include(grp_to_display="HHHH", all_grps=_pols(prod_type))

        if prod_type in ("ROFF", "GOFF"):
            _include(grp_to_display="layer1", all_grps=_layers(prod_type))

        def build_spec(name):
            """
            Visitor function used with `h5py.File.visit` to build the
            specification table for all datasets.

            Parameters
            ----------
            name : str
                Full HDF5 path for the object being visited.

            Notes
            -----
            - Only includes datasets matching paths in `must_include`.
            - Skips datasets under groups listed in `do_not_include`.
            - Records dataset name, dimensionality, dtype, and attributes.
            """
            for required in must_include:
                if required in name:
                    must_include.remove(required)
            for skip in do_not_include:
                if skip in name:
                    return

            obj = in_f[name]
            if isinstance(obj, h5py.Dataset):
                spec.append(f"\n| Path | **`{name}`** |")

                # Retrieve dataset dtype and format for display.
                dtype = obj.dtype
                if np.issubdtype(dtype, np.bytes_):
                    dtype = "fixed-length byte string"

                # Describe dataset dimensionality.
                ndim = obj.ndim
                if ndim == 0:
                    ndim = "scalar"
                else:
                    ndim = f"{ndim}-D array"

                # Append dataset summary
                spec.append(
                    f"\n|    | {prod_type.upper()} QA dataset, **ndim:** {ndim}, **dtype:** {dtype} |"
                )

                # Iterate through each dataset attribute and add to the
                # Markdown table.
                for key, val in obj.attrs.items():
                    if key == "subswathStartIndex":
                        v = (
                            "Starting index for the subswath used to"
                            " generate this plot"
                        )
                    elif key == "subswathStopIndex":
                        v = (
                            "Stopping index for the subswath used to"
                            " generate this plot"
                        )
                    elif key == "epsg":
                        v = "EPSG code"
                    elif key == "frameCoveragePercentage":
                        v = "Percentage of NISAR frame containing processed data"
                    elif key == "thresholdPercentage":
                        v = (
                            "Threshold percentage used to determine if"
                            " the product is full frame or partial frame"
                        )
                    else:
                        try:
                            v = _get_string_rep(val)
                        except TypeError:
                            print(f"NOT A STRING! OH NO! {key=}, {val=}")
                        except AttributeError:
                            # Attribute has missing dtype
                            # (Likely, it is a variable-length string)
                            v = val
                    if key == "units" and v.startswith("seconds since"):
                        if "zeroDopplerTime" in name:
                            v = "seconds since YYYY-mm-ddTHH:MM:SS"
                        else:
                            raise ValueError("ACK")

                    # Escape Markdown-sensitive characters.
                    v = v.replace("<", r"\<")
                    v = v.replace(">", r"\>")

                    spec.append(f"\n|    | _{key}:_ {v} |")

        in_f.visit(build_spec)

    spec.append("\n\n\n")
    if must_include != []:
        raise ValueError(
            "Input QA product is missing datasets that under these"
            f" groups which are required for the spec: {must_include}"
        )

    return "".join(spec)


def main(input_file: str, out_dir: str) -> None:

    # Get the product type
    with h5py.File(input_file, "r") as in_f:
        product_type = in_f["/science/LSAR/identification/productType"][()]
    product_type = nisarqa.byte_string_to_python_str(product_type)
    product_type = product_type.lower()

    if not out_dir.endswith("docs/product_specs"):
        warnings.warn(
            f"{out_dir=}, suggest using nisarqa's `docs/product_specs`"
            " directory instead to overwrite existing versions of the HDF5"
            " product spec Markdown files.",
            RuntimeWarning,
        )

    filename = os.path.join(
        out_dir, f"05{_doc_order(product_type)}_{product_type}_qa_hdf5_spec.md"
    )

    with open(filename, "w") as out_f:
        out_f.write(get_header(product_type=product_type))

        out_f.write(
            get_spec_table(input_file=input_file, product_type=product_type)
        )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate HDF5 specs of input QA file in markdown."
    )
    parser.add_argument(
        "filename",
        help=(
            "Path to input QA HDF5 file to parse the product type and its"
            " HDF5 product structure from"
        ),
    )
    parser.add_argument(
        "out_dir",
        help=(
            "Path to output directory to store the final Markdown file"
            " containing the header and QA HDF5 file structure"
        ),
    )

    args = parser.parse_args()
    input_file = args.filename
    out_dir = args.out_dir

    main(input_file, out_dir)
