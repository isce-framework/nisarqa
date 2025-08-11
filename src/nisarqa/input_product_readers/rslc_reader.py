from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from functools import cached_property, lru_cache

import h5py
import numpy as np

import nisarqa

from .radar_product import NisarRadarProduct
from .slc_product import SLCProduct

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass
class RSLC(SLCProduct, NisarRadarProduct):
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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
