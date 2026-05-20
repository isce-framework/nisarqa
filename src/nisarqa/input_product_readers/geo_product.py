from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from functools import cached_property

import h5py
import numpy as np

import nisarqa

from ._utils import (
    _get_dataset_handle,
    _get_fill_value,
    _get_or_create_cached_memmap,
    _get_path_to_nearest_dataset,
    _get_paths_in_h5,
    _get_units,
    _parse_dataset_stats_from_h5,
)
from .nisar_product import NisarProduct

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass
class NisarGeoProduct(NisarProduct):
    @property
    def is_geocoded(self) -> bool:
        return True

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

        # Get dataset object and check for correct dtype
        dataset = _get_dataset_handle(h5_file, raster_path)

        # Collect grid parameters
        # From the xml Product Spec, xCoordinateSpacing is the
        # 'Nominal spacing in meters between consecutive pixels'

        # However, this is a slight misnomer. "Spacing" refers to the
        # (positive-valued) width of a pixel while "posting" refers to
        # the (positive- or negative-valued) stride between points in a grid.
        # (The spacing is the absolute value of the posting.)

        # For NISAR L2 products, `xCoordinateSpacing` is actually the
        # x-coordinate posting.
        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="xCoordinateSpacing",
        )
        x_posting = float(h5_file[path][...])

        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="xCoordinates",
        )
        x_coordinates = h5_file[path][...]

        # From the xml Product Spec, yCoordinateSpacing is the
        # 'Nominal spacing in meters between consecutive lines'.

        # For NISAR L2 products, `yCoordinateSpacing` is actually the
        # y-coordinate posting; the y-coordinate posting of the coordinate
        # grid is negative (the positive y-axis points up in QA plots).

        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="yCoordinateSpacing",
        )
        y_posting = float(h5_file[path][...])

        path = _get_path_to_nearest_dataset(
            h5_file=h5_file,
            starting_path=raster_path,
            dataset_to_find="yCoordinates",
        )
        y_coordinates = h5_file[path][...]

        # Create the GeoGrid instance
        geo_grid = nisarqa.GeoGrid(
            epsg=self.epsg,
            x_axis_posting=x_posting,
            x_coordinates=x_coordinates,
            y_axis_posting=y_posting,
            y_coordinates=y_coordinates,
        )

        # Arguments to pass to the constructor of `GeoRaster` or `GeoRasterWithStats`
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
        kwargs["grid"] = geo_grid

        if parse_stats:
            kwargs["stats"] = _parse_dataset_stats_from_h5(
                ds=h5_file[raster_path]
            )
            return nisarqa.GeoRasterWithStats(**kwargs)
        else:
            return nisarqa.GeoRaster(**kwargs)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
