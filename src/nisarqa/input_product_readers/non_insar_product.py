from __future__ import annotations

import os
from abc import abstractmethod
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property

import h5py
import numpy as np

import nisarqa

from .nisar_product import NisarProduct

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass
class NonInsarProduct(NisarProduct):
    """Common functionality for RSLC, GLSC, and GCOV products."""

    def get_rfi_likelihood_path(self, freq: str, pol: str) -> str:
        """
        Get the path to the RFI likelihood h5py Dataset.

        Parameters
        ----------
        freq : {'A', 'B'}
            The frequency sub-band. Must be a valid sub-band in the product.
        pol : str
            The desired polarization, e.g. "HH" or "HV".
            Warning: For GCOV, this should be a polarization (e.g. "HH"), and
            not a GCOV term (e.g. "HHHH"). The list of available polarizations
            in the input product can be accessed via the product reader's
            `nisarqa.NisarProduct.get_list_of_polarizations()` method.

        Returns
        -------
        rfi_likelihood_path : str
            The path to the radio frequency interference (RFI) likelihood
            Dataset for the given freq and pol.

        Warnings
        --------
        `rfiLikelihood` was added in ISCE3 v0.17.0 for R3.4.1.
        Unfortunately, that release does not correspond directly to product
        specification version number. Product Specification v1.1.0 and later
        should have this dataset, but it's messy to algorithmically
        handle the products generated prior to that. The returned
        `rfi_likelihood_path` will be correct for products generated with
        ISCE3 v0.17.0 and later, but might not exist in earlier test datasets.
        The calling function should handle this case accordingly.

        See Also
        --------
        copy_rfi_metadata_to_stats_h5 :
            Copies RFI likelihood Dataset from the input product to STATS.h5.

        Notes
        -----
        Typically, QA returns the Dataset's actual values, and not a path
        to an h5py.Dataset. However, this Dataset is only being used by
        `copy_rfi_metadata_to_stats_h5()`, which needs to wholesale copy
        the Dataset and its Attributes. By returning just the path, then
        any new Attributes in subsequent ISCE3 releases will be automatically
        get copied as well.
        """
        path = (
            f"{self._calibration_metadata_path}/"
            + f"frequency{freq}/{pol}/rfiLikelihood"
        )

        spec = nisarqa.Version.from_string(self.product_spec_version)
        if spec < nisarqa.Version(1, 1, 0):
            nisarqa.get_logger().warning(
                "Input product was generated with an older product spec; the"
                " `rfiLikelihood` Dataset might not exist for"
                f" frequency {freq}, polarization {pol}. Path: {path}"
            )

        return path

    def metadata_neb_luts(self, freq: str) -> Iterator[nisarqa.MetadataLUT2D]:
        """
        Generator for metadata LUTs in noise equivalent backscatter Group.

        These are located under the `calibrationInformation` Group.

        Parameters
        ----------
        freq : {'A', 'B'}
            The frequency sub-band. Must be a valid sub-band in the product.

        Yields
        ------
        ds : nisarqa.MetadataLUT2D
            The next MetadataLUT2D in this Group:
            `../metadata/calibrationInformation/frequency<freq>/noiseEquivalentBackscatter`
        """
        with (
            h5py.File(self.filepath, "r") as f,
            self.get_noise_eq_group(freq) as neb_grp,
        ):
            for ds_arr in neb_grp.values():
                if isinstance(ds_arr, h5py.Group):
                    raise TypeError(
                        f"Unexpected HDF5 Group found in {neb_grp.name}."
                        " Metadata Groups should only contain Datasets."
                    )
                ds_path = ds_arr.name

                n_dim = np.ndim(ds_arr)
                if n_dim in (0, 1):
                    # Scalar and 1D Datasets in this group are coordinate
                    # dimensions and georeferencing info -- not metadata LUTs.
                    # Skip.
                    pass
                elif n_dim != 2:
                    raise ValueError(
                        "The `noiseEquivalentBackscatter` metadata group"
                        " should only contain scalar, 1D, or 2D Datasets."
                        f" Dataset contains {n_dim} dimensions: {ds_path}"
                    )
                else:
                    yield self._build_metadata_lut(f=f, ds_arr=ds_arr)

    def metadata_elevation_antenna_pat_luts(
        self, freq: str
    ) -> Iterator[nisarqa.MetadataLUT2D]:
        """
        Generator for all elevation antenna pattern metadata LUTs.

        Yields
        ------
        ds : nisarqa.MetadataLUT2D
            The next MetadataLUT2D in this Group:
            `../metadata/calibrationInformation/frequency<freq>/elevationAntennaPattern`
        """
        with h5py.File(self.filepath, "r") as f:
            grp_path = "/".join(
                [
                    self._calibration_metadata_path,
                    f"frequency{freq}/elevationAntennaPattern",
                ]
            )
            grp = f[grp_path]
            for ds_arr in grp.values():
                if isinstance(ds_arr, h5py.Group):
                    raise TypeError(
                        f"unexpected HDF5 Group found in {grp_path}."
                        " Metadata Groups should only contain Datasets."
                    )
                ds_path = ds_arr.name

                n_dim = np.ndim(ds_arr)
                if n_dim in (0, 1):
                    # Scalar and 1D Datasets in this group are coordinate
                    # dimensions and georeferencing info -- not metadata LUTs.
                    # Skip.
                    pass
                elif n_dim != 2:
                    raise ValueError(
                        f"The elevationAntennaPattern metadata group should"
                        " should only contain scalar, 1D, or 2D Datasets."
                        f" Dataset contains {n_dim} dimensions: {ds_path}"
                    )
                else:
                    yield self._build_metadata_lut(f=f, ds_arr=ds_arr)

    @abstractmethod
    def get_layers_for_browse(self) -> dict[str, list[str]]:
        """
        Determine which polarization layers to use to generate the browse image.

        Returns
        -------
        layers_for_browse : dict
            Dict of the polarizations layers to use. Its structure is:
                layers_for_browse[<freq>] : List of the polarization(s)
                                            e.g. ['HH','HV'] for SLCs,
                                            or ["HHHH", "HVHV"] for GCOV
        """
        pass

    @staticmethod
    @abstractmethod
    def save_browse(
        pol_imgs: Mapping[str, np.ndarray], filepath: str | os.PathLike
    ) -> None:
        """
        Save given polarization images to a RGB or Grayscale PNG.

        Dimensions of the output PNG (in pixels) will be the same as the
        dimensions of the input polarization image array(s). (No scaling will
        occur.) Non-finite values will be made transparent.

        Parameters
        ----------
        pol_imgs : dict of numpy.ndarray
            Dictionary of 2D array(s) that will be mapped to specific color
            channel(s) for the output browse PNG.
            If there are multiple image arrays, they must have identical shape.
            Format of dictionary:
                pol_imgs[<polarization>] : <2D numpy.ndarray image>
            Example:
                pol_imgs['HHHH'] : <2D numpy.ndarray image>
                pol_imgs['VVVV'] : <2D numpy.ndarray image>
        filepath : path-like
            Full filepath for where to save the browse image PNG.

        Notes
        -----
        Provided image array(s) must previously be image-corrected. This
        function will take the image array(s) as-is and will not apply
        additional image correction processing to them. This function directly
        combines the image(s) into a single browse image.
        If there are multiple input images, they must be thoughtfully prepared
        and standardized relative to each other prior to use by this function.
        For example, trying to combine a Freq A 20 MHz image
        and a Freq B 5 MHz image into the same output browse image might not go
        well, unless the image arrays were properly prepared and standardized
        in advance.
        """
        pass

    @contextmanager
    def get_raster(
        self, freq: str, pol: str
    ) -> Iterator[nisarqa.RadarRasterWithStats | nisarqa.GeoRasterWithStats]:
        """
        Context Manager for a *RasterWithStats for the specified imagery raster.

        Parameters
        ----------
        freq : str
            One of the frequencies returned by `self.freqs()`.
        pol : str
            The desired polarization.
              For RSLC and GSLC, use e.g. "HH", "HV",
              For GCOV, use e.g. "HHVV"

        Yields
        ------
        raster : RadarRasterWithStats or GeoRasterWithStats
            Generated *RasterWithStats for the requested dataset.
            Warning: the input NISAR file cannot be opened by ISCE3 until
            this context manager is exited.

        Raises
        ------
        DatasetNotFoundError
            If the file does not contain the requested raster dataset,
            or if any of the corresponding metadata for that raster are
            not located.
        """
        if freq not in self.freqs:
            raise ValueError(f"{freq=}, must be one of: {self.freqs=}")

        poss_pols = nisarqa.get_possible_pols(
            product_type=self.product_type.lower()
        )
        if pol not in poss_pols:
            raise ValueError(f"{pol=}, must be one of: {poss_pols}.")

        path = self._layers[freq][pol]

        with h5py.File(self.filepath, "r") as in_file:
            if path not in in_file:
                errmsg = f"Input file does not contain raster {path}"
                raise nisarqa.DatasetNotFoundError(errmsg)
            yield self._get_raster_from_path(
                h5_file=in_file, raster_path=path, parse_stats=True
            )

    def _get_raster_name(self, raster_path: str) -> str:
        """
        Return a name for the raster, e.g. 'RSLC_LSAR_A_HH'.

        Parameters
        ----------
        raster_path : str
            Full path in `h5_file` to the desired raster dataset.
            Example:
                "/science/LSAR/GSLC/grids/frequencyA/HH"

        Returns
        -------
        name : str
            The human-understandable name that is derived from the dataset.
            Example:
                "GSLC_L_A_HH"
        """
        freq = "A" if ("frequencyA" in raster_path) else "B"
        pol = raster_path.split("/")[-1]
        name = f"{self.product_type}_{self.band}_{freq}_{pol}"

        return name

    @cached_property
    def _layers(self) -> dict[str, dict[str, str]]:
        """
        Locate available bands, frequencies, and polarizations in the product.

        Returns
        -------
        layers : nested dict of str
            Nested dict of paths to input file raster datasets.
            Format: layers[<freq>][<pol>] -> str
            Example:
                layers["A"]["HH"] -> "/science/LSAR/RSLC/swaths/frequencyA/HH"
        """
        # Discover images in input file and populate the `pols` dictionary
        with h5py.File(self.filepath) as h5_file:
            layers = {}
            for freq in self.freqs:
                path = self.get_freq_path(freq=freq)
                layers[freq] = {}

                for pol in nisarqa.get_possible_pols(self.product_type.lower()):
                    raster_path = f"{path}/{pol}"
                    if raster_path in h5_file:
                        layers[freq][pol] = raster_path

        # Sanity Check - if a band/freq does not have any polarizations,
        # this is a validation error. This check should be handled during
        # the validation process before this function was called,
        # not the quality process, so raise an error.
        # In the future, this step might be moved earlier in the
        # processing, and changed to be handled via: 'log the error
        # and remove the band from the dictionary'
        for freq in layers:
            # Empty dictionaries evaluate to False in Python
            if not layers[freq]:
                raise ValueError(
                    "Provided input file does not have any polarizations"
                    f" included under band {self.band}, frequency {freq}."
                )

        return layers

    def get_pols(self, freq: str) -> tuple[str, ...]:
        """
        Get a tuple of the available polarizations for frequency `freq`.

        Parameters
        ----------
        freq : str
            One of the frequencies in `self.freqs`.

        Returns
        -------
        pols : tuple of str
            An tuple of the available polarizations for the requested
            frequency.
                Example for RSLC or GSLC: ("HH", "VV")
                Example for GCOV: ("HHHH", "HVHH", "VVVV")
        """
        if freq not in self.freqs:
            raise ValueError(
                f"Requested frequency {freq}, but product only contains"
                f" frequencies {self.freqs}."
            )

        layers = self._layers
        pols = tuple(layers[freq].keys())

        if not pols:
            # No polarizations were found for this frequency
            errmsg = f"No polarizations were found for frequency {freq}"
            raise nisarqa.DatasetNotFoundError(errmsg)

        return pols

    @cached_property
    def _calibration_metadata_path(self) -> str:
        """
        Path in the input file to the `metadata/calibrationInformation` Group.

        Returns
        -------
        path : str
            Path in input file to the metadata/calibrationInformation Group.
        """
        return "/".join([self._metadata_group_path, "calibrationInformation"])

    @contextmanager
    def get_noise_eq_group(self, freq: str) -> Iterator[h5py.Group]:
        """
        Get the `noiseEquivalentBackscatter` h5py Group.

        Parameters
        ----------
        freq : {'A', 'B'}
            The frequency sub-band. Must be a valid sub-band in the product.

        Yields
        ------
        neb_grp : h5py.Group
            Noise Equivalent Backscatter (NEB) Group in the input product for
            the given `freq`.

        Raises
        ------
        nisarqa.InvalidNISARProductError
            The returned `neb_grp` will be correct for products generated with
            ISCE3 R4 and later, but is not guaranteed for earlier test datasets.
            If QA cannot find this Group at a known path, this error is raised.

        Warnings
        --------
        ISCE3 products generated for R4 with product specification version
        1.1.0 to <1.2.0 should contain a group called `nes0`. Some products
        generated with product specifications <1.1.0 also contain a `nes0`
        group, but this cannot be guaranteed, or the nes0 data might follow
        an entirely different specification structure.
        ISCE3 products generated for R4.0.4 or later with product specification
        version >=1.2.0 should contain an equivalent group called
        `noiseEquivalentBackscatter`. (For R4.0.4, `nes0` was renamed.)
        Unfortunately, the official ISCE3 releases do not perfectly align
        with updates to the product specification version, so some products
        will have out-of-sync product spec version numbers and dataset names.

        For simplicity, QA should only support data products with the
        newer NEB structure (>= ISCE3 R4).

        Notes
        -----
        Typically, QA product reader returns a actual values, and not an
        h5py.Group. However, this function is being used by `run_neb_tool()`,
        which needs to wholesale copy the Group and its contents recursively.
        """
        log = nisarqa.get_logger()
        spec = nisarqa.Version.from_string(self.product_spec_version)

        with h5py.File(self.filepath, "r") as f:
            grp = f[f"{self._calibration_metadata_path}/frequency{freq}"]
            if "noiseEquivalentBackscatter" in grp:
                yield grp["noiseEquivalentBackscatter"]
            elif "nes0" in grp:
                if spec >= nisarqa.Version(1, 2, 0):
                    nisarqa.get_logger().error(
                        "Input product has product specification version"
                        f" {spec} and contains a `nes0` Group. As of"
                        " product specification version 1.2.0, this should"
                        " instead be named `noiseEquivalentBackscatter`."
                    )
                yield grp["nes0"]
            else:
                # product does not contain a "nes0" group (old spec)
                # nor a "noiseEquivalentBackscatter" group. Log and fail.
                msg = (
                    f"For frequency {freq}, product does not contain a"
                    " Group with noise equivalent backscatter information"
                    " at a known path."
                )

                if spec < nisarqa.Version(1, 1, 0):
                    log.error(
                        "Input product was generated with an older product"
                        " spec. " + msg
                    )
                else:
                    log.error(msg)
                raise nisarqa.InvalidNISARProductError(msg)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
