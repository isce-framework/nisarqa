from __future__ import annotations

import os
from typing import Any, Optional

import h5py
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from ..plotting_utils import (
    downsample_img_to_size_of_axes,
    format_axes_ticks_and_labels,
    format_cbar_ticks_for_multiples_of_pi,
)
from ._utils import get_phase_array, make_phase_browse
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
                nisarqa.process_and_save_basic_statistics(
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
        The multiple of pi to rewrap the unwrapped phase image and include
        as an additional plot in the PDF. If None, no rewrapped phase image
        will be plotted.
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


def make_unwrapped_phase_browse(
    product: nisarqa.UnwrappedGroup,
    *,
    freq: str,
    pol: str,
    params: Any,  # will be type-narrowed in the function
    browse_paths: nisarqa.BrowseOutputPaths,
    dem_file: str | os.PathLike | None = None,
) -> None:
    """
    Create and save the unwrapped interferogram browse products as PNG+KML.

    Parameters
    ----------
    product : nisarqa.UnwrappedGroup
        Input NISAR product.
    freq, pol : str
        The frequency and polarization (respectively) pair for the unwrapped
        interferogram to save as a PNG.
    params : nisarqa.UNWIgramBrowseParamGroup
            and nisarqa.L1RadarBrowseLatLonParamGroup or nisarqa.L2GeoBrowseLatLonParamGroup
        A structure containing the processing parameters for the browse PNG.
        Must be an instance of UNWIgramBrowseParamGroup
        and (via multiple inheritance) also an instance of either:
            L1RadarBrowseLatLonParamGroup or L2GeoBrowseLatLonParamGroup
    browse_paths : nisarqa.BrowseOutputPaths
        Container with output directory and browse/KML filenames.
    dem_file : path-like or None, optional
        Digital Elevation Model (DEM) file path in a GDAL-compatible raster
        format. Will be ignored if `params.output_browse_latlon`
        is False or if `product` is a Level-2 Geocoded product.
        Used for Level-1 products when geocoding the EPSG  (lat/lon) browse;
        if None, a zero-height DEM will be used.
        Defaults to None.
    """

    # XXX - Python's type annotations do not currently have a good syntax
    # for multiple inheritance in combination with a Union.
    # Instead, use type narrowing to assist type checkers:
    if not isinstance(params, nisarqa.UNWIgramBrowseParamGroup):
        raise TypeError(f"{type(params)=}, must be UNWIgramBrowseParamGroup")
    t = (
        nisarqa.L1RadarBrowseLatLonParamGroup
        | nisarqa.L2GeoBrowseLatLonParamGroup
    )
    if not isinstance(params, t):
        msg = f"{type(params)=}, must be L1RadarBrowseLatLonParamGroup or L2GeoBrowseLatLonParamGroup"
        raise TypeError(msg)

    with product.get_unwrapped_phase(freq=freq, pol=pol) as igram_r:
        make_phase_browse(
            raster=igram_r,
            rewrap=params.rewrap,
            longest_side_max=params.longest_side_max,
            resample=params.resample,
            browse_paths=browse_paths,
            save_latlon_browse=params.output_browse_latlon,
            # Parameters for Level-1; will be ignored for Level-2
            orbit=product.get_orbit(ref_or_sec="reference"),
            wavelength=product.wavelength(freq=freq),
            look_side=product.look_direction,
            dem_file=dem_file,
        )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
