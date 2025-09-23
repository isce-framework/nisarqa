from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import replace
from typing import Optional, overload

import matplotlib.colors as colors
import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from ..plotting_utils import (
    downsample_img_to_size_of_axes,
    format_axes_ticks_and_labels,
    format_cbar_ticks_for_multiples_of_pi,
    plot_to_rgb_png,
)
from ..processing_utils import get_phase_array, image_histogram_equalization

objects_to_skip = nisarqa.get_all(name=__name__)


def make_hsi_png_with_wrapped_phase(
    product: nisarqa.WrappedGroup,
    freq: str,
    pol: str,
    params: nisarqa.IgramBrowseParamGroup,
    png_filepath: str | os.PathLike,
) -> None:
    """
    Create and save HSI image of a wrapped interferogram with coh mag as a PNG.

    Phase values are encoded as Hue and coherence magnitude values are
    encoded as Intensity in the resulting PNG.

    Parameters
    ----------
    product : nisarqa.WrappedGroup
        Input NISAR product.
    freq, pol : str
        The frequency and polarization (respectively) pair for the wrapped
        interferogram and coh mag layer to use for generating the HSI image.
    params : nisarqa.IgramBrowseParamGroup
        A structure containing the parameters for creating the HSI image.
    png_filepath : path-like
        Filename (with path) for the image PNG.
    """

    with (
        product.get_wrapped_igram(freq=freq, pol=pol) as igram_r,
        product.get_wrapped_coh_mag(freq=freq, pol=pol) as coh_r,
    ):
        rgb_img, _ = make_hsi_raster(
            phs_or_complex_raster=igram_r,
            coh_raster=coh_r,
            equalize=params.equalize_browse,
            rewrap=None,
            longest_side_max=params.longest_side_max,
        )

    plot_to_rgb_png(
        red=rgb_img.data[:, :, 0],
        green=rgb_img.data[:, :, 1],
        blue=rgb_img.data[:, :, 2],
        filepath=png_filepath,
    )


def make_hsi_png_with_unwrapped_phase(
    product: nisarqa.UnwrappedGroup,
    freq: str,
    pol: str,
    params: nisarqa.UNWIgramBrowseParamGroup,
    png_filepath: str | os.PathLike,
) -> None:
    """
    Create and save HSI image of unwrapped interferogram with coh mag as a PNG.

    (Possibly re-wrapped) unwrapped phase values are encoded as Hue and
    coherence magnitude values are encoded as Intensity in the resulting PNG.

    Parameters
    ----------
    product : nisarqa.UnwrappedGroup
        Input NISAR product.
    freq, pol : str
        The frequency and polarization (respectively) pair for the unwrapped
        interferogram and coh mag layer to use for generating the HSI image.
    params : nisarqa.UNWIgramBrowseParamGroup
        A structure containing the parameters for creating the HSI image.
    png_filepath : path-like
        Filename (with path) for the image PNG.
    """

    with (
        product.get_unwrapped_phase(freq=freq, pol=pol) as phs_r,
        product.get_unwrapped_coh_mag(freq=freq, pol=pol) as coh_r,
    ):
        rgb_img, _ = make_hsi_raster(
            phs_or_complex_raster=phs_r,
            coh_raster=coh_r,
            equalize=params.equalize_browse,
            rewrap=params.rewrap,
            longest_side_max=params.longest_side_max,
        )
    plot_to_rgb_png(
        red=rgb_img.data[:, :, 0],
        green=rgb_img.data[:, :, 1],
        blue=rgb_img.data[:, :, 2],
        filepath=png_filepath,
    )


def hsi_images_to_pdf_wrapped(
    product: nisarqa.WrappedGroup,
    report_pdf: PdfPages,
) -> None:
    """
    Create HSI wrapped interferogram images and save to PDF.

    Parameters
    ----------
    product : nisarqa.WrappedGroup
        Input NISAR product.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the HSI image plot to.
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq=freq):
            with (
                product.get_wrapped_igram(freq=freq, pol=pol) as igram_r,
                product.get_wrapped_coh_mag(freq=freq, pol=pol) as coh_r,
            ):
                # Create a *Raster with the HSI image

                # The HSI colorbar generated in the HSI PDF function (below)
                # has a linear scale from [0, 1] for the intensity channel
                # (coherence magnitude layer). If we equalize that channel,
                # then the colorbar scale would be inaccurate.
                # So, ensure equalize=False when creating the HSI Raster.
                rgb_img, cbar_min_max = make_hsi_raster(
                    phs_or_complex_raster=igram_r,
                    coh_raster=coh_r,
                    equalize=False,  # Do not equalize the PDF HSI images
                    rewrap=None,
                    longest_side_max=None,  # Unnecessary for the PDF
                )

            save_hsi_img_to_pdf(
                img=rgb_img,
                report_pdf=report_pdf,
                cbar_min_max=cbar_min_max,
                plot_title_prefix="Wrapped Phase Image and Coherence Magnitude",
            )


def hsi_images_to_pdf_unwrapped(
    product: nisarqa.UnwrappedGroup,
    report_pdf: PdfPages,
    rewrap: Optional[float | int] = None,
) -> None:
    """
    Create HSI unwrapped phase images and save to PDF.

    Parameters
    ----------
    product : nisarqa.UnwrappedGroup
        Input NISAR product.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the HSI image plot to.
    rewrap : float or None, optional
        The multiple of pi to rewrap the unwrapped phase image when generating
        the HSI image(s). If None, no rewrapping will occur.
        Ex: If 3 is provided, the image is rewrapped to the interval [0, 3pi).
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq=freq):
            with (
                product.get_unwrapped_phase(freq=freq, pol=pol) as phs_r,
                product.get_unwrapped_coh_mag(freq=freq, pol=pol) as coh_r,
            ):
                # The HSI colorbar generated in the HSI PDF function (below)
                # has a linear scale from [0, 1] for the intensity channel
                # (coherence magnitude layer). If we equalize that channel,
                # then the colorbar scale would be inaccurate.
                # So, ensure equalize=False when creating the HSI Raster.
                rgb_img, cbar_min_max = make_hsi_raster(
                    phs_or_complex_raster=phs_r,
                    coh_raster=coh_r,
                    equalize=False,  # Do not equalize the PDF HSI images
                    rewrap=rewrap,
                    longest_side_max=None,  # Unnecessary for the PDF
                )

            save_hsi_img_to_pdf(
                img=rgb_img,
                report_pdf=report_pdf,
                cbar_min_max=cbar_min_max,
                plot_title_prefix=(
                    "Unwrapped Phase Image and Coherence Magnitude"
                ),
            )


def save_hsi_img_to_pdf(
    img: nisarqa.SARRaster,
    report_pdf: PdfPages,
    cbar_min_max: Optional[Sequence[float]] = None,
    plot_title_prefix: str = "Phase Image and Coherence Magnitude as HSI Image",
) -> None:
    """
    Annotate and save an HSI Image to PDF.

    `img.data` should be in linear.

    Parameters
    ----------
    img : *Raster
        Image in RGB color space to be saved. All image correction,
        multilooking, etc. needs to have previously been applied.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the HSI image plot to.
    cbar_min_max : pair of float or None, optional
        The range for the Hue axis of the HSI colorbar for the image raster.
        `None` to use the min and max of the image for the colorbar range.
        Defaults to None.
    plot_title_prefix : str, optional
        Prefix for the title of the backscatter plots.
        Defaults to "Phase Image and Coherence Magnitude as HSI Image".
    """
    # Plot and Save HSI Image to graphical summary pdf
    title = f"{plot_title_prefix}\n{img.name}"

    img2pdf_hsi(
        img_arr=img.data,
        title=title,
        ylim=img.y_axis_limits,
        xlim=img.x_axis_limits,
        cbar_min_max=cbar_min_max,
        xlabel=img.x_axis_label,
        ylabel=img.y_axis_label,
        plots_pdf=report_pdf,
    )


def make_hsi_as_rgb_img(
    phase_img: np.ndarray,
    coh_mag: np.ndarray,
    phs_img_range: Optional[Sequence[float | int]] = None,
    equalize: bool = False,
) -> np.ndarray:
    """
    Create HSI interferogram image array, returned in RGB colorspace.

    The phase image and coherence magnitude rasters are first processed into
    the HSI (Hue, Saturation, Intensity) colorspace, which is then converted
    to RGB values in normalized range [0, 1].

    If any input layer was NaN-valued for a given pixel, then the output
    value for that pixel will be NaN (for all channels).

    TODO: This algorithm currently uses the built-in matplotlib.hsv_to_rgb()
    to convert to RGB due to delivery schedule constraints.
    But, there is a subtle mathematical difference between the HSI and HSV
    colorspaces, and we should definitely use HSI (not HSV).
    This will require a custom implementation of HSI->RGB.

    Parameters
    ----------
    phase_img : numpy.ndarray
        2D array of a phase image (e.g. `unwrappedInterferogram`).
        This should contain real-valued pixels; if your raster is a complex
        valued interferogram, please compute the phase (e.g. use np.angle())
        and then pass in the resultant raster for `phase_img`.
    coh_mag : numpy.ndarray
        2D raster of `coherenceMagnitude` layer corresponding to `phase_img`.
        This should already be normalized to range [0, 1]. (Otherwise
        something must have gone rather wrong in the InSAR processing!)
    phs_img_range : pair of float or None, optional
        The expected range for the phase image raster. `None` to use the
        min and max of the image data. This will be used for normalization
        of the data to range [0, 1].
        Note: If `phs_img`'s data is within a known range, it is strongly
        suggested to set this parameter, otherwise unintended image correction
        will occur.
        For example, if an image was generated via np.angle(), the known range
        is (-pi, pi]. But if the actual image data only contains values from
        [-pi/2, pi/3] and `None` was provided, then the phase image will appear
        "stretched", because during normalization -pi/2 -> 0 and pi/3 -> 1.
        Defaults to None.
    equalize : bool, optional
        True to perform histogram equalization on the Intensity channel
        (the coherence magnitude layer) for the HSI image.
        See: https://scikit-image.org/docs/stable/auto_examples/color_exposure/plot_equalize.html
        Default is False.

    Returns
    -------
    rgb : numpy.ndarray
        3D array of HSI image converted to the RGB (Red Green Blue) colorspace.
        This RGB array is ready for plotting in e.g. Matplotlib.
    """
    if not np.issubdtype(phase_img.dtype, np.floating):
        raise TypeError(
            f"`phase_img` has type {type(phase_img)}, must be float. "
            "Hint: If complex, perhaps compute numpy.angle(phase_img) "
            "before passing in the array."
        )

    if phase_img.ndim != 2:
        raise ValueError(
            f"`phase_img` has shape {np.shape(phase_img)}"
            "but must be a 2D array."
        )

    if coh_mag.ndim != 2:
        raise ValueError(
            f"`coh_mag` has shape {np.shape(coh_mag)} but must be a 2D array."
        )

    if np.shape(phase_img) != np.shape(coh_mag):
        raise ValueError(
            f"`phase_img` (shape: {np.shape(phase_img)}) and `coh_mag` "
            f"(shape: {np.shape(coh_mag)}) must have the same shape."
        )

    # coh mag should already be within range [0, 1].
    if np.any(coh_mag < 0.0) or np.any(coh_mag > 1.0):
        raise ValueError("`coh_mag` contains values outside of range [0, 1].")

    # Initialize HSI array
    # Note: per hsv_to_rgb(): "All values assumed to be in range [0, 1]".
    # So, we'll need to normalize all rasters added to this array.
    hsi = np.ones((phase_img.shape[0], phase_img.shape[1], 3), dtype=np.float32)

    # First channel is hue. The phase image should be represented by hue.
    # Note: If available, make sure to specify the known min/max range for
    # the image, such as (-pi, pi] for images created with np.angle().
    # Otherwise, `nisarqa.normalize()` will take the min and max of the actual
    # data, which could have the undesirable effect of applying image
    # correction to e.g. phase images.
    hsi[:, :, 0] = nisarqa.normalize(arr=phase_img, min_max=phs_img_range)

    # Second channel is saturation. We set it to 1 always.
    # Note: Nothing more to do --> It was previously initialized to 1.

    # Third channel is intensity scaled between 0, 1.
    # If the user desires, equalize histogram
    if equalize:
        # image_histogram_equalization handles normalization
        hsi[:, :, 2] = image_histogram_equalization(image=coh_mag)
    else:
        # coh mag is already within range [0, 1].
        hsi[:, :, 2] = coh_mag

    # The input arrays may contain some nan values.
    # But, we need to set them to zero for generating the HSI array.
    # So, create a temporary mask of all NaN pixels, do the computation,
    # and then set those pixels back to NaN for the final image.

    # nan_mask: True where pixels are non-finite; False where pixels are finite
    nan_mask = ~np.isfinite(phase_img) | ~np.isfinite(coh_mag)

    # For the HSI-> RGB conversion, replace all non-finite values with 0
    hsi[nan_mask] = 0.0

    # For plotting the image, convert to RGB color space
    # TODO - We need to use HSI not HSV. There is a subtle mathematical
    # difference between the two colorspaces.
    # However, this will require a custom implementation of HSI->RGB.
    rgb = colors.hsv_to_rgb(hsi)

    # Restore the NaN values
    rgb[nan_mask] = np.nan

    return rgb


@overload
def make_hsi_raster(
    phs_or_complex_raster: nisarqa.RadarRaster,
    coh_raster: nisarqa.RadarRaster,
    equalize: bool,
    rewrap: Optional[float] = None,
    longest_side_max: Optional[int] = None,
) -> tuple[nisarqa.RadarRaster, list[float]]: ...


@overload
def make_hsi_raster(
    phs_or_complex_raster: nisarqa.GeoRaster,
    coh_raster: nisarqa.GeoRaster,
    equalize: bool,
    rewrap: Optional[float] = None,
    longest_side_max: Optional[int] = None,
) -> tuple[nisarqa.GeoRaster, list[float]]: ...


def make_hsi_raster(
    phs_or_complex_raster,
    coh_raster,
    equalize,
    rewrap=None,
    longest_side_max=None,
):
    """
    Create HSI interferogram *Raster with square pixels, and colorbar range.

    Parameters
    ----------
    phs_or_complex_raster : nisarqa.GeoRaster | nisarqa.RadarRaster
        *Raster of complex interferogram or unwrapped phase data to use to
        construct the Hue layer for the HSI *Raster.
        If *Raster is complex valued, numpy.angle() will be used to compute
        the phase image (float-valued).
        This should correspond to `coh_raster`.
    coh_raster : nisarqa.GeoRaster | nisarqa.RadarRaster
        *Raster for the coherence magnitude raster to use to construct
        the intesity layer for the HSI *Raster.
        This should correspond to `phs_or_complex_raster`.
    equalize : bool, optional
        True to perform histogram equalization on the Intensity channel
        (the coherence magnitude layer) for the HSI image.
        See: https://scikit-image.org/docs/stable/auto_examples/color_exposure/plot_equalize.html
        Default is False.
    rewrap : float or None, optional
        The multiple of pi to rewrap the unwrapped phase image when generating
        the HSI image(s). If None, no rewrapping will occur.
        Ex: If 3 is provided, the image is rewrapped to the interval [0, 3pi).
    longest_side_max : int or None, optional
        Decimate the generated HSI raster so that the max length of
        axis 0 and axis 1 in `hsi_raster` is `longest_side_max`.

    Returns
    -------
    hsi_raster : nisarqa.GeoRaster | nisarqa.RadarRaster
        A *Raster of the HSI image converted to RGB color space. This raster
        will have square pixels. (If the rasters in `phs_or_complex_raster` and
        `coh_raster` do not have square pixels, then decimation will be applied
        to achieve square pixels.)
        The type of `hsi_raster` will be the same as the type of
        `phs_or_complex_raster` and `coh_raster`.
    cbar_min_max : pair of float
        The suggested range to use for the Hue axis of the
        HSI colorbar for `hsi_raster`.
        If `phs_or_complex_raster` has complex valued data, then `cbar_min_max`
        will be the range [-pi, +pi].
    """
    # Validate input rasters
    nisarqa.compare_raster_metadata(
        phs_or_complex_raster, coh_raster, almost_identical=False
    )

    phs_img, cbar_min_max = get_phase_array(
        phs_or_complex_raster=phs_or_complex_raster,
        make_square_pixels=False,  # we'll do this on the HSI Raster later
        rewrap=rewrap,
    )

    coh_img = coh_raster.data[...]

    rgb = nisarqa.make_hsi_as_rgb_img(
        phase_img=phs_img,
        coh_mag=coh_img,
        phs_img_range=cbar_min_max,
        equalize=equalize,
    )

    # Square the pixels. Decimate if requested.
    y_axis_spacing = phs_or_complex_raster.y_axis_spacing
    x_axis_spacing = phs_or_complex_raster.x_axis_spacing

    if longest_side_max is None:
        # Update to be the longest side of the array. This way no downsizing
        # of the image will occur, but we can still output square pixels.
        longest_side_max = max(np.shape(rgb)[:2])

    ky, kx = nisarqa.compute_square_pixel_nlooks(
        img_shape=np.shape(rgb)[:2],  # only need the x and y dimensions
        sample_spacing=[y_axis_spacing, x_axis_spacing],
        longest_side_max=longest_side_max,
    )
    rgb = rgb[::ky, ::kx]

    # Update the ground spacing so that the new *Raster we are building will
    # have correct metadata.
    y_axis_spacing = y_axis_spacing * ky
    x_axis_spacing = x_axis_spacing * kx

    # Construct the name for the new raster. (`*raster.name` has a format
    # like "RUNW_L_A_interferogram_HH_unwrappedPhase". The HSI image combines
    # two rasters, so remove the final layer name of e.g. "_unwrappedPhase".)
    name = "_".join(phs_or_complex_raster.name.split("_")[:-1])
    if rewrap:
        name += f" - rewrapped to [0, {rewrap}{nisarqa.PI_UNICODE})"

    # Construct the HSI *Raster object
    if isinstance(phs_or_complex_raster, nisarqa.RadarRaster):
        hsi_raster = replace(
            phs_or_complex_raster,
            data=rgb,
            name=name,
            ground_az_spacing=y_axis_spacing,
            ground_range_spacing=x_axis_spacing,
        )
    elif isinstance(phs_or_complex_raster, nisarqa.GeoRaster):
        hsi_raster = replace(
            phs_or_complex_raster,
            data=rgb,
            name=name,
            y_spacing=y_axis_spacing,
            x_spacing=x_axis_spacing,
        )
    else:
        raise TypeError(
            f"Input rasters have type {type(phs_img)}, but must be either"
            " nisarqa.RadarRaster or nisarqa.GeoRaster."
        )

    return hsi_raster, cbar_min_max


def img2pdf_hsi(
    img_arr: npt.ArrayLike,
    plots_pdf: PdfPages,
    cbar_min_max: Optional[Sequence[float]] = None,
    title: Optional[str] = None,
    xlim: Optional[Sequence[float | int]] = None,
    ylim: Optional[Sequence[float | int]] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
) -> None:
    """
    Plot image array with a linear HSI "colorbar", then append to PDF.

    Parameters
    ----------
    img_arr : array_like
        Image to plot; image should represent an HSI (Hue,
        Saturation, Intensity) image that has been already converted to
        RGB colorspace (such as via matplotlib.colors.hsv_to_rgb()).
    plots_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the HSI image plot to.
    cbar_min_max : pair of float or None, optional
        The range for the Hue axis of the HSI colorbar for the image raster.
        `None` to use the min and max of the image data for the colorbar range.
        Defaults to None.
    title : str, optional
        The full title for the plot.
    xlim, ylim : sequence of numeric, optional
        Lower and upper limits for the axes ticks for the plot.
        Format: xlim=[<x-axis lower limit>, <x-axis upper limit>]
                ylim=[<y-axis lower limit>, <y-axis upper limit>]
    xlabel, ylabel : str, optional
        Axes labels for the x-axis and y-axis (respectively).
    """
    fig = plt.figure(
        figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE, constrained_layout=True
    )

    if title is not None:
        fig.suptitle(title)

    # Create two subplots; one to hold the actual raster image, the second
    # (smaller one) for the HSI "colorbar".
    # (Use add_subplot() to force the colorbar to be tall and skinny.)
    ax = fig.add_gridspec(5, 6)
    ax1 = fig.add_subplot(ax[:, :-2])
    # Call it `cax_pseudo` because this is a matplotlib.axes.Axes object,
    # and not a true matplotlib.colorbar.Colorbar object.
    cax_pseudo = fig.add_subplot(ax[1:4, -1])

    # Set all NaN pixels to 1 in each of the red-green-blue layers.
    # This way, the NaN pixels will appear white in the PDF.
    img_to_plot = np.array(img_arr, copy=True)
    img_to_plot[~np.isfinite(img_arr)] = 1

    # Decimate image to a size that fits on the axes without interpolation
    # and without making the size (in MB) of the PDF explode.
    img_to_plot = downsample_img_to_size_of_axes(
        ax=ax1, arr=img_to_plot, mode="decimate"
    )

    # Plot the raster image and label it
    ax1.imshow(img_to_plot, aspect="equal", cmap="hsv", interpolation="none")

    # There are two subplots, and we want the main plot title to appear
    # over both subplots (aka centered in the figure). So, do not supply
    # the title here, otherwise the main plot title will only be centered
    # over `ax1``. (The main plot title was set above, via `fig.suptitle()`.)
    format_axes_ticks_and_labels(
        ax=ax1,
        img_arr_shape=np.shape(img_to_plot),
        xlim=xlim,
        ylim=ylim,
        xlabel=xlabel,
        ylabel=ylabel,
    )

    # Create the HSI "colorbar" (which is actually a subplot)
    v, h = np.mgrid[0:1:100j, 0:1:300j]
    s = np.ones_like(v)
    hsv = np.dstack((h, s, v))
    rgb = colors.hsv_to_rgb(hsv)
    rgb = np.rot90(rgb, k=3)
    rgb = np.fliplr(rgb)

    if cbar_min_max is None:
        cbar_max = np.nanmax(img_arr)
        cbar_min = np.nanmin(img_arr)

    else:
        if (len(cbar_min_max) != 2) or (cbar_min_max[0] >= cbar_min_max[1]):
            raise ValueError(
                f"{cbar_min_max=}, must be a pair of increasing values."
            )
        cbar_max = cbar_min_max[1]
        cbar_min = cbar_min_max[0]

    cax_pseudo.imshow(
        rgb,
        origin="lower",
        extent=[0, 1, cbar_min, cbar_max],
    )
    cax_pseudo.set_xlabel("InSAR\nCoherence\nMagnitude", fontsize=8.5)
    cax_pseudo.set_ylabel(
        "InSAR Phase (radians)", fontsize=8.5, rotation=270, labelpad=10
    )
    cax_pseudo.yaxis.set_label_position("right")
    cax_pseudo.yaxis.tick_right()

    format_cbar_ticks_for_multiples_of_pi(
        cbar_min=cbar_min, cbar_max=cbar_max, cax=cax_pseudo
    )

    cax_pseudo.set_title("HSI Color Space\nSaturation=1", fontsize=8.5)

    # Append figure to the output PDF
    plots_pdf.savefig(fig)

    # Close the plot
    plt.close(fig)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
