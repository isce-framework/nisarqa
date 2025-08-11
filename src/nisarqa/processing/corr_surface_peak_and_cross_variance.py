from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, overload

import h5py
import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from .histograms import process_single_histogram, process_two_histograms
from .plotting_utils import downsample_img_to_size_of_axes

objects_to_skip = nisarqa.get_all(name=__name__)


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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
