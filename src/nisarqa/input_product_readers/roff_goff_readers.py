from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

import nisarqa

from .geo_product import NisarGeoProduct
from .offset_product import OffsetProduct
from .radar_product import NisarRadarProduct

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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
