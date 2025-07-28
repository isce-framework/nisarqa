from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

import nisarqa

from .l1_radar_base import NisarRadarProduct
from .l2_geo_base import NisarGeoProduct
from .offsets_base import OffsetProduct

objects_to_skip = nisarqa.get_all(name=__name__)


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
