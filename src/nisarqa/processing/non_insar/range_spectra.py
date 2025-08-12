from __future__ import annotations

import h5py
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy import constants

import nisarqa

from ._utils import _get_units_hz_or_mhz

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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
