from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from fractions import Fraction
from typing import Optional

import matplotlib as mpl
import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter
from numpy.typing import ArrayLike
from PIL import Image

import nisarqa

from .processing_utils import clip_array

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
    nisarqa.compute_square_pixel_nlooks :
        Function to compute the downsampling strides for an image array;
        this function also accounts for making the pixels "square".
    nisarqa.downsample_img_to_size_of_axes_with_stride :
        Same as this function, but also returns the stride used for
        decimation or multilooking.
    """
    arr, _ = downsample_img_to_size_of_axes_with_stride(
        ax=ax, arr=arr, mode=mode
    )
    return arr


def downsample_img_to_size_of_axes_with_stride(
    ax: mpl.axes.Axes, arr: np.ndarray, mode: str = "decimate"
) -> tuple[np.ndarray, int]:
    """
    Downsample array to size of axes and also return the stride.

    This is helpful for use with `interpolation='none'`.

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
    stride : int
        The stride used for performing decimation or multilooking (per `mode`)
        in both the X and Y directions.

    See Also
    --------
    nisarqa.compute_square_pixel_nlooks : Function to compute the downsampling
        strides for an image array;
        this function also accounts for making the pixels "square".
    nisarqa.downsample_img_to_size_of_axes :
        Wrapper around this function, but does not return the stride.
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
            return arr, 1

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
            return arr, 1

        # Use floor division. See explanation above.)
        stride = int(src_arr_width / desired_longest)

    # Downsample to the correct size along the X and Y directions.
    if mode == "decimate":
        return arr[::stride, ::stride], stride
    elif mode == "multilook":
        return nisarqa.multilook(arr=arr, nlooks=(stride, stride)), stride
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


def apply_image_correction(img_arr, params):
    """
    Apply image correction in `img_arr` as specified in `params`.

    Image correction is applied in the following order:
        Step 1: Per `params.percentile_for_clipping`, clip the image array's outliers
        Step 2: Per `params.linear_units`, convert from linear units to dB
        Step 3: Per `params.gamma`, apply gamma correction

    Parameters
    ----------
    img_arr : numpy.ndarray
        2D image array to have image correction applied to.
        For example, for RSLC this is the multilooked image array.
    params : BackscatterImageParamGroup
        A structure containing the parameters for processing
        and outputting the backscatter image(s).

    Returns
    -------
    out_img : numpy.ndarray
        2D image array. If any image correction was specified via `params`
        and applied to `img_arr`, this returned array will include that
        image correction.
    vmin, vmax : float
        The min and max of the image array (excluding Nan), as computed
        after Step 2 but before Step 3. These can be used to set
        colorbar tick mark values; by computing vmin and vmax prior to
        gamma correction, the tick marks values retain physical meaning.
    """

    # Step 1: Clip the image array's outliers
    img_arr = clip_array(
        img_arr, percentile_range=params.percentile_for_clipping
    )

    # Step 2: Convert from linear units to dB
    if not params.linear_units:
        with nisarqa.ignore_runtime_warnings():
            # This line throws these warnings:
            #   "RuntimeWarning: divide by zero encountered in log10"
            # when there are zero values. Ignore those warnings.
            img_arr = nisarqa.pow2db(img_arr)

    # Get the vmin and vmax prior to applying gamma correction.
    # These can later be used for setting the colorbar's
    # tick mark values.
    vmin = np.nanmin(img_arr)
    vmax = np.nanmax(img_arr)

    # Step 3: Apply gamma correction
    if params.gamma is not None:
        img_arr = apply_gamma_correction(img_arr, gamma=params.gamma)

    return img_arr, vmin, vmax


def apply_gamma_correction(img_arr, gamma):
    """
    Apply gamma correction to the input array.

    Function will normalize the array and apply gamma correction.
    The returned output array will remain in range [0,1].

    Parameters
    ----------
    img_arr : array_like
        Input array
    gamma : float
        The gamma correction parameter.
        Gamma will be applied as follows:
            array_out = normalized_array ^ gamma
        where normalized_array is a copy of `img_arr` with values
        scaled to the range [0,1].

    Returns
    -------
    out_img : numpy.ndarray
        Copy of `img_arr` with the specified gamma correction applied.
        Due to normalization, values in `out_img` will be in range [0,1].

    Also See
    --------
    invert_gamma_correction : inverts this function
    """
    # Normalize to range [0,1]
    # Any zeros in the image array will cause an expected Runtime warning.
    # Ok to suppress.
    with nisarqa.ignore_runtime_warnings():
        # This line throws these warnings:
        #   "RuntimeWarning: divide by zero encountered in divide"
        #   "RuntimeWarning: invalid value encountered in divide"
        # when there are zero values. Ignore those warnings.
        out_img = nisarqa.normalize(img_arr)

    # Apply gamma correction
    out_img = np.power(out_img, gamma)

    return out_img


def invert_gamma_correction(img_arr, gamma, vmin, vmax):
    """
    Invert the gamma correction to the input array.

    Function will normalize the array and apply gamma correction.
    The returned output array will remain in range [0,1].

    Parameters
    ----------
    img_arr : array_like
        Input array
    gamma : float
        The gamma correction parameter.
        Gamma will be inverted as follows:
            array_out = img_arr ^ (1/gamma)
        The array will then be rescaled as follows, to "undo" normalization:
            array_out = (array_out * (vmax - vmin)) + vmin
    vmin, vmax : float
        The min and max of the source image array BEFORE gamma correction
        was applied.

    Returns
    -------
    out : numpy.ndarray
        Copy of `img_arr` with the specified gamma correction inverted
        and scaled to range [<vmin>, <vmax>]

    Also See
    --------
    apply_gamma_correction : inverts this function
    """
    # Invert the power
    out = np.power(img_arr, 1 / gamma)

    # Invert the normalization
    out = (out * (vmax - vmin)) + vmin

    return out


def plot_to_grayscale_png(img_arr, filepath):
    """
    Save the image array to a 1-channel grayscale PNG with transparency.

    Finite pixels will have their values scaled to 1-255. Non-finite pixels
    will be set to 0 and made to appear transparent in the PNG.
    The pixel value of 0 is reserved for the transparent pixels.

    Parameters
    ----------
    img_arr : array_like
        2D Image to plot
    filepath : str
        Full filepath the browse image product.

    Notes
    -----
    This function does not add a full alpha channel to the output png.
    It instead uses "cheap transparency" (palette-based transparency)
    to keep file size smaller.
    See: http://www.libpng.org/pub/png/book/chapter08.html#png.ch08.div.5.4
    """

    # Only use 2D arrays
    if len(np.shape(img_arr)) != 2:
        raise ValueError("Input image array must be 2D.")

    img_arr, transparency_val = prep_arr_for_png_with_transparency(img_arr)

    # Save as grayscale image using PIL.Image. 'L' is grayscale mode.
    # (Pyplot only saves png's as RGB, even if cmap=plt.cm.gray)
    im = Image.fromarray(img_arr, mode="L")
    im.save(filepath, transparency=transparency_val)  # default = 72 dpi


def plot_to_rgb_png(red, green, blue, filepath):
    """
    Combine and save RGB channel arrays to a browse PNG with transparency.

    Finite pixels will have their values scaled to 1-255. Non-finite pixels
    will be set to 0 and made to appear transparent in the PNG.
    The pixel value of 0 is reserved for the transparent pixels.

    Parameters
    ----------
    red, green, blue : numpy.ndarray
        2D arrays that will be mapped to the red, green, and blue
        channels (respectively) for the PNG. These three arrays must have
        identical shape.
    filepath : str
        Full filepath for where to save the browse image PNG.

    Notes
    -----
    This function does not add a full alpha channel to the output png.
    It instead uses "cheap transparency" (palette-based transparency)
    to keep file size smaller.
    See: http://www.libpng.org/pub/png/book/chapter08.html#png.ch08.div.5.4
    """

    # Only use 2D arrays
    for arr in (red, green, blue):
        if len(np.shape(arr)) != 2:
            raise ValueError("Input image array must be 2D.")

    # Concatenate into uint8 RGB array.
    nrow, ncol = np.shape(red)
    rgb_arr = np.zeros((nrow, ncol, 3), dtype=np.uint8)

    # transparency_val will be the same from all calls to this function;
    # only need to capture it once.
    rgb_arr[:, :, 0], transparency_val = prep_arr_for_png_with_transparency(red)
    rgb_arr[:, :, 1] = prep_arr_for_png_with_transparency(green)[0]
    rgb_arr[:, :, 2] = prep_arr_for_png_with_transparency(blue)[0]

    # make a tuple with length 3, where each entry denotes the transparent
    # value for R, G, and B channels (respectively)
    transparency_val = (transparency_val,) * 3

    im = Image.fromarray(rgb_arr, mode="RGB")

    im.save(filepath, transparency=transparency_val)  # default = 72 dpi


def prep_arr_for_png_with_transparency(img_arr):
    """
    Prepare a 2D image array for use in a uint8 PNG with palette-based
    transparency.

    Normalizes and then scales the array values to 1-255. Non-finite pixels
    (aka invalid pixels) are set to 0.

    Parameters
    ----------
    img_arr : array_like
        2D Image to plot

    Returns
    -------
    out : numpy.ndarray with dtype numpy.uint8
        Copy of the input image array that has been prepared for use in
        a PNG file.
        Input image array values were normalized to [0,1] and then
        scaled to [1,255]. Non-finite pixels are set to 0.
    transparency_value : int
        The pixel value denoting non-finite (invalid) pixels. This is currently always 0.

    Notes
    -----
    For PNGs with palette-based transparency, one value in 0-255 will need
    to be assigned to be the fill value (i.e. the value that will appear
    as transparent). For unsigned integer data, it's conventional to use
    the largest representable value. (For signed integer data you usually
    want the most negative value.)
    However, when using RGB mode + palette-based transparency in Python's
    PIL library, if a pixel in only e.g. one color channel is invalid,
    but the corresponding pixel in other channels is valid, then the
    resulting PNG image will make the color for the first channel appear
    dominant. For example, for a given pixel in an RGB image. If a red
    channel's value for that pixel is 255 (invalid), while the green and
    blue channels' values are 123 and 67 (valid), then in the output RGB
    that pixel will appear bright red -- even if the `transparency` parameter
    is assigned correctly. So, instead we'll use 0 to represent invalid
    pixels, so that the resulting PNG "looks" more representative of the
    underlying data.
    """

    # Normalize to range [0,1]. If the array is already normalized,
    # this should have no impact.
    out = nisarqa.normalize(img_arr)

    # After normalization to range [0,1], scale to 1-255 for unsigned int8
    # Reserve the value 0 for use as the transparency value.
    #   out = (<normalized array> * (target_max - target_min)) + target_min
    with nisarqa.ignore_runtime_warnings():
        # This line throws a "RuntimeWarning: invalid value encountered in cast"
        # when there are NaN values. Ignore those warnings.
        out = (np.uint8(out * (255 - 1))) + 1

    # Set transparency value so that the "alpha" is added to the image
    transparency_value = 0

    # Denote invalid pixels with 255, so that they output as transparent
    out[~np.isfinite(img_arr)] = transparency_value

    return out, transparency_value


def img2pdf_grayscale(
    img_arr: ArrayLike,
    plots_pdf: PdfPages,
    fig_title: Optional[str] = None,
    ax_title: Optional[str] = None,
    xlim: Optional[Sequence[float]] = None,
    ylim: Optional[Sequence[float]] = None,
    colorbar_formatter: Optional[FuncFormatter] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    nan_color: str | Sequence[float] | None = "blue",
) -> None:
    """
    Plot the image array in grayscale, add a colorbar, and append to the PDF.

    Parameters
    ----------
    img_arr : array_like
        Image to plot in grayscale
    plots_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the backscatter image plot to
    fig_title : str or None, optional
        The title for the plot's figure. Defaults to None.
    ax_title : str or None, optional
        The title for the plot's axes. (Functionally akin to a subtitle.)
        Defaults to None.
    xlim, ylim : sequence of numeric or None, optional
        Lower and upper limits for the axes ticks for the plot.
        Format: xlim=[<x-axis lower limit>, <x-axis upper limit>],
                ylim=[<y-axis lower limit>, <y-axis upper limit>]
    colorbar_formatter : matplotlib.ticker.FuncFormatter or None, optional
        Tick formatter function to define how the numeric value
        associated with each tick on the colorbar axis is formatted
        as a string. `FuncFormatter`s take exactly two arguments:
        `x` for the tick value and `pos` for the tick position,
        and must return a `str`. The `pos` argument is used
        internally by Matplotlib.
        If None, then default tick values will be used. Defaults to None.
        See: https://matplotlib.org/2.0.2/examples/pylab_examples/custom_ticker1.html
        (Wrapping the function with FuncFormatter is optional.)
    xlabel, ylabel : str or None, optional
        Axes labels for the x-axis and y-axis (respectively)
    nan_color : str or Sequence of float or None, optional
        Color to plot NaN pixels for the PDF report.
        For transparent, set to None.
        The color should given in a format recognized by matplotlib:
        https://matplotlib.org/stable/users/explain/colors/colors.html
        Defaults to "blue".
    """

    # Instantiate the figure object
    # (Need to instantiate it outside of the plotting function
    # in order to later modify the plot for saving purposes.)
    f = plt.figure(figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE)
    ax = plt.gca()

    # Decimate image to a size that fits on the axes without interpolation
    # and without making the size (in MB) of the PDF explode.
    img_arr = nisarqa.downsample_img_to_size_of_axes(
        ax=ax, arr=img_arr, mode="multilook"
    )

    # grayscale
    cmap = plt.cm.gray

    if nan_color is not None:
        # set color of NaN pixels
        cmap.set_bad(nan_color)

    # Plot the img_arr image.
    ax_img = ax.imshow(X=img_arr, cmap=cmap, interpolation="none")

    # Add Colorbar
    cbar = plt.colorbar(ax_img, ax=ax)

    if colorbar_formatter is not None:
        cbar.ax.yaxis.set_major_formatter(colorbar_formatter)

    ## Label the plot
    f.suptitle(fig_title)
    format_axes_ticks_and_labels(
        ax=ax,
        xlim=xlim,
        ylim=ylim,
        img_arr_shape=np.shape(img_arr),
        title=ax_title,
        xlabel=xlabel,
        ylabel=ylabel,
    )

    # Make sure axes labels do not get cut off
    f.tight_layout()

    # Append figure to the output PDF
    plots_pdf.savefig(f)

    # Close the plot
    plt.close(f)


def format_axes_ticks_and_labels(
    ax: Axes,
    xlim: Optional[Sequence[float]] = None,
    ylim: Optional[Sequence[float]] = None,
    img_arr_shape: Optional[Sequence[int]] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
) -> None:
    """
    Format the tick marks and labels on the given axes object.

    Parameters
    ----------
    ax : matplotlib.axis.Axes
        The axes object to be modified. This axes' tick marks, labels, and
        title will be formatted as specified by the parameters provided to
        this function. `ax` should be the full size of `fig`.
    xlim, ylim : sequence of numeric or None, optional
        Lower and upper limits for the axes ticks for the plot.
        Format: xlim=[<x-axis lower limit>, <x-axis upper limit>],
                ylim=[<y-axis lower limit>, <y-axis upper limit>]
        If `xlim` is None, the x-axes ticks and labels will not be modified.
        Similar for `ylim`. (They are handled independently.) Defaults to None.
    img_arr_shape : pair of ints or None, optional
        The shape of the image which will be placed on `ax`. In practise, this
        establishes the aspect ratio for the axes.
        Required if `xlim` or `ylim` are specified; otherwise will be ignored.
    title : str or None, optional
        The title for the axes. Defaults to None (no title added).
    xlabel, ylabel : str or None, optional
        Axes labels for the x-axis and y-axis (respectively).
        Defaults to None (no labels added).
    """

    # If xlim or ylim are not provided, let Matplotlib auto-assign the ticks.
    # Otherwise, dynamically calculate and set the ticks w/ labels for
    # the x-axis and/or y-axis.
    # (Attempts to set the limits by using the `extent` argument for
    # matplotlib.imshow() caused significantly distorted images.
    # So, compute and set the ticks w/ labels manually.)
    if xlim is not None or ylim is not None:
        if img_arr_shape is None:
            raise ValueError("Must provide `img_arr_shape` input.")

        # Set the density of the ticks on the figure
        ticks_per_inch = 2.5

        # Get the dimensions of the figure object in inches
        fig_w, fig_h = ax.get_figure().get_size_inches()

        # Get the dimensions of the image array in pixels
        W = img_arr_shape[1]
        H = img_arr_shape[0]

        # Update variables to the actual, displayed image size
        # (The actual image will have a different aspect ratio
        # than the Matplotlib figure window's aspect ratio.
        # But, altering the Matplotlib figure window's aspect ratio
        # will lead to inconsistently-sized pages in the output PDF.)
        if H / W >= fig_h / fig_w:
            # image will be limited by its height, so
            # it will not use the full width of the figure
            fig_w = W * (fig_h / H)
        else:
            # image will be limited by its width, so
            # it will not use the full height of the figure
            fig_h = H * (fig_w / W)

    if xlim is not None:
        # Compute num of xticks to use
        num_xticks = int(ticks_per_inch * fig_w)

        # Always have a minimum of 2 labeled ticks
        num_xticks = max(num_xticks, 2)

        # Specify where we want the ticks, in pixel locations.
        xticks = np.linspace(0, img_arr_shape[1], num_xticks)
        ax.set_xticks(xticks)

        # Specify what those pixel locations correspond to in data coordinates.
        # By default, np.linspace is inclusive of the endpoint
        xticklabels = [
            "{:.1f}".format(i)
            for i in np.linspace(start=xlim[0], stop=xlim[1], num=num_xticks)
        ]
        ax.set_xticklabels(xticklabels, rotation=45)

    if ylim is not None:
        # Compute num of yticks to use
        num_yticks = int(ticks_per_inch * fig_h)

        # Always have a minimum of 2 labeled ticks
        num_yticks = max(num_yticks, 2)

        # Specify where we want the ticks, in pixel locations.
        yticks = np.linspace(0, img_arr_shape[0], num_yticks)
        ax.set_yticks(yticks)

        # Specify what those pixel locations correspond to in data coordinates.
        # By default, np.linspace is inclusive of the endpoint
        yticklabels = [
            "{:.1f}".format(i)
            for i in np.linspace(start=ylim[0], stop=ylim[1], num=num_yticks)
        ]
        ax.set_yticklabels(yticklabels)

    # Label the Axes
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)

    # Add title
    if title is not None:
        ax.set_title(title, fontsize=10)


def add_hist_to_axis(
    axis: Axes, counts: np.ndarray, edges: np.ndarray, label: str | None = None
) -> None:
    """Add the plot of the given counts and edges to the
    axis object. Points will be centered in each bin,
    and the plot will be denoted `label` in the legend.
    """
    bin_centers = 0.5 * (edges[:-1] + edges[1:])
    axis.plot(bin_centers, counts, label=label)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
