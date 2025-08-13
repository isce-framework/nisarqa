from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


def _get_units_hz_or_mhz(mhz: bool) -> tuple[str, str]:
    """
    Return the abbreviated and long units for Hz or MHz.

    Parameters
    ----------
    mhz : bool
        True for MHz units; False for Hz units.

    Returns
    -------
    abbreviated_units : str
        "MHz" if `mhz`, otherwise "Hz".
    long_units : str
        "megahertz" if `mhz`, otherwise "hertz".
    """
    if mhz:
        abbreviated_units = "MHz"
        long_units = "megahertz"
    else:
        abbreviated_units = "Hz"
        long_units = "hertz"

    return abbreviated_units, long_units


def _get_s_avg_for_tile(
    arr_slice: ArrayLike,
    fft_axis: int,
    num_fft_bins: int,
    averaging_denominator: int,
) -> np.ndarray:
    """
    Helper function for the power spectra; computes the S_avg array for a tile.

    This function is designed to be called by a function that is handling the
    iteration process over all tiles in an array.

    Parameters
    ----------
    arr_slice : array_like
        Slice of a 2D Array to compute the FFT of. We're in the "tiling.py"
        module; `arr_slice` should be a full tile.
    fft_axis : int
        0 to compute the FFT along the azimuth axis,
        1 to compute along the range axis.
    num_fft_bins : int
        Number of FFT bins.
    averaging_denominator : int
        Total number of elements in the source array that will be averaged
        together to form the `S_avg` array.
        For Range Spectra, this is the number of range lines.
        For Azimuth Spectra, this is the subswath width.
        (We are processing the array by tiles, but the total summation of
        power might cause float overflow.
        So, during the accumulation process, if we divide each tile's
        power density by the total number of samples used, then the
        final accumulated array will be mathematically equivalent to
        the average.)

    Returns
    -------
    S_avg_partial : numpy.ndarray
        Normalized FFT that has been "averaged" with `averaging_denominator`.
    """

    # Compute FFT
    # Ensure no normalization occurs here; do that manually below.
    # Units of `fft` are the same as the units of `arr_slice`: unitless
    fft = nisarqa.compute_fft(arr_slice, axis=fft_axis)

    # Compute the power
    S = np.abs(fft) ** 2

    # Normalize the transform
    S /= num_fft_bins

    # Average over the opposite axis
    #   `1 - fft_axis` will flip a 1 to a 0, or a 0 to a 1.
    return np.sum(S, axis=1 - fft_axis) / averaging_denominator


def _post_process_s_avg(
    S_avg: ArrayLike, sampling_rate: float, fft_shift: bool
) -> np.ndarray:
    """
    Helper function for the power spectra; post-processes average spectra.

    Parameters
    ----------
    S_avg : array_like
        The averaged spectra
    sampling_rate : numeric
        Range sample rate (inverse of the sample spacing) in Hz. Used to
        normalize `S_avg`.
    fft_shift : bool, optional
        True to shift `S_out` to correspond to frequency bins that are
        continuous from negative (min) -> positive (max) values.

        False to leave `S_out` unshifted, such that the values correspond to
        `numpy.fft.fftfreq()`, where this discrete FFT operation orders values
        from 0 -> max positive -> min negative -> 0- . (This creates
        a discontinuity in the interval's values.)

        Defaults to True.

    Returns
    -------
    S_out : numpy.ndarray
        Normalized power spectral density in dB re 1/Hz.
    """
    # Normalize by the sampling rate
    # This makes the units unitless/Hz
    S_out = S_avg / sampling_rate

    # Convert to dB
    with nisarqa.ignore_runtime_warnings():
        # This line throws these warnings:
        #   "RuntimeWarning: divide by zero encountered in log10"
        # when there are zero values. Ignore those warnings.
        S_out = nisarqa.pow2db(S_out)

    if fft_shift:
        # Shift S_out to be aligned with the shifted FFT frequencies.
        S_out = np.fft.fftshift(S_out)

    return S_out


__all__ = nisarqa.get_all(__name__, objects_to_skip)
