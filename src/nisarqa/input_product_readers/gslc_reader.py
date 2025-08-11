from __future__ import annotations

from dataclasses import dataclass

import nisarqa

from .non_insar_geo_product import NonInsarGeoProduct
from .slc_product import SLCProduct

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass
class GSLC(SLCProduct, NonInsarGeoProduct):
    @property
    def product_type(self) -> str:
        return "GSLC"


__all__ = nisarqa.get_all(__name__, objects_to_skip)
