from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from functools import lru_cache

import h5py
import isce3

import nisarqa

from .nisar_product import NisarProduct

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass
class InsarProduct(NisarProduct):
    def get_browse_freq_pol(self) -> tuple[str, str]:
        """
        Return the frequency and polarization for the browse image.

        Returns
        -------
        freq, pol : pair of str
            The frequency and polarization to use for the browse image.
        """
        for freq in ("A", "B"):
            if freq not in self.freqs:
                continue

            for pol in ("HH", "VV", "HV", "VH"):
                if pol not in self.get_pols(freq=freq):
                    continue

                return freq, pol

        # The input product does not contain the expected frequencies and/or
        # polarization combinations
        raise nisarqa.InvalidNISARProductError

    def _get_raster_name(self, raster_path: str) -> str:
        """
        Return a name for the raster, e.g. 'RSLC_LSAR_A_HH'.

        Parameters
        ----------
        raster_path : str
            Full path in `h5_file` to the desired raster dataset.
            Example:
                "/science/LSAR/GUNW/grids/frequencyA/interferogram/HH/unwrappedPhase"

        Returns
        -------
        name : str
            The human-understandable name that is derived from the dataset.
            Example:
                "GUNW_L_A_HH_unwrappedPhase"
        """
        # InSAR product. Example `raster_path` to parse:
        # "/science/LSAR/RIFG/swaths/frequencyA/pixelOffsets/HH/alongTrackOffset"
        band = self.band
        freq = "A" if ("frequencyA" in raster_path) else "B"
        path = raster_path.split("/")
        group = path[-3]
        pol = path[-2]
        layer = path[-1]

        # Sanity check
        assert pol in nisarqa.get_possible_pols(
            product_type=self.product_type.lower()
        )

        name = (
            f"{self.product_type.upper()}_{band}_{freq}_{group}_{pol}_{layer}"
        )
        return name

    @abstractmethod
    def _get_path_containing_freq_pol(self, freq: str, pol: str) -> str:
        """
        Return a potential valid path in input HDF5 containing `freq` and `pol`.

        This is a helper method (for e.g. `get_pols()`) which provides a
        generic way to get the path to a group in the product containing
        a particular frequency+polarization.
        The returned path may or may not exist in the NISAR input product.

        Parameters
        ----------
        freq : str
            Frequency of interest. Must be one of "A" or "B".
        pol : str
            Polarization of interest. Examples: "HH" or "HV".

        Returns
        -------
        path : str
            A potential valid path in the dataset which incorporates the
            requested freq and pol.

        See Also
        --------
        get_pols : Returns the polarizations for the requested frequency.
        """
        pass

    def get_pols(self, freq: str) -> tuple[str, ...]:
        """
        Get the polarizations for the given frequency.

        Parameters
        ----------
        freq : str
            Either "A" or "B".

        Returns
        -------
        pols : tuple[str]
            Tuple of the available polarizations in the input product
            for the requested frequency.

        Raises
        ------
        DatasetNotFoundError
            If no polarizations were found for this frequency.
        InvalidNISARProductError
            If the polarizations found are inconsistent with the polarizations
            listed in product's `listOfPolarizations` dataset for this freq.
        """
        if freq not in ("A", "B"):
            raise ValueError(f"{freq=}, must be one of 'A' or 'B'.")

        @lru_cache
        def _get_pols(freq):
            log = nisarqa.get_logger()
            pols = []
            with h5py.File(self.filepath) as f:
                for pol in nisarqa.get_possible_pols(self.product_type.lower()):
                    pol_path = self._get_path_containing_freq_pol(freq, pol)
                    try:
                        f[pol_path]
                    except KeyError:
                        log.info(
                            f"Did not locate polarization group at: {pol_path}"
                        )
                    else:
                        log.info(f"Located polarization group at: {pol_path}")
                        pols.append(pol)

            # Sanity checks
            # Check the "discovered" polarizations against the expected
            # `listOfPolarizations` dataset contents
            list_of_pols_ds = self.get_list_of_polarizations(freq=freq)
            if set(pols) != set(list_of_pols_ds):
                errmsg = (
                    f"Frequency {freq} contains polarizations {pols}, but"
                    f" `listOfPolarizations` says {list_of_pols_ds}"
                    " should be available."
                )
                raise nisarqa.InvalidNISARProductError(errmsg)

            if not pols:
                # No polarizations were found for this frequency
                errmsg = f"No polarizations were found for frequency {freq}"
                raise nisarqa.DatasetNotFoundError(errmsg)

            return pols

        return tuple(_get_pols(freq))

    def save_qa_metadata_to_h5(self, stats_h5: h5py.File) -> None:
        """
        Populate `stats_h5` file with a list of each available polarization.

        If the input file contains Frequency A, then this dataset will
        be created in `stats_h5`:
            /science/<band>/QA/data/frequencyA/listOfPolarizations

        If the input file contains Frequency B, then this dataset will
        be created in `stats_h5`:
            /science/<band>/QA/data/frequencyB/listOfPolarizations

        * Note: The paths are pulled from nisarqa.STATS_H5_QA_FREQ_GROUP.
        If the value of that global changes, then the path for the
        `listOfPolarizations` dataset(s) will change accordingly.

        Parameters
        ----------
        stats_h5 : h5py.File
            Handle to an HDF5 file where the list(s) of polarizations
            should be saved.
        """
        band = self.band

        for freq in self.freqs:
            list_of_pols = self.get_pols(freq=freq)

            nisarqa.create_dataset_in_h5group(
                h5_file=stats_h5,
                grp_path=nisarqa.STATS_H5_QA_FREQ_GROUP % (band, freq),
                ds_name="listOfPolarizations",
                ds_data=list_of_pols,
                ds_description=f"Polarizations for Frequency {freq}.",
            )

    def get_orbit(self, ref_or_sec: str) -> isce3.core.Orbit:
        """
        Get the orbit of the specified input RSLC for the input granule.

        Parameters
        ----------
        ref_or_sec : {"reference", "secondary"}
            InSAR granules are generated from two input RSLC granules,
            referred to as the "reference RSLC" and the "secondary RSLC".
            Specifiying "reference" will return the Orbit for the
            reference RSLC, and  specifying "secondary" will
            return the Orbit for the secondary RSLC.

        Returns
        -------
        orbit : isce3.core.Orbit
            The Orbit for the requested reference or secondary RSLC.
        """

        if ref_or_sec not in ("reference", "secondary"):
            raise ValueError(
                f"{ref_or_sec=}, must be either 'reference' or 'secondary'."
            )

        orbit_path = "/".join([self._metadata_group_path, "orbit", ref_or_sec])
        with h5py.File(self.filepath, "r") as f:
            try:
                orbit_grp = f[orbit_path]
            except KeyError as e:
                if nisarqa.Version.from_string(
                    self.product_spec_version
                ) < nisarqa.Version.from_string("1.1.1"):
                    # Prior to product specs 1.1.1, InSAR products contained
                    # only one orbit group (the orbit for the reference RSLC).
                    if ref_or_sec == "secondary":
                        raise ValueError(
                            "Input granule only contains one orbit group which"
                            " corresponds to the reference RSLC, but the orbit"
                            " for the secondary RSLC was requested."
                        )
                    orbit_path = "/".join([self._metadata_group_path, "orbit"])
                    orbit_grp = f[orbit_path]
                else:
                    raise
            orbit = isce3.core.load_orbit_from_h5_group(orbit_grp)

        return orbit

    def center_freq(self, freq: str) -> float:
        """
        The center frequency for input product's Frequency `freq`.

        Parameters
        ----------
        freq : str
            Must be either "A" or "B".

        Returns
        -------
        center_freq : float
            The center frequency for input product's Frequency `freq`, in hertz.
        """
        center_freq_path = f"{self.get_freq_path(freq=freq)}/centerFrequency"
        with h5py.File(self.filepath, "r") as f:
            center_freq = f[center_freq_path][...]

        return center_freq

    def wavelength(self, freq: str) -> float:
        """
        The wavelength for input product's Frequency `freq`.

        Parameters
        ----------
        freq : str
            Must be either "A" or "B".

        Returns
        -------
        wavelength : float
            The wavelength for input product's Frequency `freq`, in meters.
        """
        # Wavelength can be inferred from the centerFrequency dataset
        # centerFrequency is in units of hertz
        center_freq = self.center_freq(freq=freq)

        # wavelength = <speed of light> / centerFrequency
        return isce3.core.speed_of_light / center_freq


__all__ = nisarqa.get_all(__name__, objects_to_skip)
