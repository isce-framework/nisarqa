from __future__ import annotations

import os
from collections.abc import Callable
from fractions import Fraction
from typing import Optional

import matplotlib as mpl
import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
