from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property, lru_cache
from pathlib import Path
from typing import overload

import h5py
import isce3
import numpy as np
import shapely

import nisarqa

# List of objects from the import statements that
# should not be included when importing this module
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
        Handle to the input product h5 file.
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


@dataclass
class NisarProduct(ABC):
    """
    Base class for NISAR product readers.

    Parameters
    ----------
    filepath : path-like
        Filepath to the input product.
    use_cache : bool, optional
        True to use memory map(s) to cache select Dataset(s) in
        memory-mapped files in the global scratch directory.
        False to always read data directly from the input file.
        Generally, enabling caching should reduce runtime.
        Defaults to False.
    """

    filepath: str
    use_cache: bool = False

    def __post_init__(self):
        # Verify that the input product contained a product spec version.
        self.product_spec_version

        self._check_product_type()
        self._check_root_path()
        self._check_is_geocoded()
        self._check_data_group_path()

    @property
    @abstractmethod
    def product_type(self) -> str:
        """Product type (e.g. "RSLC" or "GCOV")."""
        pass

    @property
    @abstractmethod
    def is_geocoded(self) -> bool:
        """True if product is geocoded; False if range Doppler grid."""
        pass

    @abstractmethod
    def get_browse_latlonquad(self) -> nisarqa.LatLonQuad:
        """
        Create a LatLonQuad for the corners of the input product.

        Returns
        -------
        llq : LatLonQuad
            A LatLonQuad object containing the four corner coordinates for this
            product's browse image, in degrees.
        """
        pass

    @cached_property
    def bounding_polygon(self) -> str:
        """Bounding polygon WKT string."""
        id_group = self.identification_path
        with h5py.File(self.filepath) as f:
            wkt = f[id_group]["boundingPolygon"][()]
            return nisarqa.byte_string_to_python_str(wkt)

    @cached_property
    def granule_id(self) -> str:
        """Granule ID (or the base filename if granule ID is not present)."""
        id_group = self.identification_path
        with h5py.File(self.filepath) as f:
            try:
                granule_id = f[id_group]["granuleId"][()]
            except KeyError:
                # During NISAR development, we often encounter legacy products that
                # are named according to NISAR conventions but are missing granule
                # ID metadata, so this bandaid is sometimes useful.
                nisarqa.get_logger().error(
                    "`granuleId` Dataset missing from input product's"
                    "`identification` group."
                )
                return Path(self.filepath).name
            return nisarqa.byte_string_to_python_str(granule_id)

    @cached_property
    def look_direction(self) -> str:
        """Look direction of the sensor, either 'Left' or 'Right'."""
        id_group = self.identification_path
        with h5py.File(self.filepath) as f:
            lookside = f[id_group]["lookDirection"][()]

        lookside = nisarqa.byte_string_to_python_str(lookside)

        valid_options = {"Left", "Right"}
        if lookside not in valid_options:
            msg = (
                f"Input product's `lookDirection` is {lookside}, must"
                f" be one of {valid_options}."
            )
            lookside_lower = lookside.lower()
            if lookside_lower == "left":
                nisarqa.get_logger().warning(msg)
                lookside = "Left"
            elif lookside_lower == "right":
                nisarqa.get_logger().warning(msg)
                lookside = "Right"
            else:
                raise ValueError(msg)

        return lookside

    @cached_property
    def identification_path(self) -> str:
        """
        Return the path to the identification group in the input file.

        Assumes that the input file contains only one path whose base name
        is "identification". If multiple such paths exist, or if no paths
        have that base name, then an exception is raised.

        Returns
        -------
        id_group : str
            The path to the identification group in the input file.

        Raises
        ------
        nisarqa.InvalidNISARProductError
            If "identification" is not found exactly one time in the input file.
        """
        with h5py.File(self.filepath) as f:
            paths = _get_paths_in_h5(h5_file=f, name="identification")

        if len(paths) != 1:
            raise nisarqa.InvalidNISARProductError(
                "Input product must contain exactly one group named"
                f" 'identification'. Found: {paths}"
            )

        return paths[0]

    @cached_property
    def product_spec_version(self) -> str:
        """
        Return the product specification version.

        Returns
        -------
        spec_version : str
            The value of "productSpecificationVersion" in the "identification"
            group in the input file. If this field is missing (such as with
            older test datasets), "0.0.0" is returned.
        """
        id_group = self.identification_path
        with h5py.File(self.filepath) as f:
            if "productSpecificationVersion" in f[id_group]:
                spec_version = f[id_group]["productSpecificationVersion"][...]
                spec_version = nisarqa.byte_string_to_python_str(spec_version)
                nisarqa.get_logger().info(
                    "Input product's"
                    " `identification/productSpecificationVersion` dataset"
                    f" contains {spec_version}."
                )
            else:
                # spec for very old test datasets.
                # `productSpecificationVersion` metadata was added after this.
                spec_version = "0.0.0"
                nisarqa.get_logger().error(
                    "`productSpecificationVersion` missing from input product's"
                    " `identification` group. Defaulting to '0.0.0'."
                )

            return spec_version

    @cached_property
    def list_of_frequencies(self) -> tuple[str, ...]:
        """
        The contents of .../identification/listOfFrequencies in input file.

        Returns
        -------
        list_of_freqs : tuple of str
            The contents of `listOfFrequencies` in the `identification`
            group in the input file.
            `list_of_freqs` will be one of: ("A",), ("B",), or ("A", "B").

        Raises
        ------
        ValueError
            If `listOfFrequencies` contains invalid options.
        KeyError
            If `listOfFrequencies` is missing.
        """
        log = nisarqa.get_logger()

        id_group = self.identification_path

        with h5py.File(self.filepath) as f:
            # listOfFrequencies should be in all test datasets.
            # If not, let h5py handle raising an error message.
            list_of_freqs = f[id_group]["listOfFrequencies"]
            nisarqa.verify_str_meets_isce3_conventions(ds=list_of_freqs)

            if list_of_freqs.shape == ():
                # dataset is scalar, not a list
                list_of_freqs = [
                    nisarqa.byte_string_to_python_str(list_of_freqs[()])
                ]
                log.error(
                    "`listOfFrequencies` dataset is a scalar string, should"
                    " be an array of byte strings."
                )
            else:
                if np.issubdtype(list_of_freqs.dtype, np.bytes_):
                    # list of byte strings. Yay!
                    list_of_freqs = [
                        nisarqa.byte_string_to_python_str(my_str)
                        for my_str in list_of_freqs[()]
                    ]
                elif isinstance(list_of_freqs[0], bytes):
                    # list of Python bytes objects. Boo.
                    # This edge case occurs in some InSAR datasets, and should
                    # be fixed for R4.
                    list_of_freqs = [
                        my_str.decode("utf-8") for my_str in list_of_freqs[()]
                    ]
                    # That's what we want to return in this function, but it
                    # does not meet NISAR specs, so log an error.
                    log.error(
                        "`listOfFrequencies` dataset is an array of objects of"
                        " type `bytes`, but should be an array of byte strings."
                    )
                else:
                    raise TypeError(
                        "`listOfFrequencies` dataset is an array of items of"
                        f" type {type(list_of_freqs[0])}, but should be an"
                        " array of byte strings."
                    )

            # Sanity check that the contents make sense
            if not set(list_of_freqs).issubset({"A", "B"}):
                raise ValueError(
                    "Input file's `listOfFrequencies` dataset contains"
                    f" {list_of_freqs}, but must be a subset of ('A', 'B')."
                )

            return tuple(list_of_freqs)

    def get_list_of_polarizations(self, freq: str) -> tuple[str, ...]:
        """
        Gets contents of .../frequency<freq>/listOfPolarizations in input file.

        Returns
        -------
        list_of_pols : tuple of str
            The contents of `listOfPolarizations` in the `.../frequency<freq>`
            group in the input file. Example output: ("HH", "HV").

        Raises
        ------
        ValueError
            If `listOfPolarizations` contains invalid options.
        KeyError
            If `listOfPolarizations` is missing.
        """

        # `listOfPolarizations` is always a child of the frequency group.
        freq_group = self.get_freq_path(freq=freq)
        log = nisarqa.get_logger()

        with h5py.File(self.filepath) as f:
            # `listOfPolarizations` should be in all frequency groups.
            # If not, let h5py handle raising an error message.
            list_of_pols = f[freq_group]["listOfPolarizations"]
            nisarqa.verify_str_meets_isce3_conventions(ds=list_of_pols)

            if list_of_pols.shape == ():
                # dataset is scalar, not an array
                list_of_pols = [
                    nisarqa.byte_string_to_python_str(list_of_pols[()])
                ]
                log.error(
                    f"`{list_of_pols.name}` dataset is a scalar string, should"
                    " be an array of byte strings."
                )
            else:
                if np.issubdtype(list_of_pols.dtype, np.bytes_):
                    # list of byte strings. Yay!
                    list_of_pols = [
                        nisarqa.byte_string_to_python_str(my_str)
                        for my_str in list_of_pols[()]
                    ]
                elif isinstance(list_of_pols[0], bytes):
                    # list of Python bytes objects. Boo.
                    # This edge case occurs in some InSAR datasets, and should
                    # be fixed for R4.
                    list_of_pols = [
                        my_str.decode("utf-8") for my_str in list_of_pols[()]
                    ]
                    # That's what we want to return in this function, but it
                    # does not meet NISAR specs, so log an error.
                    log.error(
                        "`listOfPolarizations` dataset is an array of objects"
                        " of type `bytes`, but should be an array of byte"
                        " strings."
                    )
                else:
                    raise TypeError(
                        "`listOfPolarizations` dataset is an array of items of"
                        f" type {type(list_of_pols[0])}, but should be an array"
                        " of byte strings."
                    )

            # Sanity check that the contents make sense
            poss_pols = nisarqa.get_possible_pols(self.product_type.lower())

            if self.product_type == "GCOV":
                # For GCOV, `get_possible_pols()` actually returns the
                # possible covariance terms, e.g. "HHHH", "HVHV".
                # So to get specifically the possible polarizations, we need
                # to truncate to the first two letters, and remove duplicates.
                poss_pols = set([pol[:2] for pol in poss_pols])

            if not set(list_of_pols).issubset(set(poss_pols)):
                raise ValueError(
                    "Input file's `listOfPolarizations` dataset contains"
                    f" {list_of_pols}, but must be a subset of {poss_pols}."
                )

            return tuple(list_of_pols)

    @cached_property
    def _root_path(self) -> str:
        """
        Get the path to the group which is the root for the primary groups.

        Returns
        -------
        root : str
            Path to the directory where the product data is stored.
                Standard Format: "/science/<band>/<product_type>
                Example:
                    "/science/LSAR/RSLC"

        See Also
        --------
        _data_group_path : Constructs the path to the data group.

        Notes
        -----
        In products up to and including the R3.4 delivery (which used product
        spec 0.9.0), this will be something like "/science/LSAR".
        This structure is set up like e.g.:
            /science/LSAR/RSLC/swaths/frequencyX/...
            /science/LSAR/RSLC/metadata/...
            /science/LSAR/identification
        In subsequent deliveries, that path will likely be truncated. All
        products would follow a consistent structure, something like:
            /data/frequencyX/...
            /metadata/...
            /identification
        In that case, the empty string "" should be returned by this function.
        """
        id_group = self.identification_path
        # The `identification` group is found at e.g.:
        #   "/science/LSAR/identification"
        # Remove identification.
        root = id_group.replace("/identification", "")
        return root

    def _check_root_path(self) -> None:
        """Sanity check that `self._root_path` is valid."""

        with h5py.File(self.filepath) as f:
            # Conditional branch for datasets <=R3.4 (TBD possibly beyond)
            if self._root_path not in f:
                raise ValueError(
                    f"self._root_path determined to be {self._root_path},"
                    " but this is not a valid path in the input file."
                )

    @cached_property
    def band(self) -> str:
        """
        Get the frequency-band ("L" or "S") of the input file.

        Assumption by QA SAS: each input product contains only one band.

        Returns
        -------
        band : str
            The input file's band. (One of "L" or "S").
        """
        log = nisarqa.get_logger()

        id_group = self.identification_path
        band = None

        with h5py.File(self.filepath) as f:
            try:
                band = f[id_group]["radarBand"][...]
            except KeyError:
                # Error: product is poorly formed, will cause issues once the
                # below TODO is removed.
                log.error("`radarBand` missing from `identification` group.")
            else:
                band = nisarqa.byte_string_to_python_str(band)

        # TODO - remove the below code once all test data sets are updated to
        # new product spec
        # Attempt to determine the band from the frequency group path
        if band is None:
            # WLOG, get the path to one of the frequency groups
            path = self.get_freq_path(freq=self.freqs[0])
            for b in ("L", "S"):
                if f"{b}SAR" in path:
                    band = b
                    break
            else:
                # Product updated to not include the band in the
                # "/science/LSAR/..." directory structure
                raise ValueError("Cannot determine band from product.")

        return band

    @cached_property
    def freqs(self) -> tuple[str, ...]:
        """
        The available frequencies in the input file.

        Returns
        -------
        found_freqs : tuple of str
            The available frequencies in the input file. Will be a subset of
            ("A", "B").

        Raises
        ------
        nisarqa.InvalidNISARProductError
            If no frequency groups are found.

        Notes
        -----
        "frequency" in this context is different than the typical
        meaning of e.g. "L-band" or "S-band" frequencies.
        In QA SAS, the convention is for e.g. L band or S band
        to be referred to as "bands", while the section of the band used
        for the raster data is referred to as "frequency."
        Most satellites are single band instruments, meaning that "band" and
        "frequency" are one and the same, so this distinction is redundant.
        However, the NISAR mission is capable of dual frequency data collection,
        (meaning that two frequencies of data can be collected within a single
        band), hence the reason for this distinction. For NISAR, these
        are referred to as "Frequency A" and "Freqency B".
        """
        log = nisarqa.get_logger()

        # Get paths to the frequency groups
        found_freqs = []
        for freq in ("A", "B"):
            try:
                path = self.get_freq_path(freq=freq)
            except nisarqa.DatasetNotFoundError:
                log.info(f"Frequency{freq} group not found.")
            else:
                found_freqs.append(freq)
                log.info(f"Found Frequency {freq} group: {path}")

        # Sanity checks
        # Check the "discovered" frequencies against the contents of the
        # `listOfFrequencies` dataset
        list_of_frequencies = self.list_of_frequencies
        if set(found_freqs) != set(list_of_frequencies):
            errmsg = (
                f"Input products contains frequencies {found_freqs}, but"
                f" `listOfFrequencies` says {list_of_frequencies}"
                " should be available."
            )
            raise nisarqa.InvalidNISARProductError(errmsg)

        if not found_freqs:
            errmsg = "Input product does not contain any frequency groups."
            raise nisarqa.InvalidNISARProductError(errmsg)

        return tuple(found_freqs)

    def get_freq_path(self, freq: str) -> str:
        """
        Return the path inside the input file to the specified frequency group.

        Parameters
        ----------
        freq : str
            Must be either "A" or "B".

        Returns
        -------
        path : str
            Path inside the input file to the requested frequency group.

        Raises
        ------
        nisarqa.DatasetNotFoundError
            If frequency not found in the input file.
        """
        if freq not in ("A", "B"):
            raise ValueError(f"{freq=}, must be either 'A' or 'B'")

        # We cannot use functools.lru_cache() on a instance method due to
        # the `self` parameter, so use an inner function to cache the results.
        @lru_cache
        def _freq_path(freq):
            log = nisarqa.get_logger()
            path = self._data_group_path + f"/frequency{freq}"
            with h5py.File(self.filepath) as f:
                if path in f:
                    return path
                else:
                    errmsg = (
                        f"Input file does not contain frequency {freq} group at"
                        f" path: {path}"
                    )
                    raise nisarqa.DatasetNotFoundError(errmsg)

        return _freq_path(freq)

    @cached_property
    def metadata_path(self) -> str:
        """
        The path in the input file to the `metadata` Group.

        Returns
        -------
        path : str
            Path inside the input file to the primary `metadata` Group.
        """
        return "/".join([self._root_path, self.product_type, "metadata"])

    @cached_property
    def science_freq(self) -> str:
        """
        The science frequency (primary frequency) of the input product.

        Returns
        -------
        freq : str
            The science frequency for the input product. One of: "A" or "B".
        """
        return "A" if "A" in self.freqs else "B"

    def _check_product_type(self) -> None:
        """
        Sanity check for `self.product_type`.

        Ensures that `self.product_type` returns a value
        that matches the `identification > productType` dataset in the
        input file.
        """
        id_group = self.identification_path

        with h5py.File(self.filepath) as f:
            in_file_prod_type = f[id_group]["productType"][...]
            in_file_prod_type = nisarqa.byte_string_to_python_str(
                in_file_prod_type
            )

        if self.product_type != in_file_prod_type:
            raise ValueError(
                f"QA requested for {self.product_type}, but input file's"
                f" `productType` field is {in_file_prod_type}."
            )

    def _check_is_geocoded(self) -> None:
        """Sanity check for `self.is_geocoded`."""
        log = nisarqa.get_logger()

        id_group = self.identification_path

        with h5py.File(self.filepath) as f:
            if "isGeocoded" in f[id_group]:
                # Check that `isGeocoded` is set correctly, i.e. that it is
                # False in range Doppler products, and True in Geocoded products
                ds_handle = f[id_group]["isGeocoded"]

                # Check that the value has the correct dtype and formatting
                # (this reports the results to the log)
                nisarqa.verify_isce3_boolean(ds_handle)

                data = ds_handle[()]

                if np.issubdtype(data.dtype, np.bytes_):
                    data = nisarqa.byte_string_to_python_str(data)

                    # Convert from string to boolean. (`verify_isce3_boolean()`
                    # already logged if data is one of True or False.)
                    # Without this conversion, casting the string "False" as
                    # a boolean results in True.
                    data = data == "True"

                if self.is_geocoded != bool(data):
                    log.error(
                        "WARNING `/identification/isGeocoded` field has value"
                        f" {ds_handle[...]}, which is inconsistent with"
                        f" product type of {self.product_type}."
                    )
                else:
                    log.info(
                        "`/identification/isGeocoded` field has value"
                        f" {ds_handle[...]}, which is consistent with"
                        f" product type of {self.product_type}."
                    )
            else:
                # The `isGeocoded` field is not necessary for successful
                # completion QA SAS: whether a product is geocoded
                # or not can be determined by the product type (e.g. RSLC vs.
                # GSLC). So let's simply log the error and let QA continue;
                # this will alert developers that the product is faulty.
                log.error("Product missing `/identification/isGeocoded` field")

    def _check_data_group_path(self) -> None:
        """Sanity check to ensure the grid path exists in the input file."""
        grid_path = self._data_group_path
        with h5py.File(self.filepath) as f:
            if grid_path not in f:
                errmsg = f"Input file is missing the path: {grid_path}"
                raise nisarqa.DatasetNotFoundError(errmsg)

    def coordinate_grid_metadata_cubes(
        self,
    ) -> Iterator[nisarqa.MetadataLUT3D]:
        """
        Generator for all metadata cubes in `../metadata/xxxGrid` Group.

        For L1 products, this is the `../metadata/geolocationGrid` Group.
        For L2 products, this is the `../metadata/radarGrid` Group.

        Yields
        ------
        cube : nisarqa.MetadataLUT3D
            The next MetadataLUT3D in the Group.
        """
        with h5py.File(self.filepath, "r") as f:
            grp_path = self._coordinate_grid_metadata_group_path
            grp = f[grp_path]
            for ds_arr in grp.values():

                if isinstance(ds_arr, h5py.Group):
                    raise TypeError(
                        f"unexpected HDF5 Group found in {grp_path}."
                        " Metadata cubes Groups should only contain Datasets."
                    )
                ds_path = ds_arr.name

                n_dim = np.ndim(ds_arr)
                if n_dim in (0, 1):
                    # Scalar and 1D Datasets in this group are coordinate
                    # dimensions and georeferencing info -- not metadata LUTs.
                    # Skip.
                    pass
                elif n_dim != 3:
                    raise ValueError(
                        f"The coordinate grid metadata group should only"
                        " should only contain scalar, 1D, or 3D Datasets."
                        f" Dataset contains {n_dim} dimensions: {ds_path}"
                    )
                else:
                    yield self._build_metadata_lut(f=f, ds_arr=ds_arr)

    @abstractmethod
    def _data_group_path(self) -> str:
        """
        Return the path to the group containing the primary datasets.

        For range Doppler products, this should be e.g.:
            'science/LSAR/RIFG/swaths'
        For geocoded products, this should be e.g.:
            'science/LSAR/RIFG/grids'

        Returns
        -------
        root : str
            Path to the directory where the product data is stored.
                Standard Format:
                    "science/<band>/<product_type>/<'swaths' OR 'grids'>"
                Example:
                    "science/LSAR/RSLC/swaths"

        See Also
        --------
        _root_path : Constructs the path to the primary root group.

        Notes
        -----
        A common implementation for this would be e.g.:
            return "/".join([self._root_path, self.product_type, "swaths"])

        In products up to and including the R3.4 delivery (which used product
        spec 0.9.0), the L1/L2 product structure is set up like e.g.:
            /science/LSAR/RSLC/swaths/frequencyX/...
            /science/LSAR/RSLC/metadata/...
            /science/LSAR/identification
        In which case "/science/LSAR/RSLC/swaths" should be returned.

        In subsequent deliveries, that path will likely be truncated. All
        products would follow a consistent structure, something like:
            /data/frequencyX/...
            /metadata/...
            /identification
        In that case, the string "data" should be returned by this function.
        """
        pass

    @cached_property
    def _metadata_group_path(self) -> str:
        """
        Get the path to the metadata group.

        Returns
        -------
        root : str
            Path to the metadata directory.
                Standard Format: "/science/<band>/<product_type>/metadata
                Example:
                    "/science/LSAR/RSLC/metadata"

        Notes
        -----
        In products up to and including the R3.4 delivery (which used product
        spec 0.9.0), this input product structure is set up like e.g.:
            /science/LSAR/RSLC/swaths/frequencyX/...
            /science/LSAR/RSLC/metadata/...
            /science/LSAR/identification
        In subsequent deliveries, that path will likely be truncated. All
        products would follow a consistent structure, something like:
            /data/frequencyX/...
            /metadata/...
            /identification
        When that change is implemented, this function will need to be updated
        to accommodate the new spec.
        """
        return "/".join([self._root_path, self.product_type, "metadata"])

    @property
    @abstractmethod
    def _coordinate_grid_metadata_group_path(self) -> str:
        """
        Get the path to the coordinate grid metadata Group.

        Returns
        -------
        root : str
            Path to the metadata directory.
                Standard Rxxx Format:
                    "/science/<band>/<product_type>/metadata/geolocationGrid"
                Standard Gxxx Format:
                    "/science/<band>/<product_type>/metadata/radarGrid"
                Example:
                    "/science/LSAR/GSLC/metadata/radarGrid"
        """
        pass

    def _get_stats_h5_group_path(self, raster_path: str) -> str:
        """
        Return path where metrics for `raster_path` should be saved in STATS.h5 file.

        Parameters
        ----------
        raster_path : str
            Full path in the input HDF5 file to a raster dataset.
            Examples:
                GSLC (similar for RSLC/GCOV):
                    "/science/LSAR/GSLC/grids/frequencyA/HH"
                GUNW (similar for RIFG/RUNW):
                    "/science/LSAR/GUNW/grids/frequencyA/pixelOffsets/HH/alongTrackOffset"
                GOFF (similar for ROFF):
                    "/science/LSAR/GOFF/grids/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"

        Returns
        -------
        path : str
            Path in the STATS.h5 file for the group where all metrics and
            statistics re: this raster should be saved.
            Note that a path to a h5py.Dataset was passed in as an argument to
            this function, but a path to a h5py Group will be returned.
            Examples:
                RSLC/GSLC/GCOV: "/science/LSAR/QA/data/frequencyA/HH"
                RUNW/GUNW: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset"
                ROFF/GOFF: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"
        """
        # Let's mirror the structure of the input product for the STATS.h5 file
        # In essence, we need to replace the beginning part of the base path.

        # Check that the substring "frequency" occurs exactly once in `raster_path`
        assert raster_path.count("frequency") == 1
        _, suffix = raster_path.split("frequency")
        # remove everything before "frequency":
        suffix = f"frequency{suffix}"

        # Append the QA STATS.h5 data group path to the beginning
        path = f"{nisarqa.STATS_H5_QA_DATA_GROUP % self.band}/{suffix}"

        return path

    @abstractmethod
    def _get_raster_from_path(
        self, h5_file: h5py.File, raster_path: str, *, parse_stats: bool
    ) -> (
        nisarqa.RadarRaster
        | nisarqa.RadarRasterWithStats
        | nisarqa.GeoRaster
        | nisarqa.GeoRasterWithStats
    ):
        """
        Generate a *Raster for the raster at `raster_path`.

        Parameters
        ----------
        h5_file : h5py.File
            Open file handle for the input file containing the raster.
        raster_path : str
            Full path in `h5_file` to the desired raster dataset
            Examples:
                "/science/LSAR/RSLC/swaths/frequencyA/HH"
                "/science/LSAR/RIFG/swaths/frequencyA/interferogram/HH/wrappedInterferogram"
        parse_stats : bool
            If True, the min/max/mean/std statistics are parsed from the
            HDF5 attributes of the raster and a *RasterWithStats instance is
            returned.
            If False, a RadarRaster or GeoRaster instance is returned.

        Returns
        -------
        raster : nisarqa.RadarRaster or nisarqa.RadarRasterWithStats
                    or nisarqa.GeoRaster or nisarqa.GeoRasterWithStats
            *Raster of the given dataset.

        Raises
        ------
        DatasetNotFoundError
            If the file does not contain a raster dataset at `raster_path`,
            or if any of the corresponding metadata for that raster are
            not located.
        """
        pass

    @abstractmethod
    def _get_raster_name(self, raster_path: str) -> str:
        """
        Return a name for the raster, e.g. 'RSLC_LSAR_A_HH'.

        Parameters
        ----------
        raster_path : str
            Full path in `h5_file` to the desired raster dataset.
            Examples:
                "/science/LSAR/GSLC/grids/frequencyA/HH"
                "/science/LSAR/GUNW/grids/frequencyA/interferogram/HH/unwrappedPhase"

        Returns
        -------
        name : str
            The human-understandable name that is derived from the dataset.
            Examples: "GSLC_L_A_HH" or "GUNW_L_A_HH_unwrappedPhase".
        """
        pass

    def _build_metadata_lut(
        self,
        f: h5py.File,
        ds_arr: h5py.Dataset,
    ) -> nisarqa.typing.MetadataLUTT:
        """
        Construct a MetadataLUT for the given 1D, 2D, or 3D LUT.

        Parameters
        ----------
        f : h5py.File
            Handle to the NISAR input product.
        ds_arr : h5py.Dataset
            Path to the metadata LUT Dataset.

        Returns
        -------
        ds : nisarqa.typing.MetadataLUTT
            A constructed MetadataLUT of `ds_arr`. The number of dimensions
            of `ds_arr` determines whether a MetadataLUT1D, *2D, or *3D
            is returned.
        """
        # Get the full HDF5 path to the Dataset
        ds_path = ds_arr.name
        n_dim = ds_arr.ndim

        if n_dim not in (1, 2, 3):
            raise ValueError(f"{n_dim=}, must be 1, 2, or 3.")

        # build arguments dict for the MetadataLUTXD constructor.
        kwargs = {"data": ds_arr, "name": ds_path}

        if self.is_geocoded:
            names = ("xCoordinates", "yCoordinates")
        else:
            names = ("slantRange", "zeroDopplerTime")

        # In all L2 products, the coordinate datasets exist in the same group
        # as the dataset itself. However, in L1 products, some coordinate
        # datasets exist in a predecessor group, so we must recursively scan
        # parent directories until finding the coordinate dataset.
        kwargs["x_coord_vector"] = f[
            _get_path_to_nearest_dataset(
                h5_file=f,
                starting_path=ds_path,
                dataset_to_find=names[0],
            )
        ]
        if n_dim >= 2:
            kwargs["y_coord_vector"] = f[
                _get_path_to_nearest_dataset(
                    h5_file=f,
                    starting_path=ds_path,
                    dataset_to_find=names[1],
                )
            ]
        if n_dim == 3:
            kwargs["z_coord_vector"] = f[
                _get_path_to_nearest_dataset(
                    h5_file=f,
                    starting_path=ds_path,
                    dataset_to_find="heightAboveEllipsoid",
                )
            ]
        if n_dim == 1:
            lut_cls = nisarqa.MetadataLUT1D
        elif n_dim == 2:
            lut_cls = nisarqa.MetadataLUT2D
        else:
            lut_cls = nisarqa.MetadataLUT3D

        try:
            return lut_cls(**kwargs)
        except nisarqa.InvalidRasterError as e:
            if nisarqa.Version.from_string(
                self.product_spec_version
            ) < nisarqa.Version(1, 1, 0):
                # Older products sometimes had filler metadata.
                # log, and quiet the exception.
                nisarqa.get_logger().error(
                    f"Could not build MetadataLUT{n_dim}D for"
                    f" Dataset {ds_path}"
                )
            else:
                # Newer products should have complete metadata
                raise

    @cached_property
    def _processing_info_metadata_group_path(self) -> str:
        """
        Path in the input file to the `../metadata/processingInformation` Group.

        Returns
        -------
        path : str
            Path in input file to the ../metadata/processingInformation Group.
        """
        return "/".join([self._metadata_group_path, "processingInformation"])

    @cached_property
    def _algorithms_metadata_group_path(self) -> str:
        """
        Path in input file to `../processingInformation/algorithms` Group.

        Returns
        -------
        path : str
            Path in input file to the ../processingInformation/algorithms Group.
        """
        return "/".join(
            [self._processing_info_metadata_group_path, "algorithms"]
        )

    @cached_property
    def software_version(self) -> str:
        """
        The software version used to generate the HDF5 granule.

        For NISAR at JPL, this will typically be the version of ISCE3 used to
        generate the granule.

        Returns
        -------
        software_version : str
            The software version used to generate the HDF5 granule.
        """
        log = nisarqa.get_logger()

        path = f"{self._algorithms_metadata_group_path}/softwareVersion"

        try:
            with h5py.File(self.filepath) as in_f:
                isce3_version = in_f[path][()]
        except KeyError:
            return_val = "not available"
            msg = (
                f"Returning placeholder software version of {return_val!r}."
                f" `softwareVersion` does not exist at path: {path}"
            )
            spec = nisarqa.Version.from_string(self.product_spec_version)
            if spec < nisarqa.Version(1, 1, 0):
                log.warning(
                    f"Input product generated with an old product spec. {msg}"
                )
            else:
                log.error(msg)
            return return_val

        return nisarqa.byte_string_to_python_str(isce3_version)


@dataclass
class NisarRadarProduct(NisarProduct):
    @property
    def is_geocoded(self) -> bool:
        return False

    @cached_property
    def _data_group_path(self) -> str:
        return "/".join([self._root_path, self.product_type, "swaths"])

    @cached_property
    def _coordinate_grid_metadata_group_path(self) -> str:
        return "/".join([self._metadata_group_path, "geolocationGrid"])

    def get_browse_latlonquad(self) -> nisarqa.LatLonQuad:
        # Shapely boundary coords is a tuple of coordinate lists of
        # form ([x...], [y...])
        coords = shapely.from_wkt(self.bounding_polygon).boundary.coords
        # Rezip the coordinates to a list of (x, y) tuples.
        # Lon/lat values in the bounding polygon are in units of degrees.
        coords = [nisarqa.LonLat(c[0], c[1]) for c in zip(*coords.xy)]

        # Workaround for bug in ISCE3 generated products. We expect 41 points
        # (10 along each side + endpoint same as start point), but there
        # are 42 points (41 points in expected order + duplicated endpoint).
        # So if the endpoint is duplicated, we drop it here to handle this bug.
        # (See https://github-fn.jpl.nasa.gov/isce-3/isce/issues/1486)
        if coords[-1] == coords[-2]:
            coords = coords[:-1]

        # Drop last (same as first) coordinate
        if coords[-1] != coords[0]:
            msg = (
                "Input product's boundingPolygon is not closed"
                " (endpoint does not match start point)"
            )
            nisarqa.get_logger().warning(msg)
        coords = coords[:-1]

        if len(coords) < 4:
            raise ValueError("Not enough coordinates for bounding polygon")
        if len(coords) % 4 != 0:
            raise ValueError("Bounding polygon requires evenly spaced corners")

        # Corners are assumed to start at the 0th index and be evenly spaced
        corners = [coords[len(coords) // 4 * i] for i in range(4)]

        # Reorder the corners for the LatLonQuad constructor.
        input_spec_version = nisarqa.Version.from_string(
            self.product_spec_version
        )
        if input_spec_version <= nisarqa.Version(1, 1, 0):
            # products <= v1.1.0 use the "old style" bounding polygon order:
            # the boundingPolygon is specified in clockwise order in the
            # image coordinate system, starting at the upper-left of the image.
            geo_corners = nisarqa.LatLonQuad(
                ul=corners[0],
                ur=corners[1],
                ll=corners[3],
                lr=corners[2],
                normalize_longitudes=True,
            )
        else:
            # boundingPolygon is specifed in counter-clockwise order in
            # map coordinates (not necessarily in the image coordinate system),
            # with the first point representing the start-time, near-range
            # corner (aka the upper-left of the image).

            # In the left-looking case, the counter-clockwise orientation of
            # points in map coordinates corresponds to a counter-clockwise
            # orientation of points in image coordinates, so the order of the
            # corners must be reversed.
            if self.look_direction == "Left":
                geo_corners = nisarqa.LatLonQuad(
                    ul=corners[0],
                    ur=corners[3],
                    ll=corners[1],
                    lr=corners[2],
                    normalize_longitudes=True,
                )
            else:
                # In the right-looking case, the counter-clockwise orientation
                # of points in map coordinates corresponds to a clockwise
                # orientation of points in image coordinates, so the corners
                # are already in the correct ordering.
                assert self.look_direction == "Right"
                geo_corners = nisarqa.LatLonQuad(
                    ul=corners[0],
                    ur=corners[1],
                    ll=corners[3],
                    lr=corners[2],
                    normalize_longitudes=True,
                )

        return geo_corners

    def _get_raster_from_path(
        self, h5_file: h5py.File, raster_path: str, *, parse_stats: bool
    ) -> nisarqa.RadarRaster | nisarqa.RadarRasterWithStats:
        """
        Generate a RadarRaster* for the raster at `raster_path`.

        NISAR product type must be one of: 'RSLC', 'SLC', 'RIFG', 'RUNW', 'ROFF'
        If the raster dtype is complex float 16, then the image dataset
        will be stored as a ComplexFloat16Decoder instance; this will allow
        significantly faster access to the data.

        Parameters
        ----------
        h5_file : h5py.File
            Open file handle for the input file containing the raster.
        raster_path : str
            Full path in `h5_file` to the desired raster dataset.
            Examples:
                "/science/LSAR/RSLC/swaths/frequencyA/HH"
                "/science/LSAR/RIFG/swaths/frequencyA/interferogram/HH/wrappedInterferogram"
        parse_stats : bool
            If True, the min/max/mean/std statistics are parsed from the
            HDF5 attributes of the raster and a nisarqa.RadarRasterWithStats
            instance is returned.
            If False, a nisarqa.RadarRaster instance is returned (no stats).

        Returns
        -------
        raster : nisarqa.RadarRaster or nisarqa.RadarRasterWithStats
            RadarRaster* of the given dataset, as determined by `parse_stats`.

        Raises
        ------
        DatasetNotFoundError
            If the file does not contain a raster dataset at `raster_path`,
            or if any of the corresponding metadata for that raster are
            not located.

        Notes
        -----
        The `name` attribute will be populated per `self.get_name()`.
        As of 6/22/2023, these additional datasets which correspond to
        `raster_path` will be parsed via
        `_get_path_to_nearest_dataset(..., raster_path, <dataset name>) :
            sceneCenterAlongTrackSpacing
            sceneCenterGroundRangeSpacing
            slantRange
            zeroDopplerTime
        """
        if raster_path not in h5_file:
            errmsg = f"Input file does not contain raster {raster_path}"
            raise nisarqa.DatasetNotFoundError(errmsg)

        # Arguments to pass to the constructor of `RadarRaster` or
        # `RadarRasterWithStats`
        kwargs = {}

        # Get dataset object and check for correct dtype
        dataset = _get_dataset_handle(h5_file, raster_path)

        if self.use_cache:
            kwargs["data"] = _get_or_create_cached_memmap(
                input_file=self.filepath,
                dataset_path=raster_path,
            )
        else:
            kwargs["data"] = dataset

        kwargs["units"] = _get_units(dataset)
        kwargs["fill_value"] = _get_fill_value(dataset)

        # From the xml Product Spec, sceneCenterAlongTrackSpacing is the
        # 'Nominal along track spacing in meters between consecutive lines
        # near mid swath of the RSLC image.'
        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="sceneCenterAlongTrackSpacing",
        )
        ground_az_spacing = h5_file[path][...]
        kwargs["ground_az_spacing"] = ground_az_spacing

        # Get Azimuth (y-axis) tick range + label
        # path in h5 file: /science/LSAR/RSLC/swaths/zeroDopplerTime
        # For NISAR, radar-domain grids are referenced by the center of the
        # pixel, so +/- half the distance of the pixel's side to capture
        # the entire range.
        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="zeroDopplerTime",
        )
        kwargs["az_start"] = float(h5_file[path][0]) - 0.5 * ground_az_spacing
        kwargs["az_stop"] = float(h5_file[path][-1]) + 0.5 * ground_az_spacing

        # Use zeroDopplerTime's units attribute to get the epoch.
        kwargs["epoch"] = self._get_epoch(ds=h5_file[path])

        # From the xml Product Spec, sceneCenterGroundRangeSpacing is the
        # 'Nominal ground range spacing in meters between consecutive pixels
        # near mid swath of the RSLC image.'
        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="sceneCenterGroundRangeSpacing",
        )
        ground_range_spacing = h5_file[path][...]
        kwargs["ground_range_spacing"] = ground_range_spacing

        # Range in meters (units are specified as meters in the product spec)
        # For NISAR, radar-domain grids are referenced by the center of the
        # pixel, so +/- half the distance of the pixel's side to capture
        # the entire range.
        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="slantRange",
        )
        kwargs["rng_start"] = (
            float(h5_file[path][0]) - 0.5 * ground_range_spacing
        )
        kwargs["rng_stop"] = (
            float(h5_file[path][-1]) + 0.5 * ground_range_spacing
        )

        # Construct Name
        kwargs["name"] = self._get_raster_name(raster_path)

        kwargs["stats_h5_group_path"] = self._get_stats_h5_group_path(
            raster_path
        )

        kwargs["band"] = self.band
        kwargs["freq"] = "A" if "frequencyA" in raster_path else "B"

        if parse_stats:
            # Construct Stats
            kwargs["stats"] = _parse_dataset_stats_from_h5(
                ds=h5_file[raster_path]
            )
            return nisarqa.RadarRasterWithStats(**kwargs)
        else:
            return nisarqa.RadarRaster(**kwargs)

    @staticmethod
    def _get_epoch(ds: h5py.Dataset) -> str:
        """
        Parse, validate, and return the dataset's reference epoch.

        Reference epoch will be returned as an RFC 3339 string with
        full-date and partial-time.
        Ref: https://datatracker.ietf.org/doc/html/rfc3339#section-5.6

        Parameters
        ----------
        ds : h5py.Dataset
            Dataset with an attribute named "units", where `units` contains
            a byte string with the format 'seconds since YYYY-mm-ddTHH:MM:SS'.

        Returns
        -------
        datetime_str : str
            A string following a format like 'YYYY-mm-ddTHH:MM:SS'.
            (The "T" and any decimal seconds are optional; this function
            does not enforce strict NISAR conventions for datetime strings.)
            If datetime could not be parsed, then "INVALID EPOCH" is returned.
        """
        log = nisarqa.get_logger()

        sec_since_epoch = ds.attrs["units"]
        sec_since_epoch = nisarqa.byte_string_to_python_str(sec_since_epoch)

        if not sec_since_epoch.startswith("seconds since "):
            log.error(
                f"epoch units string is {sec_since_epoch!r}, but should"
                f" begin with 'seconds since '. Dataset: {ds.name}"
            )

        # Datetime format validation check
        if nisarqa.contains_datetime_value_substring(input_str=sec_since_epoch):
            dt_str = nisarqa.extract_datetime_value_substring(
                input_str=sec_since_epoch, dataset_name=ds.name
            )

            if not nisarqa.verify_nisar_datetime_string_format(
                datetime_str=dt_str, dataset_name=ds.name, precision="seconds"
            ):
                log.error(
                    f"epoch units string is {sec_since_epoch!r}, but must"
                    f" use a datetime string in format 'YYYY-mm-ddTHH:MM:SS'."
                    f" Dataset: {ds.name}"
                )
            return dt_str

        else:
            log.error(
                f"epoch units string is {sec_since_epoch!r}, but should"
                f" contain a datetime string. Dataset: {ds.name}"
            )
            return "INVALID EPOCH"


@dataclass
class NisarGeoProduct(NisarProduct):
    @property
    def is_geocoded(self) -> bool:
        return True

    def get_browse_latlonquad(self) -> nisarqa.LatLonQuad:
        epsg = self.epsg
        proj = isce3.core.make_projection(epsg)

        geo_corners = ()
        for y in self.browse_y_range:
            for x in self.browse_x_range:
                # Use a dummy height value in computing the inverse projection.
                # isce3 projections are always 2-D transformations -- the height
                # has no effect on lon/lat
                lon, lat, _ = proj.inverse([x, y, 0])

                # convert lon/lat radians to degrees suitable for LatLonQuad
                point = nisarqa.LonLat(np.rad2deg(lon), np.rad2deg(lat))
                geo_corners += (point,)

        return nisarqa.LatLonQuad(*geo_corners, normalize_longitudes=True)

    @cached_property
    def _data_group_path(self) -> str:
        return "/".join([self._root_path, self.product_type, "grids"])

    @cached_property
    def _coordinate_grid_metadata_group_path(self) -> str:
        return "/".join([self._metadata_group_path, "radarGrid"])

    @cached_property
    def epsg(self) -> str:
        """EPSG code for input product."""
        with h5py.File(self.filepath) as f:
            # EPSG code is consistent for both frequencies. WLOG pick the
            # science frequency.
            freq_path = self.get_freq_path(freq=self.science_freq)

            # Get the sub path to an occurrence of a `projection` dataset
            # for the chosen frequency. (Again, they're all the same.)
            proj_path = _get_paths_in_h5(
                h5_file=f[freq_path], name="projection"
            )
            try:
                proj_path = "/".join([freq_path, proj_path[0]])
            except IndexError as exc:
                raise nisarqa.DatasetNotFoundError(
                    "no projection path found"
                ) from exc

            return f[proj_path][...]

    @property
    @abstractmethod
    def browse_x_range(self) -> tuple[float, float]:
        """
        Get the x range coordinates for the browse image.

        Returns
        -------
        x_range : tuple of float
            The range of the x coordinates for the browse image.
            Format:
                (<x_start>, <x_stop>)
        """
        pass

    @property
    @abstractmethod
    def browse_y_range(self) -> tuple[float, float]:
        """
        Get the y range coordinates for the browse image.

        Returns
        -------
        y_range : tuple of float
            The range of the y coordinates for the browse image.
            Format:
                (<y_start>, <y_stop>)
        """
        pass

    def _get_raster_from_path(
        self, h5_file: h5py.File, raster_path: str, *, parse_stats: bool
    ) -> nisarqa.GeoRaster | nisarqa.GeoRasterWithStats:
        """
        Get the GeoRaster* for the raster at `raster_path`.

        NISAR product type must be one of: 'GSLC', 'GCOV', 'GUNW', 'GOFF'.

        Parameters
        ----------
        h5_file : h5py.File
            Open file handle for the input file containing the raster.
        raster_path : str
            Full path in `h5_file` to the desired raster dataset.
            Examples:
                "/science/LSAR/GSLC/grids/frequencyA/HH"
                "/science/LSAR/GUNW/grids/frequencyA/interferogram/HH/unwrappedPhase"
        parse_stats : bool
            If True, the min/max/mean/std statistics are parsed from the
            HDF5 attributes of the raster and a nisarqa.GeoRasterWithStats
            instance is returned.
            If False, a nisarqa.GeoRaster instance is returned (no stats).

        Returns
        -------
        raster : nisarqa.GeoRaster or nisarqa.GeoRasterWithStats
            GeoRaster* of the given dataset, as determined by `parse_stats`.

        Raises
        ------
        DatasetNotFoundError
            If the file does not contain a raster dataset at `raster_path`,
            or if any of the corresponding metadata for that raster are
            not located.

        Notes
        -----
        The `name` attribute will be populated per `self.get_name()`.
        As of Aug 7, 2023, these additional datasets which correspond to
        `raster_path` will be parsed via
        `_get_path_to_nearest_dataset(..., raster_path, <dataset name>) :
            xCoordinateSpacing
            xCoordinates
            yCoordinateSpacing
            yCoordinates
        """
        if raster_path not in h5_file:
            errmsg = f"Input file does not contain raster {raster_path}"
            raise nisarqa.DatasetNotFoundError(errmsg)

        # Arguments to pass to the constructor of `GeoRaster` or `GeoRasterWithStats`
        kwargs = {}

        # Get dataset object and check for correct dtype
        dataset = _get_dataset_handle(h5_file, raster_path)

        if self.use_cache:
            kwargs["data"] = _get_or_create_cached_memmap(
                input_file=self.filepath,
                dataset_path=raster_path,
            )
        else:
            kwargs["data"] = dataset

        kwargs["units"] = _get_units(dataset)
        kwargs["fill_value"] = _get_fill_value(dataset)

        # From the xml Product Spec, xCoordinateSpacing is the
        # 'Nominal spacing in meters between consecutive pixels'
        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="xCoordinateSpacing",
        )
        x_spacing = float(h5_file[path][...])
        kwargs["x_spacing"] = x_spacing

        # X in meters (units are specified as meters in the product spec)
        # For NISAR, geocoded grids are referenced by the upper-left corner
        # of the pixel to match GDAL conventions. So add the distance of
        # the pixel's side to far right side to get the actual stop value.
        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="xCoordinates",
        )
        kwargs["x_start"] = float(h5_file[path][0])
        kwargs["x_stop"] = float(h5_file[path][-1]) + x_spacing

        # From the xml Product Spec, yCoordinateSpacing is the
        # 'Nominal spacing in meters between consecutive lines'
        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="yCoordinateSpacing",
        )
        y_spacing = float(h5_file[path][...])
        kwargs["y_spacing"] = y_spacing

        # Y in meters (units are specified as meters in the product spec)
        # For NISAR, geocoded grids are referenced by the upper-left corner
        # of the pixel to match GDAL conventions. So add the distance of
        # the pixel's side to bottom to get the actual stop value.
        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="yCoordinates",
        )
        kwargs["y_start"] = float(h5_file[path][0])
        kwargs["y_stop"] = float(h5_file[path][-1]) + y_spacing

        # Construct Name
        kwargs["name"] = self._get_raster_name(raster_path)

        kwargs["stats_h5_group_path"] = self._get_stats_h5_group_path(
            raster_path
        )

        kwargs["band"] = self.band
        kwargs["freq"] = "A" if "frequencyA" in raster_path else "B"

        if parse_stats:
            kwargs["stats"] = _parse_dataset_stats_from_h5(
                ds=h5_file[raster_path]
            )
            return nisarqa.GeoRasterWithStats(**kwargs)
        else:
            return nisarqa.GeoRaster(**kwargs)


@dataclass
class NonInsarProduct(NisarProduct):
    """Common functionality for RSLC, GLSC, and GCOV products."""

    def metadata_neb_luts(self, freq: str) -> Iterator[nisarqa.MetadataLUT2D]:
        """
        Generator for metadata LUTs in noise equivalent backscatter Group.

        These are located under the `calibrationInformation` Group.

        Parameters
        ----------
        freq : {'A', 'B'}
            The frequency sub-band. Must be a valid sub-band in the product.

        Yields
        ------
        ds : nisarqa.MetadataLUT2D
            The next MetadataLUT2D in this Group:
            `../metadata/calibrationInformation/frequency<freq>/noiseEquivalentBackscatter`
        """
        with (
            h5py.File(self.filepath, "r") as f,
            self.get_noise_eq_group(freq) as neb_grp,
        ):
            for ds_arr in neb_grp.values():
                if isinstance(ds_arr, h5py.Group):
                    raise TypeError(
                        f"Unexpected HDF5 Group found in {neb_grp.name}."
                        " Metadata Groups should only contain Datasets."
                    )
                ds_path = ds_arr.name

                n_dim = np.ndim(ds_arr)
                if n_dim in (0, 1):
                    # Scalar and 1D Datasets in this group are coordinate
                    # dimensions and georeferencing info -- not metadata LUTs.
                    # Skip.
                    pass
                elif n_dim != 2:
                    raise ValueError(
                        "The `noiseEquivalentBackscatter` metadata group"
                        " should only contain scalar, 1D, or 2D Datasets."
                        f" Dataset contains {n_dim} dimensions: {ds_path}"
                    )
                else:
                    yield self._build_metadata_lut(f=f, ds_arr=ds_arr)

    def metadata_elevation_antenna_pat_luts(
        self, freq: str
    ) -> Iterator[nisarqa.MetadataLUT2D]:
        """
        Generator for all elevation antenna pattern metadata LUTs.

        Yields
        ------
        ds : nisarqa.MetadataLUT2D
            The next MetadataLUT2D in this Group:
            `../metadata/calibrationInformation/frequency<freq>/elevationAntennaPattern`
        """
        with h5py.File(self.filepath, "r") as f:
            grp_path = "/".join(
                [
                    self._calibration_metadata_path,
                    f"frequency{freq}/elevationAntennaPattern",
                ]
            )
            grp = f[grp_path]
            for ds_arr in grp.values():
                if isinstance(ds_arr, h5py.Group):
                    raise TypeError(
                        f"unexpected HDF5 Group found in {grp_path}."
                        " Metadata Groups should only contain Datasets."
                    )
                ds_path = ds_arr.name

                n_dim = np.ndim(ds_arr)
                if n_dim in (0, 1):
                    # Scalar and 1D Datasets in this group are coordinate
                    # dimensions and georeferencing info -- not metadata LUTs.
                    # Skip.
                    pass
                elif n_dim != 2:
                    raise ValueError(
                        f"The elevationAntennaPattern metadata group should"
                        " should only contain scalar, 1D, or 2D Datasets."
                        f" Dataset contains {n_dim} dimensions: {ds_path}"
                    )
                else:
                    yield self._build_metadata_lut(f=f, ds_arr=ds_arr)

    @abstractmethod
    def get_layers_for_browse(self) -> dict[str, list[str]]:
        """
        Determine which polarization layers to use to generate the browse image.

        Returns
        -------
        layers_for_browse : dict
            Dict of the polarizations layers to use. Its structure is:
                layers_for_browse[<freq>] : List of the polarization(s)
                                            e.g. ['HH','HV'] for SLCs,
                                            or ["HHHH", "HVHV"] for GCOV
        """
        pass

    @staticmethod
    @abstractmethod
    def save_browse(
        pol_imgs: Mapping[str, np.ndarray], filepath: str | os.PathLike
    ) -> None:
        """
        Save given polarization images to a RGB or Grayscale PNG.

        Dimensions of the output PNG (in pixels) will be the same as the
        dimensions of the input polarization image array(s). (No scaling will
        occur.) Non-finite values will be made transparent.

        Parameters
        ----------
        pol_imgs : dict of numpy.ndarray
            Dictionary of 2D array(s) that will be mapped to specific color
            channel(s) for the output browse PNG.
            If there are multiple image arrays, they must have identical shape.
            Format of dictionary:
                pol_imgs[<polarization>] : <2D numpy.ndarray image>
            Example:
                pol_imgs['HHHH'] : <2D numpy.ndarray image>
                pol_imgs['VVVV'] : <2D numpy.ndarray image>
        filepath : path-like
            Full filepath for where to save the browse image PNG.

        Notes
        -----
        Provided image array(s) must previously be image-corrected. This
        function will take the image array(s) as-is and will not apply
        additional image correction processing to them. This function directly
        combines the image(s) into a single browse image.
        If there are multiple input images, they must be thoughtfully prepared
        and standardized relative to each other prior to use by this function.
        For example, trying to combine a Freq A 20 MHz image
        and a Freq B 5 MHz image into the same output browse image might not go
        well, unless the image arrays were properly prepared and standardized
        in advance.
        """
        pass

    @contextmanager
    def get_raster(
        self, freq: str, pol: str
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Context Manager for a *RasterWithStats for the specified imagery raster.

        Parameters
        ----------
        freq : str
            One of the frequencies returned by `self.freqs()`.
        pol : str
            The desired polarization.
              For RSLC and GSLC, use e.g. "HH", "HV",
              For GCOV, use e.g. "HHVV"

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
            Warning: the input NISAR file cannot be opened by ISCE3 until
            this context manager is exited.

        Raises
        ------
        DatasetNotFoundError
            If the file does not contain the requested raster dataset,
            or if any of the corresponding metadata for that raster are
            not located.
        """
        if freq not in self.freqs:
            raise ValueError(f"{freq=}, must be one of: {self.freqs=}")

        poss_pols = nisarqa.get_possible_pols(
            product_type=self.product_type.lower()
        )
        if pol not in poss_pols:
            raise ValueError(f"{pol=}, must be one of: {poss_pols}.")

        path = self._layers[freq][pol]

        with h5py.File(self.filepath, "r") as in_file:
            if path not in in_file:
                errmsg = f"Input file does not contain raster {path}"
                raise nisarqa.DatasetNotFoundError(errmsg)
            yield self._get_raster_from_path(
                h5_file=in_file, raster_path=path, parse_stats=True
            )

    def _get_raster_name(self, raster_path: str) -> str:
        """
        Return a name for the raster, e.g. 'RSLC_LSAR_A_HH'.

        Parameters
        ----------
        raster_path : str
            Full path in `h5_file` to the desired raster dataset.
            Example:
                "/science/LSAR/GSLC/grids/frequencyA/HH"

        Returns
        -------
        name : str
            The human-understandable name that is derived from the dataset.
            Example:
                "GSLC_L_A_HH"
        """
        freq = "A" if ("frequencyA" in raster_path) else "B"
        pol = raster_path.split("/")[-1]
        name = f"{self.product_type}_{self.band}_{freq}_{pol}"

        return name

    @cached_property
    def _layers(self) -> dict[str, dict[str, str]]:
        """
        Locate available bands, frequencies, and polarizations in the product.

        Returns
        -------
        layers : nested dict of str
            Nested dict of paths to input file raster datasets.
            Format: layers[<freq>][<pol>] -> str
            Example:
                layers["A"]["HH"] -> "/science/LSAR/RSLC/swaths/frequencyA/HH"
        """
        # Discover images in input file and populate the `pols` dictionary
        with h5py.File(self.filepath) as h5_file:
            layers = {}
            for freq in self.freqs:
                path = self.get_freq_path(freq=freq)
                layers[freq] = {}

                for pol in nisarqa.get_possible_pols(self.product_type.lower()):
                    raster_path = f"{path}/{pol}"
                    if raster_path in h5_file:
                        layers[freq][pol] = raster_path

        # Sanity Check - if a band/freq does not have any polarizations,
        # this is a validation error. This check should be handled during
        # the validation process before this function was called,
        # not the quality process, so raise an error.
        # In the future, this step might be moved earlier in the
        # processing, and changed to be handled via: 'log the error
        # and remove the band from the dictionary'
        for freq in layers:
            # Empty dictionaries evaluate to False in Python
            if not layers[freq]:
                raise ValueError(
                    "Provided input file does not have any polarizations"
                    f" included under band {self.band}, frequency {freq}."
                )

        return layers

    def get_pols(self, freq: str) -> tuple[str, ...]:
        """
        Get a tuple of the available polarizations for frequency `freq`.

        Parameters
        ----------
        freq : str
            One of the frequencies in `self.freqs`.

        Returns
        -------
        pols : tuple of str
            An tuple of the available polarizations for the requested
            frequency.
                Example for RSLC or GSLC: ("HH", "VV")
                Example for GCOV: ("HHHH", "HVHH", "VVVV")
        """
        if freq not in self.freqs:
            raise ValueError(
                f"Requested frequency {freq}, but product only contains"
                f" frequencies {self.freqs}."
            )

        layers = self._layers
        pols = tuple(layers[freq].keys())

        if not pols:
            # No polarizations were found for this frequency
            errmsg = f"No polarizations were found for frequency {freq}"
            raise nisarqa.DatasetNotFoundError(errmsg)

        return pols

    @cached_property
    def _calibration_metadata_path(self) -> str:
        """
        Path in the input file to the `metadata/calibrationInformation` Group.

        Returns
        -------
        path : str
            Path in input file to the metadata/calibrationInformation Group.
        """
        return "/".join([self._metadata_group_path, "calibrationInformation"])

    @contextmanager
    def get_noise_eq_group(self, freq: str) -> Iterator[h5py.Group]:
        """
        Get the `noiseEquivalentBackscatter` h5py Group.

        Parameters
        ----------
        freq : {'A', 'B'}
            The frequency sub-band. Must be a valid sub-band in the product.

        Yields
        ------
        neb_grp : h5py.Group
            Noise Equivalent Backscatter (NEB) Group in the input product for
            the given `freq`.

        Raises
        ------
        nisarqa.InvalidNISARProductError
            The returned `neb_grp` will be correct for products generated with
            ISCE3 R4 and later, but is not guaranteed for earlier test datasets.
            If QA cannot find this Group at a known path, this error is raised.

        Warnings
        --------
        ISCE3 products generated for R4 with product specification version
        1.1.0 to <1.2.0 should contain a group called `nes0`. Some products
        generated with product specifications <1.1.0 also contain a `nes0`
        group, but this cannot be guaranteed, or the nes0 data might follow
        an entirely different specification structure.
        ISCE3 products generated for R4.0.4 or later with product specification
        version >=1.2.0 should contain an equivalent group called
        `noiseEquivalentBackscatter`. (For R4.0.4, `nes0` was renamed.)
        Unfortunately, the official ISCE3 releases do not perfectly align
        with updates to the product specification version, so some products
        will have out-of-sync product spec version numbers and dataset names.

        For simplicity, QA should only support data products with the
        newer NEB structure (>= ISCE3 R4).

        Notes
        -----
        Typically, QA product reader returns a actual values, and not an
        h5py.Group. However, this function is being used by `run_neb_tool()`,
        which needs to wholesale copy the Group and its contents recursively.
        """
        log = nisarqa.get_logger()
        spec = nisarqa.Version.from_string(self.product_spec_version)

        with h5py.File(self.filepath, "r") as f:
            grp = f[f"{self._calibration_metadata_path}/frequency{freq}"]
            if "noiseEquivalentBackscatter" in grp:
                yield grp["noiseEquivalentBackscatter"]
            elif "nes0" in grp:
                if spec >= nisarqa.Version(1, 2, 0):
                    nisarqa.get_logger().error(
                        "Input product has product specification version"
                        f" {spec} and contains a `nes0` Group. As of"
                        " product specification version 1.2.0, this should"
                        " instead be named `noiseEquivalentBackscatter`."
                    )
                yield grp["nes0"]
            else:
                # product does not contain a "nes0" group (old spec)
                # nor a "noiseEquivalentBackscatter" group. Log and fail.
                msg = (
                    f"For frequency {freq}, product does not contain a"
                    " Group with noise equivalent backscatter information"
                    " at a known path."
                )

                if spec < nisarqa.Version(1, 1, 0):
                    log.error(
                        "Input product was generated with an older product"
                        " spec. " + msg
                    )
                else:
                    log.error(msg)
                raise nisarqa.InvalidNISARProductError(msg)


@dataclass
class SLC(NonInsarProduct):

    def get_pols(self, freq: str) -> tuple[str, ...]:
        pols = super().get_pols(freq)

        # Sanity checks
        # Check the "discovered" polarizations against the expected
        # `listOfPolarizations` dataset contents
        list_of_pols_ds = self.get_list_of_polarizations(freq=freq)
        if set(pols) != set(list_of_pols_ds):
            errmsg = (
                f"Frequency {freq} contains polarizations {pols}, but"
                f" `listOfPolarizations` says {list_of_pols_ds}"
                " should be available."
            )
            raise nisarqa.InvalidNISARProductError(errmsg)

        return pols

    def get_layers_for_browse(self) -> dict[str, list[str]]:
        """
        Get frequencies+polarization images to use for the SLC Browse Image.

        This function should be used in conjunction with `save_browse()`,
        which handles the final greyscale or color channel assignments.

        See `Notes` for details on possible NISAR modes and assigned channels
        for LSAR band.
        Prioritization order to select the freq/pol to use:
            For frequency: Freq A then Freq B.
            For polarization: 'HH', then 'VV', then first polarization found.

        SSAR is currently only minimally supported, so only a grayscale image
        will be created.

        Returns
        -------
        layers_for_browse : dict
            A dictionary containing the frequency+polarization combinations
            that will be used to generate the browse image. Its structure is:
            layers_for_browse['A']     : list of str, optional
                                            List of the Freq A polarization(s)
                                            required to create the browse image.
                                            A subset of:
                                            ['HH','HV','VV','RH','RV','LH','LV']
            layers_for_browse['B']     : list of str, optional
                                            List of the Freq B polarizations
                                            required to create the browse image.
                                            A subset of ['HH','VV']

        Notes
        -----
        Possible modes for L-Band, as of Feb 2023:
            Single Pol      SP HH:      20+5, 40+5, 77
            Single Pol      SP VV:      5, 40
            Dual Pol        DP HH/HV:   77, 40+5, 20+5
            Dual Pol        DP VV/VH:   5, 77, 20+5, 40+5
            Quasi Quad Pol  QQ:         20+20, 20+5, 40+5, 5+5
            Quad Pol        QP:         20+5, 40+5
            Quasi Dual Pol  QD HH/VV:   5+5
            Compact Pol     CP RH/RV:   20+20           # an experimental mode
        Single Pol (SP) Assignment:
            - Freq A CoPol
            else:
            - Freq B CoPol
        DP and QQ Assignment:
            All image layers should come from a single frequency. Freq A has
            priority over Freq B.
            Two example assignments:
            - Freq A: Red=HH, Green=HV, Blue=HH
            - Freq B: Red=VV, Green=VH, Blue=VV
        QP Assignment:
            - Freq A: Red=HH, Green=HV, Blue=VV
        QD Assignment:
            - Freq A: Red=HH, Blue=HH; Freq B: Green=VV
        CP Assignment:
            - Freq A: Grayscale of one pol image, with
                    Prioritization order: ['RH','RV','LH','LV']

        See Also
        --------
        save_browse :
            Assigns the layers from this function to greyscale or RGBA channels.
        """
        layers_for_browse = {}
        log = nisarqa.get_logger()

        # Get the frequency sub-band containing science mode data.
        freq = self.science_freq
        science_pols = self.get_pols(freq=freq)

        # SSAR is not fully supported by QA, so just make a simple grayscale
        if self.band == "S":
            # Prioritize Co-Pol
            if "HH" in science_pols:
                layers_for_browse[freq] = ["HH"]
            elif "VV" in science_pols:
                layers_for_browse[freq] = ["VV"]
            else:
                # Take the first available pol
                layers_for_browse[freq] = [science_pols[0]]

            return layers_for_browse

        # The input file contains LSAR data. Will need to make
        # grayscale/RGB channel assignments

        def _assign_layers_single_freq(freq: str) -> None:
            """
            Populate `layers_for_browse` for `freq` per pols in `science_pols`.

            This function assumes all images should come from the same
            frequency group, and modifies `layers_for_browse` accordingly.

            Do not use for quasi-dual.
            """
            assert freq in ("A", "B")

            n_pols = len(science_pols)

            if all(
                pol.startswith("L") or pol.startswith("R")
                for pol in science_pols
            ):
                # Compact Pol. This is not a planned mode for LSAR,
                # and there is no test data, so simply make a grayscale image.

                # Per the Prioritization Order, use first available polarization
                for pol in ["RH", "RV", "LH", "LV"]:
                    if pol in science_pols:
                        layers_for_browse[freq] = [pol]
                        break

            elif n_pols == 1:
                # single pol mode
                layers_for_browse[freq] = science_pols

            else:
                # likely Dual Pol, Quasi Quad, Quad Pol

                # HH has priority over VV
                if "HH" in science_pols and "HV" in science_pols:
                    layers_for_browse[freq] = ["HH", "HV"]
                    if "VV" in science_pols:
                        # likely quad pol
                        layers_for_browse[freq].append("VV")

                elif "VV" in science_pols and "VH" in science_pols:
                    layers_for_browse[freq] = ["VV", "VH"]

                else:
                    # Warn, but do not fail. Attempt to continue QA.
                    log.warning(
                        "Product contains an unexpected configuration of"
                        " Frequencies and Polarizations. Please verify the"
                        " input product is as intended."
                    )

                    # Take the first available pol and make greyscale image
                    for pol in ["HH", "VV", "HV", "VH"]:
                        if pol in science_pols:
                            layers_for_browse[freq] = [pol]
                            break
                    else:
                        raise ValueError(
                            f"Input product Frequency {freq} contains unexpected"
                            f" polarization images {science_pols}."
                        )

        # For the browse images, only use images from one frequency; the
        # exception is quasi-dual, where we use layers from both A and B.

        # Identify and handle the quasi-dual case
        b_pols = self.get_pols(freq="B") if "B" in self.freqs else []
        if (freq == "A" and science_pols == ["HH"]) and b_pols == ["VV"]:
            # Quasi Dual Pol: Freq A has HH, Freq B has VV, and there
            # are no additional image layers available
            layers_for_browse["A"] = ["HH"]
            layers_for_browse["B"] = ["VV"]
        elif (freq == "A" and science_pols == ["VV"]) and b_pols == ["HH"]:
            # Quasi Dual Pol: Freq A has VV, Freq B has HH, and there
            # are no additional image layers available
            layers_for_browse["A"] = ["VV"]
            layers_for_browse["B"] = ["HH"]
        else:
            # Assign layers using only images from the primary science freq
            _assign_layers_single_freq(freq=freq)

        # Sanity Check
        if ("A" not in layers_for_browse) and ("B" not in layers_for_browse):
            raise ValueError(
                "Current Mode (configuration) of the NISAR input file"
                " not supported for browse image."
            )

        return layers_for_browse

    @staticmethod
    def save_browse(
        pol_imgs: Mapping[str, np.ndarray], filepath: str | os.PathLike
    ) -> None:
        """
        Save images in `pol_imgs` to a RGB or Grayscale PNG with transparency.

        Dimensions of the output PNG (in pixels) will be the same as the
        dimensions of the input polarization image array(s). (No scaling will
        occur.) Non-finite values will be made transparent.
        Color Channels will be assigned per the following pseudocode:
            If pol_imgs.keys() contains only one image, then:
                grayscale = <that image>
            If pol_imgs.keys() is ['HH','HV','VV'], then:
                red = 'HH'
                green = 'HV'
                blue = 'VV'
            If pol_imgs.keys() is ['HH','HV'], then:
                red = 'HH'
                green = 'HV'
                blue = 'HH'
            If pol_imgs.keys() is ['HH','VV'], then:
                red = 'HH'
                green = 'VV'
                blue = 'HH'
            If pol_imgs.keys() is ['VV','VH'], then:
                red = 'VV'
                green = 'VH'
                blue = 'VV'
            Otherwise, one image in `pol_imgs` will be output as grayscale.

        Parameters
        ----------
        pol_imgs : dict of numpy.ndarray
            Dictionary of 2D array(s) that will be mapped to specific color
            channel(s) for the output browse PNG.
            If there are multiple image arrays, they must have identical shape.
            Format of dictionary:
                pol_imgs[<polarization>] : <2D numpy.ndarray image>, where
                    <polarization> must be a subset of: 'HH', 'HV', 'VV', 'VH',
                                                        'RH', 'RV', 'LV', 'LH',
            Example:
                pol_imgs['HH'] : <2D numpy.ndarray image>
                pol_imgs['VV'] : <2D numpy.ndarray image>
        filepath : path-like
            Full filepath for where to save the browse image PNG.

        Notes
        -----
        Provided image array(s) must previously be image-corrected. This
        function will take  image array(s) as-is and will not apply additional
        image correction processing to them. This function directly combines
        the image(s) into a single browse image.
        If there are multiple input images, they must be thoughtfully prepared
        and standardized relative to each other prior to use by this function.
        For example, trying to combine a Freq A 20 MHz image
        and a Freq B 5 MHz image into the same output browse image might not go
        well, unless the image arrays were properly prepared and standardized
        in advance.
        """
        # WLOG, get the shape of the image arrays
        # They should all be the same shape; the check for this is below.
        arbitrary_img = next(iter(pol_imgs.values()))
        img_2D_shape = np.shape(arbitrary_img)
        for img in pol_imgs.values():
            # Input validation check
            if np.shape(img) != img_2D_shape:
                raise ValueError(
                    "All image arrays in `pol_imgs` must have the same shape."
                )

        # Assign color channels
        set_of_pol_imgs = set(pol_imgs)

        if set_of_pol_imgs == {"HH", "HV", "VV"}:
            # Quad Pol
            red = pol_imgs["HH"]
            green = pol_imgs["HV"]
            blue = pol_imgs["VV"]
        elif set_of_pol_imgs == {"HH", "HV"}:
            # dual pol horizontal transmit, or quasi-quad
            red = pol_imgs["HH"]
            green = pol_imgs["HV"]
            blue = pol_imgs["HH"]
        elif set_of_pol_imgs == {"HH", "VV"}:
            # quasi-dual mode
            red = pol_imgs["HH"]
            green = pol_imgs["VV"]
            blue = pol_imgs["HH"]
        elif set_of_pol_imgs == {"VV", "VH"}:
            # dual-pol only, vertical transmit
            red = pol_imgs["VV"]
            green = pol_imgs["VH"]
            blue = pol_imgs["VV"]
        else:
            # If we get into this "else" statement, then
            # either there is only one image provided (e.g. single pol),
            # or the images provided are not one of the expected cases.
            # Either way, WLOG plot one of the image(s) in `pol_imgs`.
            gray_img = pol_imgs.popitem()[1]
            nisarqa.rslc.plot_to_grayscale_png(
                img_arr=gray_img, filepath=filepath
            )

            # This `else` is a catch-all clause. Return early, so that
            # we do not try to plot to RGB
            return

        nisarqa.rslc.plot_to_rgb_png(
            red=red, green=green, blue=blue, filepath=filepath
        )

    def metadata_geometry_luts(
        self,
    ) -> Iterator[nisarqa.MetadataLUT2D]:
        """
        Generator for all metadata LUTs in geometry calibration info Group.

        Yields
        ------
        ds : nisarqa.MetadataLUT2D
            The next MetadataLUT2D in this Group:
                `../metadata/calibrationInformation/geometry`
        """
        with h5py.File(self.filepath, "r") as f:
            grp_path = "/".join([self._calibration_metadata_path, "geometry"])
            grp = f[grp_path]
            for ds_arr in grp.values():
                if isinstance(ds_arr, h5py.Group):
                    raise TypeError(
                        f"unexpected HDF5 Group found in {grp_path}."
                        " Metadata Groups should only contain Datasets."
                    )
                ds_path = ds_arr.name

                n_dim = np.ndim(ds_arr)
                if n_dim in (0, 1):
                    # Scalar and 1D Datasets in this group are coordinate
                    # dimensions and georeferencing info -- not metadata LUTs.
                    # Skip.
                    pass
                elif n_dim != 2:
                    raise ValueError(
                        f"The geometry metadata group should only contain"
                        " scalar, 1D, or 2D Datasets."
                        f" Dataset contains {n_dim} dimensions: {ds_path}"
                    )
                else:
                    yield self._build_metadata_lut(f=f, ds_arr=ds_arr)


@dataclass
class NonInsarGeoProduct(NonInsarProduct, NisarGeoProduct):
    @cached_property
    def browse_x_range(self) -> tuple[float, float]:
        # All rasters used for the browse should have the same grid specs
        # So, WLOG parse the specs from the first one of them.
        layers = self.get_layers_for_browse()
        freq = next(iter(layers.keys()))
        pol = layers[freq][0]

        with self.get_raster(freq=freq, pol=pol) as img:
            x_start = img.x_start
            x_stop = img.x_stop

        return (x_start, x_stop)

    @cached_property
    def browse_y_range(self) -> tuple[float, float]:
        # All rasters used for the browse should have the same grid specs
        # So, WLOG parse the specs from the first one of them.
        layers = self.get_layers_for_browse()
        freq = next(iter(layers.keys()))
        pol = layers[freq][0]

        with self.get_raster(freq=freq, pol=pol) as img:
            y_start = img.y_start
            y_stop = img.y_stop

        return (y_start, y_stop)


@dataclass
class RSLC(SLC, NisarRadarProduct):
    @property
    def product_type(self) -> str:
        return "RSLC"

    @cached_property
    def _data_group_path(self) -> str:
        path = super()._data_group_path

        # Special handling for old UAVSAR test datasets that have paths
        # like "/science/LSAR/SLC/..."
        with h5py.File(self.filepath) as f:
            if path in f:
                return path
            elif self.product_spec_version == "0.0.0":
                slc_path = path.replace("RSLC", "SLC")
                if slc_path in f:
                    return slc_path
                else:
                    raise ValueError(
                        "Could not determine the path to the group containing"
                        " the primary datasets."
                    )
            else:
                raise ValueError(
                    f"self._data_group_path determined to be {path}, but this"
                    " is not a valid path in the input file."
                )

    @cached_property
    def _metadata_group_path(self) -> str:
        path = super()._metadata_group_path

        # Special handling for old UAVSAR test datasets that have paths
        # like "/science/LSAR/SLC/metadata..."
        with h5py.File(self.filepath) as f:
            if path in f:
                return path
            elif self.product_spec_version == "0.0.0":
                slc_path = path.replace("RSLC", "SLC")
                if slc_path in f:
                    return slc_path
                else:
                    raise ValueError(
                        "Could not determine the path to the group containing"
                        " the product metadata."
                    )
            else:
                raise ValueError(
                    f"self._metadata_group_path determined to be {path}, but"
                    " this is not a valid path in the input file."
                )

    def get_scene_center_along_track_spacing(self, freq: str) -> float:
        """
        Get along-track spacing at mid-swath.

        Get the along-track spacing at the center of the swath, in meters, of
        the radar grid corresponding to the specified frequency sub-band.

        Parameters
        ----------
        freq : {'A', 'B'}
            The frequency sub-band. Must be a valid sub-band in the product.

        Returns
        -------
        az_spacing : float
            The mid-swath along-track sample spacing, in meters.
        """

        # Future Alert!
        # The name of the dataset accessed via this function is also
        # accessed in NisarRadarProduct._get_raster_from_path().
        # It is not ideal to have the hardcoded path in two places.
        # It is also not ideal to need to fully initialize an entire
        # RadarRaster just to access a single dataset.
        # Also, only RSLC can access `sceneCenterAlongTrackSpacing` with only
        # `freq` as an input; RIFG/RUNW/ROFF also need to know the layer group.
        # For simplicity, let's hard-code this path in two places,
        # and update later if/when a better design pattern is needed.
        # See: RSLC.get_slant_range_spacing() for a related issue.

        @lru_cache
        def _get_scene_center_along_track_spacing(freq: str) -> float:
            path = f"{self.get_freq_path(freq)}/sceneCenterAlongTrackSpacing"
            with h5py.File(self.filepath) as f:
                try:
                    return f[path][()]
                except KeyError as e:
                    raise nisarqa.DatasetNotFoundError from e

        return _get_scene_center_along_track_spacing(freq)

    def get_slant_range_spacing(self, freq: str) -> float:
        """
        Get slant range spacing.

        Get the slant range spacing, in meters, of the radar grid corresponding
        to the specified frequency sub-band.

        Parameters
        ----------
        freq : {'A', 'B'}
            The frequency sub-band. Must be a valid sub-band in the product.

        Returns
        -------
        rg_spacing : float
            The slant range sample spacing, in meters.
        """

        # Future Alert!
        # It makes sense for this dataset to be an attribute in RadarRaster.
        # However, for now, only RSLC() products need access to this dataset,
        # and we should not clutter RIFG/RUNW/ROFF RadarRasters.
        # Additionally, like RSLC.get_scene_center_along_track_spacing(),
        # it is not ideal to need to fully initialize an entire
        # RadarRaster just to access a single dataset.
        # For simplicity, let's use this design pattern for now,
        # and update later if/when a better design pattern is needed.

        @lru_cache
        def _get_slant_range_spacing(freq: str) -> float:
            path = f"{self.get_freq_path(freq)}/slantRangeSpacing"
            with h5py.File(self.filepath) as f:
                try:
                    return f[path][()]
                except KeyError as e:
                    raise nisarqa.DatasetNotFoundError from e

        return _get_slant_range_spacing(freq)

    def get_zero_doppler_time_spacing(self) -> float:
        """
        Get zero doppler time spacing.

        Get the zero doppler time spacing, in seconds, of the radar grid.
        This should be the same for both Frequency A and Frequency B.

        Returns
        -------
        zero_doppler_time_spacing : float
            The zero_doppler_time sample spacing, in seconds.
        """

        # Future Alert!
        # It makes sense for this dataset to be an attribute in RadarRaster.
        # However, for now, only RSLC() products need access to this dataset,
        # and we should not clutter RIFG/RUNW/ROFF RadarRasters.
        # Additionally, like RSLC.get_slant_range_spacing(),
        # it is not ideal to need to fully initialize an entire
        # RadarRaster just to access a single dataset.
        # For simplicity, let's use this design pattern for now,
        # and update later if/when a better design pattern is needed.

        @lru_cache
        def _get_zero_doppler_time_spacing() -> float:
            path = f"{self._data_group_path}/zeroDopplerTimeSpacing"
            with h5py.File(self.filepath) as f:
                try:
                    return f[path][()]
                except KeyError as e:
                    raise nisarqa.DatasetNotFoundError from e

        return _get_zero_doppler_time_spacing()

    def get_processed_center_frequency(self, freq: str) -> float:
        """
        Get processed center frequency.

        Get the processed center frequency, in Hz, of the radar signal
        corresponding to the specified frequency sub-band. (It is assumed
        that the input product's processed center frequency is in Hz.)

        Parameters
        ----------
        freq : {'A', 'B'}
            The frequency sub-band. Must be a valid sub-band in the product.

        Returns
        -------
        proc_center_freq : float
            The processed center frequency, in Hz.
        """

        @lru_cache
        def _get_proc_center_freq(freq: str) -> float:
            path = f"{self.get_freq_path(freq)}/processedCenterFrequency"
            log = nisarqa.get_logger()
            with h5py.File(self.filepath) as f:
                try:
                    proc_center_freq = f[path][()]
                except KeyError as e:
                    raise nisarqa.DatasetNotFoundError from e

                # As of R3.4, units for `processedCenterFrequency` are "Hz",
                # not MHz. Do a soft check that this the units are correct.
                try:
                    units = f[path].attrs["units"]
                except KeyError:
                    errmsg = (
                        "`processedCenterFrequency` missing 'units' attribute."
                    )
                    log.error(errmsg)

                units = nisarqa.byte_string_to_python_str(units)
                # units should be either "hz" or "hertz", and not MHz
                if (units[0].lower() != "h") or (units[-1].lower() != "z"):
                    errmsg = (
                        "Input product's `processedCenterFrequency` dataset"
                        f" has units of {units}, but should be in hertz."
                    )
                    log.error(errmsg)

            return proc_center_freq

        return _get_proc_center_freq(freq)

    def get_rfi_likelihood_path(self, freq: str, pol: str) -> str:
        """
        Get the path to the RFI likelihood h5py Dataset.

        Parameters
        ----------
        freq : {'A', 'B'}
            The frequency sub-band. Must be a valid sub-band in the product.
        pol : str
            The desired polarization, e.g. "HH" or "HV".

        Returns
        -------
        rfi_likelihood_path : str
            The path to the radio frequency interference (RFI) likelihood
            Dataset for the given freq and pol.

        Warnings
        --------
        `rfiLikelihood` was added in ISCE3 v0.17.0 for R3.4.1.
        Unfortunately, that release does not correspond directly to product
        specification version number. Product Specification v1.1.0 and later
        should have this dataset, but it's messy to algorithmically
        handle the products generated prior to that. The returned
        `rfi_likelihood_path` will be correct for products generated with
        ISCE3 v0.17.0 and later, but might not exist in earlier test datasets.
        The calling function should handle this case accordingly.

        See Also
        --------
        copy_rfi_metadata_to_stats_h5 :
            Copies RFI likelihood Dataset from the input product to STATS.h5.

        Notes
        -----
        Typically, QA returns the Dataset's actual values, and not a path
        to an h5py.Dataset. However, this Dataset is only being used by
        `copy_rfi_metadata_to_stats_h5()`, which needs to wholesale copy
        the Dataset and its Attributes. By returning just the path, then
        any new Attributes in subsequent ISCE3 releases will be automatically
        get copied as well.
        """
        path = (
            f"{self._calibration_metadata_path}/"
            + f"frequency{freq}/{pol}/rfiLikelihood"
        )

        spec = nisarqa.Version.from_string(self.product_spec_version)
        if spec < nisarqa.Version(1, 1, 0):
            nisarqa.get_logger().warning(
                "Input product was generated with an older product spec; the"
                " `rfiLikelihood` Dataset might not exist for"
                f" frequency {freq}, polarization {pol}. Path: {path}"
            )

        return path

    def metadata_crosstalk_luts(
        self,
    ) -> Iterator[nisarqa.MetadataLUT1D]:
        """
        Generator for all metadata LUTs in crosstalk calibration info Group.

        Yields
        ------
        ds : nisarqa.MetadataLUT1D
            The next MetadataLUT1D in this Group:
                `../metadata/calibrationInformation/crosstalk`
        """
        with h5py.File(self.filepath, "r") as f:
            grp_path = "/".join([self._calibration_metadata_path, "crosstalk"])
            grp = f[grp_path]
            for ds_arr in grp.values():
                if isinstance(ds_arr, h5py.Group):
                    raise TypeError(
                        f"unexpected HDF5 Group found in {grp_path}."
                        " Metadata Groups should only contain Datasets."
                    )
                ds_path = ds_arr.name

                n_dim = np.ndim(ds_arr)
                if n_dim not in (0, 1):
                    raise ValueError(
                        f"The crosstalk metadata group should only contain 1D"
                        f" Datasets. Dataset contains {n_dim}"
                        f" dimensions: {ds_path}"
                    )
                if grp_path.endswith("/slantRange") or (n_dim == 0):
                    pass
                else:
                    yield self._build_metadata_lut(f=f, ds_arr=ds_arr)


@dataclass
class GSLC(SLC, NonInsarGeoProduct):
    @property
    def product_type(self) -> str:
        return "GSLC"


@dataclass
class GCOV(NonInsarGeoProduct):
    @property
    def product_type(self) -> str:
        return "GCOV"

    def get_pols(self, freq: str) -> tuple[str, ...]:
        pols = super().get_pols(freq)

        # Sanity checks
        # Check the "discovered" polarizations against the expected
        # `listOfCovarianceTermss` dataset contents
        list_of_pols_ds = self.get_list_of_covariance_terms(freq=freq)
        if set(pols) != set(list_of_pols_ds):
            errmsg = (
                f"Frequency {freq} contains terms {pols}, but"
                f" `listOfCovarianceTerms` says {list_of_pols_ds}"
                " should be available."
            )
            raise nisarqa.InvalidNISARProductError(errmsg)

        return pols

    def get_layers_for_browse(self) -> dict[str, list[str]]:
        """
        Assign polarizations to grayscale or RGBA channels for the Browse Image.

        Only on-diagonal terms will be used to create the browse image.
        See `Notes` for details on the possible NISAR modes and assigned
        channels for LSAR band.
        SSAR is currently only minimally supported, so only a grayscale image
        will be created. Prioritization order to select the freq/pol to use:
            For frequency: Freq A then Freq B.
            For polarization: 'HHHH', then 'VVVV', then first pol found.

        Returns
        -------
        layers_for_browse : dict
            A dictionary containing the frequency+polarization combinations
            that will be used to generate the browse image.
            For GCOV, either `layers_for_browse['A']` or
            `layers_for_browse['B']` will exist, but not both.
            Its structure is:
            layers_for_browse['A']  : list of str, optional
                                         List of the Freq A polarization(s)
                                         required to create the browse image.
                                         Warning: Only on-diag terms supported.
            layers_for_browse['B']  : list of str, optional
                                         List of the Freq B polarizations
                                         required to create the browse image.
                                         Warning: Only on-diag terms supported.

        See Also
        --------
        save_browse : Assigns color channels and generates the browse PNG.

        Notes
        -----
        Unlike RSLC products, the polarizations contained within a GCOV product
        do not map to the NISAR mode table. For GCOV, The user selects a subset
        of polarizations of the RSLC to process. With that subset, the GCOV
        SAS workflow verifies if it should symmetrize the cross-polarimetric
        channels (HV and VH) into a single cross-polarimetric channel (HV),
        and also verifies if it should generate the full covariance or only
        the diagonal terms.
        Usually polarimetric symmetrization is applied; symmetrization
        joins HV and VH into a single polarimetric channel HV.
        Layer selection for LSAR GCOV Browse:
        - Frequency A is used if available. Otherwise, Frequency B.
        - If only one polarization is available, or if the images are cross-pol,
        make one layer into grayscale. This function selects that layer.
        - Otherwise, generate an RGB color composition, per the algorithm
        described in `save_gcov_browse_img()`. This function will gather the
        largest subset of: {HHHH, VVVV, (HVHV or VHVH)}, in prep for that
        function.
        GCOV and RTC-S1 pixels are square on the ground, so the multilooking
        factor is the same in both directions, depending only in the expected
        output dimensions.
        """
        layers_for_browse = {}

        # Get the frequency sub-band containing science mode data.
        freq = self.science_freq
        science_pols = self.get_pols(freq=freq)

        # SSAR is not fully supported by QA, so just make a simple grayscale
        if self.band == "S":
            # Prioritize Co-Pol
            if "HHHH" in science_pols:
                layers_for_browse[freq] = ["HHHH"]
            elif "VVVV" in science_pols:
                layers_for_browse[freq] = ["VVVV"]
            else:
                # Take the first available on-diagonal term
                for pol in science_pols:
                    if pol[0:2] == pol[2:4]:
                        layers_for_browse[freq] = [pol]
                        break
                else:
                    # Take first available pol, even if it is an off-diag term
                    layers_for_browse[freq] = [science_pols[0]]

            return layers_for_browse

        # The input file contains LSAR data. Will need to make
        # grayscale/RGB channel assignments

        # Keep only the on-diagonal polarizations
        # (On-diag terms have the same first two letters as second two letters,
        # e.g. HVHV or VVVV.)
        science_pols = [p for p in science_pols if (p[0:2] == p[2:4])]
        n_pols = len(science_pols)

        # Sanity check: There should always be on-diag pols for GCOV
        if n_pols == 0:
            raise ValueError(
                "No on-diagonal polarizations found in input GCOV."
            )

        elif n_pols == 1:
            # Only one image; it will be grayscale
            layers_for_browse[freq] = science_pols

        elif all(p.startswith(("R", "L")) for p in science_pols):
            # Only compact pol(s) are available. Create grayscale.
            # Per the Prioritization Order, use first available polarization
            for pol in ("RHRH", "RVRV", "LHLH", "LVLV"):
                if pol in science_pols:
                    layers_for_browse[freq] = [pol]
                    break
            else:
                # Use first available pol
                layers_for_browse[freq] = [science_pols[0]]

            assert len(layers_for_browse[freq]) == 1

        else:
            # Only keep "HHHH", "HVHV", "VHVH", "VVVV".
            keep = [
                p
                for p in science_pols
                if (p in ("HHHH", "HVHV", "VHVH", "VVVV"))
            ]

            # Sanity Check
            assert len(keep) >= 1

            # If both cross-pol terms are available, only keep one
            if ("HVHV" in keep) and ("VHVH" in keep):
                if ("VVVV" in keep) and not ("HHHH" in keep):
                    # Only VVVV is in keep, and not HHHH. So, prioritize
                    # keeping VHVH with VVVV.
                    keep.remove("HVHV")
                else:
                    # prioritize keeping "HVHV"
                    keep.remove("VHVH")

            layers_for_browse[freq] = keep

        # Sanity Checks
        if ("A" not in layers_for_browse) and ("B" not in layers_for_browse):
            raise ValueError(
                "Input file must contain either Frequency A or Frequency B"
                " iamges."
            )

        if len(layers_for_browse[freq]) == 0:
            raise ValueError(
                f"The input file's Frequency {freq} group does not contain "
                "the expected polarization names."
            )

        return layers_for_browse

    @staticmethod
    def save_browse(
        pol_imgs: Mapping[str, np.ndarray], filepath: str | os.PathLike
    ) -> None:
        """
        Save the given polarization images to a RGB or Grayscale PNG.

        Dimensions of the output PNG (in pixels) will be the same as the
        dimensions of the input polarization image array(s). (No scaling will
        occur.) Non-finite values will be made transparent.
        Color Channels will be assigned per the following pseudocode:
            If pol_imgs.keys() contains only one image, then:
                grayscale = <that image>
            Else:
                Red: first available co-pol of the list [HHHH, VVVV]
                Green: first of the list [HVHV, VHVH, VVVV]
                if Green is VVVV:
                    Blue: HHHH
                else:
                    Blue: first co-pol of the list [VVVV, HHHH]

        Parameters
        ----------
        pol_imgs : dict of numpy.ndarray
            Dictionary of 2D array(s) that will be mapped to specific color
            channel(s) for the output browse PNG.
            If there are multiple image arrays, they must have identical shape.
            Format of dictionary:
                pol_imgs[<polarization>] : <2D numpy.ndarray image>, where
                    <polarization> is a subset of:
                                            'HHHH', 'HVHV', 'VVVV', 'VHVH',
                                            'RHRH', 'RVRV', 'LVLV', 'LHLH'
            Example:
                pol_imgs['HHHH'] : <2D numpy.ndarray image>
                pol_imgs['VVVV'] : <2D numpy.ndarray image>
        filepath : path-like
            Full filepath for where to save the browse image PNG.

        See Also
        --------
        select_layers_for_browse : Function to select the layers.

        Notes
        -----
        Provided image array(s) must previously be image-corrected. This
        function will take the image array(s) as-is and will not apply
        additional image correction processing to them. This function
        directly combines the image(s) into a single browse image.
        If there are multiple input images, they must be thoughtfully prepared
        and standardized relative to each other prior to use by this function.
        For example, trying to combine a Freq A 20 MHz image
        and a Freq B 5 MHz image into the same output browse image might not go
        well, unless the image arrays were properly prepared and standardized
        in advance.
        """
        # WLOG, get the shape of the image arrays
        # They should all be the same shape; the check for this is below.
        first_img = next(iter(pol_imgs.values()))
        img_2D_shape = np.shape(first_img)
        for img in pol_imgs.values():
            # Input validation check
            if np.shape(img) != img_2D_shape:
                raise ValueError(
                    "All image arrays in `pol_imgs` must have the same shape."
                )

        # Only on-diagonal terms are supported.
        if not set(pol_imgs.keys()).issubset(set(nisarqa.GCOV_DIAG_POLS)):
            raise ValueError(
                f"{pol_imgs.keys()=}, must be a subset of"
                f" {nisarqa.GCOV_DIAG_POLS}"
            )

        # Assign channels

        if len(pol_imgs) == 1:
            # Single pol. Make a grayscale image.
            nisarqa.products.rslc.plot_to_grayscale_png(
                img_arr=first_img, filepath=filepath
            )

            # Return early, so that we do not try to plot to RGB
            return

        # Initialize variables. Later, check to ensure they were all used.
        red = None
        blue = None
        green = None

        for pol in ["HHHH", "VVVV"]:
            if pol in pol_imgs:
                red = pol_imgs[pol]
                break

        # There should only be one cross-pol in the input
        if ("HVHV" in pol_imgs) and ("VHVH" in pol_imgs):
            raise ValueError(
                "`pol_imgs` should only contain one cross-pol image."
                f"It contains {pol_imgs.keys()}. Please update logic in "
                "`_select_layers_for_gcov_browse()`"
            )

        for pol in ["HVHV", "VHVH", "VVVV"]:
            if pol in pol_imgs:
                green = pol_imgs[pol]

                if pol == "VVVV":
                    # If we get here, this means two things:
                    #   1: no cross-pol images were available
                    #   2: only HHHH and VVVV are available
                    # So, final assignment should be R: HHHH, G: VVVV, B: HHHH
                    blue = pol_imgs["HHHH"]
                else:
                    for pol2 in ["VVVV", "HHHH"]:
                        if pol2 in pol_imgs:
                            blue = pol_imgs[pol2]
                            break
                break

        # Sanity Check, and catch-all logic to make a browse image
        if any(arr is None for arr in (red, green, blue)):
            # If we get here, then the images provided are not one of the
            # expected cases. WLOG plot one of the image(s) in `pol_imgs`.
            nisarqa.get_logger().warning(
                "The images provided are not one of the expected cases to form"
                " the GCOV browse image. Grayscale image will be created by"
                " default."
            )

            for gray_img in pol_imgs.values():
                nisarqa.products.rslc.plot_to_grayscale_png(
                    img_arr=gray_img, filepath=filepath
                )

        else:
            # Output the RGB Browse Image
            nisarqa.products.rslc.plot_to_rgb_png(
                red=red, green=green, blue=blue, filepath=filepath
            )

    def get_list_of_covariance_terms(self, freq: str) -> tuple[str, ...]:
        """
        Gets contents of ../frequency<freq>/listOfCovarianceTerms in input file.

        Returns
        -------
        list_of_cov : tuple of str
            The contents of `listOfCovarianceTerms` in the `.../frequency<freq>`
            group in the input file.  Example output: ("HHHH", "HVHV").

        Raises
        ------
        ValueError
            If `listOfCovarianceTerms` contains invalid options.
        KeyError
            If `listOfCovarianceTerms` is missing.
        """

        # `listOfCovarianceTerms` is always a child of the frequency group.
        freq_group = self.get_freq_path(freq=freq)

        with h5py.File(self.filepath) as f:
            # `listOfCovarianceTerms` should be in all frequency groups.
            # If not, let h5py handle raising an error message.
            list_of_cov = f[freq_group]["listOfCovarianceTerms"]
            nisarqa.verify_str_meets_isce3_conventions(ds=list_of_cov)

            if list_of_cov.shape == ():
                # dataset is scalar, not a list
                list_of_cov = [
                    nisarqa.byte_string_to_python_str(list_of_cov[()])
                ]
                nisarqa.get_logger().error(
                    "`listOfCovarianceTerms` dataset is a scalar string, should"
                    " be a list of strings."
                )
            else:
                list_of_cov = [
                    nisarqa.byte_string_to_python_str(my_str)
                    for my_str in list_of_cov[()]
                ]

            # Sanity check that the contents make sense
            # For GCOV, `get_possible_pols()` actually returns the
            # possible covariance terms, e.g. "HHHH", "HVHV".
            poss_pols = nisarqa.get_possible_pols(self.product_type.lower())

            if not set(list_of_cov).issubset(set(poss_pols)):
                raise ValueError(
                    "Input file's `listOfCovarianceTerms` dataset contains"
                    f" {list_of_cov}, but must be a subset of {poss_pols}."
                )

            return tuple(list_of_cov)


@dataclass
class InsarProduct(NisarProduct):
    def get_browse_freq_pol(self) -> tuple[str, str]:
        """
        Return the frequency and polarization for the browse image.

        Returns
        -------
        freq, pol : pair of str
            The frequency and polarization to use for the browse image.
        """
        for freq in ("A", "B"):
            if freq not in self.freqs:
                continue

            for pol in ("HH", "VV", "HV", "VH"):
                if pol not in self.get_pols(freq=freq):
                    continue

                return freq, pol

        # The input product does not contain the expected frequencies and/or
        # polarization combinations
        raise nisarqa.InvalidNISARProductError

    def _get_raster_name(self, raster_path: str) -> str:
        """
        Return a name for the raster, e.g. 'RSLC_LSAR_A_HH'.

        Parameters
        ----------
        raster_path : str
            Full path in `h5_file` to the desired raster dataset.
            Example:
                "/science/LSAR/GUNW/grids/frequencyA/interferogram/HH/unwrappedPhase"

        Returns
        -------
        name : str
            The human-understandable name that is derived from the dataset.
            Example:
                "GUNW_L_A_HH_unwrappedPhase"
        """
        # InSAR product. Example `raster_path` to parse:
        # "/science/LSAR/RIFG/swaths/frequencyA/pixelOffsets/HH/alongTrackOffset"
        band = self.band
        freq = "A" if ("frequencyA" in raster_path) else "B"
        path = raster_path.split("/")
        group = path[-3]
        pol = path[-2]
        layer = path[-1]

        # Sanity check
        assert pol in nisarqa.get_possible_pols(
            product_type=self.product_type.lower()
        )

        name = (
            f"{self.product_type.upper()}_{band}_{freq}_{group}_{pol}_{layer}"
        )
        return name

    @abstractmethod
    def _get_path_containing_freq_pol(self, freq: str, pol: str) -> str:
        """
        Return a potential valid path in input HDF5 containing `freq` and `pol`.

        This is a helper method (for e.g. `get_pols()`) which provides a
        generic way to get the path to a group in the product containing
        a particular frequency+polarization.
        The returned path may or may not exist in the NISAR input product.

        Parameters
        ----------
        freq : str
            Frequency of interest. Must be one of "A" or "B".
        pol : str
            Polarization of interest. Examples: "HH" or "HV".

        Returns
        -------
        path : str
            A potential valid path in the dataset which incorporates the
            requested freq and pol.

        See Also
        --------
        get_pols : Returns the polarizations for the requested frequency.
        """
        pass

    def get_pols(self, freq: str) -> tuple[str, ...]:
        """
        Get the polarizations for the given frequency.

        Parameters
        ----------
        freq : str
            Either "A" or "B".

        Returns
        -------
        pols : tuple[str]
            Tuple of the available polarizations in the input product
            for the requested frequency.

        Raises
        ------
        DatasetNotFoundError
            If no polarizations were found for this frequency.
        InvalidNISARProductError
            If the polarizations found are inconsistent with the polarizations
            listed in product's `listOfPolarizations` dataset for this freq.
        """
        if freq not in ("A", "B"):
            raise ValueError(f"{freq=}, must be one of 'A' or 'B'.")

        @lru_cache
        def _get_pols(freq):
            log = nisarqa.get_logger()
            pols = []
            with h5py.File(self.filepath) as f:
                for pol in nisarqa.get_possible_pols(self.product_type.lower()):
                    pol_path = self._get_path_containing_freq_pol(freq, pol)
                    try:
                        f[pol_path]
                    except KeyError:
                        log.info(
                            f"Did not locate polarization group at: {pol_path}"
                        )
                    else:
                        log.info(f"Located polarization group at: {pol_path}")
                        pols.append(pol)

            # Sanity checks
            # Check the "discovered" polarizations against the expected
            # `listOfPolarizations` dataset contents
            list_of_pols_ds = self.get_list_of_polarizations(freq=freq)
            if set(pols) != set(list_of_pols_ds):
                errmsg = (
                    f"Frequency {freq} contains polarizations {pols}, but"
                    f" `listOfPolarizations` says {list_of_pols_ds}"
                    " should be available."
                )
                raise nisarqa.InvalidNISARProductError(errmsg)

            if not pols:
                # No polarizations were found for this frequency
                errmsg = f"No polarizations were found for frequency {freq}"
                raise nisarqa.DatasetNotFoundError(errmsg)

            return pols

        return tuple(_get_pols(freq))

    def save_qa_metadata_to_h5(self, stats_h5: h5py.File) -> None:
        """
        Populate `stats_h5` file with a list of each available polarization.

        If the input file contains Frequency A, then this dataset will
        be created in `stats_h5`:
            /science/<band>/QA/data/frequencyA/listOfPolarizations

        If the input file contains Frequency B, then this dataset will
        be created in `stats_h5`:
            /science/<band>/QA/data/frequencyB/listOfPolarizations

        * Note: The paths are pulled from nisarqa.STATS_H5_QA_FREQ_GROUP.
        If the value of that global changes, then the path for the
        `listOfPolarizations` dataset(s) will change accordingly.

        Parameters
        ----------
        stats_h5 : h5py.File
            Handle to an h5 file where the list(s) of polarizations
            should be saved.
        """
        band = self.band

        for freq in self.freqs:
            list_of_pols = self.get_pols(freq=freq)

            nisarqa.create_dataset_in_h5group(
                h5_file=stats_h5,
                grp_path=nisarqa.STATS_H5_QA_FREQ_GROUP % (band, freq),
                ds_name="listOfPolarizations",
                ds_data=list_of_pols,
                ds_description=f"Polarizations for Frequency {freq}.",
            )


class WrappedGroup(InsarProduct):
    """
    Contains common functionality for products with a wrapped igram data group.

    As of Sept. 2023, this is only for RIFG and GUNW products. RUNW products
    do not contain this group.
    """

    @staticmethod
    @abstractmethod
    def _wrapped_group_path(freq: str, pol: str) -> str:
        """Path in input file to wrapped interferogram group."""
        pass

    def _get_path_containing_freq_pol(self, freq: str, pol: str) -> str:
        return self._wrapped_group_path(freq, pol)

    @contextmanager
    def get_wrapped_igram(
        self, freq: str, pol: str
    ) -> Iterator[nisarqa.RadarRaster | nisarqa.GeoRaster]:
        """
        Get the complex-valued wrapped interferogram image *Raster.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.

        Yields
        ------
        raster : RadarRaster or GeoRaster
            Generated *Raster for the requested dataset.
        """
        parent_path = self._wrapped_group_path(freq=freq, pol=pol)
        path = f"{parent_path}/wrappedInterferogram"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=False
            )

    @contextmanager
    def get_wrapped_coh_mag(
        self, freq: str, pol: str
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the wrapped coherence magnitude *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._wrapped_group_path(freq=freq, pol=pol)
        path = f"{parent_path}/coherenceMagnitude"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )


class UnwrappedGroup(InsarProduct):
    """
    Contains common functionality for products with unwrapped phase data group.

    As of Sept. 2023, this is only for RUNW and GUNW products. RIFG products
    do not contain this group.
    """

    @staticmethod
    @abstractmethod
    def _unwrapped_group_path(freq: str, pol: str) -> str:
        """Path in input file to unwrapped interferogram group.."""
        pass

    def _get_path_containing_freq_pol(self, freq: str, pol: str) -> str:
        return self._unwrapped_group_path(freq, pol)

    @contextmanager
    def get_unwrapped_phase(
        self, freq: str, pol: str
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the unwrapped phase image *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._unwrapped_group_path(freq=freq, pol=pol)
        path = f"{parent_path}/unwrappedPhase"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_connected_components(
        self, freq: str, pol: str
    ) -> Iterator[nisarqa.RadarRaster | nisarqa.GeoRaster]:
        """
        Get the connected components *Raster.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.

        Yields
        ------
        raster : RadarRaster or GeoRaster
            Generated *Raster for the requested dataset.
        """
        parent_path = self._unwrapped_group_path(freq=freq, pol=pol)
        path = f"{parent_path}/connectedComponents"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=False
            )

    @contextmanager
    def get_unwrapped_coh_mag(
        self, freq: str, pol: str
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the unwrapped coherence magnitude *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._unwrapped_group_path(freq=freq, pol=pol)
        path = f"{parent_path}/coherenceMagnitude"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_ionosphere_phase_screen(
        self, freq: str, pol: str
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the ionosphere phase screen *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._unwrapped_group_path(freq=freq, pol=pol)
        path = f"{parent_path}/ionospherePhaseScreen"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_ionosphere_phase_screen_uncertainty(
        self, freq: str, pol: str
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the ionosphere phase screen uncertainty *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._unwrapped_group_path(freq=freq, pol=pol)
        path = f"{parent_path}/ionospherePhaseScreenUncertainty"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )


class IgramOffsetsGroup(InsarProduct):
    """
    InSAR product where pixel offsets datasets only need freq and pol to locate.

    This includes RIFG, RUNW, GUNW products, but not ROFF and GOFF products.

    RIFG, RUNW, and GUNW's structure follow a pattern like:
        .../frequencyA/pixelOffsets/HH/<data set>
    ROFF and GOFF follow a pattern like:
        .../frequencyA/pixelOffsets/pixelOffsets/HH/layer2/<data set>

    Note that RIFG/RUNW/GUNW only require freq and pol to correctly locate the
    desired dataset, while ROFF and GOFF additionally require a layer number.

    See Also
    --------
    OffsetProduct :
        Class that handles the pixel offsets group for ROFF and GOFF products.
    """

    def _igram_offsets_group_path(self, freq: str, pol: str) -> str:
        """Path in input file to the pixel offsets group."""
        return f"{self.get_freq_path(freq)}/pixelOffsets/{pol}"

    def _get_path_containing_freq_pol(self, freq: str, pol: str) -> str:
        return self._igram_offsets_group_path(freq, pol)

    @contextmanager
    def get_along_track_offset(
        self, freq: str, pol: str
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the along track offsets image *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._igram_offsets_group_path(freq=freq, pol=pol)
        path = f"{parent_path}/alongTrackOffset"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_slant_range_offset(
        self, freq: str, pol: str
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the slant range offsets image *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._igram_offsets_group_path(freq=freq, pol=pol)
        path = f"{parent_path}/slantRangeOffset"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_correlation_surface_peak(
        self, freq: str, pol: str
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the correlation surface peak image *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._igram_offsets_group_path(freq=freq, pol=pol)
        path = f"{parent_path}/correlationSurfacePeak"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )


@dataclass
class RIFG(WrappedGroup, IgramOffsetsGroup, NisarRadarProduct):
    def __post_init__(self) -> None:
        super().__post_init__()

        # Make sure that all groups contain the same polarizations
        for freq in self.freqs:
            wrapped_pols = super(WrappedGroup, self).get_pols(freq)
            offset_pols = super(IgramOffsetsGroup, self).get_pols(freq)
            if set(wrapped_pols) != set(offset_pols):
                nisarqa.get_logger().error(
                    f"Wrapped interferogram group contains {wrapped_pols},"
                    f" but the pixel offsets group contains {offset_pols}."
                )

    @property
    def product_type(self) -> str:
        return "RIFG"

    def _wrapped_group_path(self, freq: str, pol: str) -> str:
        return f"{self.get_freq_path(freq)}/interferogram/{pol}"


@dataclass
class RUNW(UnwrappedGroup, IgramOffsetsGroup, NisarRadarProduct):
    def __post_init__(self) -> None:
        super().__post_init__()

        # Make sure that all groups contain the same polarizations
        for freq in self.freqs:
            unwrapped_pols = super(UnwrappedGroup, self).get_pols(freq)
            offset_pols = super(IgramOffsetsGroup, self).get_pols(freq)
            if set(unwrapped_pols) != set(offset_pols):
                nisarqa.get_logger().error(
                    f"Unwrapped interferogram group contains {unwrapped_pols},"
                    f" but the pixel offsets group contains {offset_pols}."
                )

    @property
    def product_type(self) -> str:
        return "RUNW"

    def _unwrapped_group_path(self, freq: str, pol: str) -> str:
        return f"{self.get_freq_path(freq)}/interferogram/{pol}"


@dataclass
class GUNW(
    WrappedGroup,
    UnwrappedGroup,
    IgramOffsetsGroup,
    NisarGeoProduct,
):
    def __post_init__(self) -> None:
        super().__post_init__()

        # Make sure that all groups contain the same polarizations
        for freq in self.freqs:
            wrapped_pols = super(WrappedGroup, self).get_pols(freq)
            unwrapped_pols = super(UnwrappedGroup, self).get_pols(freq)
            offset_pols = super(IgramOffsetsGroup, self).get_pols(freq)

            log = nisarqa.get_logger()
            if set(wrapped_pols) != set(unwrapped_pols):
                log.error(
                    f"Wrapped interferogram group contains {wrapped_pols},"
                    " but the unwrapped phase image group contains "
                    f" {unwrapped_pols}."
                )
            if set(wrapped_pols) != set(offset_pols):
                log.error(
                    f"Wrapped interferogram group contains {wrapped_pols},"
                    f" but the pixel offsets group contains {offset_pols}."
                )

    @property
    def product_type(self) -> str:
        return "GUNW"

    def _wrapped_group_path(self, freq, pol) -> str:
        return f"{self.get_freq_path(freq)}/wrappedInterferogram/{pol}"

    def _unwrapped_group_path(self, freq, pol) -> str:
        if self.product_spec_version == "0.0.0":
            return f"{self.get_freq_path(freq)}/interferogram/{pol}"
        else:
            # Path for product spec v0.9.0 (...and maybe subsequent versions?)
            return f"{self.get_freq_path(freq)}/unwrappedInterferogram/{pol}"

    @cached_property
    def browse_x_range(self) -> tuple[float, float]:
        freq, pol = self.get_browse_freq_pol()

        with self.get_unwrapped_phase(freq, pol) as img:
            x_start = img.x_start
            x_stop = img.x_stop

        return (x_start, x_stop)

    @cached_property
    def browse_y_range(self) -> tuple[float, float]:
        freq, pol = self.get_browse_freq_pol()

        with self.get_unwrapped_phase(freq, pol) as img:
            y_start = img.y_start
            y_stop = img.y_stop

        return (y_start, y_stop)


class OffsetProduct(InsarProduct):
    """
    InSAR product where datasets need freq, pol, and layer number to locate.

    This includes ROFF and GOFF products, but not RIFG, RUNW, GUNW products.

    RIFG, RUNW, and GUNW's structure follow a pattern like:
        .../frequencyA/pixelOffsets/HH/<data set>
    ROFF and GOFF follow a pattern like:
        .../frequencyA/pixelOffsets/pixelOffsets/HH/layer2/<data set>

    Note that RIFG/RUNW/GUNW only require freq and pol to correctly locate a
    specific dataset, while ROFF and GOFF additionally require a layer number.

    See Also
    --------
    IgramOffsetsGroup :
        Class that handles the pixel offsets group for RIFG, RUNW, and
        GUNW products.
    """

    def _get_raster_name(self, raster_path: str) -> str:
        """
        Return name for the raster, e.g. 'ROFF_L_A_HH_Layer1_alongTrackOffset'.

        Parameters
        ----------
        raster_path : str
            Full path in `h5_file` to the desired raster dataset.
            Example:
                "/science/LSAR/ROFF/swaths/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"

        Returns
        -------
        name : str
            The human-understandable name that is derived from the dataset.
            Example:
                "ROFF_L_A_HH_Layer1_alongTrackOffset"
        """
        # We have a ROFF or GOFF product. Example `raster_path` to parse:
        # "/science/LSAR/ROFF/swaths/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"
        band = self.band
        freq = "A" if ("frequencyA" in raster_path) else "B"
        path = raster_path.split("/")
        pol = path[-3]
        layer_num = path[-2]
        layer_name = path[-1]

        # Sanity check
        assert pol in nisarqa.get_possible_pols(
            product_type=self.product_type.lower()
        )

        name = f"{self.product_type.upper()}_{band}_{freq}_{pol}_{layer_num}_{layer_name}"
        return name

    @cached_property
    def available_layer_numbers(self) -> tuple[int, ...]:
        """
        The numbers of the available layers in the input product.

        Here, a "numbered layer" refers to the layer groups:
            /science/LSAR/GOFF/grids/frequencyA/pixelOffsets/HH/layer1/...
            /science/LSAR/GOFF/grids/frequencyA/pixelOffsets/HH/layer2/...

        Each layer group in a product contains an indentical set of
        raster and metadata datasets (although the values in those datasets
        are unique).

        As of Sept 2023, ISCE3 insar.yaml runconfig file allows users the
        option to produce layer1, layer2, layer3, and/or layer4. (all optional)
        For nominal NISAR products, up to layers 1, 2, and 3 will be processed.
        (Not necessarily all 3.) Urgent response will only process layer1 and
        layer2. NISAR Science Team is itching to use up to 7 layers.
        Each layer is processed with a unique algorithm combination, which
        strikes a unique balance between the amount of noise and
        the coarseness of the granularity.

        Returns
        -------
        layers : tuple[int, ...]
            Tuple of the available layers.
        """

        def _get_available_layer_numbers(freq: str) -> tuple[int, ...]:
            golden_layers = []
            with h5py.File(self.filepath) as f:
                # if multiple pols, make sure they contain the same layers
                possible_pols = nisarqa.get_possible_pols(
                    self.product_type.lower()
                )
                for pol in possible_pols:
                    # As of Sept 2023, ISCE3 only supports up to 4 layers,
                    # however NISAR Science Team is asking for up to 7 layers.
                    layers_tmp = []
                    for l_num in range(1, 8):
                        path = self._numbered_layer_group_path(freq, pol, l_num)
                        try:
                            f[path]
                        except KeyError:
                            pass
                        else:
                            layers_tmp.append(l_num)

                    if not layers_tmp:
                        # no layers were located in this polarization
                        continue

                    # Sanity Checks that each polarization contains the
                    # same layer groups
                    if not golden_layers:
                        # First polarization found in product
                        golden_layers = layers_tmp.copy()
                        golden_pol = pol
                    elif set(golden_layers) != set(layers_tmp):
                        nisarqa.get_logger().error(
                            f"Freq {freq} Pol {golden_pol} contains layers"
                            f" {golden_layers}, but Freq {freq} Pol {pol}"
                            f" contains layers {layers_tmp}."
                        )

            if not golden_layers:
                msg = f"No layer groups found for Freq {freq}."
                raise nisarqa.DatasetNotFoundError(msg)

            return golden_layers

        # self.freqs is a property containing only confirmed frequencies
        # in the input product. If a DatasetNotFoundError is raised, then
        # the input product is incorrectly formed. Let the error propogate up.
        layers_1 = _get_available_layer_numbers(self.freqs[0])

        # If multiple frequencies, ensure they contain the same layers
        if len(self.freqs) == 2:
            layers_2 = _get_available_layer_numbers(self.freqs[1])
            if set(layers_1) != set(layers_2):
                nisarqa.get_logger().error(
                    f"Frequency {self.freqs[0]} contains layers {layers_1}, but"
                    f" Frequency {self.freqs[1]} contains layers {layers_2}."
                )

        return layers_1

    def get_browse_freq_pol_layer(self) -> tuple[str, str, int]:
        """
        Return the frequency, polarization, and layer number for browse image.

        Returns
        -------
        freq : str
            The frequency to use for the browse image.
        pol : str
            The polarization to use for the browse image.
        layer_num : int
            The layer number to use for the browse image.
        """
        freq, pol = self.get_browse_freq_pol()

        # Prioritization order, as determined by insar product lead (Sept 2023).
        # Layer 3 should be nicest-looking for the browse image; compared
        # to the other layers, it has coarser granularity but is less noisy.
        priority_order = (3, 2, 1, 4, 5, 6, 7)

        for layer_num in priority_order:
            if layer_num in self.available_layer_numbers:
                return freq, pol, layer_num
        else:
            errmsg = (
                f"Prioritization order of layer groups is {priority_order}, but"
                " the product only contains layers"
                f" {self.available_layer_numbers}."
            )
            raise nisarqa.InvalidNISARProductError(errmsg)

    def _get_path_containing_freq_pol(self, freq: str, pol: str) -> str:
        # Each polarization should contain the same layer numbers.
        # WLOG, use the first available layer number.
        return self._numbered_layer_group_path(
            freq=freq, pol=pol, layer_num=self.available_layer_numbers[0]
        )

    def _numbered_layer_group_path(
        self, freq: str, pol: str, layer_num: int
    ) -> str:
        """Get path in input file to the group for this numbered layer group."""
        return f"{self.get_freq_path(freq)}/pixelOffsets/{pol}/layer{layer_num}"

    @contextmanager
    def get_along_track_offset(
        self, freq: str, pol: str, layer_num: int
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the along track offset *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.
        layer_num : int
            Layer number of the desired raster. For example, to get the
            requested raster from the `layer1` group, set `layer_num` to `1`.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._numbered_layer_group_path(freq, pol, layer_num)
        path = f"{parent_path}/alongTrackOffset"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_slant_range_offset(
        self, freq: str, pol: str, layer_num: int
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the slant range offset *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.
        layer_num : int
            Layer number of the desired raster. For example, to get the
            requested raster from the `layer1` group, set `layer_num` to `1`.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._numbered_layer_group_path(freq, pol, layer_num)
        path = f"{parent_path}/slantRangeOffset"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_along_track_offset_variance(
        self, freq: str, pol: str, layer_num: int
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the along track offset variance *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.
        layer_num : int
            Layer number of the desired raster. For example, to get the
            requested raster from the `layer1` group, set `layer_num` to `1`.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._numbered_layer_group_path(freq, pol, layer_num)
        path = f"{parent_path}/alongTrackOffsetVariance"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_slant_range_offset_variance(
        self, freq: str, pol: str, layer_num: int
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the slant range offset variance *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.
        layer_num : int
            Layer number of the desired raster. For example, to get the
            requested raster from the `layer1` group, set `layer_num` to `1`.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._numbered_layer_group_path(freq, pol, layer_num)
        path = f"{parent_path}/slantRangeOffsetVariance"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_cross_offset_variance(
        self, freq: str, pol: str, layer_num: int
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the cross offset variance *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.
        layer_num : int
            Layer number of the desired raster. For example, to get the
            requested raster from the `layer1` group, set `layer_num` to `1`.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._numbered_layer_group_path(freq, pol, layer_num)
        path = f"{parent_path}/crossOffsetVariance"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_correlation_surface_peak(
        self, freq: str, pol: str, layer_num: int
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the correlation surface peak *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.
        layer_num : int
            Layer number of the desired raster. For example, to get the
            requested raster from the `layer1` group, set `layer_num` to `1`.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._numbered_layer_group_path(freq, pol, layer_num)
        path = f"{parent_path}/correlationSurfacePeak"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )


@dataclass
class ROFF(OffsetProduct, NisarRadarProduct):
    @property
    def product_type(self) -> str:
        return "ROFF"


@dataclass
class GOFF(OffsetProduct, NisarGeoProduct):
    @property
    def product_type(self) -> str:
        return "GOFF"

    @cached_property
    def browse_x_range(self) -> tuple[float, float]:
        freq, pol, layer = self.get_browse_freq_pol_layer()

        with self.get_along_track_offset(
            freq=freq, pol=pol, layer_num=layer
        ) as raster:
            x_start = raster.x_start
            x_stop = raster.x_stop

        return (x_start, x_stop)

    @cached_property
    def browse_y_range(self) -> tuple[float, float]:
        freq, pol, layer = self.get_browse_freq_pol_layer()

        with self.get_along_track_offset(
            freq=freq, pol=pol, layer_num=layer
        ) as raster:
            y_start = raster.y_start
            y_stop = raster.y_stop

        return (y_start, y_stop)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
