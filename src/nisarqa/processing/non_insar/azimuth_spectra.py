from __future__ import annotations

from typing import Optional

import h5py
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from numpy.typing import ArrayLike

import nisarqa

from ._utils import (
    _get_s_avg_for_tile,
    _get_units_hz_or_mhz,
    _post_process_s_avg,
)

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


def compute_az_spectra_by_tiling(
    arr: ArrayLike,
    sampling_rate: float,
    subswath_slice: Optional[slice] = None,
    tile_width: int = 256,
    fft_shift: bool = True,
) -> np.ndarray:
    """
    Compute normalized azimuth power spectral density in dB re 1/Hz by tiling.

    Parameters
    ----------
    arr : array_like
        Input array, representing a two-dimensional discrete-time signal.
    sampling_rate : numeric
        Azimuth sample rate (inverse of the sample spacing) in Hz.
    subswath_slice : slice or None, optional
        The slice for axes 1 that specifies the columns which define a subswath
        of `arr`; the azimuth spectra will be computed by averaging the
        range samples in this subswath.
            Format: slice(start, stop)
            Example: slice(2, 5)
        If None, or if the number of columns in the subswath is greater than
        the width of the input array, then the full input array will be used.
        Note that all rows will be used to compute the azimuth spectra, so
        there is no need to provide a slice for axes 0.
        Defaults to None.
    tile_width : int, optional
        Tile width (number of columns) for processing each subswath by batches.
        -1 to use the full width of the subswath.
        Defaults to 256.
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
        Normalized azimuth power spectral density in dB re 1/Hz of the
        subswath of `arr` specified by `col_indices`. Azimuth spectra will
        be computed by averaging across columns within the subswath.

    Notes
    -----
    When computing the azimuth spectra, full columns must be read in to
    perform the FFT; this means that the number of rows is always fixed to
    the height of `arr`.

    To reduce processing time, users can decrease the interval of `col_indices`.
    """
    arr_shape = np.shape(arr)
    if len(arr_shape) != 2:
        raise ValueError(
            f"Input array has {len(arr_shape)} dimensions, but must be 2D."
        )

    arr_nrows, arr_ncols = arr_shape

    # Validate column indices
    if subswath_slice is None:
        subswath_slice = np.s_[:]  # equivalent to slice(None, None, None)

    if (subswath_slice.step != 1) and (subswath_slice.step is not None):
        # In theory, having a step size >1 could be supported, but it seems
        # unnecessary and overly complicated to bookkeep for current QA needs.
        msg = (
            "Subswath slice along axes 1 has step value of:"
            f" `{subswath_slice.step}`, which is not supported. Please set"
            " the step value to 1."
        )
        raise NotImplementedError(msg)

    subswath_start, subswath_stop, _ = subswath_slice.indices(arr_ncols)
    subswath_width = subswath_stop - subswath_start

    if (tile_width == -1) or (tile_width > subswath_width):
        tile_width = subswath_width

    # Setup a 2D subblock view of the source array.
    subswath = nisarqa.SubBlock2D(arr=arr, slices=(np.s_[:], subswath_slice))
    assert arr_nrows == subswath.shape[0]
    assert subswath_width == subswath.shape[1]

    # From here on out, we'll treat the `subswath` as if it is our full array.
    # That means are index values will be in `subswath`'s "index
    # coordinate system". (They will no longer be in the "index coordinate
    # system" of the input `arr`.)

    # The TileIterator can only pull full tiles. In other functions, we simply
    # truncate the full array to have each edge be an integer multiple of the
    # tile shape. Here, the user specified an exact number of columns, so we
    # should not truncate.
    # To handle this, let's first iterate over the "truncated" array,
    # and then add in the "leftover" columns.

    # Truncate the column indices to be an integer multiple of `tile_width`.
    leftover_width = subswath_width % tile_width
    trunc_width = subswath_width - leftover_width

    # Create the Iterator over the truncated subswath array
    input_iter = nisarqa.TileIterator(
        arr_shape=(arr_nrows, trunc_width),
        axis_0_tile_dim=-1,  # use all rows
        axis_1_tile_dim=tile_width,
    )

    # Initialize the accumulator array
    S_avg = np.zeros(arr_nrows)

    # Compute FFT over the truncated portion of the subswath
    for tile_slice in input_iter:
        S_avg += _get_s_avg_for_tile(
            arr_slice=subswath[tile_slice],
            fft_axis=0,  # Compute fft over along-track axis (axis 0)
            num_fft_bins=arr_nrows,
            averaging_denominator=subswath_width,  # full subswath (not truncated)
        )

    # Repeat process for the "leftover" portion of the subswath
    if leftover_width > 0:
        leftover_2D_slice = (
            np.s_[:],
            slice(subswath_width - leftover_width, subswath_width),
        )

        leftover_subswath = subswath[leftover_2D_slice]
        S_avg += _get_s_avg_for_tile(
            arr_slice=leftover_subswath,
            fft_axis=0,  # Compute fft over along-track axis (axis 0)
            num_fft_bins=arr_nrows,
            averaging_denominator=subswath_width,
        )

    return _post_process_s_avg(
        S_avg=S_avg, sampling_rate=sampling_rate, fft_shift=fft_shift
    )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
