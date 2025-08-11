from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

import nisarqa

from .geo_product import NisarGeoProduct
from .igram_groups import IgramOffsetsGroup, UnwrappedGroup, WrappedGroup
from .radar_product import NisarRadarProduct

objects_to_skip = nisarqa.get_all(name=__name__)


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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
