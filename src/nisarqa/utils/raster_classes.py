from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, fields
from functools import cached_property
from typing import Any, Optional, Sequence, overload

import h5py
import numpy as np
import numpy.typing as npt

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


class IsComplex(ABC):
    @property
    @abstractmethod
    def is_complex(self) -> bool:
        """True if dataset is complex-valued; False if real-valued."""
        pass


def is_complex32(dataset: h5py.Dataset) -> bool:
    """
    Check if the input dataset is half-precision complex ("complex32").

    Parameters
    --------
    dataset : h5py.Dataset
        The input dataset.

    Returns
    -------
    bool
        True if the input dataset is complex32.

    Notes
    -----
    If a Dataset has dtype complex32, h5py < v3.8 will throw the error
    "data type '<c4' not understood" if the Dataset is accessed.
    h5py 3.8.0 adopted @bhawkins's patch which allows h5py to
    recognize the new complex32 datatype that is used for RSLC
    HDF5 Datasets in R3.2, R3.3, etc. That patch fixes the dtype attribute
    such that it returns a structured datatype if the data is complex32.
    """
    try:
        dataset.dtype
    except TypeError as e:
        # h5py < v3.8 will throw the error "data type '<c4' not understood"
        if str(e) == "data type '<c4' not understood":
            return True
        else:
            raise
    else:
        # h5py >= v3.8 recognizes the new complex32 datatype
        return dataset.dtype == nisarqa.complex32


class ComplexFloat16Decoder(object):
    """Wrapper to read in NISAR product datasets that are '<c4' type,
    which raise an TypeError if accessed naively by h5py.

    Indexing operatations always return data converted to numpy.complex64.

    Parameters
    ----------
    h5dataset : h5py.Dataset
        Dataset to be stored. Dataset should have type '<c4'.

    Notes
    -----
    The ComplexFloat16Decoder class is an example of what the NumPy folks call a 'duck array',
    i.e. a class that exports some subset of np.ndarray's API so that it can be used
    as a drop-in replacement for np.ndarray in some cases. This is different from an
    'array_like' object, which is simply an object that can be converted to a numpy array.
    Reference: https://numpy.org/neps/nep-0022-ndarray-duck-typing-overview.html
    """

    def __init__(self, h5dataset):
        self._dataset = h5dataset
        self._dtype = np.complex64

    def __getitem__(self, key):
        # Have h5py convert to the desired dtype on the fly when reading in data
        return self.read_c4_dataset_as_c8(self.dataset, key)

    @staticmethod
    def read_c4_dataset_as_c8(ds: h5py.Dataset, key=np.s_[...]):
        """
        Read a complex float16 HDF5 dataset as a numpy.complex64 array.

        Avoids h5py/numpy dtype bugs and uses numpy float16 -> float32
        conversions which are about 10x faster than HDF5 ones.
        """
        # This avoids h5py exception:
        # TypeError: data type '<c4' not understood
        # Also note this syntax changed in h5py 3.0 and was deprecated in 3.6,
        # see: https://docs.h5py.org/en/stable/whatsnew/3.6.html

        z = ds.astype(nisarqa.complex32)[key]

        # Define a similar datatype for complex64 to be sure we cast safely.
        complex64 = np.dtype([("r", np.float32), ("i", np.float32)])

        # Cast safely and then view as native complex64 numpy dtype.
        return z.astype(complex64).view(np.complex64)

    @property
    def dataset(self):
        return self._dataset

    @property
    def dtype(self):
        return self._dtype

    @property
    def shape(self):
        return self.dataset.shape

    @property
    def ndim(self):
        return self.dataset.ndim

    @property
    def attrs(self) -> Mapping[str, Any]:
        return self.dataset.attrs

    @property
    def name(self) -> str:
        return self.dataset.name

    def __repr__(self):
        original = self.dataset.__repr__()
        new = original.replace("HDF5 dataset", "ComplexFloat16Decoder")
        return new

    @property
    def chunks(self) -> Sequence[int]:
        return self.dataset.chunks


@dataclass
class RasterStats:
    """
    A set of Min/Max/Mean/STD statistics for a raster.

    Parameters
    ----------
    min_value, max_value, mean_value, std_value : float or None
        Minimum, maximum, mean, and standard deviation values
        (respectively) for a raster image.
        None if a value could not be provided.
    """

    min_value: float | None
    max_value: float | None
    mean_value: float | None
    std_value: float | None


@dataclass
class ComplexRasterStats:
    """
    Min/Max/Mean/STD statistics for a complex-valued raster.

    Parameters
    ----------
    real, imag : RasterStats
        Per ISCE3 convention, for complex-valued data, the statistics
        should be computed independently for the real component and
        for the imaginary component of the data.
        `real` contains the real component's statistics, and `imag` contains
        the imaginary component's statistics.
    """

    real: RasterStats
    imag: RasterStats

    def min_value(self, component: str) -> float:
        """
        Get the minimum of the requested component (either "real" or "imag").
        """
        return getattr(self, component).min_value

    def max_value(self, component: str) -> float:
        """
        Get the maximum of the requested component (either "real" or "imag").
        """
        return getattr(self, component).max_value

    def mean_value(self, component: str) -> float:
        """
        Get the mean value of the requested component (either "real" or "imag").
        """
        return getattr(self, component).mean_value

    def std_value(self, component: str) -> float:
        """
        Get the std. deviation of requested component (either "real" or "imag").
        """
        return getattr(self, component).std_value


@dataclass
class Raster(IsComplex):
    """
    Raster image dataset base class.

    Parameters
    ----------
    data : array_like
        Raster data to be stored. Can be a numpy.ndarray, h5py.Dataset, etc.
    units : str
        The units of the data. If `data` is numeric but unitless (e.g ratios),
        by NISAR convention please use the string "1".
    fill_value : int, float, complex, or None
        The fill value for the dataset. In general, all imagery datasets should
        have a `_FillValue` attribute. The exception might be RSLC (tbd).
    name : str
        Name for the dataset
    stats_h5_group_path : str
        Path in the STATS.h5 file for the group where all metrics and
        statistics re: this raster should be saved.
        Examples:
            RSLC/GSLC/GCOV: "/science/LSAR/QA/data/frequencyA/HH"
            RUNW/GUNW: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset"
            ROFF/GOFF: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"
    band : str
        Name of the band for `img`, e.g. 'LSAR'
    freq : str
        Name of the frequency for `img`, e.g. 'A' or 'B'
    """

    # Raster data. Could be a numpy.ndarray, h5py.Dataset, etc.
    data: npt.ArrayLike
    units: str
    fill_value: Optional[int | float | complex]

    # identifying name of this Raster; can be used for logging
    # e.g. 'LSAR_A_HH'
    name: str

    stats_h5_group_path: str

    band: str
    freq: str

    @cached_property
    def is_complex(self) -> bool:
        """
        True if raster data is complex-valued; False otherwise.

        Returns
        -------
        is_complex_dtype : bool
            True if raster data is complex-valued; False otherwise.

        Warnings
        --------
        If `data` does not have a `dtype` attribute, it will be copied
        into a NumPy array to get the dtype. Depending on the size of the
        raster, this could be an expensive operation.
        """
        try:
            arr_dtype = self.data.dtype
        except AttributeError:
            # Convert input data to a NumPy array only if it isn't already one.
            # If the input is already an ndarray (or a subclass), it returns
            # the input as is, without making a copy.
            arr = np.asanyarray(self.data)
            arr_dtype = arr.dtype

        # Note: Need to use `np.issubdtype` instead of `np.iscomplexobj`
        # due to e.g. RSLC and GSLC datasets of type ComplexFloat16Decoder.
        return np.issubdtype(arr_dtype, np.complexfloating)


@dataclass
class SARRaster(Raster, ABC):
    """Abstract Base Class for SAR Raster dataclasses."""

    @property
    @abstractmethod
    def y_axis_spacing(self):
        """Pixel Spacing in Y direction (azimuth for range-Doppler rasters)"""
        pass

    @property
    @abstractmethod
    def y_axis_limits(self) -> tuple[float, float]:
        """Min and max extents of the Y direction (azimuth for range-Doppler rasters)."""
        pass

    @property
    @abstractmethod
    def y_axis_label(self) -> str:
        """Label for the Y direction (azimuth for range-Doppler rasters)."""
        pass

    @property
    @abstractmethod
    def x_axis_spacing(self):
        """Pixel Spacing in X direction (range for range-Doppler rasters)"""
        pass

    @property
    @abstractmethod
    def x_axis_limits(self) -> tuple[float, float]:
        """Min and max extents of the X direction (range for range-Doppler rasters)."""
        pass

    @property
    @abstractmethod
    def x_axis_label(self) -> str:
        """Label for the X direction (range for range-Doppler rasters)."""
        pass


@dataclass
class RadarRaster(SARRaster):
    """
    A Raster with attributes specific to Radar products.

    The attributes specified here are based on the needs of the QA code
    for generating and labeling plots, etc.

    Parameters
    ----------
    data : array_like
        Raster data to be stored.
    units : str
        The units of the data. If `data` is numeric but unitless (e.g ratios),
        by NISAR convention please use the string "1".
    fill_value : int, float, complex, or None
        The fill value for the dataset. In general, all imagery datasets should
        have a `_FillValue` attribute. The exception might be RSLC (tbd).
    name : str
        Name for the dataset
    stats_h5_group_path : str
        Path in the STATS.h5 file for the group where all metrics and
        statistics re: this raster should be saved.
        Examples:
            RSLC/GSLC/GCOV: "/science/LSAR/QA/data/frequencyA/HH"
            RUNW/GUNW: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset"
            ROFF/GOFF: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"
    band : str
        name of the band for `img`, e.g. 'LSAR'
    freq : str
        name of the frequency for `img`, e.g. 'A' or 'B'
    ground_az_spacing : float
        Azimuth spacing of pixels of input array
        Units: meters
    az_start : float
        The start time of the observation for this RSLC Raster.
        This corresponds to the upper edge of the top pixels.
        Units: seconds since epoch
    az_stop : float
        The stopping time of the observation for this RSLC Raster.
        This corresponds to the lower side of the bottom pixels.
        Units: seconds since epoch
    ground_range_spacing : float
        Range spacing of pixels of input array.
        Units: meters
    rng_start : float
        Start (near) distance of the range of input array
        This corresponds to the left side of the left-most pixels.
        Units: meters
    rng_stop : float
        End (far) distance of the range of input array
        This corresponds to the right side of the right-most pixels.
        Units: meters
    epoch : str
        The start of the epoch for this observation,
        in the format 'YYYY-MM-DD HH:MM:SS'
    """

    # Attributes of the input array
    ground_az_spacing: float
    az_start: float
    az_stop: float

    ground_range_spacing: float
    rng_start: float
    rng_stop: float

    epoch: str

    @property
    def y_axis_spacing(self):
        return self.ground_az_spacing

    @property
    def y_axis_limits(self) -> tuple[float, float]:
        return (self.az_start, self.az_stop)

    @property
    def y_axis_label(self) -> str:
        return f"Zero Doppler Time\n(seconds since {self.epoch})"

    @property
    def x_axis_spacing(self):
        return self.ground_range_spacing

    @property
    def x_axis_limits(self) -> tuple[float, float]:
        return (nisarqa.m2km(self.rng_start), nisarqa.m2km(self.rng_stop))

    @property
    def x_axis_label(self) -> str:
        return "Slant Range (km)"


@dataclass
class GeoRaster(SARRaster):
    """
    A Raster with attributes specific to Geocoded products.

    The attributes specified here are based on the needs of the QA code
    for generating and labeling plots, etc.

    Parameters
    ----------
    data : array_like
        Raster data to be stored.
    units : str
        The units of the data. If `data` is numeric but unitless (e.g ratios),
        by NISAR convention please use the string "1".
    fill_value : int, float, complex, or None
        The fill value for the dataset. In general, all imagery datasets should
        have a `_FillValue` attribute. The exception might be RSLC (tbd).
    name : str
        Name for the dataset
    stats_h5_group_path : str
        Path in the STATS.h5 file for the group where all metrics and
        statistics re: this raster should be saved.
        Examples:
            RSLC/GSLC/GCOV: "/science/LSAR/QA/data/frequencyA/HH"
            RUNW/GUNW: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset"
            ROFF/GOFF: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"
    band : str
        name of the band for `data`, e.g. 'LSAR'
    freq : str
        name of the frequency for `data`, e.g. 'A' or 'B'
    x_spacing : float
        X spacing of pixels (in meters) of input array.
    x_start : float
        The starting (West) X position of the input array
        This corresponds to the left side of the left-most pixels.
    x_stop : float
        The stopping (East) X position of the input array
        This corresponds to the right side of the right-most pixels.
    y_spacing : float
        Y spacing of pixels (in meters) of input array
    y_start : float
        The starting (North) Y position of the input array
        This corresponds to the upper edge of the top pixels.
    y_stop : float
        The stopping (South) Y position of the input array
        This corresponds to the lower side of the bottom pixels.
    """

    # Attributes of the input array
    x_spacing: float
    x_start: float
    x_stop: float

    y_spacing: float
    y_start: float
    y_stop: float

    @property
    def y_axis_spacing(self):
        return self.y_spacing

    @property
    def y_axis_limits(self) -> tuple[float, float]:
        return (nisarqa.m2km(self.y_start), nisarqa.m2km(self.y_stop))

    @property
    def y_axis_label(self) -> str:
        return "Northing (km)"

    @property
    def x_axis_spacing(self):
        return self.x_spacing

    @property
    def x_axis_limits(self) -> tuple[float, float]:
        return (nisarqa.m2km(self.x_start), nisarqa.m2km(self.x_stop))

    @property
    def x_axis_label(self) -> str:
        return "Easting (km)"


@overload
def compare_raster_metadata(
    raster1: nisarqa.RadarRaster,
    raster2: nisarqa.RadarRaster,
    almost_identical: bool,
) -> None: ...


@overload
def compare_raster_metadata(
    raster1: nisarqa.GeoRaster,
    raster2: nisarqa.GeoRaster,
    almost_identical: bool,
) -> None: ...


def compare_raster_metadata(raster1, raster2, almost_identical=True):
    """
    Compare the primary metadata and shape of two *Raster instances.

    Compare metadata fields and the shape of the data for two *Raster instances.
    This is useful for checking that two rasters can be combined smoothly into
    a single image, such as combining a phase image raster and a coherence
    magnitude raster to create an HSI image.
    This function does not compare the `name` field nor the values inside the
    data arrays.
    Raises a ValueError if two fields do not match.

    Parameters
    ----------
    raster1, raster2 : nisarqa.RadarRaster | nisarqa.GeoRaster
        *Raster to compare. `raster1` and `raster2` must either both be
        instances of RadarRasters or both be instances of GeoRasters.
    almost_identical : bool, optional
        True if the two inputs rasters are expected to have identical metadata
        (except for the layer name).
            Ex 1: RSLC's frequency A HH Raster vs frequency A VV Raster
            Ex 2: RIFG's freq A HH alongTrackOffset Raster vs
                  freq A HH slantRangeOffset Raster
        False if the two input rasters are expected to have more differences in their
        metadata, and should only have matching shape, spacing, etc.
        In practice, this suppresses warnings about expected dissimilar
        fields, such as `units`.
            Ex: RIFG's freq A HH wrappedInterferogram Raster vs freq A HH
                coherenceMagnitude Raster
        Defaults to True (more verbose).

    Raises
    ------
    ValueError
        If metadata does not match
    """
    # This function only compares fields in instances of the RadarRaster or
    # GeoRaster base classes. Child classes have additional fields, which we
    # need to ignore when comparing the metadata of the two input *Rasters.
    r_raster = nisarqa.RadarRaster
    g_raster = nisarqa.GeoRaster
    if isinstance(raster1, r_raster) and isinstance(raster2, r_raster):
        raster_class = r_raster
    elif isinstance(raster1, g_raster) and isinstance(raster2, g_raster):
        raster_class = g_raster
    else:
        raise TypeError(
            f"{type(raster1)=} and {type(raster2)=}, must both be instances"
            " of either RadarRaster or of GeoRaster."
        )

    for f in fields(raster_class):
        field_name = f.name
        r1_val = getattr(raster1, field_name)
        r2_val = getattr(raster2, field_name)

        log = nisarqa.get_logger()

        if field_name == "data":
            # raster data layers should have the same shape
            if np.shape(r1_val) != np.shape(r2_val):
                raise ValueError(
                    f"Values do not match: {np.shape(raster1.data)=} but"
                    f" {np.shape(raster2.data)=}."
                )
        elif field_name == "units":
            if not almost_identical:
                if raster1.units != raster2.units:
                    log.warning(
                        f"Layer `{raster1.name}` has units attribute of"
                        f" `{raster1.units}`, and is being compared to layer"
                        f" `{raster2.name}` which has units attribute of"
                        f" `{raster2.units}`. Please confirm these two rasters"
                        " are ok to have different units."
                    )
        elif field_name == "name":
            # "name" dataclass attributes should be the same
            # except for the final layer name
            if r1_val.split("_")[:-1] != r2_val.split("_")[:-1]:
                log.warning(
                    f"{raster1.name=} but {raster2.name=}. Consider checking if"
                    " their band, frequency, polarization, etc. should match."
                )
        elif field_name == "stats_h5_group_path":
            # "stats_h5_group_path" dataclass attributes should be the same
            # except for the final layer name
            if r1_val.split("/")[:-1] != r2_val.split("/")[:-1]:
                log.warning(
                    f"{raster1.stats_h5_group_path=} but"
                    f" {raster2.stats_h5_group_path=}. Consider checking if"
                    " these base paths should match."
                )
        elif isinstance(r1_val, str):
            if r1_val != r2_val:
                raise ValueError(
                    f"Values do not match for `{field_name}` field. `raster1`"
                    f" has value {r1_val}, but `raster2` has value {r2_val}."
                )
        else:
            if np.abs(r1_val - r2_val) > 1e-6:
                raise ValueError(
                    f"Values do not match for `{field_name}` field. `raster1`"
                    f" has value {r1_val}, but `raster2` has value {r2_val}."
                )


def decimate_raster_array_to_square_pixels(
    raster_obj: RadarRaster | GeoRaster,
) -> np.ndarray:
    """
    Get *Raster's data array, decimated to square pixels in X and Y direction.

    Parameters
    ----------
    raster_obj : RadarRaster or GeoRaster
        *Raster object whose .data attribute will be read into memory
        and decimated along the first two dimensions to square pixels.

    Returns
    -------
    out : numpy.ndarray
        Copy of raster_obj.data array that has been decimated along the
        first two dimensions to have square pixels.
    """
    arr = raster_obj.data[...]

    ky, kx = nisarqa.compute_square_pixel_nlooks(
        img_shape=arr.shape[:2],
        sample_spacing=[
            raster_obj.y_axis_spacing,
            raster_obj.x_axis_spacing,
        ],
        # Only make square pixels. Use `max()` to not "shrink" the rasters.
        longest_side_max=max(arr.shape[:2]),
    )

    # Decimate to square pixels.
    return arr[::ky, ::kx]


@dataclass
class StatsMixin(IsComplex):
    """
    A mixin type providing access to dataset statistics (Min/Max/Mean/STD).

    Parameters
    ----------
    stats : nisarqa.RasterStats or nisarqa.ComplexRasterStats
        Statistics of the `data` array.
    """

    stats: RasterStats | ComplexRasterStats

    def __post_init__(self) -> None:

        if self.is_complex:
            if not isinstance(self.stats, ComplexRasterStats):
                raise TypeError(
                    f"`data` provided is complex-valued, so `stats` must"
                    f" be an instance of ComplexRasterStats. Dataset: {self.name}"
                )
        else:
            if not isinstance(self.stats, RasterStats):
                raise TypeError(
                    f"`data` provided is real-valued, so `stats` must"
                    " be an instance of RasterStats."
                )

    def get_stat(self, stat: str, component: str | None = None) -> float:
        """
        Return value for a min/max/mean/std metric.

        Parameters
        ----------
        stat : str
            One of {"min", "max", "mean", "std"}.
        component : str or None, optional
            One of "real", "imag", or None.
            Per ISCE3 convention, statistics for complex-valued data should be
            computed independently for the real and imaginary components.
            If the raster is real-valued, set this to None.
            If the raster is complex-valued, set to "real" or "imag" for the
            real or imaginery component's metric (respectively).
            Defaults to None.

        Returns
        -------
        statistic : float
            The value of the requested statistic.
        """
        stat_opts = ("min", "max", "mean", "std")
        if stat not in stat_opts:
            raise ValueError(f"{stat=!r}, must be one of {stat_opts}.")

        if self.is_complex:
            if component not in ("real", "imag"):
                raise ValueError(
                    f"{component=!r}, but Raster is complex-valued. Set to"
                    " either 'real' or 'imag'."
                )
            return getattr(getattr(self.stats, component), f"{stat}_value")

        else:
            if component is not None:
                raise ValueError(
                    f"{component=!r}, but Raster is real-valued. Set to None."
                )
            return getattr(self.stats, f"{stat}_value")

    def get_stat_val_name_descr(
        self, stat: str, component: str | None = None
    ) -> tuple[float, str, str]:
        """
        Return value, name, and description for a min/max/mean/std metric.

        The name and description returned follow the NISAR conventions for
        saving min/max/mean/std metrics in NISAR L1/L2 HDF5 metadata.

        Parameters
        ----------
        stat : str
            One of {"min", "max", "mean", "std"}.
        component : str or None, optional
            One of "real", "imag", or None.
            Per ISCE3 convention, statistics for complex-valued data should be
            computed independently for the real and imaginary components.
            If the raster is real-valued, set this to None.
            If the raster is complex-valued, set to "real" or "imag" for the
            real or imaginery component's metric (respectively).
            Defaults to None.

        Returns
        -------
        val, name, descr : float, str, str
            The value, name, and description of the requested statistic.
        """

        val = self.get_stat(stat=stat, component=component)
        name, descr = nisarqa.get_stats_name_descr(
            stat=stat, component=component
        )
        return val, name, descr


@dataclass
class RadarRasterWithStats(RadarRaster, StatsMixin):
    """
    A RadarRaster with statistics.

    Parameters
    ----------
    data : array_like
        Raster data to be stored. Can be a numpy.ndarray, h5py.Dataset, etc.
    units : str
        The units of the data. If `data` is numeric but unitless (e.g ratios),
        by NISAR convention please use the string "1".
    fill_value : int, float, complex, or None
        The fill value for the dataset. In general, all imagery datasets should
        have a `_FillValue` attribute. The exception might be RSLC (tbd).
    name : str
        Name for the dataset
    stats_h5_group_path : str
        Path in the STATS.h5 file for the group where all metrics and
        statistics re: this raster should be saved.
        Examples:
            RSLC/GSLC/GCOV: "/science/LSAR/QA/data/frequencyA/HH"
            RUNW/GUNW: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset"
            ROFF/GOFF: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"
    band : str
        Name of the band for `img`, e.g. 'LSAR'
    freq : str
        Name of the frequency for `img`, e.g. 'A' or 'B'
    ground_az_spacing : float
        Azimuth spacing of pixels of input array
        Units: meters
    az_start : float
        The start time of the observation for this RSLC Raster.
        This corresponds to the upper edge of the top pixels.
        Units: seconds since epoch
    az_stop : float
        The stopping time of the observation for this RSLC Raster.
        This corresponds to the lower side of the bottom pixels.
        Units: seconds since epoch
    ground_range_spacing : float
        Range spacing of pixels of input array.
        Units: meters
    rng_start : float
        Start (near) distance of the range of input array
        This corresponds to the left side of the left-most pixels.
        Units: meters
    rng_stop : float
        End (far) distance of the range of input array
        This corresponds to the right side of the right-most pixels.
        Units: meters
    epoch : str
        The start of the epoch for this observation,
        in the format 'YYYY-MM-DD HH:MM:SS'
    stats : nisarqa.RasterStats or nisarqa.ComplexRasterStats
        Statistics of the `data` array.
    """

    ...


@dataclass
class GeoRasterWithStats(GeoRaster, StatsMixin):
    """
    A GeoRaster with statistics.

    Parameters
    ----------
    data : array_like
        Raster data to be stored. Can be a numpy.ndarray, h5py.Dataset, etc.
    units : str
        The units of the data. If `data` is numeric but unitless (e.g ratios),
        by NISAR convention please use the string "1".
    fill_value : int, float, complex, or None
        The fill value for the dataset. In general, all imagery datasets should
        have a `_FillValue` attribute. The exception might be RSLC (tbd).
    name : str
        Name for the dataset
    stats_h5_group_path : str
        Path in the STATS.h5 file for the group where all metrics and
        statistics re: this raster should be saved.
        Examples:
            RSLC/GSLC/GCOV: "/science/LSAR/QA/data/frequencyA/HH"
            RUNW/GUNW: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset"
            ROFF/GOFF: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"
    band : str
        Name of the band for `img`, e.g. 'LSAR'
    freq : str
        Name of the frequency for `img`, e.g. 'A' or 'B'
    x_spacing : float
        X spacing of pixels (in meters) of input array.
    x_start : float
        The starting (West) X position of the input array
        This corresponds to the left side of the left-most pixels.
    x_stop : float
        The stopping (East) X position of the input array
        This corresponds to the right side of the right-most pixels.
    y_spacing : float
        Y spacing of pixels (in meters) of input array
    y_start : float
        The starting (North) Y position of the input array
        This corresponds to the upper edge of the top pixels.
    y_stop : float
        The stopping (South) Y position of the input array
        This corresponds to the lower side of the bottom pixels.
    stats : nisarqa.RasterStats or nisarqa.ComplexRasterStats
        Statistics of the `data` array.
    """

    ...


__all__ = nisarqa.get_all(__name__, objects_to_skip)
