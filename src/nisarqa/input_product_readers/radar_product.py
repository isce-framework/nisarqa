from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

import h5py

import nisarqa

from ._utils import (
    _get_dataset_handle,
    _get_fill_value,
    _get_or_create_cached_memmap,
    _get_path_to_nearest_dataset,
    _get_units,
    _parse_dataset_stats_from_h5,
)
from .nisar_product import NisarProduct

objects_to_skip = nisarqa.get_all(name=__name__)


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

        # Get dataset object and check for correct dtype
        dataset = _get_dataset_handle(h5_file, raster_path)

        # Collect grid parameters
        # From the xml Product Spec, sceneCenterAlongTrackSpacing is the
        # 'Nominal along track spacing in meters between consecutive lines
        # near mid swath of the RSLC image.'
        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="sceneCenterAlongTrackSpacing",
        )
        ground_az_spacing = h5_file[path][...]

        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="zeroDopplerTime",
        )
        zero_doppler_time = h5_file[path][...]

        # Use zeroDopplerTime's units attribute to get the epoch.
        epoch = self._get_epoch(ds=h5_file[path])

        # From the xml Product Spec, zeroDopplerTimeSpacing is the
        # '...spacing between consecutive entries in the zeroDopplerTime array'.
        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="zeroDopplerTimeSpacing",
        )
        zero_doppler_time_spacing = h5_file[path][...]

        # From the xml Product Spec, sceneCenterGroundRangeSpacing is the
        # 'Nominal ground range spacing in meters between consecutive pixels
        # near mid swath of the RSLC image.'
        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="sceneCenterGroundRangeSpacing",
        )
        ground_range_spacing = h5_file[path][...]

        # Range in meters (units are specified as meters in the product spec)
        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="slantRange",
        )
        slant_range = h5_file[path][...]

        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="slantRangeSpacing",
        )
        slant_range_spacing = h5_file[path][...]

        # Create the RadarGrid instance
        radar_grid = nisarqa.RadarGrid(
            zero_doppler_time=zero_doppler_time,
            zero_doppler_time_spacing=zero_doppler_time_spacing,
            slant_range=slant_range,
            slant_range_spacing=slant_range_spacing,
            ground_az_spacing=ground_az_spacing,
            ground_range_spacing=ground_range_spacing,
            epoch=epoch,
        )

        # Arguments to pass to the constructor of `RadarRaster` or
        # `RadarRasterWithStats`
        kwargs = {}

        if self.use_cache:
            kwargs["data"] = _get_or_create_cached_memmap(
                input_file=self.filepath,
                dataset_path=raster_path,
            )
        else:
            kwargs["data"] = dataset

        kwargs["units"] = _get_units(dataset)
        kwargs["fill_value"] = _get_fill_value(dataset)
        kwargs["name"] = self._get_raster_name(raster_path)
        kwargs["stats_h5_group_path"] = self._get_stats_h5_group_path(
            raster_path
        )
        kwargs["band"] = self.band
        kwargs["freq"] = "A" if "frequencyA" in raster_path else "B"
        kwargs["grid"] = radar_grid

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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
