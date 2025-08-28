import warnings
import h5py
import os
import argparse
import numpy as np
import nisarqa


def _doc_order(prod_type: str) -> str:
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
    prod_type = prod_type.lower()
    if prod_type in ("rslc", "gslc", "gcov"):
        freqs = nisarqa.NISAR_FREQS
    elif prod_type in nisarqa.LIST_OF_INSAR_PRODUCTS:
        freqs = ["A"]
    else:
        raise ValueError("Unsupported product type.")

    freqs = [f"`frequency{f}`" for f in freqs]
    return ", ".join(freqs)


def _pols(prod_type: str) -> list[str]:
    prod_type = prod_type.lower()
    pols = [f"`{p}`" for p in nisarqa.get_possible_pols(prod_type)]
    return ", ".join(pols)


def get_header(product_type: str) -> str:

    product_type = product_type.lower()

    header = (
        f"\n## {product_type.upper()} QA HDF5 Contents"
        f"\n\nEach QA HDF5 file includes a subset of the available options"
        " below, which will correspond to the available frequencies,"
        f" polarizations, etc. in the input {product_type.upper()} product."
        f"\n\n* Possible Frequency Groups: {_freqs(product_type)}"
    )

    if product_type == "gcov":
        header += (
            "\n\n* Possible On- and Off-diagonal Covariance Term Groups:"
            f" {_pols(product_type)}"
        )
    else:
        header += f"\n\n* Possible Polarization Groups: {_pols(product_type)}"

    if product_type in ("rslc", "gslc"):
        grps = ("`pointTargetAnalyzer`",)
        if product_type == "rslc":
            grps += (
                "`absoluteRadiometricCalibration`",
                "`noiseEquivalentBackscatter`",
            )

        header += f"\n\n* Possible CalTools groups: {', '.join(grps)}"

    if product_type in ("roff", "goff"):
        layers = [f"`{l}`" for l in nisarqa.NISAR_LAYERS]
        header += f"\n\n* Possible layer Groups: {', '.join(layers)}"

    header += "\n\n"

    return header


def get_spec_table(input_file: str, product_type: str) -> str:
    """Generator to return the next Dataset from the input file"""

    def _get_string_rep(val):
        if np.issubdtype(val.dtype, np.bytes_):
            return nisarqa.byte_string_to_python_str(val)
        else:
            raise TypeError("NOT A STRING! OH NO! ", val)

    with h5py.File(input_file, "r") as in_f:

        # Table header for Markdown file
        spec = [
            (
                f"\n|     | {product_type.upper()} QA HDF5 Dataset, Attributes, and additional metadata |"
                "\n| :---: | --------------------------------------- |"
            )
        ]

        # # Global Attributes
        # spec.append(f"\n| Path: | **`/` _(Global Attributes)_** |")
        # obj = in_f["/"]
        # for key, val in obj.attrs.items():
        #     spec.append(f"\n|    | _{key}:_ {_get_string_rep(val)} |")
        # spec.append("\n|     |     |    |")

        # Datasets and their attributes
        def build_spec(name):
            obj = in_f[name]
            if isinstance(obj, h5py.Dataset):
                spec.append(f"\n| Path: | **`{name}`** |")
                spec.append(
                    f"\n|    | _Product type:_ {product_type.upper()} QA |"
                )
                for key, val in obj.attrs.items():
                    if key == "subswathStartIndex":
                        v = "Starting index for the subswath used to generate this plot"
                    elif key == "subswathStopIndex":
                        v = "Stopping index for the subswath used to generate this plot"
                    elif key == "epsg":
                        v = "EPSG code"
                    elif key == "frameCoveragePercentage":
                        v = "Percentage of NISAR frame containing processed data"
                    elif key == "thresholdPercentage":
                        v = "Threshold percentage used to determine if the product is full frame or partial frame"
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

                    # Escape special characters
                    v = v.replace("<", r"\<")
                    v = v.replace(">", r"\>")

                    spec.append(f"\n|    | _{key}:_ {v} |")

                # Include the dtype
                dtype = obj.dtype
                if np.issubdtype(dtype, np.bytes_):
                    dtype = "fixed-length byte string"
                spec.append(f"\n|    | _dtype:_ {dtype} |")

                # Include the number of dimensions
                ndim = obj.ndim
                if ndim == 0:
                    ndim = "scalar"
                else:
                    ndim = f"{ndim}-D array"
                spec.append(f"\n|    | _ndim:_ {ndim} |")

        in_f.visit(build_spec)

    spec.append("\n\n\n")

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
        out_dir, f"05{_doc_order(product_type)}_{product_type}_hdf5_spec.md"
    )

    with open(filename, "w") as out_f:
        out_f.write(get_header(product_type=product_type))

        out_f.write(
            get_spec_table(input_file=input_file, product_type=product_type)
        )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate HDF5 specs of input file in markdown."
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
            " containing the header and HDF5 file structure"
        ),
    )

    args = parser.parse_args()
    input_file = args.filename
    out_dir = args.out_dir

    main(input_file, out_dir)
