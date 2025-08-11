from __future__ import annotations

from typing import overload

import h5py
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from .histograms import process_two_histograms
from .plotting_utils import (
    downsample_img_to_size_of_axes,
    format_axes_ticks_and_labels,
    format_cbar_ticks_for_multiples_of_pi,
)
from .processing_utils import get_phase_array

objects_to_skip = nisarqa.get_all(name=__name__)


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

    format_axes_ticks_and_labels(
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
    format_axes_ticks_and_labels(
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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
