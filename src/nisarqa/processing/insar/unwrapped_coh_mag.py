from __future__ import annotations

import h5py
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from ..plotting_utils import (
    downsample_img_to_size_of_axes,
    format_axes_ticks_and_labels,
)
from .histograms import process_single_histogram

objects_to_skip = nisarqa.get_all(name=__name__)


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

    format_axes_ticks_and_labels(
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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
