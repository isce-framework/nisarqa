from __future__ import annotations

import os
from functools import lru_cache
from typing import overload

import h5py
import numpy as np

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


def _get_units(
    ds: h5py.Dataset,
) -> str | None:
    """
    Parse, validate, and return the dataset's units.

    Parameters
    ----------
    ds : h5py.Dataset
        Dataset with an attribute named "units".

    Returns
    -------
    units : str or None
        The contents of the "units" attribute.
        If the attribute does not exist, `None` will be returned.
    """
    log = nisarqa.get_logger()

    # Extract the units attribute
    try:
        units = ds.attrs["units"]
    except KeyError:
        log.error(f"Missing `units` attribute for Dataset: {ds.name}")
        units = None
    else:
        units = nisarqa.byte_string_to_python_str(units)
    if units in ("unitless", "DN"):
        log.error(
            f"{units=}. As of R4, please use the string '1' as the"
            " `units` for numeric but unitless datasets."
        )
        units = "1"

    return units


def _get_fill_value(
    ds: h5py.Dataset,
) -> int | float | complex | None:
    """
    Parse, validate, and return the dataset's fill value.

    Parameters
    ----------
    ds : h5py.Dataset
        Dataset with an attribute named "_FillValue".

    Returns
    -------
    fill_value : int, float, complex, or None
        The contents of the "_FillValue" attribute.
        If that attribute does not exist, `None` is returned.
    """
    # Extract the _FillValue
    try:
        fill_value = ds.attrs["_FillValue"][()]
    except KeyError:
        nisarqa.get_logger().error(
            f"Missing `_FillValue` attribute for Dataset: {ds.name}"
        )
        fill_value = None

    return fill_value


def _get_path_to_nearest_dataset(
    h5_file: h5py.File, starting_path: str, dataset_to_find: str
) -> str:
    """
    Get path to the occurrence of `dataset_to_find` nearest to `starting_path`.

    Walking up each parent directory from right to left, this function
    searches each parent directory in `starting_path` (non-recursive)
    to find the first occurrence of `dataset_to_find`, and then returns
    the full path to that dataset.
    By design, this is not a recursive nor exhaustive search of
    the input file. In many NISAR products, `dataset_to_find` can occur
    in multiple groups, and the goal of this function
    is to find the occurrence of `dataset_to_find` that is in closest
    proximity to the dataset located at `starting_path`.

    Parameters
    ----------
    h5_file : h5py.File
        Handle to the input product HDF5 file.
    starting_path : str
        Path to the starting dataset. This function will iterate up through
        each successive parent directory in `starting_path` to find the first
        occurrence of `dataset_to_find`.
    dataset_to_find : str
        Base name of the dataset to locate in `h5_file`.

    Returns
    -------
    path : str
        Path inside `h5_file` to the requested `dataset_to_find`.

    Raises
    ------
    nisarqa.DatasetNotFoundError
        If `dataset_to_find` is not found.

    Examples
    --------
    Example setup, using an InSAR product

    >>> import h5py
    >>> in_file = h5py.File("RIFG_product.h5", "r")

    Initial path is to a specific raster layer (dataset).

    >>> path = "/science/LSAR/RIFG/swaths/frequencyA/interferogram/HH/wrappedInterferogram"

    First, find the coherence magnitude layer that (likely) corresponds to
    that wrapped interferogram dataset. Since this function searches the
    dataset's parent directory first, it locates the coherence magnitude
    layer inside the same directory as our provided path.

    >>> name = "coherenceMagnitude"
    >>> nisarqa._get_path_to_nearest_dataset(in_file, path, name)
    '/science/LSAR/RIFG/swaths/frequencyA/interferogram/HH/coherenceMagnitude'

    Now, find the "zeroDopplerTime" dataset that corresponds to that layer.
    Note: The located dataset will be one level higher in the directory tree.

    >>> name = "zeroDopplerTime"
    >>> _get_path_to_nearest_dataset(in_file, path, name)
    '/science/LSAR/RIFG/swaths/frequencyA/interferogram/zeroDopplerTime'

    If we provide a path to a different raster in the pixel offsets group,
    but give it the same dataset name to find, the function locates the
    "zeroDopplerTime" dataset which (likely) corresponds to that other layer.

    >>> path2 = "/science/LSAR/RIFG/swaths/frequencyA/pixelOffsets/HH/alongTrackOffset"
    >>> _get_path_to_nearest_dataset(in_file, path2, name)
    '/science/LSAR/RIFG/swaths/frequencyA/pixelOffsets/zeroDopplerTime'

    If a dataset is not found, an error is raised.

    >>> name2 = "zeroDopplerTimeFake"
    >>> path3 = _get_path_to_nearest_dataset(in_file, path2, name2)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File ".../product_reader.py", line 98, in _get_path_to_nearest_dataset
        raise nisarqa.DatasetNotFoundError
    nisarqa.utils.utils.DatasetNotFoundError: Dataset not found.
    """
    path_list = starting_path.split("/")

    # Iterate through each parent directory of the dataset (raster image),
    # starting with the directory that the dataset (raster) itself is inside.
    for i in reversed(range(len(path_list))):
        parent = "/".join(path_list[:i])

        path = f"{parent}/{dataset_to_find}"
        if path in h5_file:
            return path
    else:
        raise nisarqa.DatasetNotFoundError(
            f"`{dataset_to_find}` not found in any of the parent directories of"
            f" {starting_path}."
        )


def _get_paths_in_h5(h5_file: h5py.File, name: str) -> list[str]:
    """
    Return the path(s) to the `name` group or dataset in the input file.

    Parameters
    ----------
    h5_file : h5py.File, h5py.Group
        Handle to HDF5 input file or Group to be searched.
    name : str
        Base Name of a h5py.Dataset or h5py.Group to be located.

    Returns
    -------
    paths : list of str
        List containing the paths to each dataset or group with the
        name `name` in the input file. For example, if `name` is
        "identification", this function could return
        "science/LSAR/identification"].
        If no occurrences are found, returns an empty list.
    """
    paths = []

    def get_path(path: str) -> None:
        """Find all paths to the group or dataset specified."""
        if path.split("/")[-1] == name:
            paths.append(path)

    h5_file.visit(get_path)

    return paths


def _parse_dataset_stats_from_h5(
    ds: h5py.Dataset,
) -> nisarqa.RasterStats | nisarqa.ComplexRasterStats:
    """
    Return the statistics from a Dataset in the input file.

    Parameters
    ----------
    ds : h5py.Dataset
        Handle to HDF5 Dataset. Should contain min/max/mean/std Attributes,
        with Attribute names corresponding to the naming conventions in
        `nisarqa.get_stats_name_descr()`.

    Returns
    -------
    stats : nisarqa.RasterStats or nisarqa.ComplexRasterStats
        Statistics for the input Dataset, parsed from that Dataset's Attributes.
        If a particular statistic is not found, it will be set to None.
        If `ds`'s raster is real-valued, a RadarStats is returned.
        If the raster is complex-valued, a ComplexRadarStats is returned.
    """

    # Helper function to get the value from a Dataset's Attribute
    def _get_attribute_val(attr_name: str) -> float | None:
        if attr_name in ds.attrs:
            return ds.attrs[attr_name]
        else:
            nisarqa.get_logger().warning(
                f"Attribute `{attr_name}` not found in the dataset {ds.name}"
            )
            return None

    # Helper function to construct a RasterStats or ComplexRasterStats object
    # for the input Dataset
    @overload
    def _get_stats_object(component: None) -> nisarqa.RasterStats:
        pass

    @overload
    def _get_stats_object(component: str) -> nisarqa.ComplexRasterStats:
        pass

    def _get_stats_object(component):
        kwargs = {
            f"{stat}_value": _get_attribute_val(
                nisarqa.get_stats_name_descr(stat=stat, component=component)[0]
            )
            for stat in ("min", "max", "mean", "std")
        }

        return nisarqa.RasterStats(**kwargs)

    # Based on the dtype, construct the *RasterStats for the input Dataset
    # Note: Check for `.is_complex32()` first so that code works with h5py<3.8.
    # In older versions of h5py, even accessing ds.dtype will cause a TypeError
    # to be raised if the dataset is complex32.
    if nisarqa.is_complex32(dataset=ds) or np.issubdtype(
        ds.dtype, np.complexfloating
    ):
        real_stats = _get_stats_object(component="real")
        imag_stats = _get_stats_object(component="imag")
        raster_stats = nisarqa.ComplexRasterStats(
            real=real_stats, imag=imag_stats
        )
    else:
        if not nisarqa.has_integer_or_float_dtype(ds):
            raise TypeError(
                f"Dataset has type {type(ds)}, but must be either real-valued"
                f" or complex-valued. Dataset: {ds.name}"
            )
        raster_stats = _get_stats_object(component=None)

    return raster_stats


def _get_dataset_handle(
    h5_file: h5py.File, raster_path: str
) -> h5py.Dataset | nisarqa.ComplexFloat16Decoder:
    """
    Return a handle to the requested Dataset.

    If Dataset is complex32, it will be wrapped with the ComplexFloat16Decoder.

    Parameters
    ----------
    h5_file : h5py.File
        File handle for the input file.
    raster_path : str
        Path in the input file to the desired Dataset.
        Example: "/science/LSAR/RSLC/grids/frequencyA/HH"

    Returns
    -------
    dataset : h5py.Dataset or ComplexFloat16Decoder
        Handle to the requested dataset.

    Notes
    -----
    As of R4.0.2, the baseline is that both RSLC and GSLC produce
    their imagery layers in complex64 (float32+float32) format
    with some bits zeroed out for compression.
    However, older test datasets were produced with imagery layers in
    complex32 format, and ISCE3 can still be configured to generate the
    layers in that format.
    """
    # Get Dataset handle via h5py's standard reader
    dataset = h5_file[raster_path]

    if nisarqa.is_complex32(dataset):
        # As of h5py 3.8.0, h5py gained the ability to read complex32
        # datasets, however numpy and other downstream packages do not
        # necessarily have that flexibility.
        # If the input product has dtype complex32, then we'll need to use
        # ComplexFloat16Decoder so that numpy et al can read the datasets.
        return nisarqa.ComplexFloat16Decoder(dataset)
    else:
        # Stick with h5py's standard reader
        return dataset


@lru_cache
def _get_or_create_cached_memmap(
    input_file: str | os.PathLike,
    dataset_path: str,
) -> np.memmap:
    """
    Get or create a cached memmap of the requested Dataset.

    On first invocation, creates a memory-mapped file in the global
    scratch directory and copies the contents of a 2D HDF5 Dataset to that file.
    The memory map object is cached and simply returned on subsequent
    invocations with the same arguments.

    The Dataset contents are copied tile-by-tile to avoid oversubscribing
    system memory. If the Dataset is chunked, the tile shape will match the
    chunk dimensions. Otherwise, the tile shape defaults to:
        (32, <dataset.shape[1]>)
    The full width is used because HDF5 Datasets use row-major ordering.

    Parameters
    ----------
    input_file : path-like
        HDF5 input file.
    dataset_path : string
        Path in the HDF5 input file to the 2D Dataset to be copied to a
        memory-mapped file.
        Example: "/science/LSAR/RSLC/swaths/frequencyA/HH".

    Returns
    -------
    img_memmap : numpy.memmap
        `memmap` copy of the `dataset_path` Dataset.
    """
    # Note: numpy.memmap relies on mmap.mmap, which, prior to Python 3.13,
    # had no interface to close the underlying file descriptor.
    # In addition, numpy.memmap doesn't provide an API to close the mmap object.
    # (And, since numpy.memmap hides the details of how it calls mmap.mmap,
    # it doesn't have a way to close the file handle either, even in
    # Python 3.13+.) So both the file descriptor and the memory map may
    # stay open for the lifetime of the process.

    log = nisarqa.get_logger()

    # Construct file name for memory-mapped file
    filename = f"{dataset_path.replace('/', '-')}.dat"
    mmap_file = nisarqa.get_global_scratch_dir() / filename

    # A user should never be able to trip this assert because the scratch
    # directory should always be unique. But if we change the behavior
    # of the QA scratch directory without thinking through all consequences,
    # this assertion will alert us to the issue.
    msg = (
        "A file already exists with the memory-mapped file's default path"
        f" and name: {mmap_file}"
    )
    assert not mmap_file.exists(), msg

    # Create a memmap with dtype and shape that matches our data
    with h5py.File(input_file, "r") as h5_f:
        h5_ds = _get_dataset_handle(h5_file=h5_f, raster_path=dataset_path)
        shape = np.shape(h5_ds)
        if len(shape) != 2:
            raise ValueError(
                f"Input array has {len(shape)} dimensions, but must be 2D."
            )

        img_memmap = np.memmap(
            mmap_file, dtype=h5_ds.dtype, mode="w+", shape=shape
        )

        # Copy data to memory-mapped file.
        # Note: This is an expensive operation. All decompression, etc. costs
        # are incurred here.

        # tuple giving the chunk shape, or None if chunked storage is not used
        if (chunks := h5_ds.chunks) is not None:
            log.debug(f"Dataset {dataset_path} has chunk shape {chunks}.")
            # Number of chunk dimensions must match number of Dataset dimensions.
            assert len(chunks) == 2
            # Edge case: dimension(s) are smaller than the chunk size,
            # so adjust the lengths which will be used for the tile iterators
            tile_height = min(chunks[0], shape[0])
            tile_width = min(chunks[1], shape[1])

        else:
            # HDF5 uses row-major ordering, so use full rows
            default_tile_height = 32
            tile_height = min(default_tile_height, shape[0])
            tile_width = shape[1]
            log.debug(
                f"Dataset {dataset_path} not written with chunked storage."
                f" Input array with shape {shape} will be copied tile-by-tile"
                " to memory-mapped file using tile shape"
                f" ({tile_height}, {tile_width})."
            )

        msg = f"Copy Dataset contents to memory-mapped file: {dataset_path}"
        with nisarqa.log_runtime(msg):
            for i in range(0, shape[0], tile_height):
                for j in range(0, shape[1], tile_width):
                    slices = np.s_[i : (i + tile_height), j : (j + tile_width)]
                    img_memmap[slices] = h5_ds[slices]

        log.info(f"Memory-mapped scratch file saved: {mmap_file}")

        return img_memmap


__all__ = nisarqa.get_all(__name__, objects_to_skip)
