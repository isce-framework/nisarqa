from __future__ import annotations

import os
from typing import overload

import h5py
import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from ..plotting_utils import (
    downsample_img_to_size_of_axes,
    format_axes_ticks_and_labels,
)
from .histograms import process_two_histograms
from .quiver_plots import (
    plot_offsets_quiver_plot_to_pdf,
    plot_single_quiver_plot_to_png,
)

objects_to_skip = nisarqa.get_all(name=__name__)


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

        proj_params = {}
        if isinstance(az_off, nisarqa.GeoRaster):
            # Construct the `proj_params` object. This will trigger
            # downstream functions to modify the quiver arrows for the
            # input product's projected coordinates.
            proj_params["quiver_projection_params"] = (
                nisarqa.ParamsForAzRgOffsetsToProjected(
                    orbit=product.get_orbit(ref_or_sec="reference"),
                    wavelength=product.wavelength(freq=freq),
                    look_side=product.look_direction,
                )
            )

        y_dec, x_dec = plot_single_quiver_plot_to_png(
            az_offset=az_off,
            rg_offset=rg_off,
            params=params_quiver,
            png_filepath=browse_png,
            **proj_params,
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
                        **proj_params,
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
    title = "Along Track Offsets and Slant Range Offsets (meters)"
    if isinstance(az_offset, nisarqa.GeoRaster):
        title = "Geocoded " + title
    fig.suptitle(title)

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
    format_axes_ticks_and_labels(
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
    format_axes_ticks_and_labels(
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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
