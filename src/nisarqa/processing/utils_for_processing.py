from __future__ import annotations

from typing import Optional

import numpy as np

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


def get_phase_array(
    phs_or_complex_raster: nisarqa.GeoRaster | nisarqa.RadarRaster,
    make_square_pixels: bool,
    rewrap: Optional[float] = None,
) -> tuple[np.ndarray, list[float]]:
    """
    Get the phase image from the input *Raster.

    Parameters
    ----------
    phs_or_complex_raster : nisarqa.GeoRaster | nisarqa.RadarRaster
        *Raster of complex interferogram or unwrapped phase data.
        If *Raster is complex valued, numpy.angle() will be used to compute
        the phase image (float-valued).
    make_square_pixels : bool
        True to decimate the image to have square pixels.
        False for `phs_img` to always keep the same shape as
        `phs_or_complex_raster.data`
    rewrap : float or None, optional
        The multiple of pi to rewrap the unwrapped phase image.
        If None, no rewrapping will occur.
        If `phs_or_complex_raster` is complex valued, this will be ignored.
        Ex: If 3 is provided, the image is rewrapped to the interval [0, 3pi).
        Defaults to None.

    Returns
    -------
    phs_img : numpy.ndarray
        The phase image from the input raster, processed according to the input
        parameters.
    cbar_min_max : pair of float
        The suggested range to use for plotting the phase image.
        If `phs_or_complex_raster` has complex valued data, then `cbar_min_max`
        will be the range (-pi, +pi].
        If `rewrap` is a float, the range will be [0, <rewrap * pi>).
        If `rewrap` is a None, the range will be [<array min>, <array max>].
    """

    phs_img = phs_or_complex_raster.data[...]

    if phs_or_complex_raster.is_complex:
        # complex data; take the phase angle.
        phs_img = np.angle(phs_img.data)

        # np.angle() returns output in range (-pi, pi]
        # So, set the colobar's min and max to be the range (-pi, +pi].
        cbar_min_max = [-np.pi, np.pi]

        # Helpful hint for user!
        if rewrap is not None:
            raise ValueError(
                "Input raster has a complex dtype (implying a wrapped"
                f" interferogram), but input parameter {rewrap=}. `rewrap` is"
                " only used in the case of real-valued data (implying an"
                " unwrapped phase image). Please check that this is intended."
            )

    else:
        # unwrapped phase image
        if rewrap is None:
            cbar_min_max = [
                np.nanmin(phs_img),
                np.nanmax(phs_img),
            ]
        else:
            # `rewrap` is a multiple of pi. Convert to the full float value.
            rewrap_final = rewrap * np.pi

            # The sign of the output of the modulo operator
            # is the same as the sign of `rewrap_final`.
            # This means that it will always put the output
            # into range [0, <rewrap_final>)
            phs_img %= rewrap_final
            cbar_min_max = [0, rewrap_final]

    if make_square_pixels:
        raster_shape = phs_img.shape

        ky, kx = nisarqa.compute_square_pixel_nlooks(
            img_shape=raster_shape,
            sample_spacing=[
                phs_or_complex_raster.y_axis_spacing,
                phs_or_complex_raster.x_axis_spacing,
            ],
            # Only make square pixels. Use `max()` to not "shrink" the rasters.
            longest_side_max=max(raster_shape),
        )

        # Decimate to square pixels.
        phs_img = phs_img[::ky, ::kx]

    return phs_img, cbar_min_max


def image_histogram_equalization(
    image: np.ndarray, nbins: int = 256
) -> np.ndarray:
    """
    Perform histogram equalization of a grayscale image.

    Parameters
    ----------
    image : numpy.ndarray
        N-dimensional image array. All dimensions will be combined when
        computing the histogram.
    nbins : int, optional
        Number of bins for computing the histogram.
        Defaults to 256.

    Returns
    -------
    equalized_img : numpy.ndarray
        The image with histogram equalization applied.
        This image will be in range [0, 1].

    References
    ----------
    Adapted from: skimage.exposure.equalize_hist
    Description of histogram equalization:
    https://scikit-image.org/docs/stable/auto_examples/color_exposure/plot_equalize.html
    """
    # Do not include NaN values
    img = image[np.isfinite(image)]

    hist, bin_edges = np.histogram(img.flatten(), bins=nbins, range=None)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0

    cdf = hist.cumsum()
    cdf = cdf / float(cdf[-1])

    out = np.interp(image.flatten(), bin_centers, cdf)
    out = out.reshape(image.shape)

    # Sanity Check. Mathematically, the output should be within range [0, 1].
    assert np.all(
        (0.0 <= out[np.isfinite(out)]) & (out[np.isfinite(out)] <= 1.0)
    ), "`out` contains values outside of range [0, 1]."

    # Unfortunately, np.interp currently always promotes to float64, so we
    # have to cast back to single precision when float32 output is desired
    return out.astype(image.dtype, copy=False)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
