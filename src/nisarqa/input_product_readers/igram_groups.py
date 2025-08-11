from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager

import h5py

import nisarqa

from .insar_product import InsarProduct

objects_to_skip = nisarqa.get_all(name=__name__)


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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
