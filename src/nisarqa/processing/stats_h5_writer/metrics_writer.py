from __future__ import annotations

import h5py

import nisarqa

objects_to_skip = nisarqa.get_all(__name__)


def save_percent_nan_to_stats_h5(
    percentage: float, stats_h5: h5py.File, grp_path: str
) -> None:
    """
    Save the percent of NaN pixels to a Dataset named "percentNan".

    Parameters
    ----------
    percentage : float
        Percentage of a raster that is NaN.
    h5_file : h5py.File
        HDF5 File handle to save this dataset to.
    grp_path : str
        Path to h5py Group to add the dataset and attributes to.
    """
    nisarqa.verify_valid_percent(percentage)

    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=grp_path,
        ds_name="percentNan",
        ds_data=percentage,
        ds_units="1",
        ds_description="Percent of dataset elements with a NaN value.",
    )


def save_percent_inf_to_stats_h5(
    percentage: float, stats_h5: h5py.File, grp_path: str
) -> None:
    """
    Save the percent of +/- Inf pixels to a Dataset named "percentInf".

    Parameters
    ----------
    percentage : float
        Percentage of a raster that is +/- Inf.
    h5_file : h5py.File
        HDF5 File handle to save this dataset to.
    grp_path : str
        Path to h5py Group to add the dataset and attributes to.
    """
    nisarqa.verify_valid_percent(percentage)

    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=grp_path,
        ds_name="percentInf",
        ds_data=percentage,
        ds_units="1",
        ds_description="Percent of dataset elements with a +/- inf value.",
    )


def save_percent_fill_to_stats_h5(
    percentage: float,
    fill_value: int | float | complex,
    stats_h5: h5py.File,
    grp_path: str,
) -> None:
    """
    Save the percent of fill pixels to a Dataset named "percentFill".

    Note: By QA convention, if the fill value is NaN, it's ok that
    this check is redundant to the % NaN value metrics.

    Parameters
    ----------
    percentage : float
        Percentage of a raster that is fill value.
    fill_value : int, float, or complex
        The fill value for the raster. (Will be used for description.)
    h5_file : h5py.File
        HDF5 File handle to save this dataset to.
    grp_path : str
        Path to h5py Group to add the dataset and attributes to.
    """
    nisarqa.verify_valid_percent(percentage)

    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=grp_path,
        ds_name="percentFill",
        ds_data=percentage,
        ds_units="1",
        ds_description=(
            "Percent of dataset elements containing the fill value, which"
            f" is: {fill_value}."
        ),
    )


def save_percent_near_zero_to_stats_h5(
    percentage: float, epsilon: float, stats_h5: h5py.File, grp_path: str
) -> None:
    """
    Save the percent of near-zero pixels to a Dataset named "percentNearZero".

    Parameters
    ----------
    percentage : float
        Percentage of a raster that is fill value.
    epsilon : float
        Absolute tolerance that was used for determining if a raster pixel
        was 'almost zero'.
    h5_file : h5py.File
        HDF5 File handle to save this dataset to.
    grp_path : str
        Path to h5py Group to add the dataset and attributes to.
    """
    nisarqa.verify_valid_percent(percentage)

    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=grp_path,
        ds_name="percentNearZero",
        ds_data=percentage,
        ds_units="1",
        ds_description=(
            f"Percent of dataset elements that are within {epsilon} of zero."
        ),
    )


def save_percent_total_invalid_to_stats_h5(
    percentage: float, stats_h5: h5py.File, grp_path: str, zero_is_invalid: bool
) -> None:
    """
    Save the percent of total invalid pixels to a Dataset named "percentTotalInvalid".

    Invalid pixels include NaN, Inf, fill, or (optionally) near-zero valued
    pixels.

    Parameters
    ----------
    percentage : float
        Percentage of a raster that is invalid pixels.
    h5_file : h5py.File
        HDF5 File handle to save this dataset to.
    grp_path : str
        Path to h5py Group to add the dataset and attributes to.
    zero_is_invalid : bool
        True if near-zero pixels were included in the
        total number of invalid pixels. False if they were excluded.
        (This will impact the description for the Dataset.)
    """
    nisarqa.verify_valid_percent(percentage)

    if zero_is_invalid:
        msg = (
            "Percent of dataset elements that are either NaN, Inf, fill,"
            " or near-zero valued pixels."
        )
    else:
        msg = (
            "Percent of dataset elements that are either NaN, Inf, or fill"
            " valued pixels. (Near-zero valued pixels are not included.)"
        )

    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=grp_path,
        ds_name="percentTotalInvalid",
        ds_data=percentage,
        ds_units="1",
        ds_description=msg,
    )


def _percent_value_is_within_threshold(
    name_of_value: str,
    count: int,
    arr_size: int,
    threshold_percentage: float,
    arr_name: str,
) -> tuple[bool, float]:
    """
    Check if a percentage is within threshold; note in log.

    The percentage of the array that is considered to be `name_of_value`
    is computed by `count / arr_size`.

    Parameters
    ----------
    name_of_value : str
        Name of the metric being checked, e.g. "NaN" or "+/- Inf". This will
        be used for the log messages.
    count : int
        Number of pixels that are `name_of_value`.
    arr_size : int
        Total size of array.
    threshold_percentage : float
        Percentage of a raster that is okay to be `name_of_value`.
        If `percentage` is greater than `threshold_percentage`,
        it will be logged as an error. A threshold value of -1 indicates
        to always log as info (not as an error), and `passes_metric` will
        always return `True`.
    arr_name : str
        Name of the array; will be used in log messages and similar.

    Returns
    -------
    passes_metric : bool
        True if the percentage is within acceptable limits. False if not.
    percentage : float
        Percentage of a raster that is `name_of_value`.
    """
    log = nisarqa.get_logger()

    percentage = count / arr_size * 100

    nisarqa.verify_valid_percent(percentage)

    msg = (
        f"Array {arr_name} contains {count}/{arr_size} ({percentage:.2f}%)"
        f" {name_of_value} pixels."
    )

    if threshold_percentage != -1:
        nisarqa.verify_valid_percent(threshold_percentage)
        msg += (
            f" Acceptable threshold is {threshold_percentage} percent"
            f" {name_of_value}"
        )

    if (percentage > threshold_percentage) and (threshold_percentage != -1):
        log.error(msg)
        passes_metric = False
    else:
        log.info(msg)
        passes_metric = True

    return passes_metric, percentage


def percent_nan_is_within_threshold(
    count: int,
    arr_size: int,
    threshold_percentage: float,
    arr_name: str,
) -> tuple[bool, float]:
    """
    Check if % of NaN values is within threshold; note in log and summary CSV.

    Parameters
    ----------
    count : int
        Number of pixels that are NaN-valued.
    arr_size : int
        Total size of array.
    threshold_percentage : float
        Percentage of a raster that is okay to be NaN.
        If `percentage` is greater than `threshold_percentage`,
        it will be logged as an error. A threshold value of -1 indicates
        to always log as info (not as an error), and `passes_metric` will
        always return `True`.
    arr_name : str
        Name of the array; will be used in log messages and similar.

    Returns
    -------
    passes_metric : bool
        True if the percentage is within acceptable limits. False if not.
    percentage : float
        Percentage of a raster that is NaN.
    """
    passes_metric, percentage = _percent_value_is_within_threshold(
        name_of_value="NaN",
        count=count,
        arr_size=arr_size,
        threshold_percentage=threshold_percentage,
        arr_name=arr_name,
    )

    if threshold_percentage != -1:
        summary_threshold = str(threshold_percentage)
    else:
        summary_threshold = ""

    nisarqa.get_summary().check_nan_pixels_within_threshold(
        result="PASS" if passes_metric else "FAIL",
        threshold=summary_threshold,
        actual=f"{percentage:.2f}",
        notes=arr_name,
    )

    return passes_metric, percentage


def percent_inf_is_within_threshold(
    count: int,
    arr_size: int,
    threshold_percentage: float,
    arr_name: str,
) -> tuple[bool, float]:
    """
    Check if % of +/- Inf values is within threshold; note in log.

    Parameters
    ----------
    count : int
        Number of pixels that are +/- Inf.
    arr_size : int
        Total size of array.
    threshold_percentage : float
        Percentage of a raster that is okay to be +/- Inf.
        If `percentage` is greater than `threshold_percentage`,
        it will be logged as an error. A threshold value of -1 indicates
        to always log as info (not as an error), and `passes_metric` will
        always return `True`.
    arr_name : str
        Name of the array; will be used in log messages and similar.

    Returns
    -------
    passes_metric : bool
        True if the percentage is within acceptable limits. False if not.
    percentage : float
        Percentage of a raster that is +/- Inf.
    """
    return _percent_value_is_within_threshold(
        name_of_value="+/- Inf",
        count=count,
        arr_size=arr_size,
        threshold_percentage=threshold_percentage,
        arr_name=arr_name,
    )


def percent_fill_is_within_threshold(
    count: int,
    arr_size: int,
    threshold_percentage: float,
    fill_value: int | float | complex,
    arr_name: str,
) -> tuple[bool, float]:
    """
    Check if % of fill values is within threshold; note in log.

    Parameters
    ----------
    count : int
        Number of pixels that are fill-valued.
    arr_size : int
        Total size of array.
    threshold_percentage : float
        Percentage of a raster that is okay to be fill.
        If `percentage` is greater than `threshold_percentage`,
        it will be logged as an error. A threshold value of -1 indicates
        to always log as info (not as an error), and `passes_metric` will
        always return `True`.
    fill_value : int or float or complex
        The fill value for the raster. (Will be used for description.)
    arr_name : str
        Name of the array; will be used in log messages and similar.

    Returns
    -------
    passes_metric : bool
        True if the percentage is within acceptable limits. False if not.
    percentage : float
        Percentage of a raster that is fill.
    """

    return _percent_value_is_within_threshold(
        name_of_value=f"fill value (fill value is `{fill_value}`)",
        count=count,
        arr_size=arr_size,
        threshold_percentage=threshold_percentage,
        arr_name=arr_name,
    )


def percent_near_zero_is_within_threshold(
    count: int,
    arr_size: int,
    threshold_percentage: float,
    arr_name: str,
) -> tuple[bool, float]:
    """
    Check if % of near-zero values is within threshold; note in log.

    Parameters
    ----------
    count : int
        Number of pixels that are near-zero valued.
    arr_size : int
        Total size of array.
    threshold_percentage : float
        Percentage of a raster that is okay to be near-zero.
        If `percentage` is greater than `threshold_percentage`,
        it will be logged as an error. A threshold value of -1 indicates
        to always log as info (not as an error), and `passes_metric` will
        always return `True`.
    arr_name : str
        Name of the array; will be used in log messages and similar.

    Returns
    -------
    passes_metric : bool
        True if the percentage is within acceptable limits. False if not.
    percentage : float
        Percentage of a raster that is near-zero.
    """

    return _percent_value_is_within_threshold(
        name_of_value="near-zero",
        count=count,
        arr_size=arr_size,
        threshold_percentage=threshold_percentage,
        arr_name=arr_name,
    )


def percent_total_invalid_is_within_threshold(
    count: int,
    arr_size: int,
    threshold_percentage: float,
    arr_name: str,
    zero_is_invalid: bool,
) -> tuple[bool, float]:
    """
    Check if % of total invalid values is within threshold; note in log.

    Invalid pixels include NaN, Inf, fill, or (optionally) near-zero valued
    pixels.

    Parameters
    ----------
    count : int
        Number of pixels that are invalid.
    arr_size : int
        Total size of array.
    threshold_percentage : float
        Percentage of a raster that is okay to be invalid.
        If `percentage` is greater than `threshold_percentage`,
        it will be logged as an error. A threshold value of -1 indicates
        to always log as info (not as an error), and `passes_metric` will
        always return `True`.
    arr_name : str
        Name of the array; will be used in log messages and similar.
    zero_is_invalid : bool
        True if near-zero pixels were included in the
        total number of invalid pixels. False if they were excluded.
        (This will impact the description for the Dataset.)

    Returns
    -------
    passes_metric : bool
        True if the percentage is within acceptable limits. False if not.
    percentage : float
        Percentage of a raster that is invalid.
    """

    if zero_is_invalid:
        msg = "NaN, Inf, fill, or near-zero"
    else:
        msg = "NaN, Inf, or fill-valued"

    passes_metric, percentage = _percent_value_is_within_threshold(
        name_of_value=f"invalid ({msg})",
        count=count,
        arr_size=arr_size,
        threshold_percentage=threshold_percentage,
        arr_name=arr_name,
    )

    # Note the metrics in the SUMMARY CSV
    if threshold_percentage == -1:
        summary_threshold = ""
    else:
        summary_threshold = str(threshold_percentage)

    nisarqa.get_summary().check_invalid_pixels_within_threshold(
        result="PASS" if passes_metric else "FAIL",
        threshold=summary_threshold,
        actual=f"{percentage:.2f}",
        notes=arr_name,
    )

    return passes_metric, percentage


def get_stats_name_descr(stat: str, component: str | None) -> tuple[str, str]:
    """
    Return name and description for a min/max/mean/std metric for the STATS.h5.

    Parameters
    ----------
    stat : str
        One of {"min", "max", "mean", "std"}.
    component : str or None
        One of "real", "imag", or None.
        Per ISCE3 convention, for complex-valued data, the statistics
        should be computed independently for the real component and
        for the imaginary component of the data.
        If the source dataset is real-valued, set this to None.
        If the source dataset is complex-valued, set this to "real" for the
        real-valued component's name and description, or set to "imag"
        for the imaginary component's name and description.

    Returns
    -------
    name, description : str, str
        Official name and description (respectively) for the requested stat.
    """
    # Per ISCE3 R4 conventions, for floating-point datasets, use:
    #     min_value
    #     mean_value
    #     max_value
    #     sample_stddev

    # For complex-valued dataset, use:
    #     min_real_value
    #     mean_real_value
    #     max_real_value
    #     sample_stddev_real
    #     min_imag_value
    #     mean_imag_value
    #     max_imag_value
    #     sample_stddev_imag

    stat_opts = ("min", "max", "mean", "std")
    if stat not in stat_opts:
        raise ValueError(f"{stat=!r}, must be one of {stat_opts}.")

    if (component is not None) and (component not in ("real", "imag")):
        raise ValueError(f"`{component=!r}, must be 'real', 'imag', or None.")

    if component is None:
        if stat == "min":
            return "min_value", "Minimum value of the numeric data points"
        if stat == "max":
            return "max_value", "Maximum value of the numeric data points"
        if stat == "mean":
            return "mean_value", "Arithmetic average of the numeric data points"
        if stat == "std":
            return (
                "sample_stddev",
                "Standard deviation of the numeric data points",
            )

    # Complex data
    if component == "real":
        short_name = "real"
        long_name = "real"
    else:
        assert component == "imag"
        short_name = "imag"
        long_name = "imaginary"

    if stat == "min":
        return (
            f"min_{short_name}_value",
            (
                f"Minimum value of the {long_name} component of the"
                " numeric data points"
            ),
        )
    if stat == "max":
        return (
            f"max_{short_name}_value",
            (
                f"Maximum value of the {long_name} component of the"
                " numeric data points"
            ),
        )
    if stat == "mean":
        return (
            f"mean_{short_name}_value",
            (
                f"Arithmetic average of the {long_name} component of the"
                " numeric data points"
            ),
        )
    if stat == "std":
        return (
            f"sample_stddev_{short_name}",
            (
                f"Standard deviation of the {long_name} component"
                " of the numeric data points"
            ),
        )


def copy_non_insar_imagery_metrics(
    product: nisarqa.NonInsarProduct, stats_h5: h5py.File
) -> None:
    """
    Copy min/max/mean/std metrics of freq+pol imagery layers to QA HDF5.

    This function accommodates both real and complex datasets.

    Parameters
    ----------
    product : nisarqa.NonInsarProduct
        Input NISAR product.
    stats_h5 : h5py.File
        Handle to an HDF5 file where the metrics should be saved.
    """
    log = nisarqa.get_logger()

    for freq in product.freqs:
        for pol in product.get_pols(freq=freq):
            with product.get_raster(freq=freq, pol=pol) as img:
                dest_path = (
                    f"{nisarqa.STATS_H5_QA_FREQ_GROUP % (product.band, freq)}"
                    f"/{pol}"
                )

                for m in ("min", "max", "mean", "std"):
                    metrics = []
                    if img.is_complex:
                        for component in ("real", "imag"):
                            # get tuple of (val, name, descr)
                            val_name_descr = img.get_stat_val_name_descr(
                                stat=m, component=component
                            )
                            metrics.append(val_name_descr)
                    else:
                        # get tuple of (val, name, descr)
                        val_name_descr = img.get_stat_val_name_descr(stat=m)
                        metrics.append(val_name_descr)

                    for val, name, descr in metrics:
                        if val is not None:
                            # XXX: This will create a dataset with a snake_case name,
                            # which differs from the usual camelCase naming convention,
                            # but matches the name of the attribute in the input
                            # product.
                            nisarqa.create_dataset_in_h5group(
                                h5_file=stats_h5,
                                grp_path=dest_path,
                                ds_name=name,
                                ds_data=val,
                                ds_description=descr,
                                ds_units=img.units,
                            )
                        else:
                            log.error(
                                f"Attribute `{name}` is missing or has no"
                                f" value. Dataset: {img.name}"
                            )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
