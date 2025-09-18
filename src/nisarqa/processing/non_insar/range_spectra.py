from __future__ import annotations

import h5py
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from numpy.typing import ArrayLike
from scipy import constants

import nisarqa

from ._utils import (
    _get_s_avg_for_tile,
    _get_units_hz_or_mhz,
    _post_process_s_avg,
)

objects_to_skip = nisarqa.get_all(name=__name__)


@nisarqa.log_function_runtime
def process_range_spectra(
    product: nisarqa.RSLC,
    params: nisarqa.RangeSpectraParamGroup,
    stats_h5: h5py.File,
    report_pdf: PdfPages,
) -> None:
    """
    Generate the RSLC Range Spectra plot(s) and save to PDF and stats.h5.

    Generate the RSLC Range Spectra; save the plot
    to the graphical summary .pdf file and the data to the
    statistics .h5 file.

    Power Spectral Density (PSD) is computed in decibels referenced to
    1/hertz (dB re 1/Hz) units, and Frequency in Hz or MHz (specified
    per `params.hz_to_mhz`).

    Parameters
    ----------
    product : nisarqa.RSLC
        Input RSLC product.
    params : nisarqa.RangeSpectraParamGroup
        A structure containing the parameters for processing
        and outputting the range spectra.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the range spectra plots plot to.
    """

    # Generate and store the range spectra plots
    for freq in product.freqs:
        with nisarqa.log_runtime(
            f"`generate_range_spectra_single_freq` for Frequency {freq}"
        ):
            generate_range_spectra_single_freq(
                product=product,
                freq=freq,
                params=params,
                stats_h5=stats_h5,
                report_pdf=report_pdf,
            )


def generate_range_spectra_single_freq(
    product: nisarqa.RSLC,
    freq: str,
    params: nisarqa.RangeSpectraParamGroup,
    stats_h5: h5py.File,
    report_pdf: PdfPages,
) -> None:
    """
    Generate the RSLC Range Spectra for a single frequency.

    Generate the RSLC Range Spectra; save the plot
    to the graphical summary .pdf file and the data to the
    statistics .h5 file.

    Power Spectral Density (PSD) is computed in decibels referenced to
    1/hertz (dB re 1/Hz) units, and Frequency in Hz or MHz (specified
    per `params.hz_to_mhz`).

    Parameters
    ----------
    product : nisarqa.RSLC
        Input RSLC product.
    freq : str
        Frequency name for the range power spectra to be processed,
        e.g. 'A' or 'B'
    params : RangeSpectraParamGroup
        A structure containing the parameters for processing
        and outputting the spectra.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the range spectra plots plot to.
    """
    log = nisarqa.get_logger()
    log.info(f"Generating Range Spectra for Frequency {freq}...")

    # Plot the range spectra using strictly increasing sample frequencies
    # (no discontinuity).
    fft_shift = True

    # Get the FFT spacing
    # Because `freq` is fixed, and all polarizations within
    # the same frequency will have the same `fft_freqs`.
    # So, we only need to do this computation one time.
    first_pol = product.get_pols(freq=freq)[0]
    with product.get_raster(freq, first_pol) as img:
        # Compute the sample rate
        # c/2 for radar energy round-trip; units for `sample_rate` will be Hz
        dr = product.get_slant_range_spacing(freq)
        sample_rate = (constants.c / 2.0) / dr

        fft_freqs = nisarqa.generate_fft_freqs(
            num_samples=img.data.shape[1],
            sampling_rate=sample_rate,
            fft_shift=fft_shift,
        )

        proc_center_freq = product.get_processed_center_frequency(freq)

        if params.hz_to_mhz:
            fft_freqs = nisarqa.hz2mhz(fft_freqs)
            proc_center_freq = nisarqa.hz2mhz(proc_center_freq)

        abbreviated_units, hdf5_units = _get_units_hz_or_mhz(params.hz_to_mhz)

    # Save x-axis values to stats.h5 file
    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=nisarqa.STATS_H5_QA_FREQ_GROUP % (product.band, freq),
        ds_name="rangeSpectraFrequencies",
        ds_data=fft_freqs,
        ds_units=hdf5_units,
        ds_description=(
            f"Frequency coordinates for Frequency {freq} range power spectra."
        ),
    )

    # Plot the Range Power Spectra for each pol onto the same axes.
    fig, ax = plt.subplots(
        nrows=1, ncols=1, figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE
    )

    # Use custom cycler for accessibility
    ax.set_prop_cycle(nisarqa.CUSTOM_CYCLER)

    rng_spec_units_pdf = "dB re 1/Hz"
    rng_spec_units_hdf5 = "decibel re 1/hertz"

    for pol in product.get_pols(freq):
        with product.get_raster(freq=freq, pol=pol) as img:
            with nisarqa.log_runtime(
                f"`compute_range_spectra_by_tiling` for Frequency {freq}"
                f" Polarization {pol} with shape {img.data.shape} using"
                f" azimuth decimation of {params.az_decimation} and tile"
                f" height of {params.tile_height}"
            ):
                # Get the Range Spectra
                # (The returned array is in dB re 1/Hz)
                rng_spectrum = nisarqa.compute_range_spectra_by_tiling(
                    arr=img.data,
                    sampling_rate=sample_rate,
                    az_decimation=params.az_decimation,
                    tile_height=params.tile_height,
                    fft_shift=fft_shift,
                )

            # Save normalized range power spectra values to stats.h5 file
            nisarqa.create_dataset_in_h5group(
                h5_file=stats_h5,
                grp_path=img.stats_h5_group_path,
                ds_name="rangePowerSpectralDensity",
                ds_data=rng_spectrum,
                ds_units=rng_spec_units_hdf5,
                ds_description=(
                    "Normalized range power spectral density for Frequency"
                    f" {freq}, Polarization {pol}."
                ),
            )

            # Add this power spectrum to the figure
            ax.plot(fft_freqs, rng_spectrum, label=pol)

    # Label the Plot
    ax.set_title(f"Range Power Spectra for Frequency {freq}\n")
    ax.set_xlabel(f"Frequency rel. {proc_center_freq} {abbreviated_units}")

    ax.set_ylabel(f"Power Spectral Density ({rng_spec_units_pdf})")

    ax.legend(loc="upper right")
    ax.grid(visible=True)

    # Save complete plots to graphical summary pdf file
    report_pdf.savefig(fig)

    # Close the plot
    plt.close()

    log.info(f"Range Power Spectra for Frequency {freq} complete.")


def compute_range_spectra_by_tiling(
    arr: ArrayLike,
    sampling_rate: float,
    az_decimation: int = 1,
    tile_height: int = 512,
    fft_shift: bool = True,
) -> np.ndarray:
    """
    Compute the normalized range power spectral density in dB re 1/Hz by tiling.

    Parameters
    ----------
    arr : array_like
        The input array, representing a two-dimensional discrete-time signal.
    sampling_rate : numeric
        Range sample rate (inverse of the sample spacing) in Hz.
    az_decimation : int, optional
        The stride to decimate the input array along the azimuth axis.
        For example, `4` means every 4th range line will
        be used to compute the range spectra.
        If `1`, no decimation will occur (but is slower to compute).
        Must be greater than zero. Defaults to 1.
    tile_height : int, optional
        User-preferred tile height (number of range lines) for processing
        images by batches. Actual tile shape may be modified by QA to be
        an integer multiple of `az_decimation`. -1 to use all rows.
        Note: full rows must be read in, so the number of columns for each tile
        will be fixed to the number of columns in the input raster.
        Defaults to 512.
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
        Normalized range power spectral density in dB re 1/Hz of `arr`.
    """
    shape = np.shape(arr)
    if len(shape) != 2:
        raise ValueError(
            f"Input array has {len(shape)} dimensions, but must be 2D."
        )

    nrows, ncols = shape

    if az_decimation > nrows:
        raise ValueError(
            f"{az_decimation=}, must be <= the height of the input array"
            f" ({nrows} pixels)."
        )

    if tile_height == -1:
        tile_height = nrows

    # Adjust the tile height to be an integer multiple of `az_decimation`.
    # Otherwise, the decimation will get messy to book-keep.
    if tile_height < az_decimation:
        # Grow tile height
        tile_height = az_decimation
    else:
        # Shrink tile height (less risk of memory issues)
        tile_height = tile_height - (tile_height % az_decimation)

    # Compute total number of range lines that will be used to generate
    # the range power spectra. This will be used for averaging.
    # The TileIterator will truncate the array azimuth direction to be
    # an integer multiple of the stride, so use integer division here.
    num_range_lines = nrows // az_decimation

    # Create the Iterator over the input array
    input_iter = nisarqa.TileIterator(
        arr_shape=np.shape(arr),
        axis_0_tile_dim=tile_height,
        axis_0_stride=az_decimation,
    )

    # Initialize the accumulator array
    S_avg = np.zeros(ncols)

    for tile_slice in input_iter:
        S_avg += _get_s_avg_for_tile(
            arr_slice=arr[tile_slice],
            fft_axis=1,  # Compute fft over range axis (axis 1)
            num_fft_bins=ncols,
            averaging_denominator=num_range_lines,
        )

    return _post_process_s_avg(
        S_avg=S_avg, sampling_rate=sampling_rate, fft_shift=fft_shift
    )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
