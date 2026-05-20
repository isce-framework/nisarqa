from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
import h5py

import nisarqa

from .geo_product import NisarGeoProduct
from .non_insar_product import NonInsarProduct

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass
class NonInsarGeoProduct(NonInsarProduct, NisarGeoProduct):

    @cached_property
    def _source_data_path(self) -> str:
        """
        Get the path to the sourceData group.

        Returns
        -------
        source_data_path : str
            Path to the sourceData group.
                Standard Format:
                    "/science/<band>/<product_type>/metadata/sourceData"
                Example:
                    "/science/LSAR/GCOV/metadata/sourceData"
        """

        return f"{self._metadata_group_path}/sourceData"

    @cached_property
    def _source_data_swaths_path(self) -> str:
        """
        Get the path to the sourceData/swaths group.

        Returns
        -------
        source_data_path : str
            Path to the sourceData group.
                Standard Format:
                    "/science/<band>/<product_type>/metadata/sourceData/swaths"
                Example:
                    "/science/LSAR/GCOV/metadata/sourceData/swaths"
        """

        return f"{self._source_data_path}/swaths"

    def _source_data_swaths_freq_path(self, freq: str) -> str:
        """
        Get the path to the sourceData/swaths/frequencyX group.

        Parameters
        ----------
        freq : str
            Must be either "A" or "B".

        Returns
        -------
        source_data_path : str
            Path to the sourceData group.
                Standard Format:
                    "/science/<band>/<product_type>/metadata/sourceData/swaths/frequency<freq>"
                Example:
                    "/science/LSAR/GCOV/metadata/sourceData/swaths/frequencyA"
        """
        if freq not in ("A", "B"):
            raise ValueError(f"{freq=}, must be either 'A' or 'B'")

        return f"{self._source_data_swaths_path}/frequency{freq}"

    def center_freq(self, freq: str) -> float:
        """
        The processed center frequency for input product's Frequency `freq`.

        This is read from the `centerFrequency` dataset in the metadata
        sourceData swaths group.

        Parameters
        ----------
        freq : str
            Must be either "A" or "B".

        Returns
        -------
        center_freq : float
            The processed center frequency for input product's Frequency `freq`,
            in hertz.
        """

        source_group = self._source_data_swaths_freq_path(freq=freq)

        with h5py.File(self.filepath) as f:
            assert source_group in f
            try:
                center_freq = f[source_group]["centerFrequency"][()]
            except KeyError as e:
                raise nisarqa.DatasetNotFoundError from e

        return center_freq

__all__ = nisarqa.get_all(__name__, objects_to_skip)
