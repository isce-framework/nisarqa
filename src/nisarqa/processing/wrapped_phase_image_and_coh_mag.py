from __future__ import annotations

import os
from typing import Optional, overload

import h5py
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from .histograms import process_two_histograms
from .plotting_utils import (
    downsample_img_to_size_of_axes,
    format_cbar_ticks_for_multiples_of_pi,
    plot_2d_array_and_save_to_png,
)
from .processing_utils import get_phase_array

objects_to_skip = nisarqa.get_all(name=__name__)


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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
