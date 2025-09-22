from __future__ import annotations

from collections.abc import Sequence

import h5py
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from numpy.typing import ArrayLike

import nisarqa

objects_to_skip = nisarqa.get_all(__name__)


def arr2pow(arr):
    """
    Compute power in linear units of the input array.

    Power is computed as magnitude squared.

    Parameters
    ----------
    arr : array_like
        Input array.

    Returns
    -------
    power : numpy.ndarray
        Power of input array, with the same shape as the input.
    """

    power = np.abs(arr) ** 2

    return power


def amp2db(amp: ArrayLike) -> np.ndarray:
    """
    Convert a root-power quantity from linear units to decibels.

    Parameters
    ----------
    amp : array_like
        Input in linear units.

    Returns
    -------
    db : numpy scalar or numpy.ndarray
        Output in decibels, with the same shape as the input.
    """
    return 20.0 * np.log10(amp)


def pow2db(power):
    """
    Convert a power quantity from linear units to decibels.

    Parameters
    ----------
    power : array_like
        Input in linear units.

    Returns
    -------
    power_db : numpy scalar or numpy.ndarray
        Output in decibels, with the same shape as the input.
    """
    return 10.0 * np.log10(power)


def nearest_odd_int(k):
    """Compute the nearest odd integer to `k`"""
    result = int(np.floor(k))
    if result % 2 == 0:
        result = result + 1

    # Sanity Check
    assert result % 2 == 1, print("the result should be an odd value.")
    assert isinstance(result, int), print("the result should be an integer.")

    return result


def counts2density(counts, bins):
    """
    Compute the probability density for the given counts and bins.

    This function implements numpy.histogram's 'density' parameter.
    Each bin will display the bin's raw count divided by the
    total number of counts and the bin width
    (density = counts / (sum(counts) * np.diff(bins))),
    so that the area under the histogram integrates to 1
    (np.sum(density * np.diff(bins)) == 1).

    Parameters
    ----------
    counts : array_like
        The values of the histogram bins, such as returned from np.histogram.
        This is an array of length (len(bins) - 1).
    bins : array_like
        The edges of the bins. Length is the number of bins + 1,
        i.e. len(counts) + 1.

    Returns
    -------
    density : numpy.ndarray
        Each bin will contain that bin's density (as described above),
        so that the area under the histogram integrates to 1.
    """

    # Formula per numpy.histogram's documentation:
    density = counts / (np.sum(counts) * np.diff(bins))

    # Sanity check
    actual = np.sum(density * np.diff(bins))
    assert np.abs(actual - 1) < 1e-6

    return density


def normalize(
    arr: ArrayLike, min_max: Sequence[float] | None = None
) -> np.ndarray:
    """
    Normalize input array to range [0,1], ignoring any NaN values.

    Parameters
    ----------
    arr : array_like
        Input array to be normalized
    min_max : pair of numeric or None, optional
        Defaults to None, which means that `arr`'s min and max will be
        computed and used for normalization. (This is most common.)
        If provided, the normalization computation will use `min_max` as
        the range which determines the scaling to [0,1].
        Format: [<minimum>, <maximum>]

    Returns
    -------
    normalized_arr : numpy.ndarray
        A normalized copy of `arr`.
    """
    arr = np.asanyarray(arr)

    if min_max is None:
        arr_min = np.nanmin(arr)
        arr_max = np.nanmax(arr)
    else:
        if min_max[0] >= min_max[1]:
            raise ValueError(
                f"{min_max=}, but min_max[0] must be less than min_max[1]"
            )
        arr_min = min_max[0]
        arr_max = min_max[1]

    return (arr - arr_min) / (arr_max - arr_min)


def compute_fft(slc_arr: ArrayLike, axis: int = 1) -> np.ndarray:
    """
    Compute FFT of the input array along the given axis.

    Non-finite values in `slc_arr` will be filled with zero.
    No normalization will be applied.

    Parameters
    ----------
    slc_arr : array_like
        Input SLC array
    axis : int, optional
        Axis along which to take the FFT. Default is axis = 1.
        (For NISAR, axis 1 is the range axis, and axis 0 is the azimuth axis.)

    Returns
    -------
    fft : numpy.ndarray
        The FFT of `slc_arr` along `axis`. Non-finite values filled with zero.

    Notes
    -----
    Similar to ISCE3, non-finite values in `slc_arr` will be filled with zeros.
    An alternative would be to implement non-equispace FFT's, but that could be
    too computationally and algorithmically complicated for the QA Code.
    """

    finite_slc_arr = np.where(np.isfinite(slc_arr), slc_arr, 0.0)

    fft = np.fft.fft(finite_slc_arr, axis=axis)

    return fft


def generate_fft_freqs(
    num_samples: int, sampling_rate: float, fft_shift: bool = True
) -> np.ndarray:
    """
    Return the Discrete Fourier Transform sample frequencies.

    Parameters
    ----------
    num_samples : int
        Window length.
    sampling_rate : numeric
        Sample rate (inverse of the sample spacing).
    fft_shift : bool, optional
        True to have the frequencies in `fft_freqs` be continuous from
        negative (min) -> positive (max) values.

        False to leave `fft_freqs` as the output from `numpy.fft.fftfreq()`,
        where this discrete FFT operation orders values
        from 0 -> max positive -> min negative -> 0- . (This creates
        a discontinuity in the interval's values.)

        Defaults to True.

    Returns
    -------
    fft_freqs : numpy.ndarray
        Array of length `num_samples` containing the sample frequencies
        (frequency bin centers) in the same units as `sampling_rate`.
        For instance, if the sampling rate is in Hz, then the frequency
        unit is also cycles/second.
    """
    fft_freqs = np.fft.fftfreq(num_samples, 1.0 / sampling_rate)

    if fft_shift:
        # Shift fft_freqs to be continuous from
        # negative (min) -> positive (max) values.
        # (The output from the discrete FFT operation orders values
        # from 0 -> max positive -> min negative -> 0- .
        # Doing this will remove that discontinuity.)
        fft_freqs = np.fft.fftshift(fft_freqs)

    return fft_freqs


def hz2mhz(arr: np.ndarray) -> np.ndarray:
    """Convert input array from Hz to MHz."""
    return arr * 1.0e-06


def compute_and_save_basic_statistics(
    raster: nisarqa.Raster,
    stats_h5: h5py.File,
    params: nisarqa.ThresholdParamGroup,
) -> None:
    """
    Compute and save min, max, mean, std, % nan, % zero, % fill, % inf to HDF5.

    Parameters
    ----------
    raster : nisarqa.Raster
        Input Raster.
    stats_h5 : h5py.File
        The output file to save QA metrics to.
    params : nisarqa.ThresholdParamGroup
        A structure containing the parameters for checking the percentage
        of invalid pixels in a raster.

    Warnings
    --------
    The entire input array will be read into memory and processed.
    Only use this function for small datasets.

    Notes
    -----
    If the fill value is set to None in the input *Raster, that field will
    not be computed nor included in the STATS.h5 file.
    """
    arr = raster.data
    units = raster.units
    grp_path = raster.stats_h5_group_path
    fill_value = raster.fill_value

    # Step 1: Compute min/max/mean/STD
    # TODO: refactor aka redesign this code chunk.

    def _compute_min_max_mean_std(
        arr: np.ndarray, component: str | None
    ) -> None:
        """
        Compute min, max, mean, and samples standard deviation; save to HDF5.

        Parameters
        ----------
        arr : numpy.ndarray
            The input array to have statistics run on. Note: If `arr` has a
            complex dtype, this function will need to access the `arr.real`
            and `arr.imag` parts separately. Unfortunately, h5py.Dataset
            instances do not allow access to these parts using that syntax,
            so to be safe, please pass in a Numpy array.
        component : str or None
            One of "real", "imag", or None.
            Per ISCE3 convention, for complex-valued data, the statistics
            should be computed independently for the real component and
            for the imaginary component of the data.
            If the source dataset is real-valued, set this to None.
            If the source dataset is complex-valued, set this to "real" for the
            real-valued component's name and description, or set to "imag"
            for the imaginary component's name and description.

        Notes
        -----
        TODO: This is a clunky, kludgy function. When these statistics get
        implemented for RSLC, GSLC, and GCOV after R4, the developer
        should consider pulling this function out into a standalone function.
        For expediency, for R4, all InSAR products will use this function,
        so this information can live here.
        """
        if (component is not None) and (component not in ("real", "imag")):
            raise ValueError(
                f"`{component=!r}, must be 'real', 'imag', or None."
            )

        # Fill all invalid pixels in array with NaN, to easily compute metrics
        arr_copy = np.where(
            (np.isfinite(arr) & (arr != fill_value)), arr, np.nan
        )

        # Compute min/max/mean/std of valid pixels
        for key, func in [
            ("min", np.nanmin),
            ("max", np.nanmax),
            ("mean", np.nanmean),
            ("std", lambda x: np.nanstd(x, ddof=1)),
        ]:

            name, descr = nisarqa.get_stats_name_descr(
                stat=key, component=component
            )

            nisarqa.create_dataset_in_h5group(
                h5_file=stats_h5,
                grp_path=grp_path,
                ds_name=name,
                ds_data=func(arr_copy),
                ds_units=units,
                ds_description=descr,
            )

    if raster.is_complex:
        # HDF5 Datasets cannot access .real nor .imag, so we need
        # to read the array into a numpy array in memory first.
        _compute_min_max_mean_std(arr[()].real, "real")
        _compute_min_max_mean_std(arr[()].imag, "imag")
    else:
        _compute_min_max_mean_std(arr[()], None)

    # Step 2: Compute % NaN, % Inf, % Fill, % near-zero, % invalid
    compute_percentage_metrics(
        raster=raster,
        stats_h5=stats_h5,
        params=params,
    )


def compute_nan_count(arr: ArrayLike) -> int:
    """
    Get the number of NaN elements in the input array.

    Parameters
    ----------
    arr : array_like
        Input array; can have a real or complex dtype.
        (For complex data, if either the real or imag part is NaN,
        then the element is considered NaN.)

    Returns
    -------
    count : int
        Number of NaN elements in `arr`.
    """
    # np.isnan works for both real and complex data. For complex data, if
    # either the real or imag part is NaN, then the pixel is considered NaN.
    return np.sum(np.isnan(arr))


def compute_inf_count(arr: ArrayLike) -> int:
    """
    Get the number of +/- Inf elements in the input array.

    Parameters
    ----------
    arr : array_like
        Input array; can have a real or complex dtype.
        (For complex data, if either the real or imag part is +/- Inf,
        then the element is considered +/- Inf.)

    Returns
    -------
    count : int
        Number of +/- Inf elements in `arr`.
    """
    # (np.isinf works for both real and complex data. For complex data, if
    # either real or imag part is +/- inf, then the pixel is considered inf.)
    return np.sum(np.isinf(arr))


def compute_fill_count(
    arr: ArrayLike, fill_value: int | float | complex
) -> int:
    """
    Get the number of fill value elements in the input array.

    Parameters
    ----------
    arr : array_like
        Input array.
    fill_value : int or float or complex
        The fill value for `arr`. The type should correspond to dtype of `arr`.

    Returns
    -------
    count : int
        Number of elements in `arr` that are `fill_value`.
    """
    if np.isnan(fill_value):
        # `np.nan == np.nan` evaluates to False, so handle this case here
        return compute_nan_count(arr=arr)

    return np.sum(np.equal(arr, fill_value))


def compute_near_zero_count(arr: ArrayLike, epsilon: float = 1e-6) -> int:
    """
    Get the number of near-zero elements in the input array.

    Parameters
    ----------
    arr : array_like
        Input array; can have a real or complex dtype.
        (For complex data, the magnitude must be ~0.0.)
    epsilon : float, optional
        Absolute tolerance for determining if a raster pixel is 'near zero'.
        Defaults to 1e-6.

    Returns
    -------
    count : int
        Number of near-zero elements in `arr`.
    """
    # By using np.abs(), for complex values this will compute the magnitude.
    return np.sum(np.abs(arr) < epsilon)


def compute_percentage_metrics(
    raster: nisarqa.Raster,
    params: nisarqa.ThresholdParamGroup,
    stats_h5: h5py.File,
) -> None:
    """
    Check % nan, % zero, % fill, % inf, % total invalid; save to HDF5 and CSV.

    Parameters
    ----------
    raster : nisarqa.Raster
        Input Raster.
    params : nisarqa.ThresholdParamGroup
        A structure containing the parameters for checking the percentage
        of invalid pixels in a raster.
    stats_h5 : h5py.File
        The output file to save QA metrics to.

    Warnings
    --------
    The entire input array will be read into memory and processed.
    Only use this function for small datasets.

    Notes
    -----
    If the fill value is set to None in the input *Raster, that field will
    not be computed nor included in the STATS.h5 file.
    """
    # Create flags, to be used for the PASS/FAIL Summary CSV
    all_metrics_pass = True

    # Total number of pixels that were NaN, +/-Inf, fill, or near-zero
    total_num_invalid = 0

    arr = np.asanyarray(raster.data)
    grp_path = raster.stats_h5_group_path
    fill_value = raster.fill_value
    arr_name = raster.name
    arr_size = np.size(arr)

    # Compute NaN value metrics
    num_nan = compute_nan_count(arr)
    total_num_invalid += num_nan

    passes_metric, percent_nan = nisarqa.percent_nan_is_within_threshold(
        count=num_nan,
        arr_size=arr_size,
        threshold_percentage=params.nan_threshold,
        arr_name=arr_name,
    )
    all_metrics_pass &= passes_metric
    nisarqa.save_percent_nan_to_stats_h5(
        percentage=percent_nan, stats_h5=stats_h5, grp_path=grp_path
    )

    # Compute +/- inf metrics.
    num_inf = compute_inf_count(arr)
    total_num_invalid += num_inf

    passes_metric, percent_inf = nisarqa.percent_inf_is_within_threshold(
        count=num_inf,
        arr_size=arr_size,
        threshold_percentage=params.inf_threshold,
        arr_name=arr_name,
    )
    all_metrics_pass &= passes_metric
    nisarqa.save_percent_inf_to_stats_h5(
        percentage=percent_inf, stats_h5=stats_h5, grp_path=grp_path
    )

    # Compute near-zeros metrics.
    num_zero = compute_near_zero_count(arr, epsilon=params.epsilon)
    if params.zero_is_invalid:
        total_num_invalid += num_zero

    passes_metric, percent_zero = nisarqa.percent_near_zero_is_within_threshold(
        count=num_zero,
        arr_size=arr_size,
        threshold_percentage=params.near_zero_threshold,
        arr_name=arr_name,
    )

    all_metrics_pass &= passes_metric
    nisarqa.save_percent_near_zero_to_stats_h5(
        percentage=percent_zero,
        epsilon=params.epsilon,
        stats_h5=stats_h5,
        grp_path=grp_path,
    )

    # Compute fill value metrics. Do not double-count NaNs nor zeros.
    if fill_value is not None:
        fill_is_zero = np.isclose(
            fill_value, 0.0, atol=params.epsilon, rtol=0.0
        )

        if np.isnan(fill_value):
            num_fill = num_nan
            # We already accumulated the number of NaN to `total_num_invalid`,
            # skip doing that here so that we do not double-count the NaN
        elif np.isinf(fill_value):
            num_fill = compute_fill_count(arr, fill_value=fill_value)
            # We already accumulated the number of +/- Inf to `total_num_invalid`,
            # skip doing that here so that we do not double-count them
        elif fill_is_zero:
            num_fill = num_zero
            if not params.zero_is_invalid:
                # Fill values should always be included as invalid pixels.
                total_num_invalid += num_zero
        else:
            num_fill = compute_fill_count(arr, fill_value=fill_value)
            total_num_invalid += num_fill

        passes_metric, percent_fill = nisarqa.percent_fill_is_within_threshold(
            count=num_fill,
            arr_size=arr_size,
            threshold_percentage=params.fill_threshold,
            fill_value=fill_value,
            arr_name=arr_name,
        )

        all_metrics_pass &= passes_metric
        nisarqa.save_percent_fill_to_stats_h5(
            percentage=percent_fill,
            fill_value=fill_value,
            stats_h5=stats_h5,
            grp_path=grp_path,
        )

    # Compute cumulative total invalid pixels
    assert total_num_invalid <= arr_size

    passes_metric, percent_invalid = (
        nisarqa.percent_total_invalid_is_within_threshold(
            count=total_num_invalid,
            arr_size=arr_size,
            threshold_percentage=params.total_invalid_threshold,
            arr_name=arr_name,
            zero_is_invalid=params.zero_is_invalid,
        )
    )

    all_metrics_pass &= passes_metric
    nisarqa.save_percent_total_invalid_to_stats_h5(
        percentage=percent_invalid,
        stats_h5=stats_h5,
        grp_path=grp_path,
        zero_is_invalid=params.zero_is_invalid,
    )

    # Now, all metrics have been computed and logged. Raise exception
    # if an issue was identified.
    if not all_metrics_pass:
        msg = (
            f"Array {arr_name} did not pass at least one of the percentage"
            " threshold metrics; either the % Nan, % Inf, % 'fill', % near-zero"
            " and/or % total invalid pixels was greater than its requested"
            " threshold. See the log for details."
        )

        raise nisarqa.InvalidRasterError(msg)


def get_unique_elements_and_percentages(
    arr: ArrayLike,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Return the sorted unique elements of an array and the percentage they occur.

    Parameters
    ----------
    arr : array_like
        Input array.

    Returns
    -------
    unique_values : numpy.ndarray
        1D array of the sorted unique values in `arr`.
    percentages : numpy.ndarray
        1D array of the relative frequency that each of the unique values in
        `unique_values` occurs in `arr`, as a percentage of the total array
        size. Elements in `percentages` correspond to the elements in
        `unique_values`.
    """

    unique_values, counts = np.unique(arr, return_counts=True)

    percentages = (counts / np.size(arr)) * 100.0

    return unique_values, percentages


def connected_components_metrics(
    cc_raster: nisarqa.RadarRaster | nisarqa.GeoRaster,
    stats_h5: PdfPages,
    max_num_cc: int | None = None,
) -> None:
    """
    Compute metrics specific to Connected Components; save to HDF5 and CSV.

    Parameters
    ----------
    raster : nisarqa.Raster
        Input Raster.
    stats_h5 : h5py.File
        The output file to save QA metrics to.
    max_num_cc : int or None, optional
        Maximum number of valid connected components allowed.
        If the number of valid connected components (not including
        zero nor the fill value) is greater than this value,
        it will be recorded in the summary file and an exception will be raised.
        If None, this error check will be skipped.
        Defaults to None.

    Warnings
    --------
    The entire input array will be read into memory and processed.
    Only use this function for small datasets.
    """

    log = nisarqa.get_logger()
    grp_path = cc_raster.stats_h5_group_path
    name = cc_raster.name
    fill_value = cc_raster.fill_value

    # Get unique CC labels and the % of area labeled with each.
    labels, percentages = get_unique_elements_and_percentages(
        arr=cc_raster.data[()]
    )

    # Note the CC labels in the log and STATS h5
    log.info(
        f"Raster {cc_raster.name} contains Connected Component labels: {labels}"
    )

    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=grp_path,
        ds_name="connectedComponentLabels",
        ds_data=labels,
        ds_units=None,
        ds_description=(
            "List of all connected component labels, including 0 and"
            f" the fill value `{fill_value}`"
        ),
    )

    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=grp_path,
        ds_name=f"connectedComponentPercentages",
        ds_data=percentages,
        ds_units="1",
        ds_description=(
            "Percentages of total raster area with each connected component"
            " label. Indices correspond to `connectedComponentLabels`"
        ),
    )

    for label, percent in zip(labels, percentages):
        log.info(
            f"Connected Component `{label}` covers {percent} percent of the"
            f" {name} raster."
        )

    # Exclude 0 and the fill value when saving the remaining metrics.
    # For ease, let's simply remove them from the lists.
    labels_list = list(labels)
    percentages_list = list(percentages)

    for label in [0, fill_value]:
        if label in labels_list:
            idx = labels_list.index(label)
            del labels_list[idx]
            del percentages_list[idx]

    num_valid_cc = len(labels_list)
    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=grp_path,
        ds_name="numValidConnectedComponents",
        ds_data=num_valid_cc,
        ds_units="1",
        ds_description=(
            "Number of valid connected components, excluding 0 and"
            f" the fill value `{fill_value}`"
        ),
    )
    log.info(
        f"Raster {name} contains {num_valid_cc} valid connected components"
        f" (excluding 0 and fill value of {fill_value})."
    )

    # Percentage of pixels in largest connected component
    percent_largest_cc = 0.0 if num_valid_cc == 0 else max(percentages_list)
    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=grp_path,
        ds_name="percentPixelsInLargestCC",
        ds_data=percent_largest_cc,
        ds_units="1",
        ds_description=(
            "Percentage of pixels in the largest valid connected component"
            " relative to the total image size. (0"
            f" and fill value ({fill_value}) are not valid connected"
            " components."
        ),
    )

    # Percentage of pixels with non-zero, non-fill connected components
    percent_non_zero_cc = 0.0 if num_valid_cc == 0 else sum(percentages_list)
    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=grp_path,
        ds_name="percentPixelsWithNonZeroCC",
        ds_data=percent_non_zero_cc,
        ds_units="1",
        ds_description=(
            "Percentage of pixels with non-zero, non-fill connected components"
            " relative to the total image size."
            f" (0 and fill value ({fill_value}) are not valid connected"
            " components."
        ),
    )

    # If there are too many connected components, raise an exception.
    if max_num_cc is not None:
        summary = nisarqa.get_summary()
        summary_kwargs = {
            "threshold": max_num_cc,
            "actual": num_valid_cc,
            "notes": name,
        }
        if num_valid_cc > max_num_cc:
            summary.check_connected_components_within_threshold(
                result="FAIL", **summary_kwargs
            )
            msg = (
                f"Raster {name} contains {num_valid_cc} valid connected"
                f" components (excluding 0 and fill value of {fill_value}). It"
                f" is only permitted to contain a max of {max_num_cc} valid"
                " connected components."
            )
            raise ValueError(msg)
        else:
            summary.check_connected_components_within_threshold(
                result="PASS", **summary_kwargs
            )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
