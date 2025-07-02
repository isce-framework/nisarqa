from __future__ import annotations

import functools
import os
from collections.abc import Callable, Sequence
from dataclasses import replace
from datetime import datetime
from fractions import Fraction
from typing import Optional, overload

import h5py
import matplotlib as mpl
import matplotlib.colors as colors
import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter

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


def process_ionosphere_phase_screen(
    product: nisarqa.UnwrappedGroup,
    params_iono_phs_screen: nisarqa.ThresholdParamGroup,
    params_iono_phs_uncert: nisarqa.ThresholdParamGroup,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
) -> None:
    """
    Process all ionosphere phase screen and uncertainty layers, and plot to PDF.

    Parameters
    ----------
    product : nisarqa.UnwrappedGroup
        Input NISAR product.
    params_iono_phs_screen : nisarqa.ThresholdParamGroup
        A structure containing the parameters for checking the percentage
        of invalid pixels in the ionosphere phase screen layer.
    params_iono_phs_uncert : nisarqa.ThresholdParamGroup
        A structure containing the parameters for checking the percentage
        of invalid pixels in the ionosphere phase screen uncertainty layer.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the unwrapped phase image plots to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq=freq):
            with (
                product.get_ionosphere_phase_screen(
                    freq=freq, pol=pol
                ) as iono_phs,
                product.get_ionosphere_phase_screen_uncertainty(
                    freq=freq, pol=pol
                ) as iono_uncertainty,
            ):
                # Compute Statistics first, in case of malformed layers
                # (which could cause plotting to fail)
                nisarqa.compute_and_save_basic_statistics(
                    raster=iono_phs,
                    stats_h5=stats_h5,
                    params=params_iono_phs_screen,
                )
                nisarqa.compute_and_save_basic_statistics(
                    raster=iono_uncertainty,
                    stats_h5=stats_h5,
                    params=params_iono_phs_uncert,
                )

                plot_ionosphere_phase_screen_to_pdf(
                    iono_raster=iono_phs,
                    iono_uncertainty_raster=iono_uncertainty,
                    report_pdf=report_pdf,
                )

                # Plot Histograms
                process_two_histograms(
                    raster1=iono_phs,
                    raster2=iono_uncertainty,
                    r1_xlabel="Ionosphere Phase Screen",
                    r2_xlabel="Ionosphere Phase Screen STD",
                    name_of_histogram_pair="Ionosphere Phase Screen",
                    report_pdf=report_pdf,
                    stats_h5=stats_h5,
                    sharey=False,
                )


@overload
def plot_ionosphere_phase_screen_to_pdf(
    iono_raster: nisarqa.RadarRaster,
    iono_uncertainty_raster: nisarqa.RadarRaster,
    report_pdf: PdfPages,
) -> None: ...


@overload
def plot_ionosphere_phase_screen_to_pdf(
    iono_raster: nisarqa.GeoRaster,
    iono_uncertainty_raster: nisarqa.GeoRaster,
    report_pdf: PdfPages,
) -> None: ...


def plot_ionosphere_phase_screen_to_pdf(
    iono_raster,
    iono_uncertainty_raster,
    report_pdf,
):
    """
    Create and append plots of ionosphere phase screen and uncertainty to PDF.

    Ionosphere phase screen layer will be rewrapped to the interval (-pi, pi].
    Ionosphere phase screen uncertainty layer will be plotted on the interval
    [min, max] of that layer.

    Parameters
    ----------
    iono_raster : nisarqa.RadarRaster or nisarqa.GeoRaster
        Ionosphere Phase Screen layer to be processed. Must correspond to
        `iono_uncertainty_raster`.
    iono_uncertainty_raster : nisarqa.RadarRaster or nisarqa.GeoRaster
        Ionosphere Phase Screen Uncertainty layer to be processed. Must
        correspond to `iono_raster`.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the offsets plots to.

    Notes
    -----
    For consistency with the output from numpy.angle(), the ionosphere phase
    screen layer will be rewrapped to (-pi, pi] and not [-pi, pi).
    """
    # Validate that the pertinent metadata in the rasters is equal.
    nisarqa.compare_raster_metadata(
        iono_raster, iono_uncertainty_raster, almost_identical=False
    )

    # Setup the side-by-side PDF page
    fig, (ax1, ax2) = plt.subplots(
        ncols=2,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_TWO_PLOTS_PER_PAGE,
        sharey=True,
    )

    # Construct title for the overall PDF page. (`*raster.name` has a format
    # like "RUNW_L_A_pixelOffsets_HH_slantRangeOffset". We need to
    # remove the final layer name of e.g. "_slantRangeOffset".)
    name = "_".join(iono_raster.name.split("_")[:-1])
    title = f"Ionosphere Phase Screen\n{name}"
    fig.suptitle(title)

    # Plot the ionosphere phase screen raster on the left-side plot.

    # Rewrap the ionosphere phase screen array to (-pi, pi]
    # Step 1: Rewrap to [0, 2pi) via `get_phase_array()`.
    iono_arr, cbar_min_max = get_phase_array(
        phs_or_complex_raster=iono_raster,
        make_square_pixels=True,
        rewrap=2.0,
    )

    # Step 2: adjust to (-pi, pi].
    iono_arr = np.where(iono_arr > np.pi, iono_arr - (2.0 * np.pi), iono_arr)
    cbar_min_max = [-np.pi, np.pi]

    epsilon = 1e-6
    assert np.nanmin(iono_arr) >= (-np.pi - epsilon)
    assert np.nanmax(iono_arr) <= (np.pi + epsilon)

    # Decimate to fit nicely on the figure.
    iono_arr = downsample_img_to_size_of_axes(
        ax=ax1, arr=iono_arr, mode="decimate"
    )

    # Add the wrapped phase image plot
    im = ax1.imshow(
        iono_arr,
        aspect="equal",
        cmap="twilight_shifted",
        interpolation="none",
        vmin=cbar_min_max[0],
        vmax=cbar_min_max[1],
    )

    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax1,
        xlim=iono_raster.x_axis_limits,
        ylim=iono_raster.y_axis_limits,
        img_arr_shape=np.shape(iono_arr),
        xlabel=iono_raster.x_axis_label,
        ylabel=iono_raster.y_axis_label,
        title=(
            f"{iono_raster.name.split('_')[-1]}\nrewrapped to"
            f" (-{nisarqa.PI_UNICODE}, {nisarqa.PI_UNICODE}]"
        ),
    )

    # Add a colorbar to the figure
    cax = fig.colorbar(im)
    cax.ax.set_ylabel(
        ylabel="Ionosphere Phase Screen (radians)", rotation=270, labelpad=10.0
    )

    format_cbar_ticks_for_multiples_of_pi(
        cbar_min=cbar_min_max[0], cbar_max=cbar_min_max[1], cax=cax
    )

    # Plot ionosphere phase screen uncertainty raster on the right-side plot.
    uncertainty_arr = nisarqa.decimate_raster_array_to_square_pixels(
        iono_uncertainty_raster
    )

    uncertainty_arr = downsample_img_to_size_of_axes(
        ax=ax2, arr=uncertainty_arr, mode="decimate"
    )

    im2 = ax2.imshow(
        uncertainty_arr,
        aspect="equal",
        cmap="magma",
        interpolation="none",
        vmin=np.nanmin(uncertainty_arr),
        vmax=np.nanmax(uncertainty_arr),
    )

    # No y-axis label nor ticks. This is the right side plot; y-axis is shared.
    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax2,
        xlim=iono_uncertainty_raster.x_axis_limits,
        img_arr_shape=np.shape(uncertainty_arr),
        xlabel=iono_uncertainty_raster.x_axis_label,
        title=iono_uncertainty_raster.name.split("_")[-1],
    )

    # Add a colorbar to the figure
    cax = fig.colorbar(im2)
    cax.ax.set_ylabel(
        ylabel="Ionosphere Phase Screen STD (radians)",
        rotation=270,
        labelpad=10.0,
    )

    # Append figure to the output PDF
    report_pdf.savefig(fig)

    # Close the plot
    plt.close(fig)


def process_phase_image_unwrapped(
    product: nisarqa.UnwrappedGroup,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
    params: nisarqa.UNWPhaseImageParamGroup,
) -> None:
    """
    Process the unwrapped phase image and plot to PDF.

    Parameters
    ----------
    product : nisarqa.UnwrappedGroup
        Input NISAR product.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the unwrapped phase image plots to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    params : nisarqa.UNWPhaseImageParamGroup
        A structure containing processing parameters to generate the
        unwrapped phase image plots.
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq=freq):
            with product.get_unwrapped_phase(freq=freq, pol=pol) as img:
                # Compute Statistics first, in case of malformed layers
                # (which could cause plotting to fail)
                nisarqa.compute_and_save_basic_statistics(
                    raster=img, stats_h5=stats_h5, params=params
                )

                # Plot phase image
                plot_unwrapped_phase_image_to_pdf(
                    phs_raster=img,
                    report_pdf=report_pdf,
                    rewrap=params.rewrap,
                )

                # Plot Histogram
                process_single_histogram(
                    raster=img,
                    xlabel="InSAR Phase",
                    name_of_histogram="Unwrapped Phase Image",
                    report_pdf=report_pdf,
                    stats_h5=stats_h5,
                )


def plot_unwrapped_phase_image_to_pdf(
    phs_raster: nisarqa.GeoRaster | nisarqa.RadarRaster,
    report_pdf: PdfPages,
    rewrap: Optional[float] = None,
) -> None:
    """
    Plot the unwrapped phase image to PDF.

    If `rewrap` is not None, then two images will be plotted:
        1) The unwrapped phase image without any rewrapping applied, and
        2) The unwrapped phase image that has been rewrapped.
    If `rewrap` is None, then only the first of those images will be plotted.

    Parameters
    ----------
    phs_raster : nisarqa.GeoRaster | nisarqa.RadarRaster
        *Raster of unwrapped phase data (float-valued).
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the unwrapped phase image plot(s) to.
    rewrap : float or None, optional
        The multiple of pi to rewrap the unwrapped phase image when generating
        the HSI image(s). If None, no rewrapped phase image will be plotted.
        Ex: If 3 is provided, the image is rewrapped to the interval [0, 3pi).
        Defaults to None.
    """
    # Overview: If no re-wrapping is requested, simply make one plot.
    # If re-wrapping is requested, make the plot on the left the original
    # unwrapped plot, and the plot on the right the rewrapped plot.
    # Set up the left (and possibly right) plots
    if rewrap is None:
        fig, ax1 = plt.subplots(
            ncols=1,
            nrows=1,
            constrained_layout="tight",
            figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE,
        )
    else:
        fig, (ax1, ax2) = plt.subplots(
            ncols=2,
            nrows=1,
            constrained_layout="tight",
            figsize=nisarqa.FIG_SIZE_TWO_PLOTS_PER_PAGE,
            sharey=True,
        )

    title = f"Unwrapped Phase Image\n{phs_raster.name}"
    fig.suptitle(title)

    # Plot the "left" plot (fully unwrapped interferogram)
    phs_img_unw, cbar_min_max_unw = get_phase_array(
        phs_or_complex_raster=phs_raster,
        make_square_pixels=True,
        rewrap=None,
    )

    # Decimate to fit nicely on the figure.
    phs_img_unw = downsample_img_to_size_of_axes(
        ax=ax1, arr=phs_img_unw, mode="decimate"
    )

    im1 = ax1.imshow(
        phs_img_unw,
        aspect="equal",
        cmap="plasma",
        interpolation="none",
        vmin=cbar_min_max_unw[0],
        vmax=cbar_min_max_unw[1],
    )

    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax1,
        xlim=phs_raster.x_axis_limits,
        ylim=phs_raster.y_axis_limits,
        img_arr_shape=phs_img_unw.shape,
        xlabel=phs_raster.x_axis_label,
        ylabel=phs_raster.y_axis_label,
        title="Unwrapped Phase",
    )

    # Add a colorbar to the figure
    cax1 = fig.colorbar(im1, ax=ax1)
    cax1.ax.set_ylabel(
        ylabel="InSAR Phase (radians)", rotation=270, labelpad=10.0
    )

    format_cbar_ticks_for_multiples_of_pi(
        cbar_min=cbar_min_max_unw[0], cbar_max=cbar_min_max_unw[1], cax=cax1
    )

    # If requested, plot the "right" plot (rewrapped interferogram)
    if rewrap is not None:
        phs_img_rewrapped, cbar_min_max_rewrapped = get_phase_array(
            phs_or_complex_raster=phs_raster,
            make_square_pixels=True,
            rewrap=rewrap,
        )

        phs_img_rewrapped = downsample_img_to_size_of_axes(
            ax=ax2, arr=phs_img_rewrapped, mode="decimate"
        )

        im2 = ax2.imshow(
            phs_img_rewrapped,
            aspect="equal",
            cmap="twilight_shifted",
            interpolation="none",
            vmin=cbar_min_max_rewrapped[0],
            vmax=cbar_min_max_rewrapped[1],
        )

        pi_unicode = "\u03c0"
        title = f"Unwrapped Phase\nrewrapped to [0, {rewrap}{pi_unicode})"
        # No y-axis label nor ticks for the right side plot; y-axis is shared.
        nisarqa.rslc.format_axes_ticks_and_labels(
            ax=ax2,
            xlim=phs_raster.x_axis_limits,
            img_arr_shape=phs_img_rewrapped.shape,
            xlabel=phs_raster.x_axis_label,
            title=title,
        )

        # Add a colorbar to the figure
        cax2 = fig.colorbar(im2, ax=ax2)
        cax2.ax.set_ylabel(
            ylabel="InSAR Phase (radians)", rotation=270, labelpad=10.0
        )

        format_cbar_ticks_for_multiples_of_pi(
            cbar_min=cbar_min_max_rewrapped[0],
            cbar_max=cbar_min_max_rewrapped[1],
            cax=cax2,
        )

    # Append figure to the output PDF
    report_pdf.savefig(fig)

    # Close the plot
    plt.close(fig)


def process_phase_image_wrapped(
    product: nisarqa.WrappedGroup,
    params_wrapped_igram: nisarqa.ThresholdParamGroup,
    params_coh_mag: nisarqa.ThresholdParamGroup,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
) -> None:
    """
    Process the wrapped groups' phase and coherence magnitude layers.

    Appends plots of each layer to the report PDF file.

    Parameters
    ----------
    product : nisarqa.WrappedGroup
        Input NISAR product.
    params_wrapped_igram : nisarqa.ThresholdParamGroup
        A structure containing the parameters for checking the percentage
        of invalid pixels in the wrapped interferogram layer.
    params_coh_mag : nisarqa.ThresholdParamGroup
        A structure containing the parameters for checking the percentage
        of invalid pixels in the coherence magnitude layer.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        Output PDF file to append the phase and coherence magnitude plots to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq=freq):
            with (
                product.get_wrapped_igram(freq=freq, pol=pol) as complex_img,
                product.get_wrapped_coh_mag(freq=freq, pol=pol) as coh_img,
            ):
                # Compute Statistics first, in case of malformed layers
                # (which could cause plotting to fail)
                nisarqa.compute_and_save_basic_statistics(
                    raster=complex_img,
                    params=params_wrapped_igram,
                    stats_h5=stats_h5,
                )
                nisarqa.compute_and_save_basic_statistics(
                    raster=coh_img,
                    params=params_coh_mag,
                    stats_h5=stats_h5,
                )

                plot_wrapped_phase_image_and_coh_mag_to_pdf(
                    complex_raster=complex_img,
                    coh_raster=coh_img,
                    report_pdf=report_pdf,
                )

                # Plot Histograms
                process_two_histograms(
                    raster1=complex_img,
                    raster2=coh_img,
                    r1_xlabel="InSAR Phase",
                    r2_xlabel="Coherence Magnitude",
                    name_of_histogram_pair="Wrapped Phase Image Group",
                    report_pdf=report_pdf,
                    stats_h5=stats_h5,
                    sharey=False,
                    r1_data_prep_func=np.angle,
                )


@overload
def plot_wrapped_phase_image_and_coh_mag_to_pdf(
    complex_raster: nisarqa.RadarRaster,
    coh_raster: nisarqa.RadarRaster,
    report_pdf: PdfPages,
) -> None: ...


@overload
def plot_wrapped_phase_image_and_coh_mag_to_pdf(
    complex_raster: nisarqa.GeoRaster,
    coh_raster: nisarqa.GeoRaster,
    report_pdf: PdfPages,
) -> None: ...


def plot_wrapped_phase_image_and_coh_mag_to_pdf(
    complex_raster,
    coh_raster,
    report_pdf,
):
    """
    Plot a complex raster and coherence magnitude layers side-by-side on PDF.

    Parameters
    ----------
    complex_raster : nisarqa.RadarRaster or nisarqa.GeoRaster
        *Raster of complex interferogram data. This should correspond to
        `coh_raster`.
    coh_raster : nisarqa.GeoRaster or nisarqa.RadarRaster
        *Raster for the coherence magnitude raster. This should correspond to
        `complex_raster`.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        Output PDF file to append the phase and coherence magnitude plots to.
    """

    # Validate that the pertinent metadata in the rasters is equal.
    nisarqa.compare_raster_metadata(
        complex_raster, coh_raster, almost_identical=False
    )

    phs_img, cbar_min_max = get_phase_array(
        phs_or_complex_raster=complex_raster,
        make_square_pixels=True,
        rewrap=None,
    )

    coh_img = nisarqa.decimate_raster_array_to_square_pixels(coh_raster)

    fig, (ax1, ax2) = plt.subplots(
        ncols=2,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_TWO_PLOTS_PER_PAGE,
        sharey=True,
    )

    # Decimate to fit nicely on the figure.
    phs_img = downsample_img_to_size_of_axes(
        ax=ax1, arr=phs_img, mode="decimate"
    )
    coh_img = downsample_img_to_size_of_axes(
        ax=ax2, arr=coh_img, mode="decimate"
    )

    # Construct title for the overall PDF page. (`*raster.name` has a format
    # like "RIFG_L_A_interferogram_HH_wrappedInterferogram". We need to
    # remove the final layer name of e.g. "_wrappedInterferogram".)
    name = "_".join(complex_raster.name.split("_")[:-1])
    title = f"Wrapped Phase Image Group\n{name}"
    fig.suptitle(title)

    # Add the wrapped phase image plot
    im1 = ax1.imshow(
        phs_img,
        aspect="equal",
        cmap="twilight_shifted",
        interpolation="none",
        vmin=cbar_min_max[0],
        vmax=cbar_min_max[1],
    )

    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax1,
        xlim=complex_raster.x_axis_limits,
        ylim=complex_raster.y_axis_limits,
        img_arr_shape=np.shape(phs_img),
        xlabel=complex_raster.x_axis_label,
        ylabel=complex_raster.y_axis_label,
        title=complex_raster.name.split("_")[-1],  # use only the layer's name
    )

    # Add a colorbar to the figure
    cax1 = fig.colorbar(im1)
    cax1.ax.set_ylabel(
        ylabel="InSAR Phase (radians)", rotation=270, labelpad=10.0
    )

    format_cbar_ticks_for_multiples_of_pi(
        cbar_min=cbar_min_max[0], cbar_max=cbar_min_max[1], cax=cax1
    )

    # Add the coh mag layer corresponding to the wrapped phase image plot
    im2 = ax2.imshow(
        coh_img,
        aspect="equal",
        cmap="gray",
        interpolation="none",
        vmin=0.0,
        vmax=1.0,
    )

    # No y-axis label nor ticks. This is the right side plot; y-axis is shared.
    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax2,
        xlim=coh_raster.x_axis_limits,
        img_arr_shape=np.shape(coh_img),
        xlabel=coh_raster.x_axis_label,
        # Use only the final layer name for `title`. (`coh_raster.name` has
        # format like: "RUNW_L_A_interferogram_HH_unwrappedPhase".)
        title=coh_raster.name.split("_")[-1],
    )

    # Add a colorbar to the figure
    cax2 = fig.colorbar(im2)
    cax2.ax.set_ylabel(
        ylabel="Coherence Magnitude", rotation=270, labelpad=10.0
    )

    # Append figure to the output PDF
    report_pdf.savefig(fig)

    # Close the plot
    plt.close(fig)


def make_wrapped_phase_png(
    product: nisarqa.WrappedGroup,
    freq: str,
    pol: str,
    png_filepath: str | os.PathLike,
    longest_side_max: Optional[int] = None,
) -> None:
    """
    Create and save the wrapped interferogram as a PNG.

    Parameters
    ----------
    product : nisarqa.WrappedGroup
        Input NISAR product.
    freq, pol : str
        The frequency and polarization (respectively) pair for the wrapped
        interferogram to save as a PNG.
    png_filepath : path-like
        Filename (with path) for the image PNG.
    longest_side_max : int or None, optional
        The maximum number of pixels allowed for the longest side of the final
        2D multilooked image. If None, the longest edge of `arr` will be used.
        Defaults to None.
    """

    with product.get_wrapped_igram(freq=freq, pol=pol) as igram_r:
        phase, cbar_min_max = get_phase_array(
            phs_or_complex_raster=igram_r,
            make_square_pixels=False,  # we'll do this while downsampling
            rewrap=None,
        )

    plot_2d_array_and_save_to_png(
        arr=phase,
        cmap="twilight_shifted",
        sample_spacing=(igram_r.y_axis_spacing, igram_r.x_axis_spacing),
        longest_side_max=longest_side_max,
        png_filepath=png_filepath,
        vmin=cbar_min_max[0],
        vmax=cbar_min_max[1],
    )


def make_unwrapped_phase_png(
    product: nisarqa.UnwrappedGroup,
    freq: str,
    pol: str,
    params: nisarqa.UNWIgramBrowseParamGroup,
    png_filepath: str | os.PathLike,
) -> None:
    """
    Create and save the unwrapped interferogram as a PNG.

    Parameters
    ----------
    product : nisarqa.UnwrappedGroup
        Input NISAR product.
    freq, pol : str
        The frequency and polarization (respectively) pair for the unwrapped
        interferogram to save as a PNG.
    params : nisarqa.UNWIgramBrowseParamGroup
        A structure containing the parameters for creating the browse image.
    png_filepath : path-like
        Filename (with path) for the image PNG.
    """

    with product.get_unwrapped_phase(freq=freq, pol=pol) as igram_r:
        phase, cbar_min_max = get_phase_array(
            phs_or_complex_raster=igram_r,
            make_square_pixels=False,  # we'll do this while downsampling
            rewrap=params.rewrap,
        )

    plot_2d_array_and_save_to_png(
        arr=phase,
        cmap="twilight_shifted",
        sample_spacing=(igram_r.y_axis_spacing, igram_r.x_axis_spacing),
        longest_side_max=params.longest_side_max,
        png_filepath=png_filepath,
        vmin=cbar_min_max[0],
        vmax=cbar_min_max[1],
    )


def plot_2d_array_and_save_to_png(
    arr: npt.ArrayLike,
    png_filepath: str | os.PathLike,
    cmap: str | mpl.colors.Colormap = "viridis",
    sample_spacing: Optional[tuple[float, float]] = None,
    longest_side_max: Optional[int] = None,
    *,
    vmin: float | None = None,
    vmax: float | None = None,
) -> None:
    """
    Plot a 2D raster to square pixels, and save to PNG.

    Parameters
    ----------
    arr : npt.ArrayLike
        Raster to be plotted and saved to as PNG.
    png_filepath : path-like
        Filename (with path) for the image PNG.
    cmap : str or mpl.colors.Colormap, optional
        Colormap to use while plotting the raster. Must be compliant with
        `matplotlib.pyplot.imshow`'s `cmap` parameter.
        Defaults to "viridis".
    sample_spacing : pair of float or None, optional
        The Y direction sample spacing and X direction sample spacing
        of the source array. These values are used to decimate the raster
        to have square pixels.
        For radar-domain products, Y direction corresponds to azimuth,
        and X direction corresponds to range.
        Only the magnitude (absolute value) of the sample spacing is used.
        Format: (dy, dx)
        If None, the raster is assumed to have square pixels and so the aspect
        ratio of `arr` will not change.
    longest_side_max : int, optional
        The maximum number of pixels allowed for the longest side of the final
        2D multilooked image. If None, the longest edge of `arr` will be used.
        Defaults to None.
    vmin, vmax : float or None, optional
        The vmin and vmax (respectively) to use when plotting the input array
        using `matplotlib.imshow()`. These define the data range that the
        colormap covers. If None, the min and max values (respectively) of the
        input array will be used.
    """
    if sample_spacing is None:
        sample_spacing = (1, 1)

    if longest_side_max is None:
        longest_side_max = max(np.shape(arr))

    # decimate to square pixels
    ky, kx = nisarqa.compute_square_pixel_nlooks(
        img_shape=np.shape(arr),
        sample_spacing=sample_spacing,
        longest_side_max=longest_side_max,
    )
    arr = arr[::ky, ::kx]

    # partial function for use by save_mpl_plot_to_png()
    def plot_image(ax: mpl.axes.Axes) -> None:
        ax.imshow(
            arr,
            aspect="equal",
            cmap=cmap,
            interpolation="none",
            vmin=vmin,
            vmax=vmax,
        )

    save_mpl_plot_to_png(
        axes_partial_func=plot_image,
        raster_shape=np.shape(arr),
        png_filepath=png_filepath,
    )


def make_hsi_png_with_wrapped_phase(
    product: nisarqa.WrappedGroup,
    freq: str,
    pol: str,
    params: nisarqa.IgramBrowseParamGroup,
    png_filepath: str | os.PathLike,
) -> None:
    """
    Create and save HSI image of a wrapped interferogram with coh mag as a PNG.

    Phase values are encoded as Hue and coherence magnitude values are
    encoded as Intensity in the resulting PNG.

    Parameters
    ----------
    product : nisarqa.WrappedGroup
        Input NISAR product.
    freq, pol : str
        The frequency and polarization (respectively) pair for the wrapped
        interferogram and coh mag layer to use for generating the HSI image.
    params : nisarqa.IgramBrowseParamGroup
        A structure containing the parameters for creating the HSI image.
    png_filepath : path-like
        Filename (with path) for the image PNG.
    """

    with (
        product.get_wrapped_igram(freq=freq, pol=pol) as igram_r,
        product.get_wrapped_coh_mag(freq=freq, pol=pol) as coh_r,
    ):
        rgb_img, _ = make_hsi_raster(
            phs_or_complex_raster=igram_r,
            coh_raster=coh_r,
            equalize=params.equalize_browse,
            rewrap=None,
            longest_side_max=params.longest_side_max,
        )

    nisarqa.rslc.plot_to_rgb_png(
        red=rgb_img.data[:, :, 0],
        green=rgb_img.data[:, :, 1],
        blue=rgb_img.data[:, :, 2],
        filepath=png_filepath,
    )


def make_hsi_png_with_unwrapped_phase(
    product: nisarqa.UnwrappedGroup,
    freq: str,
    pol: str,
    params: nisarqa.UNWIgramBrowseParamGroup,
    png_filepath: str | os.PathLike,
) -> None:
    """
    Create and save HSI image of unwrapped interferogram with coh mag as a PNG.

    (Possibly re-wrapped) unwrapped phase values are encoded as Hue and
    coherence magnitude values are encoded as Intensity in the resulting PNG.

    Parameters
    ----------
    product : nisarqa.UnwrappedGroup
        Input NISAR product.
    freq, pol : str
        The frequency and polarization (respectively) pair for the unwrapped
        interferogram and coh mag layer to use for generating the HSI image.
    params : nisarqa.UNWIgramBrowseParamGroup
        A structure containing the parameters for creating the HSI image.
    png_filepath : path-like
        Filename (with path) for the image PNG.
    """

    with (
        product.get_unwrapped_phase(freq=freq, pol=pol) as phs_r,
        product.get_unwrapped_coh_mag(freq=freq, pol=pol) as coh_r,
    ):
        rgb_img, _ = make_hsi_raster(
            phs_or_complex_raster=phs_r,
            coh_raster=coh_r,
            equalize=params.equalize_browse,
            rewrap=params.rewrap,
            longest_side_max=params.longest_side_max,
        )
    nisarqa.rslc.plot_to_rgb_png(
        red=rgb_img.data[:, :, 0],
        green=rgb_img.data[:, :, 1],
        blue=rgb_img.data[:, :, 2],
        filepath=png_filepath,
    )


def hsi_images_to_pdf_wrapped(
    product: nisarqa.WrappedGroup,
    report_pdf: PdfPages,
) -> None:
    """
    Create HSI wrapped interferogram images and save to PDF.

    Parameters
    ----------
    product : nisarqa.WrappedGroup
        Input NISAR product.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the HSI image plot to.
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq=freq):
            with (
                product.get_wrapped_igram(freq=freq, pol=pol) as igram_r,
                product.get_wrapped_coh_mag(freq=freq, pol=pol) as coh_r,
            ):
                # Create a *Raster with the HSI image

                # The HSI colorbar generated in the HSI PDF function (below)
                # has a linear scale from [0, 1] for the intensity channel
                # (coherence magnitude layer). If we equalize that channel,
                # then the colorbar scale would be inaccurate.
                # So, ensure equalize=False when creating the HSI Raster.
                rgb_img, cbar_min_max = make_hsi_raster(
                    phs_or_complex_raster=igram_r,
                    coh_raster=coh_r,
                    equalize=False,  # Do not equalize the PDF HSI images
                    rewrap=None,
                    longest_side_max=None,  # Unnecessary for the PDF
                )

            save_hsi_img_to_pdf(
                img=rgb_img,
                report_pdf=report_pdf,
                cbar_min_max=cbar_min_max,
                plot_title_prefix="Wrapped Phase Image and Coherence Magnitude",
            )


def hsi_images_to_pdf_unwrapped(
    product: nisarqa.UnwrappedGroup,
    report_pdf: PdfPages,
    rewrap: Optional[float | int] = None,
) -> None:
    """
    Create HSI unwrapped phase images and save to PDF.

    Parameters
    ----------
    product : nisarqa.UnwrappedGroup
        Input NISAR product.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the HSI image plot to.
    rewrap : float or None, optional
        The multiple of pi to rewrap the unwrapped phase image when generating
        the HSI image(s). If None, no rewrapping will occur.
        Ex: If 3 is provided, the image is rewrapped to the interval [0, 3pi).
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq=freq):
            with (
                product.get_unwrapped_phase(freq=freq, pol=pol) as phs_r,
                product.get_unwrapped_coh_mag(freq=freq, pol=pol) as coh_r,
            ):
                # The HSI colorbar generated in the HSI PDF function (below)
                # has a linear scale from [0, 1] for the intensity channel
                # (coherence magnitude layer). If we equalize that channel,
                # then the colorbar scale would be inaccurate.
                # So, ensure equalize=False when creating the HSI Raster.
                rgb_img, cbar_min_max = make_hsi_raster(
                    phs_or_complex_raster=phs_r,
                    coh_raster=coh_r,
                    equalize=False,  # Do not equalize the PDF HSI images
                    rewrap=rewrap,
                    longest_side_max=None,  # Unnecessary for the PDF
                )

            save_hsi_img_to_pdf(
                img=rgb_img,
                report_pdf=report_pdf,
                cbar_min_max=cbar_min_max,
                plot_title_prefix=(
                    "Unwrapped Phase Image and Coherence Magnitude"
                ),
            )


def save_hsi_img_to_pdf(
    img: nisarqa.SARRaster,
    report_pdf: PdfPages,
    cbar_min_max: Optional[Sequence[float]] = None,
    plot_title_prefix: str = "Phase Image and Coherence Magnitude as HSI Image",
) -> None:
    """
    Annotate and save an HSI Image to PDF.

    `img.data` should be in linear.

    Parameters
    ----------
    img : *Raster
        Image in RGB color space to be saved. All image correction,
        multilooking, etc. needs to have previously been applied.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the HSI image plot to.
    cbar_min_max : pair of float or None, optional
        The range for the Hue axis of the HSI colorbar for the image raster.
        `None` to use the min and max of the image for the colorbar range.
        Defaults to None.
    plot_title_prefix : str, optional
        Prefix for the title of the backscatter plots.
        Defaults to "Phase Image and Coherence Magnitude as HSI Image".
    """
    # Plot and Save HSI Image to graphical summary pdf
    title = f"{plot_title_prefix}\n{img.name}"

    img2pdf_hsi(
        img_arr=img.data,
        title=title,
        ylim=img.y_axis_limits,
        xlim=img.x_axis_limits,
        cbar_min_max=cbar_min_max,
        xlabel=img.x_axis_label,
        ylabel=img.y_axis_label,
        plots_pdf=report_pdf,
    )


def make_hsi_as_rgb_img(
    phase_img: np.ndarray,
    coh_mag: np.ndarray,
    phs_img_range: Optional[Sequence[float | int]] = None,
    equalize: bool = False,
) -> np.ndarray:
    """
    Create HSI interferogram image array, returned in RGB colorspace.

    The phase image and coherence magnitude rasters are first processed into
    the HSI (Hue, Saturation, Intensity) colorspace, which is then converted
    to RGB values in normalized range [0, 1].

    If any input layer was NaN-valued for a given pixel, then the output
    value for that pixel will be NaN (for all channels).

    TODO: This algorithm currently uses the built-in matplotlib.hsv_to_rgb()
    to convert to RGB due to delivery schedule constraints.
    But, there is a subtle mathematical difference between the HSI and HSV
    colorspaces, and we should definitely use HSI (not HSV).
    This will require a custom implementation of HSI->RGB.

    Parameters
    ----------
    phase_img : numpy.ndarray
        2D array of a phase image (e.g. `unwrappedInterferogram`).
        This should contain real-valued pixels; if your raster is a complex
        valued interferogram, please compute the phase (e.g. use np.angle())
        and then pass in the resultant raster for `phase_img`.
    coh_mag : numpy.ndarray
        2D raster of `coherenceMagnitude` layer corresponding to `phase_img`.
        This should already be normalized to range [0, 1]. (Otherwise
        something must have gone rather wrong in the InSAR processing!)
    phs_img_range : pair of float or None, optional
        The expected range for the phase image raster. `None` to use the
        min and max of the image data. This will be used for normalization
        of the data to range [0, 1].
        Note: If `phs_img`'s data is within a known range, it is strongly
        suggested to set this parameter, otherwise unintended image correction
        will occur.
        For example, if an image was generated via np.angle(), the known range
        is (-pi, pi]. But if the actual image data only contains values from
        [-pi/2, pi/3] and `None` was provided, then the phase image will appear
        "stretched", because during normalization -pi/2 -> 0 and pi/3 -> 1.
        Defaults to None.
    equalize : bool, optional
        True to perform histogram equalization on the Intensity channel
        (the coherence magnitude layer) for the HSI image.
        See: https://scikit-image.org/docs/stable/auto_examples/color_exposure/plot_equalize.html
        Default is False.

    Returns
    -------
    rgb : numpy.ndarray
        3D array of HSI image converted to the RGB (Red Green Blue) colorspace.
        This RGB array is ready for plotting in e.g. Matplotlib.
    """
    if not np.issubdtype(phase_img.dtype, np.floating):
        raise TypeError(
            f"`phase_img` has type {type(phase_img)}, must be float. "
            "Hint: If complex, perhaps compute numpy.angle(phase_img) "
            "before passing in the array."
        )

    if phase_img.ndim != 2:
        raise ValueError(
            f"`phase_img` has shape {np.shape(phase_img)}"
            "but must be a 2D array."
        )

    if coh_mag.ndim != 2:
        raise ValueError(
            f"`coh_mag` has shape {np.shape(coh_mag)} but must be a 2D array."
        )

    if np.shape(phase_img) != np.shape(coh_mag):
        raise ValueError(
            f"`phase_img` (shape: {np.shape(phase_img)}) and `coh_mag` "
            f"(shape: {np.shape(coh_mag)}) must have the same shape."
        )

    # coh mag should already be within range [0, 1].
    if np.any(coh_mag < 0.0) or np.any(coh_mag > 1.0):
        raise ValueError("`coh_mag` contains values outside of range [0, 1].")

    # Initialize HSI array
    # Note: per hsv_to_rgb(): "All values assumed to be in range [0, 1]".
    # So, we'll need to normalize all rasters added to this array.
    hsi = np.ones((phase_img.shape[0], phase_img.shape[1], 3), dtype=np.float32)

    # First channel is hue. The phase image should be represented by hue.
    # Note: If available, make sure to specify the known min/max range for
    # the image, such as (-pi, pi] for images created with np.angle().
    # Otherwise, `nisarqa.normalize()` will take the min and max of the actual
    # data, which could have the undesirable effect of applying image
    # correction to e.g. phase images.
    hsi[:, :, 0] = nisarqa.normalize(arr=phase_img, min_max=phs_img_range)

    # Second channel is saturation. We set it to 1 always.
    # Note: Nothing more to do --> It was previously initialized to 1.

    # Third channel is intensity scaled between 0, 1.
    # If the user desires, equalize histogram
    if equalize:
        # image_histogram_equalization handles normalization
        hsi[:, :, 2] = image_histogram_equalization(image=coh_mag)
    else:
        # coh mag is already within range [0, 1].
        hsi[:, :, 2] = coh_mag

    # The input arrays may contain some nan values.
    # But, we need to set them to zero for generating the HSI array.
    # So, create a temporary mask of all NaN pixels, do the computation,
    # and then set those pixels back to NaN for the final image.

    # nan_mask: True where pixels are non-finite; False where pixels are finite
    nan_mask = ~np.isfinite(phase_img) | ~np.isfinite(coh_mag)

    # For the HSI-> RGB conversion, replace all non-finite values with 0
    hsi[nan_mask] = 0.0

    # For plotting the image, convert to RGB color space
    # TODO - We need to use HSI not HSV. There is a subtle mathematical
    # difference between the two colorspaces.
    # However, this will require a custom implementation of HSI->RGB.
    rgb = colors.hsv_to_rgb(hsi)

    # Restore the NaN values
    rgb[nan_mask] = np.nan

    return rgb


def get_phase_array(
    phs_or_complex_raster: nisarqa.GeoRaster | nisarqa.RadarRaster,
    make_square_pixels: bool,
    rewrap: Optional[float] = None,
) -> tuple[np.ndarray, list[float]]:
    """
    Get the phase image from the input *Raster.

    Parameters
    ----------
    phs_or_complex_raster : nisarqa.GeoRaster | nisarqa.RadarRaster
        *Raster of complex interferogram or unwrapped phase data.
        If *Raster is complex valued, numpy.angle() will be used to compute
        the phase image (float-valued).
    make_square_pixels : bool
        True to decimate the image to have square pixels.
        False for `phs_img` to always keep the same shape as
        `phs_or_complex_raster.data`
    rewrap : float or None, optional
        The multiple of pi to rewrap the unwrapped phase image.
        If None, no rewrapping will occur.
        If `phs_or_complex_raster` is complex valued, this will be ignored.
        Ex: If 3 is provided, the image is rewrapped to the interval [0, 3pi).
        Defaults to None.

    Returns
    -------
    phs_img : numpy.ndarray
        The phase image from the input raster, processed according to the input
        parameters.
    cbar_min_max : pair of float
        The suggested range to use for plotting the phase image.
        If `phs_or_complex_raster` has complex valued data, then `cbar_min_max`
        will be the range (-pi, +pi].
        If `rewrap` is a float, the range will be [0, <rewrap * pi>).
        If `rewrap` is a None, the range will be [<array min>, <array max>].
    """

    phs_img = phs_or_complex_raster.data[...]

    if phs_or_complex_raster.is_complex:
        # complex data; take the phase angle.
        phs_img = np.angle(phs_img.data)

        # np.angle() returns output in range (-pi, pi]
        # So, set the colobar's min and max to be the range (-pi, +pi].
        cbar_min_max = [-np.pi, np.pi]

        # Helpful hint for user!
        if rewrap is not None:
            raise ValueError(
                "Input raster has a complex dtype (implying a wrapped"
                f" interferogram), but input parameter {rewrap=}. `rewrap` is"
                " only used in the case of real-valued data (implying an"
                " unwrapped phase image). Please check that this is intended."
            )

    else:
        # unwrapped phase image
        if rewrap is None:
            cbar_min_max = [
                np.nanmin(phs_img),
                np.nanmax(phs_img),
            ]
        else:
            # `rewrap` is a multiple of pi. Convert to the full float value.
            rewrap_final = rewrap * np.pi

            # The sign of the output of the modulo operator
            # is the same as the sign of `rewrap_final`.
            # This means that it will always put the output
            # into range [0, <rewrap_final>)
            phs_img %= rewrap_final
            cbar_min_max = [0, rewrap_final]

    if make_square_pixels:
        raster_shape = phs_img.shape

        ky, kx = nisarqa.compute_square_pixel_nlooks(
            img_shape=raster_shape,
            sample_spacing=[
                phs_or_complex_raster.y_axis_spacing,
                phs_or_complex_raster.x_axis_spacing,
            ],
            # Only make square pixels. Use `max()` to not "shrink" the rasters.
            longest_side_max=max(raster_shape),
        )

        # Decimate to square pixels.
        phs_img = phs_img[::ky, ::kx]

    return phs_img, cbar_min_max


@overload
def make_hsi_raster(
    phs_or_complex_raster: nisarqa.RadarRaster,
    coh_raster: nisarqa.RadarRaster,
    equalize: bool,
    rewrap: Optional[float] = None,
    longest_side_max: Optional[int] = None,
) -> tuple[nisarqa.RadarRaster, list[float]]: ...


@overload
def make_hsi_raster(
    phs_or_complex_raster: nisarqa.GeoRaster,
    coh_raster: nisarqa.GeoRaster,
    equalize: bool,
    rewrap: Optional[float] = None,
    longest_side_max: Optional[int] = None,
) -> tuple[nisarqa.GeoRaster, list[float]]: ...


def make_hsi_raster(
    phs_or_complex_raster,
    coh_raster,
    equalize,
    rewrap=None,
    longest_side_max=None,
):
    """
    Create HSI interferogram *Raster with square pixels, and colorbar range.

    Parameters
    ----------
    phs_or_complex_raster : nisarqa.GeoRaster | nisarqa.RadarRaster
        *Raster of complex interferogram or unwrapped phase data to use to
        construct the Hue layer for the HSI *Raster.
        If *Raster is complex valued, numpy.angle() will be used to compute
        the phase image (float-valued).
        This should correspond to `coh_raster`.
    coh_raster : nisarqa.GeoRaster | nisarqa.RadarRaster
        *Raster for the coherence magnitude raster to use to construct
        the intesity layer for the HSI *Raster.
        This should correspond to `phs_or_complex_raster`.
    equalize : bool, optional
        True to perform histogram equalization on the Intensity channel
        (the coherence magnitude layer) for the HSI image.
        See: https://scikit-image.org/docs/stable/auto_examples/color_exposure/plot_equalize.html
        Default is False.
    rewrap : float or None, optional
        The multiple of pi to rewrap the unwrapped phase image when generating
        the HSI image(s). If None, no rewrapping will occur.
        Ex: If 3 is provided, the image is rewrapped to the interval [0, 3pi).
    longest_side_max : int or None, optional
        Decimate the generated HSI raster so that the max length of
        axis 0 and axis 1 in `hsi_raster` is `longest_side_max`.

    Returns
    -------
    hsi_raster : nisarqa.GeoRaster | nisarqa.RadarRaster
        A *Raster of the HSI image converted to RGB color space. This raster
        will have square pixels. (If the rasters in `phs_or_complex_raster` and
        `coh_raster` do not have square pixels, then decimation will be applied
        to achieve square pixels.)
        The type of `hsi_raster` will be the same as the type of
        `phs_or_complex_raster` and `coh_raster`.
    cbar_min_max : pair of float
        The suggested range to use for the Hue axis of the
        HSI colorbar for `hsi_raster`.
        If `phs_or_complex_raster` has complex valued data, then `cbar_min_max`
        will be the range [-pi, +pi].
    """
    # Validate input rasters
    nisarqa.compare_raster_metadata(
        phs_or_complex_raster, coh_raster, almost_identical=False
    )

    phs_img, cbar_min_max = get_phase_array(
        phs_or_complex_raster=phs_or_complex_raster,
        make_square_pixels=False,  # we'll do this on the HSI Raster later
        rewrap=rewrap,
    )

    coh_img = coh_raster.data[...]

    rgb = nisarqa.make_hsi_as_rgb_img(
        phase_img=phs_img,
        coh_mag=coh_img,
        phs_img_range=cbar_min_max,
        equalize=equalize,
    )

    # Square the pixels. Decimate if requested.
    y_axis_spacing = phs_or_complex_raster.y_axis_spacing
    x_axis_spacing = phs_or_complex_raster.x_axis_spacing

    if longest_side_max is None:
        # Update to be the longest side of the array. This way no downsizing
        # of the image will occur, but we can still output square pixels.
        longest_side_max = max(np.shape(rgb)[:2])

    ky, kx = nisarqa.compute_square_pixel_nlooks(
        img_shape=np.shape(rgb)[:2],  # only need the x and y dimensions
        sample_spacing=[y_axis_spacing, x_axis_spacing],
        longest_side_max=longest_side_max,
    )
    rgb = rgb[::ky, ::kx]

    # Update the ground spacing so that the new *Raster we are building will
    # have correct metadata.
    y_axis_spacing = y_axis_spacing * ky
    x_axis_spacing = x_axis_spacing * kx

    # Construct the name for the new raster. (`*raster.name` has a format
    # like "RUNW_L_A_interferogram_HH_unwrappedPhase". The HSI image combines
    # two rasters, so remove the final layer name of e.g. "_unwrappedPhase".)
    name = "_".join(phs_or_complex_raster.name.split("_")[:-1])
    if rewrap:
        name += f" - rewrapped to [0, {rewrap}{nisarqa.PI_UNICODE})"

    # Construct the HSI *Raster object
    if isinstance(phs_or_complex_raster, nisarqa.RadarRaster):
        hsi_raster = replace(
            phs_or_complex_raster,
            data=rgb,
            name=name,
            ground_az_spacing=y_axis_spacing,
            ground_range_spacing=x_axis_spacing,
        )
    elif isinstance(phs_or_complex_raster, nisarqa.GeoRaster):
        hsi_raster = replace(
            phs_or_complex_raster,
            data=rgb,
            name=name,
            y_spacing=y_axis_spacing,
            x_spacing=x_axis_spacing,
        )
    else:
        raise TypeError(
            f"Input rasters have type {type(phs_img)}, but must be either"
            " nisarqa.RadarRaster or nisarqa.GeoRaster."
        )

    return hsi_raster, cbar_min_max


def img2pdf_hsi(
    img_arr: npt.ArrayLike,
    plots_pdf: PdfPages,
    cbar_min_max: Optional[Sequence[float]] = None,
    title: Optional[str] = None,
    xlim: Optional[Sequence[float | int]] = None,
    ylim: Optional[Sequence[float | int]] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
) -> None:
    """
    Plot image array with a linear HSI "colorbar", then append to PDF.

    Parameters
    ----------
    img_arr : array_like
        Image to plot; image should represent an HSI (Hue,
        Saturation, Intensity) image that has been already converted to
        RGB colorspace (such as via matplotlib.colors.hsv_to_rgb()).
    plots_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the HSI image plot to.
    cbar_min_max : pair of float or None, optional
        The range for the Hue axis of the HSI colorbar for the image raster.
        `None` to use the min and max of the image data for the colorbar range.
        Defaults to None.
    title : str, optional
        The full title for the plot.
    xlim, ylim : sequence of numeric, optional
        Lower and upper limits for the axes ticks for the plot.
        Format: xlim=[<x-axis lower limit>, <x-axis upper limit>]
                ylim=[<y-axis lower limit>, <y-axis upper limit>]
    xlabel, ylabel : str, optional
        Axes labels for the x-axis and y-axis (respectively).
    """
    fig = plt.figure(
        figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE, constrained_layout=True
    )

    if title is not None:
        fig.suptitle(title)

    # Create two subplots; one to hold the actual raster image, the second
    # (smaller one) for the HSI "colorbar".
    # (Use add_subplot() to force the colorbar to be tall and skinny.)
    ax = fig.add_gridspec(5, 6)
    ax1 = fig.add_subplot(ax[:, :-2])
    # Call it `cax_pseudo` because this is a matplotlib.axes.Axes object,
    # and not a true matplotlib.colorbar.Colorbar object.
    cax_pseudo = fig.add_subplot(ax[1:4, -1])

    # Set all NaN pixels to 1 in each of the red-green-blue layers.
    # This way, the NaN pixels will appear white in the PDF.
    img_to_plot = img_arr.copy()
    img_to_plot[~np.isfinite(img_arr)] = 1

    # Decimate image to a size that fits on the axes without interpolation
    # and without making the size (in MB) of the PDF explode.
    img_to_plot = downsample_img_to_size_of_axes(
        ax=ax1, arr=img_to_plot, mode="decimate"
    )

    # Plot the raster image and label it
    ax1.imshow(img_to_plot, aspect="equal", cmap="hsv", interpolation="none")

    # There are two subplots, and we want the main plot title to appear
    # over both subplots (aka centered in the figure). So, do not supply
    # the title here, otherwise the main plot title will only be centered
    # over `ax1``. (The main plot title was set above, via `fig.suptitle()`.)
    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax1,
        img_arr_shape=np.shape(img_to_plot),
        xlim=xlim,
        ylim=ylim,
        xlabel=xlabel,
        ylabel=ylabel,
    )

    # Create the HSI "colorbar" (which is actually a subplot)
    v, h = np.mgrid[0:1:100j, 0:1:300j]
    s = np.ones_like(v)
    hsv = np.dstack((h, s, v))
    rgb = colors.hsv_to_rgb(hsv)
    rgb = np.rot90(rgb, k=3)
    rgb = np.fliplr(rgb)

    if cbar_min_max is None:
        cbar_max = np.nanmax(img_arr)
        cbar_min = np.nanmin(img_arr)

    else:
        if (len(cbar_min_max) != 2) or (cbar_min_max[0] >= cbar_min_max[1]):
            raise ValueError(
                f"{cbar_min_max=}, must be a pair of increasing values."
            )
        cbar_max = cbar_min_max[1]
        cbar_min = cbar_min_max[0]

    cax_pseudo.imshow(
        rgb,
        origin="lower",
        extent=[0, 1, cbar_min, cbar_max],
    )
    cax_pseudo.set_xlabel("InSAR\nCoherence\nMagnitude", fontsize=8.5)
    cax_pseudo.set_ylabel(
        "InSAR Phase (radians)", fontsize=8.5, rotation=270, labelpad=10
    )
    cax_pseudo.yaxis.set_label_position("right")
    cax_pseudo.yaxis.tick_right()

    format_cbar_ticks_for_multiples_of_pi(
        cbar_min=cbar_min, cbar_max=cbar_max, cax=cax_pseudo
    )

    cax_pseudo.set_title("HSI Color Space\nSaturation=1", fontsize=8.5)

    # Append figure to the output PDF
    plots_pdf.savefig(fig)

    # Close the plot
    plt.close(fig)


def format_cbar_ticks_for_multiples_of_pi(
    cbar_min: float,
    cbar_max: float,
    cax: mpl.colorbar.Colorbar | mpl.axes.Axes,
) -> None:
    """
    Pretty-format a colorbar-like axis so its y-axis labels are multiples of pi.

    If the min/max interval is too large, or if the interval does not evenly
    divide into multiples of pi, then `cax` will not be modified.

    Parameters
    ----------
    cbar_min, cbar_max : float
        The lower and upper values (respectively) for the colorbar interval.
    cax : mpl.colorbar.Colorbar | mpl.axes.Axes
        The "colorbar" axes whose y labels and ticks will be modified.
    """
    if isinstance(cax, mpl.colorbar.Colorbar):
        cax_yaxis = cax.ax.yaxis
    elif isinstance(cax, mpl.axes.Axes):
        cax_yaxis = cax.yaxis
    else:
        raise TypeError(
            f"`cax` has type {type(cax)}, must be type"
            " matplotlib.colorbar.Colorbar or matplotlib.axes.Axes."
        )

    if np.isclose(cbar_max, cbar_max, atol=1e-6, rtol=0.0):
        nisarqa.get_logger().warning(
            f"{cbar_max=} and {cbar_min=}, which are approximately equal."
            " Suggest double-checking datasets are as expected."
        )
    # To be NaN-safe, do not simply use `if cbar_max <= cbar_min`.
    elif not (cbar_max > cbar_min):
        raise ValueError(
            f"cbar_max must be > cbar_min, but got {cbar_max=} and {cbar_min=}."
        )

    # If the colorbar range covers an integer multiple of pi, then re-format
    # the ticks marks to look nice.
    epsilon = 1e-6
    if ((cbar_max % np.pi) < epsilon) and ((cbar_min % np.pi) < epsilon):
        # Compute tick values
        num_ticks = int(round((cbar_max - cbar_min) / np.pi)) + 1
        tick_vals = cbar_min + np.pi * np.arange(num_ticks)

        # Only pretty-format if there are a small-ish number of ticks
        # If support for a higher number is desired, then add'l code will
        # need to be written to decimate `tick_vals` appropriately.
        if len(tick_vals) < 9:

            def _format_pi(val, pos):
                x = val / np.pi
                atol = 1e-3
                if np.isclose(x, 0.0, atol=atol):
                    return "0"
                if np.isclose(x, 1.0, atol=atol):
                    return r"$\pi$"
                if np.isclose(x, -1.0, atol=atol):
                    return r"$-\pi$"
                return rf"{Fraction(f'{x:.2f}')}$\pi$"

            cax_yaxis.set_ticks(tick_vals)
            cax_yaxis.set_major_formatter(FuncFormatter(_format_pi))
    else:
        nisarqa.get_logger().info(
            f"Provided interval [{cbar_min}, {cbar_max}] does not"
            " nicely divide into multiples of pi for the colorbar, so axis"
            " will not be modified."
        )


def downsample_img_to_size_of_axes(
    ax: mpl.axes.Axes, arr: np.ndarray, mode: str = "decimate"
) -> np.ndarray:
    """
    Downsample array to size of axes for use with `interpolation='none'`.

    In Matplotlib, setting `interpolation='none'` is useful for creating crisp
    images in e.g. output PDFs. However, when an image array is very large,
    this setting causes the generated plots (and the PDFs they're saved to)
    to be very large in size (potentially several hundred MB).

    This function is designed to downsample a large image array to have X and Y
    dimensions appropriate for the size of the given axes object.
    It maintains the same aspect ratio as the source image array.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes object. The window extent and other properties of this axes
        will be used to compute the downsampling factor for the image array.
    arr : numpy.ndarray
        The (image) array to be downsampled.
    mode : str, optional
        Downsampling algorithm. One of:
            "decimate" : (default) Pure decimation. For example, if the
                downsampling stride is determined to be `3`, then every 3rd row
                and 3rd column will be extracted to form the downsampled image.
            "multilook" : Naive, unweighted multilooking. For example,
                if the downsampling stride is determined to be `3`,
                then every 3-by-3 window (9 pixels total) will be averaged
                to form the output pixel.
                Note that if any of those 9 input pixels is NaN, then the
                output pixel will be NaN.

    Returns
    -------
    out_arr : numpy.ndarry
        Copy of `arr` that has been downsampled along the first two dimensions
        so that the number of pixels in the X and Y dimensions
        approximately fits "nicely" in the window extent of the given axes.
        If the image is smaller than the axes, no downsampling will occur.

    See Also
    --------
    nisarqa.compute_square_pixel_nlooks : Function to compute the downsampling
        strides for an image array;
        this function also accounts for making the pixels "square".
    """
    fig = ax.get_figure()

    # Get size of ax window in inches
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

    src_arr_height, src_arr_width = np.shape(arr)[:2]
    if src_arr_height >= src_arr_width:
        # In this conditional, the image is taller than it is wide.
        # So, we'll want to "shrink" the image to the height of the axis.
        # (Multiply by fig.dpi to convert from inches to pixels.)
        desired_longest = bbox.height * fig.dpi

        if src_arr_height <= desired_longest:
            # input array is smaller than window extent. No downsampling needed.
            return arr

        # Use floor division. (Better to have resolution that is *slightly*
        # better than the axes size, rather than the image being too small
        # and needing to re-stretch it bigger to the size of the axes.)
        stride = int(src_arr_height / desired_longest)
    else:
        # In this conditional, the image is shorter than it is tall.
        # So,  we'll want to "shrink" the image to the width of the axis.
        # (Multiply by fig.dpi to convert from inches to pixels.)
        desired_longest = bbox.width * fig.dpi

        if src_arr_width <= desired_longest:
            # input array is smaller than window extent. No downsampling needed.
            return arr

        # Use floor division. See explanation above.)
        stride = int(src_arr_width / desired_longest)

    # Downsample to the correct size along the X and Y directions.
    if mode == "decimate":
        return arr[::stride, ::stride]
    elif mode == "multilook":
        return nisarqa.multilook(arr=arr, nlooks=(stride, stride))
    else:
        raise ValueError(
            f"`{mode=}`, only 'decimate' and 'multilook' supported."
        )


def image_histogram_equalization(
    image: np.ndarray, nbins: int = 256
) -> np.ndarray:
    """
    Perform histogram equalization of a grayscale image.

    Parameters
    ----------
    image : numpy.ndarray
        N-dimensional image array. All dimensions will be combined when
        computing the histogram.
    nbins : int, optional
        Number of bins for computing the histogram.
        Defaults to 256.

    Returns
    -------
    equalized_img : numpy.ndarray
        The image with histogram equalization applied.
        This image will be in range [0, 1].

    References
    ----------
    Adapted from: skimage.exposure.equalize_hist
    Description of histogram equalization:
    https://scikit-image.org/docs/stable/auto_examples/color_exposure/plot_equalize.html
    """
    # Do not include NaN values
    img = image[np.isfinite(image)]

    hist, bin_edges = np.histogram(img.flatten(), bins=nbins, range=None)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0

    cdf = hist.cumsum()
    cdf = cdf / float(cdf[-1])

    out = np.interp(image.flatten(), bin_centers, cdf)
    out = out.reshape(image.shape)

    # Sanity Check. Mathematically, the output should be within range [0, 1].
    assert np.all(
        (0.0 <= out[np.isfinite(out)]) & (out[np.isfinite(out)] <= 1.0)
    ), "`out` contains values outside of range [0, 1]."

    # Unfortunately, np.interp currently always promotes to float64, so we
    # have to cast back to single precision when float32 output is desired
    return out.astype(image.dtype, copy=False)


def process_az_and_slant_rg_offsets_from_igram_product(
    product: nisarqa.IgramOffsetsGroup,
    params: nisarqa.ThresholdParamGroup,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
) -> None:
    """
    Create and append azimuth and slant range offsets plots to PDF.

    This function is for use with nisarqa.IgramOffsetsGroup products
    (RIFG, RUNW, and GUNW). It it not compatible with nisarqa.OffsetProduct
    products (ROFF and GOFF).

    Parameters
    ----------
    product : nisarqa.OffsetProduct
        Input NISAR product.
    params : nisarqa.ThresholdParamGroup
        A structure containing the parameters for checking the percentage
        of invalid pixels in the azimuth and slant range offsets layers.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the offsets plots to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq=freq):
            with (
                product.get_along_track_offset(freq=freq, pol=pol) as az_raster,
                product.get_slant_range_offset(freq=freq, pol=pol) as rg_raster,
            ):
                process_range_and_az_offsets(
                    az_offset=az_raster,
                    rg_offset=rg_raster,
                    params=params,
                    report_pdf=report_pdf,
                    stats_h5=stats_h5,
                )


@overload
def process_range_and_az_offsets(
    az_offset: nisarqa.RadarRaster,
    rg_offset: nisarqa.RadarRaster,
    params: nisarqa.ThresholdParamGroup,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
) -> None: ...


@overload
def process_range_and_az_offsets(
    az_offset: nisarqa.GeoRaster,
    rg_offset: nisarqa.GeoRaster,
    params: nisarqa.ThresholdParamGroup,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
) -> None: ...


def process_range_and_az_offsets(
    az_offset, rg_offset, params, report_pdf, stats_h5
):
    """
    Plot azimuth and range offsets to PDF, and compute statistics on them.

    The colorbar interval is determined by the maximum offset value in
    either raster, and then centered at zero. This way the side-by-side plots
    will be plotted with the same colorbar scale.

    Parameters
    ----------
    az_offset : nisarqa.RadarRaster or nisarqa.GeoRaster
        Along track offset layer to be processed. Must correspond to
        `rg_offset`.
    rg_offset : nisarqa.RadarRaster or nisarqa.GeoRaster
        Slant range offset layer to be processed. Must correspond to
        `az_offset`.
    params : nisarqa.ThresholdParamGroup
        A structure containing the parameters for checking the percentage
        of invalid pixels in the input *Rasters.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the offsets plots to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    """
    # Compute Statistics first, in case of malformed layers
    # (which could cause plotting to fail)
    nisarqa.compute_and_save_basic_statistics(
        raster=az_offset, stats_h5=stats_h5, params=params
    )

    nisarqa.compute_and_save_basic_statistics(
        raster=rg_offset, stats_h5=stats_h5, params=params
    )

    # Plot offset layers to PDF
    plot_range_and_az_offsets_to_pdf(
        az_offset=az_offset, rg_offset=rg_offset, report_pdf=report_pdf
    )

    # Plot Histograms
    process_two_histograms(
        raster1=az_offset,
        raster2=rg_offset,
        report_pdf=report_pdf,
        stats_h5=stats_h5,
        name_of_histogram_pair="Along Track and Slant Range Offsets",
        r1_xlabel="Displacement",
        r2_xlabel="Displacement",
        sharey=True,
    )


@overload
def plot_range_and_az_offsets_to_pdf(
    az_offset: nisarqa.RadarRaster,
    rg_offset: nisarqa.RadarRaster,
    report_pdf: PdfPages,
) -> None: ...


@overload
def plot_range_and_az_offsets_to_pdf(
    az_offset: nisarqa.GeoRaster,
    rg_offset: nisarqa.GeoRaster,
    report_pdf: PdfPages,
) -> None: ...


def plot_range_and_az_offsets_to_pdf(az_offset, rg_offset, report_pdf):
    """
    Create and append a side-by-side plot of azimuth and range offsets to PDF.

    The colorbar interval is determined by the maximum offset value in
    either raster, and then centered at zero. This way the side-by-side plots
    will be plotted with the same colorbar scale.

    Parameters
    ----------
    az_offset : nisarqa.RadarRaster or nisarqa.GeoRaster
        Along track offset layer to be processed. Must correspond to
        `rg_offset`.
    rg_offset : nisarqa.RadarRaster or nisarqa.GeoRaster
        Slant range offset layer to be processed. Must correspond to
        `az_offset`.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the offsets plots to.
    """
    # Validate that the pertinent metadata in the rasters is equal.
    nisarqa.compare_raster_metadata(az_offset, rg_offset, almost_identical=True)

    az_img = nisarqa.decimate_raster_array_to_square_pixels(az_offset)
    rg_img = nisarqa.decimate_raster_array_to_square_pixels(rg_offset)

    # Compute the colorbar interval, centered around zero.
    # Both plots should use the larger of the intervals.
    def get_max_abs_val(img: npt.ArrayLike) -> float:
        return max(np.abs(np.nanmax(img)), np.abs(np.nanmin(img)))

    az_max = get_max_abs_val(az_img)
    rg_max = get_max_abs_val(rg_img)
    cbar_max = max(az_max, rg_max)
    cbar_min = -cbar_max  # center around zero

    # Create figure and add the rasters.
    fig, (ax1, ax2) = plt.subplots(
        nrows=1,
        ncols=2,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_TWO_PLOTS_PER_PAGE,
        sharey=True,
    )
    fig.suptitle("Along Track Offsets and Slant Range Offsets (meters)")

    # Decimate Along Track Offset raster and plot on left (ax1)
    az_img = downsample_img_to_size_of_axes(ax=ax1, arr=az_img, mode="decimate")
    ax1.imshow(
        az_img,
        aspect="equal",
        cmap="magma",
        interpolation="none",
        vmin=cbar_min,
        vmax=cbar_max,
    )

    # Form axes title. Split raster's name onto a new line to look nicer.
    # `az_offset.name` has a format like:
    #     "RUNW_L_A_pixelOffsets_HH_alongTrackOffset"
    raster_name = az_offset.name.split("_")[-1]
    axes_title = az_offset.name.replace(f"_{raster_name}", f"\n{raster_name}")
    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax1,
        img_arr_shape=np.shape(az_img),
        xlim=az_offset.x_axis_limits,
        ylim=az_offset.y_axis_limits,
        xlabel=az_offset.x_axis_label,
        ylabel=az_offset.y_axis_label,
        title=axes_title,
    )

    # Decimate slant range Offset raster and plot on right (ax2)
    rg_img = downsample_img_to_size_of_axes(ax=ax2, arr=rg_img, mode="decimate")
    im2 = ax2.imshow(
        rg_img,
        aspect="equal",
        cmap="magma",
        interpolation="none",
        vmin=cbar_min,
        vmax=cbar_max,
    )
    # Form axes title. Split raster's name onto a new line to look nicer.
    # `rg_offset.name` has a format like:
    #     "RUNW_L_A_pixelOffsets_HH_slantRangeOffset"
    raster_name = rg_offset.name.split("_")[-1]
    axes_title = rg_offset.name.replace(f"_{raster_name}", f"\n{raster_name}")
    # No y-axis label nor ticks for the right side plot; y-axis is shared.
    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax2,
        img_arr_shape=np.shape(rg_img),
        xlim=rg_offset.x_axis_limits,
        xlabel=rg_offset.x_axis_label,
        title=axes_title,
    )

    # To save space on the PDF page, add the colorbar to only the right plot.
    # (Both plots have the same colorbar scale.)
    cax = fig.colorbar(im2, ax=ax2)
    cax.ax.set_ylabel(ylabel="Displacement (m)", rotation=270, labelpad=8.0)

    # Save complete plots to graphical summary PDF file
    report_pdf.savefig(fig)

    # Close figure
    plt.close(fig)


def process_az_and_slant_rg_offsets_from_offset_product(
    product: nisarqa.OffsetProduct,
    params_quiver: nisarqa.QuiverParamGroup,
    params_offsets: nisarqa.ThresholdParamGroup,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
    browse_png: str | os.PathLike,
):
    """
    Process side-by-side az and range offsets plots and quiver plots.

    This function takes each pair of along track offset and slant range offset
    raster layers, and:
        * Saves the browse image quiver plot as a PNG.
            - (The specific freq+pol+layer_number to use for the browse image
               is determined by the input `product`.)
        * Plots them side-by-side and appends this plot to PDF
        * Computes statistics for these layers
        * Plots them as a quiver plot and appends this plot to PDF

    This function is for use with nisarqa.OffsetProduct products (ROFF, GOFF).
    It it not compatible with nisarqa.IgramOffsetsGroup products (RIFG,
    RUNW, GUNW).

    Parameters
    ----------
    product : nisarqa.OffsetProduct
        Input NISAR product.
    params_quiver : nisarqa.QuiverParamGroup
        A structure containing processing parameters to generate quiver plots.
    params_offsets : nisarqa.ThresholdParamGroup
        A structure containing the parameters for checking the percentage
        of invalid pixels in the azimuth and slant range offsets layers.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output pdf file to append the quiver plot to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    browse_png : path-like
        Filename (with path) for the browse image PNG.
    """
    # Generate a browse PNG for one layer
    freq, pol, layer_num = product.get_browse_freq_pol_layer()

    with (
        product.get_along_track_offset(
            freq=freq, pol=pol, layer_num=layer_num
        ) as az_off,
        product.get_slant_range_offset(
            freq=freq, pol=pol, layer_num=layer_num
        ) as rg_off,
    ):
        y_dec, x_dec = plot_single_quiver_plot_to_png(
            az_offset=az_off,
            rg_offset=rg_off,
            params=params_quiver,
            png_filepath=browse_png,
        )

        nisarqa.create_dataset_in_h5group(
            h5_file=stats_h5,
            grp_path=nisarqa.STATS_H5_QA_PROCESSING_GROUP % product.band,
            ds_name="browseDecimation",
            ds_data=[y_dec, x_dec],
            ds_units="1",
            ds_description=(
                "Decimation strides for the browse image."
                " Format: [<y decimation>, <x decimation>]."
            ),
        )

    # Populate PDF with side-by-side plots and quiver plots.
    for freq in product.freqs:
        for pol in product.get_pols(freq):
            for layer_num in product.available_layer_numbers:
                with (
                    product.get_along_track_offset(
                        freq=freq, pol=pol, layer_num=layer_num
                    ) as az_off,
                    product.get_slant_range_offset(
                        freq=freq, pol=pol, layer_num=layer_num
                    ) as rg_off,
                ):
                    # First, create the canonical side-by-side plot of the
                    # along track offsets vs. the slant range offsets.
                    process_range_and_az_offsets(
                        az_offset=az_off,
                        rg_offset=rg_off,
                        params=params_offsets,
                        report_pdf=report_pdf,
                        stats_h5=stats_h5,
                    )

                    # Second, create the quiver plots for PDF
                    cbar_min, cbar_max = plot_offsets_quiver_plot_to_pdf(
                        az_offset=az_off,
                        rg_offset=rg_off,
                        params=params_quiver,
                        report_pdf=report_pdf,
                    )

                # Add final colorbar range processing parameter for this
                # freq+pol+layer quiver plot to stats.h5.
                # (This was a YAML runconfig processing parameter, so we should
                # document it in the stats.h5. However, when dynamically
                # computed, this range is not consistent between the numbered
                # layers. So, let's use a longer name.
                name = (
                    f"quiverPlotColorbarIntervalFrequency{freq}"
                    f"Polarization{pol}Layer{layer_num}"
                )
                nisarqa.create_dataset_in_h5group(
                    h5_file=stats_h5,
                    grp_path=nisarqa.STATS_H5_QA_PROCESSING_GROUP
                    % product.band,
                    ds_name=name,
                    ds_data=(cbar_min, cbar_max),
                    ds_units="meters",
                    ds_description=(
                        "Colorbar interval for the slant range and along track"
                        " offset layers' quiver plot(s)."
                    ),
                )


@overload
def plot_offsets_quiver_plot_to_pdf(
    az_offset: nisarqa.RadarRaster,
    rg_offset: nisarqa.RadarRaster,
    params: nisarqa.QuiverParamGroup,
    report_pdf: PdfPages,
) -> tuple[float, float]: ...


@overload
def plot_offsets_quiver_plot_to_pdf(
    az_offset: nisarqa.GeoRaster,
    rg_offset: nisarqa.GeoRaster,
    params: nisarqa.QuiverParamGroup,
    report_pdf: PdfPages,
) -> tuple[float, float]: ...


def plot_offsets_quiver_plot_to_pdf(az_offset, rg_offset, params, report_pdf):
    """
    Process and save a single quiver plot to PDF.

    Parameters
    ----------
    az_offset : nisarqa.RadarRaster or nisarqa.GeoRaster
        Along track offset layer to be processed. Must correspond to
        `rg_offset`.
    rg_offset : nisarqa.RadarRaster or nisarqa.GeoRaster
        Slant range offset layer to be processed. Must correspond to
        `az_offset`.
    params : nisarqa.QuiverParamGroup
        A structure containing processing parameters to generate quiver plots.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the quiver plot to.

    Returns
    -------
    cbar_min, cbar_max : float
        The vmin and vmax (respectively) used for the colorbar and clipping
        the pixel offset displacement image.
    """
    # Validate input rasters
    nisarqa.compare_raster_metadata(az_offset, rg_offset, almost_identical=True)

    # Grab the datasets into arrays in memory (with square pixels).
    az_off = nisarqa.decimate_raster_array_to_square_pixels(
        raster_obj=az_offset
    )
    rg_off = nisarqa.decimate_raster_array_to_square_pixels(
        raster_obj=rg_offset
    )

    fig, ax = plt.subplots(
        ncols=1,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE,
    )

    # Form the plot title (Remove the layer name from the layer's `name`)
    # Because of the constrained layout (which optimizes for all Artists in
    # the Figure), let's add the title before decimating the rasters.
    # (`az_offset.name` is formatted like "ROFF_L_A_HH_layer1_alongTrackOffset".
    # The PDF page has two rasters, so remove the final layer name for title.)
    title = (
        "Combined Pixel Offsets (meters)\n"
        f"{'_'.join(az_offset.name.split('_')[:-1])}"
    )
    fig.suptitle(title)

    az_off = downsample_img_to_size_of_axes(ax=ax, arr=az_off, mode="decimate")
    rg_off = downsample_img_to_size_of_axes(ax=ax, arr=rg_off, mode="decimate")

    im, cbar_min, cbar_max = add_magnitude_image_and_quiver_plot_to_axes(
        ax=ax, az_off=az_off, rg_off=rg_off, params=params
    )

    # Add a colorbar to the figure
    cax = fig.colorbar(im)
    cax.ax.set_ylabel(ylabel="Displacement (m)", rotation=270, labelpad=10.0)

    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax,
        xlim=az_offset.x_axis_limits,
        ylim=az_offset.y_axis_limits,
        img_arr_shape=np.shape(az_off),
        xlabel=az_offset.x_axis_label,
        ylabel=az_offset.y_axis_label,
    )

    # Append figure to the output PDF
    report_pdf.savefig(fig)

    # Close the plot
    plt.close(fig)

    return cbar_min, cbar_max


@overload
def plot_single_quiver_plot_to_png(
    az_offset: nisarqa.RadarRaster,
    rg_offset: nisarqa.RadarRaster,
    params: nisarqa.QuiverParamGroup,
    png_filepath: str | os.PathLike,
) -> tuple[int, int]: ...


@overload
def plot_single_quiver_plot_to_png(
    az_offset: nisarqa.GeoRaster,
    rg_offset: nisarqa.GeoRaster,
    params: nisarqa.QuiverParamGroup,
    png_filepath: str | os.PathLike,
) -> tuple[int, int]: ...


def plot_single_quiver_plot_to_png(
    az_offset,
    rg_offset,
    params,
    png_filepath,
):
    """
    Process and save a single quiver plot to PDF and (optional) PNG.

    Parameters
    ----------
    az_offset : nisarqa.RadarRaster or nisarqa.GeoRaster
        Along track offset layer to be processed. Must correspond to
        `rg_offset`.
    rg_offset : nisarqa.RadarRaster or nisarqa.GeoRaster
        Slant range offset layer to be processed. Must correspond to
        `az_offset`.
    params : nisarqa.QuiverParamGroup
        A structure containing processing parameters to generate quiver plots.
    png_filepath : path-like
        Filename (with path) for the image PNG.

    Returns
    -------
    y_dec, x_dec : int
        The decimation stride value used in the Y axis direction and X axis
        direction (respectively).
    """
    # Validate input rasters
    nisarqa.compare_raster_metadata(az_offset, rg_offset, almost_identical=True)

    # Compute decimation values for the browse image PNG.
    if (az_offset.freq == "A") and (params.browse_decimation_freqa is not None):
        y_decimation, x_decimation = params.browse_decimation_freqa
    elif (az_offset.freq == "B") and (
        params.browse_decimation_freqb is not None
    ):
        y_decimation, x_decimation = params.browse_decimation_freqb
    else:
        # Square the pixels. Decimate if needed to stay within longest side max.
        longest_side_max = params.longest_side_max

        if longest_side_max is None:
            # Update to be the longest side of the array. This way no downsizing
            # of the image will occur, but we can still output square pixels.
            longest_side_max = max(np.shape(rg_offset.data))

        y_decimation, x_decimation = nisarqa.compute_square_pixel_nlooks(
            img_shape=np.shape(az_offset.data),
            sample_spacing=[az_offset.y_axis_spacing, az_offset.x_axis_spacing],
            longest_side_max=longest_side_max,
        )

    # Grab the datasets into arrays in memory.
    # While doing this, convert to square pixels and correct pixel dimensions.
    az_off = az_offset.data[::y_decimation, ::x_decimation]
    rg_off = rg_offset.data[::y_decimation, ::x_decimation]

    # Next, we need to add the background image + quiver plot arrows onto
    # an Axes, and then save this to a PNG with exact pixel dimensions as
    # `az_off` and `rg_off`.
    quiver_func = functools.partial(
        add_magnitude_image_and_quiver_plot_to_axes,
        az_off=az_off,
        rg_off=rg_off,
        params=params,
    )

    save_mpl_plot_to_png(
        axes_partial_func=quiver_func,
        raster_shape=az_off.shape,
        png_filepath=png_filepath,
    )

    return y_decimation, x_decimation


def add_magnitude_image_and_quiver_plot_to_axes(
    ax: mpl.axes.Axes,
    az_off: np.ndarray,
    rg_off: np.ndarray,
    params: nisarqa.QuiverParamGroup,
) -> tuple[mpl.AxesImage, float, float]:
    """
    Compute the total offset magnitude and add as a quiver plot to an Axes.

    This function computes the total offset magnitude via this formula:
        total_offset = sqrt(rg_off**2 + az_off**2)
    `total_offset` is used as the background image, with the magma color map.
    The quiver arrows (vector arrows) are added to the Axes on top of the
    `total_offset` image.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes object that will be modified; the total offset magnitude image
        and the quiver plot arrows will be added to this axes.
    az_off : numpy.ndarray
        Along track offset raster array.
    rg_off : numpy.ndarray
        Slant range offset raster array.
    params : nisarqa.QuiverParamGroup
        A structure containing processing parameters to generate quiver plots.

    Returns
    -------
    im : matplotlib.AxesImage
        AxesImage containing the final plotted image (including quiver arrows).
    vmin, vmax : float
        The vmin and vmax (respectively) used for clipping the pixel offset
        displacement image and for the colorbar interval.

    Notes
    -----
    No decimation occurs in this function, and the image arrays are
    plotted on `ax` with interpolation set to "none". This is to maintain the
    same pixel dimensions of the input arrays.

    Prior to calling this function, it is suggested that the user size the
    axes and the input arrays to have matching dimensions. This helps to
    ensure that the aspect ratio of `im` is as expected.
    """

    # Use the full resolution image as the colorful background image of the plot
    total_offset = np.sqrt(rg_off**2 + az_off**2)

    # Compute the vmin and vmax for the colorbar range
    # Note: because we're getting `cbar_min_max` from the `params`, the values
    # have already been validated. No further checks needed.
    cbar_min_max = params.cbar_min_max
    if cbar_min_max is None:
        # Dynamically compute the colorbar interval to be [0, max].
        # (`total_offset` represents magnitude; these are positive values)
        vmin, vmax = 0, np.nanmax(total_offset)
    else:
        vmin, vmax = cbar_min_max

    # Truncate the magma cmap to only use the top half of the magma colormap
    # Adapted from: https://stackoverflow.com/a/18926541
    def truncate_colormap(
        cmap: colors.ListedColormap,
        minval: float = 0.0,
        maxval: float = 1.0,
        n: int = -1,
    ) -> colors.LinearSegmentedColormap:
        """
        Truncate a colormap to only use a subset of the colormap.

        A colormap maps values in the interval [0.0, 1.0] to specific visual
        colors. For a known colormap, sometimes we only want to use a
        sub-interval of its visual color range for our plot. This function
        allows the user to specify the sub-interval of the existing colorbar
        that they want to use, and returns a new colormap with the
        visual colors from that sub-interval "stretched" to fill the entire
        [0.0, 1.0] colormap range.

        Parameters
        ----------
        cmap : colors.ListedColormap
            An existing colormap. This can be fetched by calling e.g.
            matplotlib.pyplot.get_cmap("magma").
        minval : float, optional
            Minimum value of the sub-interval of `cmap` to use. Must be >= 0.0.
            Defaults to 0.0.
        maxval : float, optional
            Maximum value of the sub-interval of `cmap` to use. Must be <= 1.0.
            Defaults to 1.0.
        n : int, optional
            Number of entries to generate in the truncated colormap. (256 is
            a typical value.) -1 to use the same numbers of entries as `cmap`.
            Defaults to -1.

        Returns
        -------
        truncated_cmap : matplotlib.colors.LinearSegmentedColormap
            A new colormap with the visual colors from the sub-interval
            [`minval`, `maxval`] of `cmap`'s colormap "stretched" to
            fill the entire colormap range.
        """
        if (minval < 0.0) or (maxval > 1.0):
            raise ValueError(
                f"{minval=} and {maxval=}, but must be in range [0.0, 1.0]."
            )
        if n == -1:
            n = cmap.N
        new_cmap = colors.LinearSegmentedColormap.from_list(
            "trunc({name},{a:.2f},{b:.2f})".format(
                name=cmap.name, a=minval, b=maxval
            ),
            cmap(np.linspace(minval, maxval, n)),
        )
        return new_cmap

    # Use interval from [0.5, 1.0] to truncate to the top half of the magma
    # colormap range. (We do not want to use the very-dark lower half
    # for these quiver plots.)
    # Definitions: the colormap range is different than the colorbar range.
    # Colorbar range refers to the range of tick label values, while the
    # colormap determines the mapping of those values to actual visual colors.
    magma_cmap = truncate_colormap(plt.get_cmap("magma"), 0.5, 1.0)

    # Add the background image to the axes
    im = ax.imshow(
        total_offset,
        vmin=vmin,
        vmax=vmax,
        cmap=magma_cmap,
        interpolation="none",
    )

    # Now, prepare and add the quiver plot arrows to the axes
    arrow_stride = int(max(np.shape(total_offset)) / params.arrow_density)

    # Only plot the arrows at the requested strides.
    arrow_y = az_off[::arrow_stride, ::arrow_stride]
    arrow_x = rg_off[::arrow_stride, ::arrow_stride]

    x = np.linspace(0, arrow_x.shape[1] - 1, arrow_x.shape[1])
    y = np.linspace(0, arrow_x.shape[0] - 1, arrow_x.shape[0])
    X, Y = np.meshgrid(x, y)

    # Add the quiver arrows to the plot.
    # Multiply the start and end points for each arrow by the decimation factor;
    # this is to ensure that each arrow is placed on the correct pixel on
    # the full-resolution `total_offset` background image.
    ax.quiver(
        # starting x coordinate for each arrow
        X * arrow_stride,
        # starting y coordinate for each arrow
        Y * arrow_stride,
        # ending x direction component of for each arrow vector
        arrow_x * arrow_stride,
        # ending y direction component of for each arrow vector
        arrow_y * arrow_stride,
        angles="xy",
        scale_units="xy",
        # Use a scale less that 1 to exaggerate the arrows.
        scale=params.arrow_scaling,
        color="b",
    )

    return im, vmin, vmax


def save_mpl_plot_to_png(
    axes_partial_func: Callable[[mpl.axes.Axes], None],
    raster_shape: tuple[int, int],
    png_filepath: str | os.PathLike,
) -> None:
    """
    Save a Matplotlib plot to PNG with exact pixel dimensions.

    Matplotlib's `figsave` and related functions are useful for saving plots
    to PNG, etc. files. However, these built-in functions do not preserve
    the exact 2D pixel dimensions of the source array in the PNG, which is
    necessary when generating the browse images. This function works
    around this issue, and saves the plot with the exact pixel dimensions.

    Parameters
    ----------
    axes_partial_func : callable
        Function with a single positional argument of type matplotlib.axes.Axes.
        Internally, this function should take the input Axes object and
        modify that Axes with the correct raster plot, colormap, etc.
        (See example below.)
    raster_shape : pair of int
        2D shape of the raster plotted by `axes_partial_func`. The output
        PNG will have these pixel dimensions.
    png_filepath : path-like
        Filename (with path) for the image PNG.

    Examples
    --------
    >>> import nisarqa
    >>> import numpy as np
    >>> arr = np.random.rand(30,50)
    >>> def my_partial(ax):
    ...     ax.imshow(arr, cmap="magma", interpolation="none")
    ...
    >>> nisarqa.save_mpl_plot_to_png(
                axes_partial_func=my_partial,
                raster_shape=np.shape(arr),
                png_filepath="browse.png")

    The array is now plotted with the magma colormap and saved as a PNG to the
    file browse.png, and the PNG has exact dimensions of 30 pixels x 50 pixels.
    """

    # We can set the exact size of a Figure window, but not the exact
    # size of an Axes object that sits within that Figure.
    # Since matplotilb defaults to adding extra "stuff" (white space,
    # labels, tick marks, title, etc.) in the border around the Axes, this
    # forces the Axes size to be smaller than the Figure size.
    # This means that using the typical process to create and saving the image
    # plot out to PNG results in a PNG whose pixel dimensions are
    # significantly smaller than the dimensions of the source np.array.
    # Not ideal in for our browse.

    # Strategy to get around this: Create a Figure with our desired dimensions,
    # and then add an Axes object whose extents are set to ENTIRE Figure.
    # We'll need to take care that there is no added space around the border for
    # labels, tick marks, title, etc. which could cause Matplotlib to
    # automagically downscale (and mess up) the dimensions of the Axes.

    # Step 1: Create a figure with the exact shape in pixels as our array
    # (Matplotlib's Figure uses units of inches, but the image array
    # and our browse image PNG requirements are in units of pixels.)
    dpi = 72
    figure_shape_in_inches = (raster_shape[1] / dpi, raster_shape[0] / dpi)
    fig = plt.figure(figsize=figure_shape_in_inches, dpi=dpi)

    # Step 2: Use tight layout with 0 padding so that Matplotlib does not
    # attempt to add padding around the axes.
    fig.tight_layout(pad=0)

    # Step 3: add a new Axes object; set `rect` to be the ENTIRE Figure shape
    # Order of arguments for rect: left, bottom, right, top
    ax = fig.add_axes(rect=[0, 0, 1, 1])

    # Since we set `rect`, the axes labels, titles, etc. should all be
    # outside of `rect` and thus hidden from the final PNG.
    # But for good measure, let's go ahead and hide them anyways.
    ax.set_axis_off()

    # Use this Axes for plotting
    axes_partial_func(ax)

    # Save to PNG - Make sure to keep the same DPI!
    fig.savefig(png_filepath, transparent=True, dpi=dpi)

    # Close the plot
    plt.close(fig)


def process_az_and_slant_rg_variances_from_offset_product(
    product: nisarqa.OffsetProduct,
    params: nisarqa.VarianceLayersParamGroup,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
) -> None:
    """
    Process az and range offset variance layers: plots to PDF, metrics to HDF5.

    This function takes each pair of along track offset and slant range offset
    variance layers, and:
        * Plots them side-by-side and appends this plot to PDF
        * Computes statistics for these layers

    This function is for use with nisarqa.OffsetProduct products (ROFF, GOFF).
    It it not compatible with nisarqa.IgramOffsetsGroup products (RIFG,
    RUNW, GUNW).

    Parameters
    ----------
    product : nisarqa.OffsetProduct
        Input NISAR product.
    params : nisarqa.VarianceLayersParamGroup
        A structure containing processing parameters to generate the plots
        for the *Variance layers.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output pdf file to append the plot to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq):
            for layer_num in product.available_layer_numbers:
                with (
                    product.get_along_track_offset_variance(
                        freq=freq, pol=pol, layer_num=layer_num
                    ) as az_off_var,
                    product.get_slant_range_offset_variance(
                        freq=freq, pol=pol, layer_num=layer_num
                    ) as rg_off_var,
                ):
                    # Compute Statistics first, in case of malformed layers
                    # (which could cause plotting to fail)
                    nisarqa.compute_and_save_basic_statistics(
                        raster=az_off_var,
                        params=params,
                        stats_h5=stats_h5,
                    )
                    nisarqa.compute_and_save_basic_statistics(
                        raster=rg_off_var,
                        params=params,
                        stats_h5=stats_h5,
                    )

                    plot_range_and_az_offsets_variances_to_pdf(
                        az_offset_variance=az_off_var,
                        rg_offset_variance=rg_off_var,
                        report_pdf=report_pdf,
                        cbar_min_max=params.cbar_min_max,
                    )

                    # Plot Histograms
                    process_two_histograms(
                        raster1=az_off_var,
                        raster2=rg_off_var,
                        report_pdf=report_pdf,
                        stats_h5=stats_h5,
                        name_of_histogram_pair="Azimuth and Slant Range Offsets STD",
                        r1_xlabel="Standard Deviation",
                        r2_xlabel="Standard Deviation",
                        sharey=True,
                        r1_data_prep_func=np.sqrt,
                        r2_data_prep_func=np.sqrt,
                    )


@overload
def plot_range_and_az_offsets_variances_to_pdf(
    az_offset_variance: nisarqa.RadarRaster,
    rg_offset_variance: nisarqa.RadarRaster,
    report_pdf: PdfPages,
    cbar_min_max: Optional[Sequence[float, float]],
) -> None: ...


@overload
def plot_range_and_az_offsets_variances_to_pdf(
    az_offset_variance: nisarqa.GeoRaster,
    rg_offset_variance: nisarqa.GeoRaster,
    report_pdf: PdfPages,
    cbar_min_max: Optional[Sequence[float, float]],
) -> None: ...


def plot_range_and_az_offsets_variances_to_pdf(
    az_offset_variance, rg_offset_variance, report_pdf, cbar_min_max=None
):
    """
    Plot azimuth and slant range offset variance layers as standard dev to PDF.

    The variance raster layers contain "variance" values. This function
    plots the square root of the variance layers, aka the standard deviation
    of the offsets.

    Parameters
    ----------
    az_offset_variance : nisarqa.RadarRaster or nisarqa.GeoRaster
        Along track offset variance layer to be plotted. Must correspond to
        `rg_offset_variance `.
    rg_offset_variance : nisarqa.RadarRaster or nisarqa.GeoRaster
        Slant range offset variance layer to be plotted. Must correspond to
        `az_offset_variance `.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the plots to.
    cbar_min_max : pair of float or None, optional
        The vmin and vmax values to generate the plots
        for the az and slant range variance layers.
        The square root of these layers (i.e. the standard deviation
        of the offsets) is computed, clipped to this interval, and
        then plotted using this interval for the colorbar.
        If `None`:
            If the variance layers' units are meters^2, default to:
                [0.0, 10.0]
            If the variance layers' units are pixels^2, default to:
                [0.0, 0.1]
            If variance layers' units are anything else, default to:
                [0.0, max(max(sqrt(<az var layer>)), max(sqrt(<rg var layer>)))]
        Defaults to None.
    """
    # Validate that the pertinent metadata in the rasters is equal.
    nisarqa.compare_raster_metadata(
        az_offset_variance, rg_offset_variance, almost_identical=True
    )

    az_var = nisarqa.decimate_raster_array_to_square_pixels(az_offset_variance)
    rg_var = nisarqa.decimate_raster_array_to_square_pixels(rg_offset_variance)

    # Setup the side-by-side PDF page
    fig, (ax1, ax2) = plt.subplots(
        ncols=2,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_TWO_PLOTS_PER_PAGE,
        sharey=True,
    )

    # Variance should be in units of e.g. pixels^2 or meters^2. We're plotting
    # stddev, so get the square root of the units.
    var_units = az_offset_variance.units
    if var_units == "meters^2":
        std_units = "meters"
    elif var_units == "pixels^2":
        std_units = "pixels"
    else:
        nisarqa.get_logger().warning(
            "Azimuth and range offset variance layers have units of"
            f" {var_units}. Suggest units of 'pixels^2' or 'meters^2' for"
            " better colorbar range defaults."
        )
        std_units = f"sqrt({var_units})"

    # Construct title for the overall PDF page. (`*raster.name` has a format
    # like "RUNW_L_A_pixelOffsets_HH_slantRangeOffset". We need to
    # remove the final layer name of e.g. "_slantRangeOffset".)
    name = "_".join(az_offset_variance.name.split("_")[:-1])
    title = f"Azimuth and Slant Range Offsets STD ({std_units})\n{name}"
    fig.suptitle(title)

    # Replace non-finite and/or masked-out pixels (i.e. pixels set to the
    # fill value) with NaNs.
    az_fill = az_offset_variance.fill_value
    az_var[~np.isfinite(az_var) | (az_var == az_fill)] = np.nan
    rg_fill = rg_offset_variance.fill_value
    rg_var[~np.isfinite(rg_var) | (rg_var == rg_fill)] = np.nan

    # convert variance layers to standard deviation form
    az_std = np.sqrt(az_var)
    rg_std = np.sqrt(rg_var)

    if cbar_min_max is None:
        # Use same colorbar scale for both plots
        cbar_min = 0.0
        if std_units == "pixels":
            cbar_max = 0.1
        elif std_units == "meters":
            cbar_max = 10.0
        else:
            # Units could not be determined. Set the max to the largest
            # value in the actual arrays being plotted.
            cbar_max = max(np.nanmax(az_std), np.nanmax(rg_std))
    else:
        cbar_min, cbar_max = cbar_min_max

    # Decimate to fit nicely on the figure.
    az_std = downsample_img_to_size_of_axes(ax=ax1, arr=az_std, mode="decimate")
    rg_std = downsample_img_to_size_of_axes(ax=ax2, arr=rg_std, mode="decimate")

    # Add the azimuth offsets variance plot (left plot)
    ax1.imshow(
        az_std,
        aspect="equal",
        cmap="magma_r",
        interpolation="none",
        vmin=cbar_min,
        vmax=cbar_max,
    )

    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax1,
        xlim=az_offset_variance.x_axis_limits,
        ylim=az_offset_variance.y_axis_limits,
        img_arr_shape=np.shape(az_std),
        xlabel=az_offset_variance.x_axis_label,
        ylabel=az_offset_variance.y_axis_label,
        title=az_offset_variance.name.split("_")[-1],
    )

    # Add the slant range offsets variance plot (right plot)
    im2 = ax2.imshow(
        rg_std,
        aspect="equal",
        cmap="magma_r",
        interpolation="none",
        vmin=cbar_min,
        vmax=cbar_max,
    )

    # No y-axis label nor ticks. This is the right side plot; y-axis is shared.
    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax2,
        xlim=rg_offset_variance.x_axis_limits,
        img_arr_shape=np.shape(rg_std),
        xlabel=rg_offset_variance.x_axis_label,
        title=rg_offset_variance.name.split("_")[-1],
    )

    # Add a colorbar to the figure
    cax = fig.colorbar(im2, ax=ax2)
    cax.ax.set_ylabel(
        ylabel=f"Standard deviation ({std_units})",
        rotation=270,
        labelpad=10.0,
    )

    # Append figure to the output PDF
    report_pdf.savefig(fig)

    # Close the plot
    plt.close(fig)


def process_surface_peak(
    product: nisarqa.IgramOffsetsGroup,
    params_surface_peak: nisarqa.ThresholdParamGroup,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
) -> None:
    """
    Process correlation surface peak layers for interferogram products.

    This function takes the correlation surface peak layers, and:
        * Plots them to PDF
        * Computes statistics for these layers

    This function is for use with nisarqa.IgramOffsetsGroup products (RIFG,
    RUNW, GUNW).
    It it not compatible with nisarqa.OffsetProduct products (ROFF, GOFF).

    Parameters
    ----------
    product : nisarqa.IgramOffsetsGroup
        Input NISAR product.
    params_surface_peak : nisarqa.ThresholdParamGroup
        A structure containing processing parameters to generate the
        correlation surface peak layer plots.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the plot to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq):
            with (
                product.get_correlation_surface_peak(
                    freq=freq, pol=pol
                ) as surface_peak,
            ):
                # Compute Statistics first, in case of malformed layers
                nisarqa.compute_and_save_basic_statistics(
                    raster=surface_peak,
                    params=params_surface_peak,
                    stats_h5=stats_h5,
                )

                plot_corr_surface_peak_to_pdf(
                    corr_surf_peak=surface_peak,
                    report_pdf=report_pdf,
                )

                process_single_histogram(
                    raster=surface_peak,
                    report_pdf=report_pdf,
                    stats_h5=stats_h5,
                    xlabel="Normalized Correlation Peak",
                    name_of_histogram="Correlation Surface Peak",
                )


def add_corr_surface_peak_to_axes(
    corr_surf_peak: nisarqa.RadarRaster | nisarqa.GeoRaster,
    ax: mpl.axes.Axes,
    *,
    include_y_axes_labels: bool = True,
    include_axes_title: bool = True,
) -> None:
    """
    Add plot of correlation surface peak layer on a Matplotlib Axes.

    Parameters
    ----------
    corr_surf_peak : nisarqa.RadarRaster or nisarqa.GeoRaster
        Correlation Surface Peak layer to be plotted.
    ax : matplotlib.axes.Axes
        Axes object. The window extent and other properties of this axes
        will be used to compute the downsampling factor for the image array.
    include_y_axes_labels : bool, optional
        True to include the y-axis label and y-axis tick mark labels; False to
        exclude. (The tick marks will still appear, but will be unlabeled.)
        Defaults to True.
    include_axes_title : bool, optional
        True to include a title on the axes itself; False to exclude it.
        Defaults to True.
    """
    # Prepare and plot the correlation surface peak on the right sub-plot
    surf_peak = nisarqa.decimate_raster_array_to_square_pixels(corr_surf_peak)

    # Decimate to fit nicely on the figure.
    surf_peak = downsample_img_to_size_of_axes(
        ax=ax, arr=surf_peak, mode="decimate"
    )

    # Correlation surface peak should always be in range [0, 1]
    if np.any(surf_peak < 0.0) or np.any(surf_peak > 1.0):
        nisarqa.get_logger().error(
            f"{corr_surf_peak.name} contains elements outside of expected range"
            " of [0, 1]."
        )

    # Add the correlation surface peak plot
    im = ax.imshow(
        surf_peak,
        aspect="equal",
        cmap="gray",
        interpolation="none",
        vmin=0.0,
        vmax=1.0,
    )

    if include_axes_title:
        ax_title = corr_surf_peak.name.split("_")[-1]
    else:
        ax_title = None

    if include_y_axes_labels:
        ylim = corr_surf_peak.y_axis_limits
        ylabel = corr_surf_peak.y_axis_label
    else:
        ylim = None
        ylabel = None

    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax,
        xlim=corr_surf_peak.x_axis_limits,
        ylim=ylim,
        img_arr_shape=np.shape(surf_peak),
        xlabel=corr_surf_peak.x_axis_label,
        ylabel=ylabel,
        title=ax_title,
    )

    # Add a colorbar to the surface peak plot
    fig = ax.get_figure()
    cax = fig.colorbar(im, ax=ax)
    cax.ax.set_ylabel(
        ylabel="Normalized correlation peak (unitless)",
        rotation=270,
        labelpad=10.0,
    )


def plot_corr_surface_peak_to_pdf(
    corr_surf_peak: nisarqa.RadarRaster | nisarqa.GeoRaster,
    report_pdf: PdfPages,
) -> None:
    """
    Plot correlation surface peak layer on a single PDF page.

    Parameters
    ----------
    corr_surf_peak : nisarqa.RadarRaster or nisarqa.GeoRaster
        Correlation Surface Peak layer to be plotted.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the offsets plots to.
    """
    # Setup the PDF page
    fig, ax = plt.subplots(
        ncols=1,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE,
    )

    # Construct title for the overall PDF page.
    title = f"Correlation Surface Peak (unitless)\n{corr_surf_peak.name}"
    fig.suptitle(title)

    # Construct the correlation surface peak plot on the axes
    # This is on a single PDF page, so  include y-axis labels, but no need to
    # add a dedicated axes label (info would be redundant to the suptitle).
    add_corr_surface_peak_to_axes(
        corr_surf_peak=corr_surf_peak,
        ax=ax,
        include_y_axes_labels=True,
        include_axes_title=False,
    )

    # Append figure to the output PDF
    report_pdf.savefig(fig)

    # Close the plot
    plt.close(fig)


def process_cross_variance_and_surface_peak(
    product: nisarqa.OffsetProduct,
    params_cross_offset: nisarqa.CrossOffsetVarianceLayerParamGroup,
    params_surface_peak: nisarqa.ThresholdParamGroup,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
) -> None:
    """
    Process cross offset variance and correlation surface peak layers.

    This function takes each pair of cross offset variance and
    correlation surface peak layers, and:
        * Plots them side-by-side and appends this plot to PDF
        * Computes statistics for these layers

    This function is for use with nisarqa.OffsetProduct products (ROFF, GOFF).
    It it not compatible with nisarqa.IgramOffsetsGroup products (RIFG,
    RUNW, GUNW).

    Parameters
    ----------
    product : nisarqa.OffsetProduct
        Input NISAR product.
    params_cross_offset : nisarqa.CrossOffsetVarianceLayerParamGroup
        A structure containing processing parameters to generate the
        cross offset variance layer plots.
    params_surface_peak : nisarqa.ThresholdParamGroup
        A structure containing processing parameters to generate the
        correlation surface peak layer plots.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output pdf file to append the plot to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq):
            for layer_num in product.available_layer_numbers:
                with (
                    product.get_cross_offset_variance(
                        freq=freq, pol=pol, layer_num=layer_num
                    ) as cross_off_var,
                    product.get_correlation_surface_peak(
                        freq=freq, pol=pol, layer_num=layer_num
                    ) as surface_peak,
                ):
                    # Compute Statistics first, in case of malformed layers
                    nisarqa.compute_and_save_basic_statistics(
                        raster=cross_off_var,
                        params=params_cross_offset,
                        stats_h5=stats_h5,
                    )
                    nisarqa.compute_and_save_basic_statistics(
                        raster=surface_peak,
                        params=params_surface_peak,
                        stats_h5=stats_h5,
                    )

                    plot_cross_offset_variances_and_corr_surface_peak_to_pdf(
                        cross_offset_variance=cross_off_var,
                        corr_surf_peak=surface_peak,
                        report_pdf=report_pdf,
                        offset_cbar_min_max=params_cross_offset.cbar_min_max,
                        percentile_for_clipping=params_cross_offset.percentile_for_clipping,
                    )

                    # Plot Histograms
                    process_two_histograms(
                        raster1=cross_off_var,
                        raster2=surface_peak,
                        report_pdf=report_pdf,
                        stats_h5=stats_h5,
                        name_of_histogram_pair="Cross Offset Covariance and Correlation Surface Peak",
                        r1_xlabel="Covariance",
                        r2_xlabel="Normalized Correlation Peak",
                        r1_clip_percentile=params_cross_offset.percentile_for_clipping,
                        sharey=False,
                    )


@overload
def plot_cross_offset_variances_and_corr_surface_peak_to_pdf(
    cross_offset_variance: nisarqa.RadarRaster,
    corr_surf_peak: nisarqa.RadarRaster,
    report_pdf: PdfPages,
    offset_cbar_min_max: Optional[Sequence[float]] = None,
    percentile_for_clipping: Sequence[float] = (1.0, 99.0),
) -> None: ...


@overload
def plot_cross_offset_variances_and_corr_surface_peak_to_pdf(
    cross_offset_variance: nisarqa.GeoRaster,
    corr_surf_peak: nisarqa.GeoRaster,
    report_pdf: PdfPages,
    offset_cbar_min_max: Optional[Sequence[float]] = None,
    percentile_for_clipping: Sequence[float] = (1.0, 99.0),
) -> None: ...


def plot_cross_offset_variances_and_corr_surface_peak_to_pdf(
    cross_offset_variance,
    corr_surf_peak,
    report_pdf,
    offset_cbar_min_max=None,
    percentile_for_clipping=(1.0, 99.0),
):
    """
    Plot cross offset variance and correlation surface peak layers to PDF.

    Note: The cross offset variance raster layer actually contains "covariance"
    values. So, that plot will be marked as having covariance values.

    Parameters
    ----------
    cross_offset_variance : nisarqa.RadarRaster or nisarqa.GeoRaster
        Cross offset layer to be processed. Should correspond to
        `corr_surf_peak`.
    corr_surf_peak : nisarqa.RadarRaster or nisarqa.GeoRaster
        Correlation Surface Peak layer to be processed. Should correspond to
        `cross_offset_variance`.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the offsets plots to.
    offset_cbar_min_max : pair of float or None, optional
        The range for the colorbar for the cross offset variance raster.
        If None, then the colorbar range will be computed based
        on `percentile_for_clipping`.
        Defaults to None.
    percentile_for_clipping : pair of float, optional
        Percentile range that the cross offset variance raster
        will be clipped to, which determines the colormap interval.
        Must be in range [0.0, 100.0].
        Superseded by `offset_cbar_min_max` parameter.
        Defaults to (1.0, 99.0).
    """
    # Validate that the pertinent metadata in the rasters is equal.
    nisarqa.compare_raster_metadata(
        cross_offset_variance, corr_surf_peak, almost_identical=False
    )

    # Setup the side-by-side PDF page
    fig, (ax1, ax2) = plt.subplots(
        ncols=2,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_TWO_PLOTS_PER_PAGE,
        sharey=True,
    )

    cross_offset_units = cross_offset_variance.units

    # Construct title for the overall PDF page. (`*raster.name` has a format
    # like "RUNW_L_A_pixelOffsets_HH_slantRangeOffset". We need to
    # remove the final layer name of e.g. "_slantRangeOffset".)
    name = "_".join(cross_offset_variance.name.split("_")[:-1])
    title = (
        f"Cross Offset Covariance ({cross_offset_units}) and Correlation"
        f" Surface Peak (unitless)\n{name}"
    )
    fig.suptitle(title)

    # Prepare and plot the cross offset layer on the left sub-plot
    cross_off = nisarqa.decimate_raster_array_to_square_pixels(
        cross_offset_variance
    )

    # Replace non-finite and/or masked-out pixels (i.e. pixels set to the fill
    # value) with NaNs. Make sure to do this before any clipping occurs;
    # otherwise, 'fill' pixels might influence the clipping values.
    cross_fill = cross_offset_variance.fill_value
    cross_off[~np.isfinite(cross_off) | (cross_off == cross_fill)] = np.nan

    if offset_cbar_min_max is None:
        cross_off = nisarqa.rslc.clip_array(
            arr=cross_off, percentile_range=percentile_for_clipping
        )

    if offset_cbar_min_max is None:
        offset_cbar_min = np.nanmin(cross_off)
        offset_cbar_max = np.nanmax(cross_off)
    else:
        offset_cbar_min, offset_cbar_max = offset_cbar_min_max

    # Decimate to fit nicely on the figure.
    cross_off = downsample_img_to_size_of_axes(
        ax=ax1, arr=cross_off, mode="decimate"
    )

    # Add the cross offsets variance plot (left plot)
    im1 = ax1.imshow(
        cross_off,
        aspect="equal",
        cmap="magma_r",
        interpolation="none",
        vmin=offset_cbar_min,
        vmax=offset_cbar_max,
    )

    cross_var_title = f"{cross_offset_variance.name.split('_')[-1]}"
    if offset_cbar_min_max is None:
        cross_var_title += (
            f"\nclipped to percentile range {percentile_for_clipping}"
        )

    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax1,
        xlim=cross_offset_variance.x_axis_limits,
        ylim=cross_offset_variance.y_axis_limits,
        img_arr_shape=np.shape(cross_off),
        xlabel=cross_offset_variance.x_axis_label,
        ylabel=cross_offset_variance.y_axis_label,
        title=cross_var_title,
    )

    # Add a colorbar to the cross offsets variance plot
    cax1 = fig.colorbar(im1, ax=ax1)
    cax1.ax.set_ylabel(
        ylabel=f"Covariance ({cross_offset_units})",
        rotation=270,
        labelpad=10.0,
    )

    # Construct the correlation surface peak plot on `ax2` with axes title.
    # No y-axis label nor ticks. This is the right side plot; y-axis is shared.
    add_corr_surface_peak_to_axes(
        corr_surf_peak=corr_surf_peak,
        ax=ax2,
        include_y_axes_labels=False,
        include_axes_title=True,
    )

    # Append figure to the output PDF
    report_pdf.savefig(fig)

    # Close the plot
    plt.close(fig)


def process_connected_components(
    product: nisarqa.UnwrappedGroup,
    params: nisarqa.ConnectedComponentsParamGroup,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
) -> None:
    """
    Process connected components layer: metrics to STATS h5, plots to PDF.

    Parameters
    ----------
    product : nisarqa.UnwrappedGroup
        Input NISAR product.
    params : nisarqa.ConnectedComponentsParamGroup
        A structure containing processing parameters to generate the
        connected components layer plots and metrics.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the unwrapped phase image plots to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq=freq):
            with product.get_connected_components(freq=freq, pol=pol) as cc:
                # Compute % NaN, % Inf, % Fill, % near-zero, % invalid,
                # metrics first in case of malformed layers (which could cause
                # plotting to fail).
                nisarqa.compute_percentage_metrics(
                    raster=cc,
                    stats_h5=stats_h5,
                    params=params,
                )

                plot_connected_components_layer(
                    cc_raster=cc, report_pdf=report_pdf
                )

                # Compute the Connected Components metrics last. None of these
                # metrics should trigger the plotting to fail, so let's try to
                # finish the plots beforehand.
                nisarqa.connected_components_metrics(
                    cc_raster=cc,
                    stats_h5=stats_h5,
                    max_num_cc=params.max_num_cc,
                )


def plot_connected_components_layer(
    cc_raster: nisarqa.RadarRaster | nisarqa.GeoRaster,
    report_pdf: PdfPages,
) -> None:
    """
    Plot a connected components layer and a bar chart of percentages on PDF.

    Parameters
    ----------
    cc_raster : nisarqa.RadarRaster or nisarqa.GeoRaster
        *Raster of connected components data.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        Output PDF file to append the generated plots to.
    """

    # Setup PDF page
    fig, (ax1, ax2) = plt.subplots(
        ncols=2,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_TWO_PLOTS_PER_PAGE,
    )

    # Construct title for the overall PDF page.
    title = f"Connected Components Mask\n{cc_raster.name}"
    fig.suptitle(title)

    # Step 1: Compute metrics on full raster (We should not skip any CC!):
    cc_full = cc_raster.data[()]

    labels, percentages = nisarqa.get_unique_elements_and_percentages(cc_full)
    num_features = len(labels)

    # Step 2: Setup colormap and boundaries between integer values.
    # Note: `labels` is guaranteed to be sorted and unique values, but
    # depending on how the CC layer was created, there might be skipped values
    # in the labels, e.g. the CC layer only contains labels [0, 1, 3, 4].

    # Create a color map with distinct color for each connected component
    # If there are more than 10 connected components, simply repeat the colors.
    # (Per the product lead, it will likely be an edge case if more than
    # 10 connected components.)
    # Kludge: We need to ensure that the "fill value" color is white.
    # colors.ListedColormap is able to do the repeating automatically using
    # the `N` parameter, however, I don't know a clever way to then make
    # only fill value white. For now, simply constuct the full list manually.
    quot, rem = divmod(num_features, len(nisarqa.SEABORN_COLORBLIND))
    colors_list = nisarqa.SEABORN_COLORBLIND * quot
    colors_list += nisarqa.SEABORN_COLORBLIND[:rem]

    # If the raster contains any fill value pixels, set them to white
    # so they look "transparent" in the PDF
    fill_idx = np.where(labels == cc_raster.fill_value)[0]
    if fill_idx.size > 0:
        colors_list[fill_idx[0]] = (1.0, 1.0, 1.0, 0.0)  # transparent white

    # To create the colorbar for the CC image raster, we'll use a
    # a ListedColormap for the discrete colors, and use a BoundaryNorm for
    # to create a colormap based on discrete intervals. (BoundaryNorm maps
    # values to integers, instead of to e.g. the interval [0, 1].)
    # Reference:
    # https://www.geeksforgeeks.org/matplotlib-colors-listedcolormap-class-in-python/

    cmap = colors.ListedColormap(colors=colors_list)

    # Create a list of the boundaries (aka the halfway points) between
    # each integer label; also include the very max and min values
    # of the interval for the colorbar.
    # Hint: Visually, the "boundary" between two integer labels is where the
    # colorbar changes from one color to the next color.

    # Kludge: the `labels` returned above use the same dtype as `cc_full`.
    # As of March 2024, the product spec for the CC layer specifies a
    # dtype of unsigned int16 with a fill value of 65535. For the CC layer,
    # `0` designates pixels with invalid unwrapping, so `labels` will
    # typically be [0, ..., 65535].
    # Because 0 and 65535 are the min and max values for uint16, when
    # we try to subtract 1 and add 1 to those values below when creating the
    # `boundaries` variable, we'll run into overflow errors.
    # Prior to NumPy 2.0 (e.g. NumPy 1.26), the datatype would automatically
    # be promoted to avoid overflow. Starting with NumPy 2.0, datatypes were
    # no longer promoted. So, manually promote the datatype to avoid overflow.
    # Sources:
    #     [1] https://numpy.org/doc/stable/numpy_2_0_migration_guide.html#changes-to-numpy-data-type-promotion
    #     [2] https://numpy.org/neps/nep-0050-scalar-promotion.html
    info = np.iinfo(np.int64)
    if (np.min(labels) <= info.min) or (np.max(labels) >= info.max):
        # The label values fall outside the permissible interval of NumPy's
        # int64, +/- 1 to account for the algorithm below.
        # This could happen if e.g. the CC layer has dtype uint64 and the
        # fill value is set to 2 ** 63 - 1.
        # However, this should not occur in nominal products, so simply raise
        # an error for now.
        raise NotImplementedError(
            f"Connected components label value(s) fall outside of the"
            " permissible interval for QA's plotting tools. Please update QA."
        )
    else:
        labels_promoted = labels.astype(np.int64)

    # This assumes that `labels` is in sorted, ascending order.
    boundaries = np.concatenate(
        (
            [labels_promoted[0] - 1],
            labels_promoted[:-1] + np.diff(labels_promoted) / 2.0,
            [labels_promoted[-1] + 1],
        )
    )
    norm = colors.BoundaryNorm(boundaries, len(boundaries) - 1)

    # Step 3: Decimate Connected Components array to square pixels and plot
    # Note: We do not need to decimate again to a smaller size to fit nicely
    # on the axes in order to reduce PDF file size. PdfPages defaults to
    # using Flate compression, a lossless compression method that works well
    # on images with large areas of single colors or repeating patterns.
    cc_decimated = nisarqa.decimate_raster_array_to_square_pixels(cc_raster)

    # Plot connected components mask
    im1 = ax1.imshow(cc_decimated, cmap=cmap, norm=norm, interpolation="none")

    cax1 = fig.colorbar(im1, cmap=cmap, norm=norm)

    # The CC image plot visualizes discrete data; the colorbar ticks are
    # for the integer CC labels.
    # Set colorbar ticks to appear at the midpoint between each `boundaries`
    # transition:
    cax1.set_ticks(boundaries[:-1] + np.diff(boundaries) / 2.0)
    # Labels the tick marks with the `labels`
    cax1.ax.set_yticklabels(labels)
    # Hide the ticks at the boundaries
    cax1.ax.minorticks_off()

    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax1,
        xlim=cc_raster.x_axis_limits,
        ylim=cc_raster.y_axis_limits,
        img_arr_shape=np.shape(cc_decimated),
        xlabel=cc_raster.x_axis_label,
        ylabel=cc_raster.y_axis_label,
        title=f"{(cc_raster.name.split('_')[-1])} Layer",
    )

    # Step 4: Create a bar chart of the connected components on ax2
    ax2.set_title("Percentage of Pixels per Connected Component", fontsize=10)

    x_locations_of_bars = range(len(percentages))

    ax2.bar(
        x_locations_of_bars,
        percentages,
        color=cmap.colors,
        edgecolor="black",
        linewidth=0.5,
    )
    ax2.set_ylabel("Percentage of Pixels")
    ax2.xaxis.set_ticks(x_locations_of_bars)
    xlabel = (
        "Connected Component Label\n(0 denotes pixels with invalid unwrapping"
    )
    if cc_raster.fill_value in labels:
        xlabel += f",\n{cc_raster.fill_value} is fill value from geocoding)"
    else:
        xlabel += ")"
    ax2.set_xlabel(xlabel)

    rotation = 45 if len(labels) > 10 else 0
    ax2.xaxis.set_ticklabels(labels, rotation=rotation)

    if num_features < 25:
        # Note the percentage at the top of each bar. (Cap this at 25. If there
        # are too many bars, it will be too cluttered to read the percentages.)
        font_size = 8 if num_features < 12 else 6

        for i, val in enumerate(percentages):
            ax2.text(
                x_locations_of_bars[i],  # location on x-axis
                val,  # location on y-axis
                f"{val:.1f}",
                fontsize=font_size,
                horizontalalignment="center",
                verticalalignment="bottom",
            )

    # Append figure to the output PDF
    report_pdf.savefig(fig)

    # Close the plot
    plt.close(fig)


def process_unw_coh_mag(
    product: nisarqa.UnwrappedGroup,
    params: nisarqa.ThresholdParamGroup,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
) -> None:
    """
    Process unwrapped coherence magnitude layer: metrics to STATS h5, plots to PDF.

    Parameters
    ----------
    product : nisarqa.UnwrappedGroup
        Input NISAR product.
    params : nisarqa.ThresholdParamGroup
        A structure containing processing parameters to generate the
        coherence magnitude layer plots.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the coherence magnitude image plot to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq=freq):
            with product.get_unwrapped_coh_mag(freq=freq, pol=pol) as coh_mag:
                # Compute Statistics first, in case of malformed layers
                # (which could cause plotting to fail)
                nisarqa.compute_and_save_basic_statistics(
                    raster=coh_mag,
                    params=params,
                    stats_h5=stats_h5,
                )

                plot_unwrapped_coh_mag_to_pdf(
                    coh_raster=coh_mag, report_pdf=report_pdf
                )

                # Plot Histogram
                process_single_histogram(
                    raster=coh_mag,
                    xlabel="Coherence Magnitude",
                    name_of_histogram="Coherence Magnitude (Unwrapped Group)",
                    report_pdf=report_pdf,
                    stats_h5=stats_h5,
                )


def plot_unwrapped_coh_mag_to_pdf(
    coh_raster: nisarqa.RadarRaster | nisarqa.GeoRaster,
    report_pdf: PdfPages,
) -> None:
    """
    Plot unwrapped coherence magnitude layer to PDF.

    Parameters
    ----------
    coh_raster : nisarqa.GeoRaster or nisarqa.RadarRaster
        *Raster for the unwrapped coherence magnitude raster.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        Output PDF file to append the plot to.
    """
    fig, ax = plt.subplots(
        ncols=1,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE,
    )

    # Construct title for the overall PDF page.
    title = f"Coherence Magnitude (Unwrapped Group)\n{coh_raster.name}"
    fig.suptitle(title)

    coh_img = nisarqa.decimate_raster_array_to_square_pixels(coh_raster)

    # Decimate to fit nicely on the figure.
    coh_img = downsample_img_to_size_of_axes(
        ax=ax, arr=coh_img, mode="decimate"
    )

    # Add the coh mag layer
    im = ax.imshow(
        coh_img,
        aspect="equal",
        cmap="gray",
        interpolation="none",
        vmin=0.0,
        vmax=1.0,
    )

    nisarqa.rslc.format_axes_ticks_and_labels(
        ax=ax,
        xlim=coh_raster.x_axis_limits,
        ylim=coh_raster.y_axis_limits,
        img_arr_shape=np.shape(coh_img),
        xlabel=coh_raster.x_axis_label,
        ylabel=coh_raster.y_axis_label,
    )

    # Add a colorbar to the figure
    cax = fig.colorbar(im)
    cax.ax.set_ylabel(ylabel="Coherence Magnitude", rotation=270, labelpad=10.0)

    # Append figure to the output PDF
    report_pdf.savefig(fig)

    plt.close(fig)


def generate_histogram_to_axes_and_h5(
    raster: nisarqa.RadarRaster | nisarqa.GeoRaster,
    ax: mpl.axes.Axes,
    stats_h5: h5py.File,
    *,
    xlabel=str,
    include_axes_title: bool = True,
    percentile_for_clipping: tuple[float, float] | None = None,
    data_prep_func: Callable | None = None,
) -> None:
    """
    Compute histogram and save to PDF and STATS HDF5 file.

    Parameters
    ----------
    raster : nisarqa.RadarRaster or nisarqa.GeoRaster
        *Raster to generate the histogram for. Non-finite values are ignored.
    ax : matplotlib.axes.Axes
        Axes object.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    xlabel : str
        Label to use for the x-axis histogram bins, not including units.
            Correct: "InSAR Phase"
            Wrong: "InSAR Phase (radians)"
        The units for this label will be set per `raster.units`.
    include_axes_title : bool, optional
        True to include a title on the axes itself; False to exclude it.
        Defaults to True.
    percentile_for_clipping : None or pair of float, optional
        Percentile range that the finite raster values will be clipped to prior
        to creating the histogram. If None, no clipping will occur.
        Must be in range [0.0, 100.0] or None. Defaults to None.
    data_prep_func : Callable or None, optional
        Function to transform the raster data before applying
        `percentile_for_clipping` and before computing
        the histogram counts. For example, this function could be
        `numpy.angle` to convert complex values into float values,
        or it could be `numpy.sqrt` for converting variances
        into standard deviation.
        If `None`, then histogram will be computed on the raster as-is,
        and no pre-processing of the data will occur.
        Defaults to None.
    """
    # Get histogram probability density
    arr = np.asanyarray(raster.data)
    arr = arr[np.isfinite(arr)]
    if data_prep_func is not None:
        arr = data_prep_func(arr)

    if percentile_for_clipping is not None:
        arr = nisarqa.rslc.clip_array(
            arr=arr, percentile_range=percentile_for_clipping
        )

    # Fix the number of bins to keep the output file size small
    # NOTE: InSAR phase histograms were observed to have a spike at 0 radians,
    # likely due to imperfect overlap between the reference and secondary
    # SLC footprints.
    # This histogram feature may be masked if the number of bins is too low.
    density, bin_edges = np.histogram(arr, bins=200, density=True)

    # Append to Axes
    if include_axes_title:
        # Get the layer name. (`*raster.name` has a format
        # like "RUNW_L_A_pixelOffsets_HH_slantRangeOffset". We need to
        # get the last component, e.g. "slantRangeOffset".)
        ax_title = raster.name.split("_")[-1]
    else:
        ax_title = None

    add_histogram_to_axes(
        ax=ax,
        density=density,
        bin_edges=bin_edges,
        xlabel=xlabel,
        units=raster.units,
        axes_title=ax_title,
        percentile_for_clipping=percentile_for_clipping,
    )

    # Save to stats HDF5
    add_histogram_data_to_h5(
        stats_h5=stats_h5,
        stats_h5_group_path=raster.stats_h5_group_path,
        density=density,
        bin_edges=bin_edges,
        units=raster.units,
    )


def add_histogram_to_axes(
    density: np.ndarray,
    bin_edges: np.ndarray,
    ax: mpl.axes.Axes,
    *,
    xlabel: str,
    units: str,
    axes_title: str | None = None,
    percentile_for_clipping: tuple[float, float] | None = None,
) -> None:
    """
    Plot a histogram on a Matplotlib Axes.

    Parameters
    ----------
    density: np.ndarray
        The normalized density values for the histogram.
    bin_edges: np.ndarray
        The bin edges for the histogram.
    ax : matplotlib.axes.Axes
        Axes object to plot the histogram on.
    xlabel : str
        Label to use for the x-axis histogram bins, not including units.
            Correct: "InSAR Phase"
            Wrong: "InSAR Phase (radians)"
        The units for this label will be set per `units`.
    units : str
        Units which will be used for labeling axes.
        The x-axis bins will be labeled with units of "`units`", and
        the y-axis densities will be labeled with units of "1/`units`".
    axes_title : str or None, optional
        Title for the Axes. If None, no title will be added. Defaults to None.
    percentile_for_clipping : None or pair of float, optional
        Percentile range that the finite raster values will be clipped to prior
        to creating the histogram. If None, no clipping will occur.
        Must be in range [0.0, 100.0] or None. Defaults to None.
    """
    # Use custom cycler for accessibility
    ax.set_prop_cycle(nisarqa.CUSTOM_CYCLER)

    # Add backscatter histogram density to the figure
    nisarqa.rslc.add_hist_to_axis(
        ax,
        counts=density,
        edges=bin_edges,
        label=None,
    )

    # Construct the axes title
    final_axes_title = None
    if axes_title is not None:
        final_axes_title = axes_title
    if percentile_for_clipping is not None:
        txt = (
            f"clipped to percentile range"
            f" [{percentile_for_clipping[0]}, {percentile_for_clipping[1]}]"
        )
        if axes_title is None:
            final_axes_title = txt
        else:
            final_axes_title += f"\n{txt}"
    ax.set_title(final_axes_title, fontsize=10)

    if units == "1":
        units = "unitless"
    ax.set_xlabel(f"{xlabel} ({units})")
    ax.set_ylabel(f"Density (1/{units})")

    # TODO: For RSLC/GSLC/GCOV, the top limit floats. Do the same for InSAR?
    # Let the top limit float
    ax.set_ylim(bottom=0.0)
    ax.grid(visible=True)


def add_histogram_data_to_h5(
    density: np.ndarray,
    bin_edges: np.ndarray,
    stats_h5: h5py.File,
    *,
    units: str,
    stats_h5_group_path: str,
) -> None:
    """
    Add histogram data to the STATS HDF5 file.

    Parameters
    ----------
    density : numpy.ndarray
        The normalized density values for the histogram.
    bin_edges : numpy.ndarray
        The bin edges for the histogram.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    units : str
        Units which will be used for labeling axes.
        The bin edges will be denoted with units of "`units`", and
        the densities will be denoted with units of "1/`units`".
    stats_h5_group_path : str
        Path in the STATS.h5 file for the group where all metrics and
        statistics re: this raster should be saved.
        If calling function has a *Raster, suggest using the *Raster's
        `stats_h5_group_path` attribute.
        Examples:
            RSLC/GSLC/GCOV: "/science/LSAR/QA/data/frequencyA/HH"
            RUNW/GUNW: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset"
            ROFF/GOFF: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"
    """
    # Save density values to stats.h5 file
    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=stats_h5_group_path,
        ds_name="histogramDensity",
        ds_data=density,
        ds_units=f"1/{units}",
        ds_description="Normalized density of the histogram",
    )

    # Save bins to stats.h5 file
    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=stats_h5_group_path,
        ds_name="histogramBins",
        ds_data=bin_edges,
        ds_units=units,
        ds_description="Histogram bin edges",
    )


def process_single_histogram(
    raster: nisarqa.GeoRaster | nisarqa.RadarRaster,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
    *,
    xlabel: str,
    name_of_histogram: str,
    percentile_for_clipping: tuple[float, float] | None = None,
) -> None:
    """
    Make histogram of a *Raster; plot to single PDF page and add metrics to HDF5.

    Parameters
    ----------
    raster : nisarqa.GeoRaster | nisarqa.RadarRaster
        *Raster to generate the histogram for.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the histogram to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    xlabel : str
        Label to use for the x-axis histogram bins, not including units.
            Correct: "InSAR Phase"
            Wrong: "InSAR Phase (radians)"
        The units for this label will be set per `raster.units`.
    name_of_histogram : str
        What is this histogram of? This string will be used in the main title
        of the PDF page, like this: "Histogram of <name_of_histogram>".
    percentile_for_clipping : None or pair of float, optional
        Percentile range that the finite raster values will be clipped to prior
        to creating the histogram. If None, no clipping will occur.
        Must be in range [0.0, 100.0] or None. Defaults to None.

    Warnings
    --------
    The entire input array will be read into memory and processed.
    Only use this function for small datasets.
    """
    fig, ax = plt.subplots(
        ncols=1,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE,
    )

    # Form the plot title
    title = f"Histogram of {name_of_histogram}\n{raster.name}"
    fig.suptitle(title)

    generate_histogram_to_axes_and_h5(
        raster=raster,
        ax=ax,
        stats_h5=stats_h5,
        xlabel=xlabel,
        include_axes_title=False,
        percentile_for_clipping=percentile_for_clipping,
    )

    # Save complete plots to graphical summary PDF file
    report_pdf.savefig(fig)

    # Close figure
    plt.close(fig)


def process_two_histograms(
    raster1: nisarqa.GeoRaster | nisarqa.RadarRaster,
    raster2: nisarqa.GeoRaster | nisarqa.RadarRaster,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
    *,
    name_of_histogram_pair: str,
    r1_xlabel: str,
    r2_xlabel: str,
    r1_clip_percentile: tuple[float, float] | None = None,
    r2_clip_percentile: tuple[float, float] | None = None,
    sharey: bool = False,
    r1_data_prep_func: Callable | None = None,
    r2_data_prep_func: Callable | None = None,
) -> None:
    """
    Make histograms of two *Rasters; plot to PDF page and add metrics to HDF5.

    The histograms of the two rasters will be plotted side-by-side on a
    single PDF page.

    Parameters
    ----------
    raster1, raster2 : nisarqa.GeoRaster | nisarqa.RadarRaster
        *Rasters to generate the histograms for. Non-finite values are ignored.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the histogram plots to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    name_of_histogram_pair : str
        What are these histograms of? This string will be used in the main title
        of the PDF page, like this: "Histograms of <name_of_histogram_pair>".
    r1_xlabel, r2_xlabel : str
        Label to use for the x-axis histogram bins for `raster1` and `raster2`
        (respectively), not including units.
            Correct: "InSAR Phase"
            Wrong: "InSAR Phase (radians)"
        The units for this label will be set per `raster.units`.
    r1_clip_percentile, r2_clip_percentile : None or pair of float, optional
        Percentile range that the finite raster values will be clipped to prior
        to creating the histogram for `raster1` and `raster2`, respectively.
        If None, no clipping will occur. Must be in range [0.0, 100.0] or None.
        Defaults to None.
    sharey : bool, optional
        True to have the plots share a y-axes; False otherwise.
    r1_data_prep_func, r2_data_prep_func : Callable or None, optional
        Function to transform the raster1 and raster2 (respectively) data
        before clipping outliers and before computing
        the histogram counts. For example, this function could be
        `numpy.angle` to convert complex values into float values,
        or it could be `numpy.sqrt` for converting variances
        into standard deviation.
        If `None`, then histogram will be computed on the rasters as-is,
        and no pre-processing of the data will occur.
        Defaults to None.

    Warnings
    --------
    The entire input arrays will be read into memory and processed.
    Only use this function for small datasets.
    """
    fig, (ax1, ax2) = plt.subplots(
        ncols=2,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_TWO_PLOTS_PER_PAGE,
        sharey=sharey,
    )

    # Construct title for the overall PDF page. (`*raster.name` has a format
    # like "RUNW_L_A_pixelOffsets_HH_slantRangeOffset". We need to
    # remove the final layer name of e.g. "_slantRangeOffset".)
    name = "_".join(raster1.name.split("_")[:-1])
    title = f"Histograms of {name_of_histogram_pair}\n{name}"
    fig.suptitle(title)

    generate_histogram_to_axes_and_h5(
        raster=raster1,
        ax=ax1,
        stats_h5=stats_h5,
        xlabel=r1_xlabel,
        include_axes_title=True,
        percentile_for_clipping=r1_clip_percentile,
        data_prep_func=r1_data_prep_func,
    )

    generate_histogram_to_axes_and_h5(
        raster=raster2,
        ax=ax2,
        stats_h5=stats_h5,
        xlabel=r2_xlabel,
        include_axes_title=True,
        percentile_for_clipping=r2_clip_percentile,
        data_prep_func=r2_data_prep_func,
    )

    if sharey:
        ax2.set_ylabel("")

    # Save complete plots to graphical summary PDF file
    report_pdf.savefig(fig)

    # Close figure
    plt.close(fig)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
