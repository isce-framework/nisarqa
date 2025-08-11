from __future__ import annotations

import functools
import os
from typing import overload

import matplotlib as mpl
import matplotlib.colors as colors
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from ..plotting_utils import (
    downsample_img_to_size_of_axes,
    format_axes_ticks_and_labels,
    save_mpl_plot_to_png,
)

objects_to_skip = nisarqa.get_all(name=__name__)


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

    format_axes_ticks_and_labels(
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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
