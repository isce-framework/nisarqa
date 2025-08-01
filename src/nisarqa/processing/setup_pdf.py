from __future__ import annotations

from datetime import datetime

import h5py
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


def add_metadata_to_report_pdf(
    product: nisarqa.NisarProduct, report_pdf: PdfPages
) -> None:
    """
    Add global PDF metadata to the report PDF.

    Parameters
    ----------
    product : nisarqa.NisarProduct
        Input NISAR product.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to set the global metadata for.

    See Also
    --------
    nisarqa.utils.stats_h5_writer.setup_writer.add_global_metadata_to_stats_h5
        Sister function which adds global metadata to the STATS.h5 file.
    """
    product_type = product.product_type.upper()

    # Set the PDF file's metadata via the PdfPages object:
    d = report_pdf.infodict()
    d["Title"] = "NISAR Quality Assurance Report"
    d["Author"] = "nisar-sds-ops@jpl.nasa.gov"
    d["Subject"] = (
        f"NISAR Quality Assurance Report on {product_type} HDF5 Product"
        f" with Granule ID {product.granule_id}"
    )
    d["Keywords"] = (
        f"NASA JPL NISAR Mission Quality Assurance QA {product_type}"
    )
    # A datetime object is required. (Not a string.)
    d["CreationDate"] = datetime.fromisoformat(nisarqa.QA_PROCESSING_DATETIME)
    d["ModDate"] = datetime.fromisoformat(nisarqa.QA_PROCESSING_DATETIME)


def add_title_page_to_report_pdf(
    product: nisarqa.NisarProduct, report_pdf: PdfPages
) -> None:
    """
    Add a title page with identification information to the report PDF.

    Parameters
    ----------
    product : nisarqa.NisarProduct
        Input NISAR product.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the PDF title page to.
    """
    product_type = product.product_type.upper()
    # Construct page title
    # granule IDs are very long. Split into two lines.
    gran_id = product.granule_id.split("_")
    gran_id_final = "_".join(gran_id[:11])
    if len(gran_id_final) < 40:
        # For e.g. GCOV, if the granule ID was not constructed it gets saved
        # as something like "(NOT SPECIFIED)", which is very short.
        table_pos_top = 0.9
    else:
        if isinstance(product, nisarqa.InsarProduct):
            gran_id_final += f"\n_{'_'.join(gran_id[11:13])}"
            gran_id_final += f"\n_{'_'.join(gran_id[13:15])}"
            gran_id_final += f"\n_{'_'.join(gran_id[15:])}"
            table_pos_top = 0.87
        else:
            gran_id_final += f"\n_{'_'.join(gran_id[11:])}"
            table_pos_top = 0.9

    subtitle = (
        f"$\\bf{{Input\ {product_type}\ HDF5\ Granule\ ID:}}$\n{gran_id_final}\n\n"
        f"$\\bf{{QA\ Software\ Version:}}$ {nisarqa.__version__}\n"
        f"$\\bf{{QA\ Processing\ Date:}}$ {nisarqa.QA_PROCESSING_DATETIME} UTC"
    )

    # Collect the metadata to be printed in the table on the title page.
    # As of Python 3.7, dictionaries guarantee insertion order.
    metadata = {}

    with h5py.File(product.filepath, "r") as in_f:

        metadata["softwareVersion"] = product.software_version

        id_group = in_f[product.identification_path]
        for key, val in id_group.items():
            if key == "granuleId":
                # granule ID is part of the title; do not repeat in the table
                continue

            # Read the value, then convert to its string representation
            v = val[()]

            if np.issubdtype(v.dtype, np.bytes_):
                # decode scalar byte strings and arrays of byte strings
                v = nisarqa.byte_string_to_python_str(v)

            v = str(v)

            if len(v) > 30:
                # Value is too long for a visually-appealing table.
                # Length of 30 looks ok (empirical testing), and nanosecond
                # precision datetime strings have length 29; if a "Z" is
                # appended to the datetimes, we're still ok.
                # (Matplotlib dynamically adjusts the fontsize based on the
                # lengths of the table's values. If any one of the values is
                # too long, it makes all of the text imperceptably small. Ugh.)
                # Examples that will be skipped: boundingPolygon, granuleId.
                continue
            metadata[key] = v

            # Include the list of polarizations after the list of frequencies
            if key == "listOfFrequencies":
                # Add lists of polarizations
                for f in nisarqa.NISAR_FREQS:
                    try:
                        pols = product.get_list_of_polarizations(freq=f)
                    except nisarqa.DatasetNotFoundError:
                        pols_val = "n/a"
                    else:
                        pols_val = f"{list(pols)!r}"
                    metadata[f"listOfPolarizations (frequency {f})"] = pols_val

                # Add lists of terms for GCOV
                if isinstance(product, nisarqa.GCOV):
                    for f in nisarqa.NISAR_FREQS:
                        try:
                            terms = product.get_list_of_covariance_terms(freq=f)
                        except nisarqa.DatasetNotFoundError:
                            terms_val = "n/a"
                        else:
                            # Baseline on-diagonal GCOV processing generates
                            # up to 4 terms. Typical on- and off- diagonal
                            # processing for quad-pol generates 10 terms.
                            # <=5 terms fits nicely on 1 line in the PDF,
                            # <=10 terms needs to have a newline inserted.
                            # Handle these cases.

                            if len(terms) > 10:
                                # There are more terms than simply the e.g.
                                # upper diagonal elements.
                                # This causes the text to be too small to read
                                # in the PDF, so skip including this metadata.
                                continue

                            terms_val = f"{list(terms)!r}"  # <= 5 terms
                            if len(terms) > 5:
                                terms_val = terms_val.split(",")
                                terms_val = (
                                    ",".join(terms_val[:5])
                                    + "\n"
                                    + ",".join(terms_val[5:])
                                )
                        metadata[f"listOfCovarianceTerms (frequency {f})"] = (
                            terms_val
                        )

    fig = plt.figure(figsize=nisarqa.FIG_SIZE_THREE_PLOTS_PER_PAGE_STACKED)

    fig.suptitle(
        f"NISAR Quality Assurance (QA) Report",
        fontsize=15,
        fontweight="bold",
    )

    ax = plt.subplot(111)
    ax.set_title(subtitle, fontsize=10, y=table_pos_top + 0.02)
    ax.axis("off")
    ax.table(
        cellText=np.hstack(
            [
                np.expand_dims(np.array(list(metadata.keys())), axis=1),
                np.expand_dims(np.array(list(metadata.values())), axis=1),
            ]
        ),
        cellLoc="left",
        colLabels=[
            f"Input {product_type} HDF5 Metadata",
            "Value",
        ],
        colLoc="center",
        colColours=["lightgray", "lightgray"],
        bbox=[0, 0, 1, table_pos_top],
    )
    report_pdf.savefig(fig)
    plt.close()


def setup_report_pdf(
    product: nisarqa.NisarProduct, report_pdf: PdfPages
) -> None:
    """
    Setup the report PDF with PDF metadata and a title page.

    Parameters
    ----------
    product : nisarqa.NisarProduct
        Input NISAR product.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to set the global attributes for and append the
        PDF title page to.
    """
    add_metadata_to_report_pdf(product=product, report_pdf=report_pdf)
    add_title_page_to_report_pdf(product=product, report_pdf=report_pdf)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
