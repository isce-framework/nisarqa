from __future__ import annotations

from dataclasses import dataclass

import nisarqa

from .non_insar_geo_base import NonInsarGeoProduct
from .slc_base import SLC

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass
class GSLC(SLC, NonInsarGeoProduct):
    @property
    def product_type(self) -> str:
        return "GSLC"


__all__ = nisarqa.get_all(__name__, objects_to_skip)
