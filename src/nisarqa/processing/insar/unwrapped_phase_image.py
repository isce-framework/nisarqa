from __future__ import annotations

import os
from typing import Optional

import h5py
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from ..plotting_utils import (
    downsample_img_to_size_of_axes,
    format_axes_ticks_and_labels,
    format_cbar_ticks_for_multiples_of_pi,
    plot_2d_array_and_save_to_png,
)
from ..processing_utils import get_phase_array
from .histograms import process_single_histogram

objects_to_skip = nisarqa.get_all(name=__name__)


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

    format_axes_ticks_and_labels(
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
        format_axes_ticks_and_labels(
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
        sample_spacing=(igram_r.y_ground_spacing, igram_r.x_ground_spacing),
        longest_side_max=params.longest_side_max,
        png_filepath=png_filepath,
        vmin=cbar_min_max[0],
        vmax=cbar_min_max[1],
    )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
