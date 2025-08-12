from __future__ import annotations

import h5py
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from ._utils import _get_units_hz_or_mhz

objects_to_skip = nisarqa.get_all(name=__name__)


@nisarqa.log_function_runtime
def process_azimuth_spectra(
    product: nisarqa.RSLC,
    params: nisarqa.AzimuthSpectraParamGroup,
    stats_h5: h5py.File,
    report_pdf: PdfPages,
) -> None:
    """
    Generate the RSLC Azimuth Spectra plot(s) and save to PDF and stats.h5.

    Generate the RSLC Azimuth Spectra; save the plots to the PDF and
    statistics to the .h5 file. For each frequency+polarization, azimuth
    spectra plots are generated for three subswaths: one at near range,
    one at mid range, and one at far range.
    The size of the subswaths is specified in `params`; the azimuth spectra
    are formed by averaging the contiguous range samples in each subswath.

    Power Spectral Density (PSD) is computed in decibels referenced to
    1/hertz (dB re 1/Hz) units, and Frequency in Hz or MHz (specified
    per `params.hz_to_mhz`).

    Parameters
    ----------
    product : nisarqa.RSLC
        Input RSLC product.
    params : nisarqa.AzimuthSpectraParamGroup
        A structure containing the parameters for processing
        and outputting the azimuth spectra.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the range spectra plots plot to.
    """

    # Generate and store the az spectra plots
    for freq in product.freqs:
        with nisarqa.log_runtime(
            f"`generate_az_spectra_single_freq` for Frequency {freq}"
        ):
            generate_az_spectra_single_freq(
                product=product,
                freq=freq,
                params=params,
                stats_h5=stats_h5,
                report_pdf=report_pdf,
            )


def generate_az_spectra_single_freq(
    product: nisarqa.RSLC,
    freq: str,
    params: nisarqa.AzimuthSpectraParamGroup,
    stats_h5: h5py.File,
    report_pdf: PdfPages,
) -> None:
    """
    Generate the RSLC Azimuth Spectra for a single frequency.

    Generate the RSLC Azimuth Spectra; save the plots to the PDF and
    statistics to the .h5 file. An azimuth spectra plot is computed for
    each of three subswaths: near range, mid range, and far range.
    The size of the subswaths is specified in `params`; the azimuth spectra
    are formed by averaging the contiguous range samples in each subswath.

    Power Spectral Density (PSD) is computed in decibels referenced to
    1/hertz (dB re 1/Hz) units, and Frequency in Hz or MHz (specified
    per `params.hz_to_mhz`).

    Parameters
    ----------
    product : nisarqa.RSLC
        Input RSLC product.
    freq : str
        Frequency name for the azimuth power spectra to be processed,
        e.g. 'A' or 'B'
    params : AzimuthSpectraParamGroup
        A structure containing the parameters for processing
        and outputting the spectra.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the spectra plots plot to.
    """
    log = nisarqa.get_logger()
    log.info(f"Generating Azimuth Power Spectra for Frequency {freq}...")

    # Plot the az spectra using strictly increasing sample frequencies
    # (no discontinuity).
    fft_shift = True

    # TODO: Consider breaking this out into a separate function that returns
    # fft_freqs and fft freq units
    # Get the FFT spacing (will be the same for all product images):

    # Compute the sample rate
    # zero doppler time is in seconds; units for `sample_rate` will be Hz
    da = product.get_zero_doppler_time_spacing()
    sample_rate = 1 / da

    # Get the number of range lines
    first_pol = product.get_pols(freq=freq)[0]
    with product.get_raster(freq, first_pol) as img:
        num_range_lines = img.data.shape[0]

    # Compute fft_freqs
    fft_freqs = nisarqa.generate_fft_freqs(
        num_samples=num_range_lines,
        sampling_rate=sample_rate,
        fft_shift=fft_shift,
    )

    if params.hz_to_mhz:
        fft_freqs = nisarqa.hz2mhz(fft_freqs)

    abbreviated_units, hdf5_units = _get_units_hz_or_mhz(params.hz_to_mhz)

    # Save x-axis values to stats.h5 file
    grp_path = nisarqa.STATS_H5_QA_DATA_GROUP % product.band
    ds_name = "azimuthSpectraFrequencies"
    if f"{grp_path}/{ds_name}" not in stats_h5:
        nisarqa.create_dataset_in_h5group(
            h5_file=stats_h5,
            grp_path=grp_path,
            ds_name=ds_name,
            ds_data=fft_freqs,
            ds_units=hdf5_units,
            ds_description=(
                f"Frequency coordinates for azimuth power spectra."
            ),
        )

    # Plot the Azimuth Power Spectra for each pol+subswath onto the same axes
    fig, all_axes = plt.subplots(
        nrows=3, ncols=1, figsize=nisarqa.FIG_SIZE_THREE_PLOTS_PER_PAGE_STACKED
    )

    ax_near, ax_mid, ax_far = all_axes

    fig.suptitle(f"Azimuth Power Spectra for Frequency {freq}")

    # Use custom cycler for accessibility
    for ax in all_axes:
        ax.set_prop_cycle(nisarqa.CUSTOM_CYCLER)

    az_spec_units_pdf = "dB re 1/Hz"
    az_spec_units_hdf5 = "decibel re 1/hertz"

    # We want the y-axis label limits to be consistent for all three plots.
    # Initialize variables to track the limits.
    y_min = np.nan
    y_max = np.nan

    for pol in product.get_pols(freq):
        with product.get_raster(freq=freq, pol=pol) as img:

            for subswath, ax in zip(("Near", "Mid", "Far"), all_axes):
                img_width = np.shape(img.data)[1]
                num_col = params.num_columns

                # Get the start and stop column index for each subswath.
                if (num_col == -1) or (num_col >= img_width):
                    col_slice = slice(0, img_width)
                else:
                    if subswath == "Near":
                        col_slice = slice(0, num_col)
                    elif subswath == "Far":
                        col_slice = slice(img_width - num_col, img_width)
                    else:
                        assert subswath == "Mid"
                        mid_img = img_width // 2
                        mid_num_col = num_col // 2
                        start_idx = mid_img - mid_num_col
                        col_slice = slice(start_idx, start_idx + num_col)

                with nisarqa.log_runtime(
                    f"`compute_az_spectra_by_tiling` for Frequency {freq},"
                    f" Polarization {pol}, {subswath}-Range subswath"
                    f" (columns [{col_slice.start}:{col_slice.stop}],"
                    f" step={1 if col_slice.step is None else col_slice.step})"
                    f" using tile width {params.tile_width}"
                ):
                    # The returned array is in dB re 1/Hz
                    az_spectrum = nisarqa.compute_az_spectra_by_tiling(
                        arr=img.data,
                        sampling_rate=sample_rate,
                        subswath_slice=col_slice,
                        tile_width=params.tile_width,
                        fft_shift=fft_shift,
                    )

                # Save normalized power spectra values to stats.h5 file
                nisarqa.create_dataset_in_h5group(
                    h5_file=stats_h5,
                    grp_path=img.stats_h5_group_path,
                    ds_name=f"azimuthPowerSpectralDensity{subswath}Range",
                    ds_data=az_spectrum,
                    ds_units=az_spec_units_hdf5,
                    ds_description=(
                        "Normalized azimuth power spectral density for"
                        f" Frequency {freq}, Polarization {pol}"
                        f" {subswath}-Range."
                    ),
                    ds_attrs={
                        "subswathStartIndex": col_slice.start,
                        "subswathStopIndex": col_slice.stop,
                    },
                )

                # Add this power spectrum to the figure
                ax.plot(fft_freqs, az_spectrum, label=pol)
                ax.grid(visible=True)

                y_ax_min, y_ax_max = ax.get_ylim()
                y_min = np.nanmin([y_min, y_ax_min])
                y_max = np.nanmax([y_max, y_ax_max])

                # Label the Plot
                ax.set_title(
                    f"{subswath}-Range (columns {col_slice.start}-{col_slice.stop})",
                    fontsize=9,
                )

    # All axes can share the same y-label. Attach that label to the middle
    # axes, so that it is centered.
    ax_mid.set_ylabel(f"Power Spectral Density ({az_spec_units_pdf})")

    ax_near.xaxis.set_ticklabels([])
    ax_mid.xaxis.set_ticklabels([])
    ax_far.set_xlabel(f"Frequency ({abbreviated_units})")

    # Make the y axis labels consistent
    for ax in all_axes:
        ax.set_ylim([y_min, y_max])

    ax_near.legend(loc="upper right")

    # Save complete plots to graphical summary pdf file
    report_pdf.savefig(fig)

    # Close the plot
    plt.close()

    log.info(f"Azimuth Power Spectra for Frequency {freq} complete.")


__all__ = nisarqa.get_all(__name__, objects_to_skip)
