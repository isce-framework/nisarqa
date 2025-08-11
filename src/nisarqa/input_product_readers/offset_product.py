from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from functools import cached_property

import h5py

import nisarqa

from .insar_product import InsarProduct

objects_to_skip = nisarqa.get_all(name=__name__)


class OffsetProduct(InsarProduct):
    """
    InSAR product where datasets need freq, pol, and layer number to locate.

    This includes ROFF and GOFF products, but not RIFG, RUNW, GUNW products.

    RIFG, RUNW, and GUNW's structure follow a pattern like:
        .../frequencyA/pixelOffsets/HH/<data set>
    ROFF and GOFF follow a pattern like:
        .../frequencyA/pixelOffsets/pixelOffsets/HH/layer2/<data set>

    Note that RIFG/RUNW/GUNW only require freq and pol to correctly locate a
    specific dataset, while ROFF and GOFF additionally require a layer number.

    See Also
    --------
    IgramOffsetsGroup :
        Class that handles the pixel offsets group for RIFG, RUNW, and
        GUNW products.
    """

    def _get_raster_name(self, raster_path: str) -> str:
        """
        Return name for the raster, e.g. 'ROFF_L_A_HH_Layer1_alongTrackOffset'.

        Parameters
        ----------
        raster_path : str
            Full path in `h5_file` to the desired raster dataset.
            Example:
                "/science/LSAR/ROFF/swaths/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"

        Returns
        -------
        name : str
            The human-understandable name that is derived from the dataset.
            Example:
                "ROFF_L_A_HH_Layer1_alongTrackOffset"
        """
        # We have a ROFF or GOFF product. Example `raster_path` to parse:
        # "/science/LSAR/ROFF/swaths/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"
        band = self.band
        freq = "A" if ("frequencyA" in raster_path) else "B"
        path = raster_path.split("/")
        pol = path[-3]
        layer_num = path[-2]
        layer_name = path[-1]

        # Sanity check
        assert pol in nisarqa.get_possible_pols(
            product_type=self.product_type.lower()
        )

        name = f"{self.product_type.upper()}_{band}_{freq}_{pol}_{layer_num}_{layer_name}"
        return name

    @cached_property
    def available_layer_numbers(self) -> tuple[int, ...]:
        """
        The numbers of the available layers in the input product.

        Here, a "numbered layer" refers to the layer groups:
            /science/LSAR/GOFF/grids/frequencyA/pixelOffsets/HH/layer1/...
            /science/LSAR/GOFF/grids/frequencyA/pixelOffsets/HH/layer2/...

        Each layer group in a product contains an indentical set of
        raster and metadata datasets (although the values in those datasets
        are unique).

        As of Sept 2023, ISCE3 insar.yaml runconfig file allows users the
        option to produce layer1, layer2, layer3, and/or layer4. (all optional)
        For nominal NISAR products, up to layers 1, 2, and 3 will be processed.
        (Not necessarily all 3.) Urgent response will only process layer1 and
        layer2. NISAR Science Team is itching to use up to 7 layers.
        Each layer is processed with a unique algorithm combination, which
        strikes a unique balance between the amount of noise and
        the coarseness of the granularity.

        Returns
        -------
        layers : tuple[int, ...]
            Tuple of the available layers.
        """

        def _get_available_layer_numbers(freq: str) -> tuple[int, ...]:
            golden_layers = []
            with h5py.File(self.filepath) as f:
                # if multiple pols, make sure they contain the same layers
                possible_pols = nisarqa.get_possible_pols(
                    self.product_type.lower()
                )
                for pol in possible_pols:
                    # As of Sept 2023, ISCE3 only supports up to 4 layers,
                    # however NISAR Science Team is asking for up to 7 layers.
                    layers_tmp = []
                    for l_num in range(1, 8):
                        path = self._numbered_layer_group_path(freq, pol, l_num)
                        try:
                            f[path]
                        except KeyError:
                            pass
                        else:
                            layers_tmp.append(l_num)

                    if not layers_tmp:
                        # no layers were located in this polarization
                        continue

                    # Sanity Checks that each polarization contains the
                    # same layer groups
                    if not golden_layers:
                        # First polarization found in product
                        golden_layers = layers_tmp.copy()
                        golden_pol = pol
                    elif set(golden_layers) != set(layers_tmp):
                        nisarqa.get_logger().error(
                            f"Freq {freq} Pol {golden_pol} contains layers"
                            f" {golden_layers}, but Freq {freq} Pol {pol}"
                            f" contains layers {layers_tmp}."
                        )

            if not golden_layers:
                msg = f"No layer groups found for Freq {freq}."
                raise nisarqa.DatasetNotFoundError(msg)

            return golden_layers

        # self.freqs is a property containing only confirmed frequencies
        # in the input product. If a DatasetNotFoundError is raised, then
        # the input product is incorrectly formed. Let the error propogate up.
        layers_1 = _get_available_layer_numbers(self.freqs[0])

        # If multiple frequencies, ensure they contain the same layers
        if len(self.freqs) == 2:
            layers_2 = _get_available_layer_numbers(self.freqs[1])
            if set(layers_1) != set(layers_2):
                nisarqa.get_logger().error(
                    f"Frequency {self.freqs[0]} contains layers {layers_1}, but"
                    f" Frequency {self.freqs[1]} contains layers {layers_2}."
                )

        return layers_1

    def get_browse_freq_pol_layer(self) -> tuple[str, str, int]:
        """
        Return the frequency, polarization, and layer number for browse image.

        Returns
        -------
        freq : str
            The frequency to use for the browse image.
        pol : str
            The polarization to use for the browse image.
        layer_num : int
            The layer number to use for the browse image.
        """
        freq, pol = self.get_browse_freq_pol()

        # Prioritization order, as determined by insar product lead (Sept 2023).
        # Layer 3 should be nicest-looking for the browse image; compared
        # to the other layers, it has coarser granularity but is less noisy.
        priority_order = (3, 2, 1, 4, 5, 6, 7)

        for layer_num in priority_order:
            if layer_num in self.available_layer_numbers:
                return freq, pol, layer_num
        else:
            errmsg = (
                f"Prioritization order of layer groups is {priority_order}, but"
                " the product only contains layers"
                f" {self.available_layer_numbers}."
            )
            raise nisarqa.InvalidNISARProductError(errmsg)

    def _get_path_containing_freq_pol(self, freq: str, pol: str) -> str:
        # Each polarization should contain the same layer numbers.
        # WLOG, use the first available layer number.
        return self._numbered_layer_group_path(
            freq=freq, pol=pol, layer_num=self.available_layer_numbers[0]
        )

    def _numbered_layer_group_path(
        self, freq: str, pol: str, layer_num: int
    ) -> str:
        """Get path in input file to the group for this numbered layer group."""
        return f"{self.get_freq_path(freq)}/pixelOffsets/{pol}/layer{layer_num}"

    @contextmanager
    def get_along_track_offset(
        self, freq: str, pol: str, layer_num: int
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the along track offset *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.
        layer_num : int
            Layer number of the desired raster. For example, to get the
            requested raster from the `layer1` group, set `layer_num` to `1`.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._numbered_layer_group_path(freq, pol, layer_num)
        path = f"{parent_path}/alongTrackOffset"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_slant_range_offset(
        self, freq: str, pol: str, layer_num: int
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the slant range offset *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.
        layer_num : int
            Layer number of the desired raster. For example, to get the
            requested raster from the `layer1` group, set `layer_num` to `1`.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._numbered_layer_group_path(freq, pol, layer_num)
        path = f"{parent_path}/slantRangeOffset"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_along_track_offset_variance(
        self, freq: str, pol: str, layer_num: int
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the along track offset variance *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.
        layer_num : int
            Layer number of the desired raster. For example, to get the
            requested raster from the `layer1` group, set `layer_num` to `1`.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._numbered_layer_group_path(freq, pol, layer_num)
        path = f"{parent_path}/alongTrackOffsetVariance"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_slant_range_offset_variance(
        self, freq: str, pol: str, layer_num: int
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the slant range offset variance *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.
        layer_num : int
            Layer number of the desired raster. For example, to get the
            requested raster from the `layer1` group, set `layer_num` to `1`.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._numbered_layer_group_path(freq, pol, layer_num)
        path = f"{parent_path}/slantRangeOffsetVariance"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_cross_offset_variance(
        self, freq: str, pol: str, layer_num: int
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the cross offset variance *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.
        layer_num : int
            Layer number of the desired raster. For example, to get the
            requested raster from the `layer1` group, set `layer_num` to `1`.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._numbered_layer_group_path(freq, pol, layer_num)
        path = f"{parent_path}/crossOffsetVariance"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )

    @contextmanager
    def get_correlation_surface_peak(
        self, freq: str, pol: str, layer_num: int
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Get the correlation surface peak *RasterWithStats.

        Parameters
        ----------
        freq, pol : str
            Frequency and polarization (respectively) for the desired raster.
        layer_num : int
            Layer number of the desired raster. For example, to get the
            requested raster from the `layer1` group, set `layer_num` to `1`.

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
        """
        parent_path = self._numbered_layer_group_path(freq, pol, layer_num)
        path = f"{parent_path}/correlationSurfacePeak"

        with h5py.File(self.filepath) as f:
            yield self._get_raster_from_path(
                h5_file=f, raster_path=path, parse_stats=True
            )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
