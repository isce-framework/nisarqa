from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, overload

import h5py
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from .histograms import process_two_histograms
from .plotting_utils import (
    downsample_img_to_size_of_axes,
    format_axes_ticks_and_labels,
)

objects_to_skip = nisarqa.get_all(name=__name__)


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

    format_axes_ticks_and_labels(
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
    format_axes_ticks_and_labels(
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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
