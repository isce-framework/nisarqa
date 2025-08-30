from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from functools import cached_property, lru_cache
from pathlib import Path

import h5py
import numpy as np

import nisarqa

from ._utils import _get_path_to_nearest_dataset, _get_paths_in_h5

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass
class NisarProduct(ABC):
    """
    Base class for NISAR product readers.

    Parameters
    ----------
    filepath : path-like
        Filepath to the input product.
    use_cache : bool, optional
        True to use memory map(s) to cache select Dataset(s) in
        memory-mapped files in the global scratch directory.
        False to always read data directly from the input file.
        Generally, enabling caching should reduce runtime.
        Defaults to False.
    """

    filepath: str
    use_cache: bool = False

    def __post_init__(self):
        # Verify that the input product contained a product spec version.
        self.product_spec_version

        self._check_product_type()
        self._check_root_path()
        self._check_is_geocoded()
        self._check_data_group_path()

    @property
    @abstractmethod
    def product_type(self) -> str:
        """Product type (e.g. "RSLC" or "GCOV")."""
        pass

    @property
    @abstractmethod
    def is_geocoded(self) -> bool:
        """True if product is geocoded; False if range Doppler grid."""
        pass

    @abstractmethod
    def get_browse_latlonquad(self) -> nisarqa.LatLonQuad:
        """
        Create a LatLonQuad for the corners of the input product.

        Returns
        -------
        llq : LatLonQuad
            A LatLonQuad object containing the four corner coordinates for this
            product's browse image, in degrees.
        """
        pass

    @cached_property
    def bounding_polygon(self) -> str:
        """Bounding polygon WKT string."""
        id_group = self.identification_path
        with h5py.File(self.filepath) as f:
            wkt = f[id_group]["boundingPolygon"][()]
            return nisarqa.byte_string_to_python_str(wkt)

    @cached_property
    def granule_id(self) -> str:
        """Granule ID (or the base filename if granule ID is not present)."""
        id_group = self.identification_path
        with h5py.File(self.filepath) as f:
            try:
                granule_id = f[id_group]["granuleId"][()]
            except KeyError:
                # During NISAR development, we often encounter legacy products that
                # are named according to NISAR conventions but are missing granule
                # ID metadata, so this bandaid is sometimes useful.
                nisarqa.get_logger().error(
                    "`granuleId` Dataset missing from input product's"
                    "`identification` group."
                )
                return Path(self.filepath).name
            return nisarqa.byte_string_to_python_str(granule_id)

    @cached_property
    def look_direction(self) -> str:
        """Look direction of the sensor, either 'Left' or 'Right'."""
        id_group = self.identification_path
        with h5py.File(self.filepath) as f:
            lookside = f[id_group]["lookDirection"][()]

        lookside = nisarqa.byte_string_to_python_str(lookside)

        valid_options = {"Left", "Right"}
        if lookside not in valid_options:
            msg = (
                f"Input product's `lookDirection` is {lookside}, must"
                f" be one of {valid_options}."
            )
            lookside_lower = lookside.lower()
            if lookside_lower == "left":
                nisarqa.get_logger().warning(msg)
                lookside = "Left"
            elif lookside_lower == "right":
                nisarqa.get_logger().warning(msg)
                lookside = "Right"
            else:
                raise ValueError(msg)

        return lookside

    @cached_property
    def identification_path(self) -> str:
        """
        Return the path to the identification group in the input file.

        Assumes that the input file contains only one path whose base name
        is "identification". If multiple such paths exist, or if no paths
        have that base name, then an exception is raised.

        Returns
        -------
        id_group : str
            The path to the identification group in the input file.

        Raises
        ------
        nisarqa.InvalidNISARProductError
            If "identification" is not found exactly one time in the input file.
        """
        with h5py.File(self.filepath) as f:
            paths = _get_paths_in_h5(h5_file=f, name="identification")

        if len(paths) != 1:
            raise nisarqa.InvalidNISARProductError(
                "Input product must contain exactly one group named"
                f" 'identification'. Found: {paths}"
            )

        return paths[0]

    @cached_property
    def product_spec_version(self) -> str:
        """
        Return the product specification version.

        Returns
        -------
        spec_version : str
            The value of "productSpecificationVersion" in the "identification"
            group in the input file. If this field is missing (such as with
            older test datasets), "0.0.0" is returned.
        """
        id_group = self.identification_path
        with h5py.File(self.filepath) as f:
            if "productSpecificationVersion" in f[id_group]:
                spec_version = f[id_group]["productSpecificationVersion"][...]
                spec_version = nisarqa.byte_string_to_python_str(spec_version)
                nisarqa.get_logger().info(
                    "Input product's"
                    " `identification/productSpecificationVersion` dataset"
                    f" contains {spec_version}."
                )
            else:
                # spec for very old test datasets.
                # `productSpecificationVersion` metadata was added after this.
                spec_version = "0.0.0"
                nisarqa.get_logger().error(
                    "`productSpecificationVersion` missing from input product's"
                    " `identification` group. Defaulting to '0.0.0'."
                )

            return spec_version

    @cached_property
    def runconfig_contents(self) -> str:
        """
        Contents (verbatim) of input granule's `runConfigurationContents`.

        Returns the Dataset contents as-is, with no further processing.
        It is a known issue that the L1/L2 product types use different formats
        for `runConfigurationContents` (e.g. JSON, YAML). If that format is
        updated within ISCE3, then this function will simply continue to
        copy the Dataset's contents as-is.

        Returns
        -------
        runconfig_contents : str
            Contents (verbatim) of input granule's `runConfigurationContents`.
            If the product does not contain that Dataset (such as for older
            granules), "N/A" is returned.
        """
        path = (
            self._processing_info_metadata_group_path
            + "/parameters/runConfigurationContents"
        )
        with h5py.File(self.filepath) as f:
            if path in f:
                runconfig = f[path][...]
                return nisarqa.byte_string_to_python_str(runconfig)
            else:
                # Very old test datasets did not have this field.
                # Discrepancies between this and the spec will be logged
                # via the XML checker; no need to report again here.
                nisarqa.get_logger().error(
                    "`runConfigurationContents` not found in input product"
                    f" at the path {path}. Defaulting to 'N/A'."
                )
                return "N/A"

    @cached_property
    def list_of_frequencies(self) -> tuple[str, ...]:
        """
        The contents of .../identification/listOfFrequencies in input file.

        Returns
        -------
        list_of_freqs : tuple of str
            The contents of `listOfFrequencies` in the `identification`
            group in the input file.
            `list_of_freqs` will be one of: ("A",), ("B",), or ("A", "B").

        Raises
        ------
        ValueError
            If `listOfFrequencies` contains invalid options.
        KeyError
            If `listOfFrequencies` is missing.
        """
        log = nisarqa.get_logger()

        id_group = self.identification_path

        with h5py.File(self.filepath) as f:
            # listOfFrequencies should be in all test datasets.
            # If not, let h5py handle raising an error message.
            list_of_freqs = f[id_group]["listOfFrequencies"]
            nisarqa.verify_str_meets_isce3_conventions(ds=list_of_freqs)

            if list_of_freqs.shape == ():
                # dataset is scalar, not a list
                list_of_freqs = [
                    nisarqa.byte_string_to_python_str(list_of_freqs[()])
                ]
                log.error(
                    "`listOfFrequencies` dataset is a scalar string, should"
                    " be an array of byte strings."
                )
            else:
                if np.issubdtype(list_of_freqs.dtype, np.bytes_):
                    # list of byte strings. Yay!
                    list_of_freqs = nisarqa.byte_string_to_python_str(
                        list_of_freqs[()]
                    )
                elif isinstance(list_of_freqs[0], bytes):
                    # list of Python bytes objects. Boo.
                    # This edge case occurs in some InSAR datasets, and should
                    # be fixed for R4.
                    list_of_freqs = [
                        my_str.decode("utf-8") for my_str in list_of_freqs[()]
                    ]
                    # That's what we want to return in this function, but it
                    # does not meet NISAR specs, so log an error.
                    log.error(
                        "`listOfFrequencies` dataset is an array of objects of"
                        " type `bytes`, but should be an array of byte strings."
                    )
                else:
                    raise TypeError(
                        "`listOfFrequencies` dataset is an array of items of"
                        f" type {type(list_of_freqs[0])}, but should be an"
                        " array of byte strings."
                    )

            # Sanity check that the contents make sense
            if not set(list_of_freqs).issubset({"A", "B"}):
                raise ValueError(
                    "Input file's `listOfFrequencies` dataset contains"
                    f" {list_of_freqs}, but must be a subset of ('A', 'B')."
                )

            return tuple(list_of_freqs)

    def get_list_of_polarizations(self, freq: str) -> tuple[str, ...]:
        """
        Gets contents of .../frequency<freq>/listOfPolarizations in input file.

        Returns
        -------
        list_of_pols : tuple of str
            The contents of `listOfPolarizations` in the `.../frequency<freq>`
            group in the input file. Example output: ("HH", "HV").

        Raises
        ------
        ValueError
            If `listOfPolarizations` contains invalid options.
        KeyError
            If `listOfPolarizations` is missing.
        """

        # `listOfPolarizations` is always a child of the frequency group.
        freq_group = self.get_freq_path(freq=freq)
        log = nisarqa.get_logger()

        with h5py.File(self.filepath) as f:
            # `listOfPolarizations` should be in all frequency groups.
            # If not, let h5py handle raising an error message.
            list_of_pols = f[freq_group]["listOfPolarizations"]
            nisarqa.verify_str_meets_isce3_conventions(ds=list_of_pols)

            if list_of_pols.shape == ():
                # dataset is scalar, not an array
                list_of_pols = [
                    nisarqa.byte_string_to_python_str(list_of_pols[()])
                ]
                log.error(
                    f"`{list_of_pols.name}` dataset is a scalar string, should"
                    " be an array of byte strings."
                )
            else:
                if np.issubdtype(list_of_pols.dtype, np.bytes_):
                    # list of byte strings. Yay!
                    list_of_pols = nisarqa.byte_string_to_python_str(
                        list_of_pols[()]
                    )
                elif isinstance(list_of_pols[0], bytes):
                    # list of Python bytes objects. Boo.
                    # This edge case occurs in some InSAR datasets, and should
                    # be fixed for R4.
                    list_of_pols = [
                        my_str.decode("utf-8") for my_str in list_of_pols[()]
                    ]
                    # That's what we want to return in this function, but it
                    # does not meet NISAR specs, so log an error.
                    log.error(
                        "`listOfPolarizations` dataset is an array of objects"
                        " of type `bytes`, but should be an array of byte"
                        " strings."
                    )
                else:
                    raise TypeError(
                        "`listOfPolarizations` dataset is an array of items of"
                        f" type {type(list_of_pols[0])}, but should be an array"
                        " of byte strings."
                    )

            # Sanity check that the contents make sense
            poss_pols = nisarqa.get_possible_pols(self.product_type.lower())

            if self.product_type == "GCOV":
                # For GCOV, `get_possible_pols()` actually returns the
                # possible covariance terms, e.g. "HHHH", "HVHV".
                # So to get specifically the possible polarizations, we need
                # to truncate to the first two letters, and remove duplicates.
                poss_pols = set([pol[:2] for pol in poss_pols])

            if not set(list_of_pols).issubset(set(poss_pols)):
                raise ValueError(
                    "Input file's `listOfPolarizations` dataset contains"
                    f" {list_of_pols}, but must be a subset of {poss_pols}."
                )

            return tuple(list_of_pols)

    @cached_property
    def _root_path(self) -> str:
        """
        Get the path to the group which is the root for the primary groups.

        Returns
        -------
        root : str
            Path to the directory where the product data is stored.
                Standard Format: "/science/<band>/<product_type>
                Example:
                    "/science/LSAR/RSLC"

        See Also
        --------
        _data_group_path : Constructs the path to the data group.

        Notes
        -----
        In products up to and including the R3.4 delivery (which used product
        spec 0.9.0), this will be something like "/science/LSAR".
        This structure is set up like e.g.:
            /science/LSAR/RSLC/swaths/frequencyX/...
            /science/LSAR/RSLC/metadata/...
            /science/LSAR/identification
        In subsequent deliveries, that path will likely be truncated. All
        products would follow a consistent structure, something like:
            /data/frequencyX/...
            /metadata/...
            /identification
        In that case, the empty string "" should be returned by this function.
        """
        id_group = self.identification_path
        # The `identification` group is found at e.g.:
        #   "/science/LSAR/identification"
        # Remove identification.
        root = id_group.replace("/identification", "")
        return root

    def _check_root_path(self) -> None:
        """Sanity check that `self._root_path` is valid."""

        with h5py.File(self.filepath) as f:
            # Conditional branch for datasets <=R3.4 (TBD possibly beyond)
            if self._root_path not in f:
                raise ValueError(
                    f"self._root_path determined to be {self._root_path},"
                    " but this is not a valid path in the input file."
                )

    @cached_property
    def band(self) -> str:
        """
        Get the frequency-band ("L" or "S") of the input file.

        Assumption by QA SAS: each input product contains only one band.

        Returns
        -------
        band : str
            The input file's band. (One of "L" or "S").
        """
        log = nisarqa.get_logger()

        id_group = self.identification_path
        band = None

        with h5py.File(self.filepath) as f:
            try:
                band = f[id_group]["radarBand"][...]
            except KeyError:
                # Error: product is poorly formed, will cause issues once the
                # below TODO is removed.
                log.error("`radarBand` missing from `identification` group.")
            else:
                band = nisarqa.byte_string_to_python_str(band)

        # TODO - remove the below code once all test data sets are updated to
        # new product spec
        # Attempt to determine the band from the frequency group path
        if band is None:
            # WLOG, get the path to one of the frequency groups
            path = self.get_freq_path(freq=self.freqs[0])
            for b in ("L", "S"):
                if f"{b}SAR" in path:
                    band = b
                    break
            else:
                # Product updated to not include the band in the
                # "/science/LSAR/..." directory structure
                raise ValueError("Cannot determine band from product.")

        return band

    @cached_property
    def freqs(self) -> tuple[str, ...]:
        """
        The available frequencies in the input file.

        Returns
        -------
        found_freqs : tuple of str
            The available frequencies in the input file. Will be a subset of
            ("A", "B").

        Raises
        ------
        nisarqa.InvalidNISARProductError
            If no frequency groups are found.

        Notes
        -----
        "frequency" in this context is different than the typical
        meaning of e.g. "L-band" or "S-band" frequencies.
        In QA SAS, the convention is for e.g. L band or S band
        to be referred to as "bands", while the section of the band used
        for the raster data is referred to as "frequency."
        Most satellites are single band instruments, meaning that "band" and
        "frequency" are one and the same, so this distinction is redundant.
        However, the NISAR mission is capable of dual frequency data collection,
        (meaning that two frequencies of data can be collected within a single
        band), hence the reason for this distinction. For NISAR, these
        are referred to as "Frequency A" and "Freqency B".
        """
        log = nisarqa.get_logger()

        # Get paths to the frequency groups
        found_freqs = []
        for freq in ("A", "B"):
            try:
                path = self.get_freq_path(freq=freq)
            except nisarqa.DatasetNotFoundError:
                log.info(f"Frequency{freq} group not found.")
            else:
                found_freqs.append(freq)
                log.info(f"Found Frequency {freq} group: {path}")

        # Sanity checks
        # Check the "discovered" frequencies against the contents of the
        # `listOfFrequencies` dataset
        list_of_frequencies = self.list_of_frequencies
        if set(found_freqs) != set(list_of_frequencies):
            errmsg = (
                f"Input products contains frequencies {found_freqs}, but"
                f" `listOfFrequencies` says {list_of_frequencies}"
                " should be available."
            )
            raise nisarqa.InvalidNISARProductError(errmsg)

        if not found_freqs:
            errmsg = "Input product does not contain any frequency groups."
            raise nisarqa.InvalidNISARProductError(errmsg)

        return tuple(found_freqs)

    def get_freq_path(self, freq: str) -> str:
        """
        Return the path inside the input file to the specified frequency group.

        Parameters
        ----------
        freq : str
            Must be either "A" or "B".

        Returns
        -------
        path : str
            Path inside the input file to the requested frequency group.

        Raises
        ------
        nisarqa.DatasetNotFoundError
            If frequency not found in the input file.
        """
        if freq not in ("A", "B"):
            raise ValueError(f"{freq=}, must be either 'A' or 'B'")

        # We cannot use functools.lru_cache() on a instance method due to
        # the `self` parameter, so use an inner function to cache the results.
        @lru_cache
        def _freq_path(freq):
            log = nisarqa.get_logger()
            path = self._data_group_path + f"/frequency{freq}"
            with h5py.File(self.filepath) as f:
                if path in f:
                    return path
                else:
                    errmsg = (
                        f"Input file does not contain frequency {freq} group at"
                        f" path: {path}"
                    )
                    raise nisarqa.DatasetNotFoundError(errmsg)

        return _freq_path(freq)

    @cached_property
    def metadata_path(self) -> str:
        """
        The path in the input file to the `metadata` Group.

        Returns
        -------
        path : str
            Path inside the input file to the primary `metadata` Group.
        """
        return "/".join([self._root_path, self.product_type, "metadata"])

    @cached_property
    def science_freq(self) -> str:
        """
        The science frequency (primary frequency) of the input product.

        Returns
        -------
        freq : str
            The science frequency for the input product. One of: "A" or "B".
        """
        return "A" if "A" in self.freqs else "B"

    def ground_track_velocity(self) -> nisarqa.MetadataLUT3D:
        """
        Get the ground track velocity metadata cube.

        Returns
        -------
        grd_trk_vel : nisarqa.MetadataLUT3D
            The ground track velocity metadata cube.
        """
        grd_trk_path = "/".join(
            [self._coordinate_grid_metadata_group_path, "groundTrackVelocity"]
        )

        with h5py.File(self.filepath, "r") as f:
            return self._build_metadata_lut(f=f, ds_arr=f[grd_trk_path])

    def _check_product_type(self) -> None:
        """
        Sanity check for `self.product_type`.

        Ensures that `self.product_type` returns a value
        that matches the `identification > productType` dataset in the
        input file.
        """
        id_group = self.identification_path

        with h5py.File(self.filepath) as f:
            in_file_prod_type = f[id_group]["productType"][...]
            in_file_prod_type = nisarqa.byte_string_to_python_str(
                in_file_prod_type
            )

        if self.product_type != in_file_prod_type:
            raise ValueError(
                f"QA requested for {self.product_type}, but input file's"
                f" `productType` field is {in_file_prod_type}."
            )

    def _check_is_geocoded(self) -> None:
        """Sanity check for `self.is_geocoded`."""
        log = nisarqa.get_logger()

        id_group = self.identification_path

        with h5py.File(self.filepath) as f:
            if "isGeocoded" in f[id_group]:
                # Check that `isGeocoded` is set correctly, i.e. that it is
                # False in range Doppler products, and True in Geocoded products
                ds_handle = f[id_group]["isGeocoded"]

                # Check that the value has the correct dtype and formatting
                # (this reports the results to the log)
                nisarqa.verify_isce3_boolean(ds_handle)

                data = ds_handle[()]

                if np.issubdtype(data.dtype, np.bytes_):
                    data = nisarqa.byte_string_to_python_str(data)

                    # Convert from string to boolean. (`verify_isce3_boolean()`
                    # already logged if data is one of True or False.)
                    # Without this conversion, casting the string "False" as
                    # a boolean results in True.
                    data = data == "True"

                if self.is_geocoded != bool(data):
                    log.error(
                        "WARNING `/identification/isGeocoded` field has value"
                        f" {ds_handle[...]}, which is inconsistent with"
                        f" product type of {self.product_type}."
                    )
                else:
                    log.info(
                        "`/identification/isGeocoded` field has value"
                        f" {ds_handle[...]}, which is consistent with"
                        f" product type of {self.product_type}."
                    )
            else:
                # The `isGeocoded` field is not necessary for successful
                # completion QA SAS: whether a product is geocoded
                # or not can be determined by the product type (e.g. RSLC vs.
                # GSLC). So let's simply log the error and let QA continue;
                # this will alert developers that the product is faulty.
                log.error("Product missing `/identification/isGeocoded` field")

    def _check_data_group_path(self) -> None:
        """Sanity check to ensure the grid path exists in the input file."""
        grid_path = self._data_group_path
        with h5py.File(self.filepath) as f:
            if grid_path not in f:
                errmsg = f"Input file is missing the path: {grid_path}"
                raise nisarqa.DatasetNotFoundError(errmsg)

    def coordinate_grid_metadata_cubes(
        self,
    ) -> Iterator[nisarqa.MetadataLUT3D]:
        """
        Generator for all metadata cubes in `../metadata/xxxGrid` Group.

        For L1 products, this is the `../metadata/geolocationGrid` Group.
        For L2 products, this is the `../metadata/radarGrid` Group.

        Yields
        ------
        cube : nisarqa.MetadataLUT3D
            The next MetadataLUT3D in the Group.
        """
        with h5py.File(self.filepath, "r") as f:
            grp_path = self._coordinate_grid_metadata_group_path
            grp = f[grp_path]
            for ds_arr in grp.values():

                if isinstance(ds_arr, h5py.Group):
                    raise TypeError(
                        f"unexpected HDF5 Group found in {grp_path}."
                        " Metadata cubes Groups should only contain Datasets."
                    )
                ds_path = ds_arr.name

                n_dim = np.ndim(ds_arr)
                if n_dim in (0, 1):
                    # Scalar and 1D Datasets in this group are coordinate
                    # dimensions and georeferencing info -- not metadata LUTs.
                    # Skip.
                    pass
                elif n_dim != 3:
                    raise ValueError(
                        f"The coordinate grid metadata group should only"
                        " should only contain scalar, 1D, or 3D Datasets."
                        f" Dataset contains {n_dim} dimensions: {ds_path}"
                    )
                else:
                    yield self._build_metadata_lut(f=f, ds_arr=ds_arr)

    @abstractmethod
    def _data_group_path(self) -> str:
        """
        Return the path to the group containing the primary datasets.

        For range Doppler products, this should be e.g.:
            'science/LSAR/RIFG/swaths'
        For geocoded products, this should be e.g.:
            'science/LSAR/RIFG/grids'

        Returns
        -------
        root : str
            Path to the directory where the product data is stored.
                Standard Format:
                    "science/<band>/<product_type>/<'swaths' OR 'grids'>"
                Example:
                    "science/LSAR/RSLC/swaths"

        See Also
        --------
        _root_path : Constructs the path to the primary root group.

        Notes
        -----
        A common implementation for this would be e.g.:
            return "/".join([self._root_path, self.product_type, "swaths"])

        In products up to and including the R3.4 delivery (which used product
        spec 0.9.0), the L1/L2 product structure is set up like e.g.:
            /science/LSAR/RSLC/swaths/frequencyX/...
            /science/LSAR/RSLC/metadata/...
            /science/LSAR/identification
        In which case "/science/LSAR/RSLC/swaths" should be returned.

        In subsequent deliveries, that path will likely be truncated. All
        products would follow a consistent structure, something like:
            /data/frequencyX/...
            /metadata/...
            /identification
        In that case, the string "data" should be returned by this function.
        """
        pass

    @cached_property
    def _metadata_group_path(self) -> str:
        """
        Get the path to the metadata group.

        Returns
        -------
        root : str
            Path to the metadata directory.
                Standard Format: "/science/<band>/<product_type>/metadata
                Example:
                    "/science/LSAR/RSLC/metadata"

        Notes
        -----
        In products up to and including the R3.4 delivery (which used product
        spec 0.9.0), this input product structure is set up like e.g.:
            /science/LSAR/RSLC/swaths/frequencyX/...
            /science/LSAR/RSLC/metadata/...
            /science/LSAR/identification
        In subsequent deliveries, that path will likely be truncated. All
        products would follow a consistent structure, something like:
            /data/frequencyX/...
            /metadata/...
            /identification
        When that change is implemented, this function will need to be updated
        to accommodate the new spec.
        """
        return "/".join([self._root_path, self.product_type, "metadata"])

    @property
    @abstractmethod
    def _coordinate_grid_metadata_group_path(self) -> str:
        """
        Get the path to the coordinate grid metadata Group.

        Returns
        -------
        root : str
            Path to the metadata directory.
                Standard Rxxx Format:
                    "/science/<band>/<product_type>/metadata/geolocationGrid"
                Standard Gxxx Format:
                    "/science/<band>/<product_type>/metadata/radarGrid"
                Example:
                    "/science/LSAR/GSLC/metadata/radarGrid"
        """
        pass

    def _get_stats_h5_group_path(self, raster_path: str) -> str:
        """
        Return path where metrics for `raster_path` should be saved in STATS.h5 file.

        Parameters
        ----------
        raster_path : str
            Full path in the input HDF5 file to a raster dataset.
            Examples:
                GSLC (similar for RSLC/GCOV):
                    "/science/LSAR/GSLC/grids/frequencyA/HH"
                GUNW (similar for RIFG/RUNW):
                    "/science/LSAR/GUNW/grids/frequencyA/pixelOffsets/HH/alongTrackOffset"
                GOFF (similar for ROFF):
                    "/science/LSAR/GOFF/grids/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"

        Returns
        -------
        path : str
            Path in the STATS.h5 file for the group where all metrics and
            statistics re: this raster should be saved.
            Note that a path to a h5py.Dataset was passed in as an argument to
            this function, but a path to a h5py Group will be returned.
            Examples:
                RSLC/GSLC/GCOV: "/science/LSAR/QA/data/frequencyA/HH"
                RUNW/GUNW: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset"
                ROFF/GOFF: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"
        """
        # Let's mirror the structure of the input product for the STATS.h5 file
        # In essence, we need to replace the beginning part of the base path.

        # Check that the substring "frequency" occurs exactly once in `raster_path`
        assert raster_path.count("frequency") == 1
        _, suffix = raster_path.split("frequency")
        # remove everything before "frequency":
        suffix = f"frequency{suffix}"

        # Append the QA STATS.h5 data group path to the beginning
        path = f"{nisarqa.STATS_H5_QA_DATA_GROUP % self.band}/{suffix}"

        return path

    @abstractmethod
    def _get_raster_from_path(
        self, h5_file: h5py.File, raster_path: str, *, parse_stats: bool
    ) -> (
        nisarqa.RadarRaster
        | nisarqa.RadarRasterWithStats
        | nisarqa.GeoRaster
        | nisarqa.GeoRasterWithStats
    ):
        """
        Generate a *Raster for the raster at `raster_path`.

        Parameters
        ----------
        h5_file : h5py.File
            Open file handle for the input file containing the raster.
        raster_path : str
            Full path in `h5_file` to the desired raster dataset
            Examples:
                "/science/LSAR/RSLC/swaths/frequencyA/HH"
                "/science/LSAR/RIFG/swaths/frequencyA/interferogram/HH/wrappedInterferogram"
        parse_stats : bool
            If True, the min/max/mean/std statistics are parsed from the
            HDF5 attributes of the raster and a *RasterWithStats instance is
            returned.
            If False, a RadarRaster or GeoRaster instance is returned.

        Returns
        -------
        raster : nisarqa.RadarRaster or nisarqa.RadarRasterWithStats
                    or nisarqa.GeoRaster or nisarqa.GeoRasterWithStats
            *Raster of the given dataset.

        Raises
        ------
        DatasetNotFoundError
            If the file does not contain a raster dataset at `raster_path`,
            or if any of the corresponding metadata for that raster are
            not located.
        """
        pass

    @abstractmethod
    def _get_raster_name(self, raster_path: str) -> str:
        """
        Return a name for the raster, e.g. 'RSLC_LSAR_A_HH'.

        Parameters
        ----------
        raster_path : str
            Full path in `h5_file` to the desired raster dataset.
            Examples:
                "/science/LSAR/GSLC/grids/frequencyA/HH"
                "/science/LSAR/GUNW/grids/frequencyA/interferogram/HH/unwrappedPhase"

        Returns
        -------
        name : str
            The human-understandable name that is derived from the dataset.
            Examples: "GSLC_L_A_HH" or "GUNW_L_A_HH_unwrappedPhase".
        """
        pass

    def _build_metadata_lut(
        self,
        f: h5py.File,
        ds_arr: h5py.Dataset,
    ) -> nisarqa.typing.MetadataLUTT:
        """
        Construct a MetadataLUT for the given 1D, 2D, or 3D LUT.

        Parameters
        ----------
        f : h5py.File
            Handle to the NISAR input product.
        ds_arr : h5py.Dataset
            Path to the metadata LUT Dataset.

        Returns
        -------
        ds : nisarqa.typing.MetadataLUTT
            A constructed MetadataLUT of `ds_arr`. The number of dimensions
            of `ds_arr` determines whether a MetadataLUT1D, *2D, or *3D
            is returned.
        """
        # Get the full HDF5 path to the Dataset
        ds_path = ds_arr.name
        n_dim = ds_arr.ndim

        if n_dim not in (1, 2, 3):
            raise ValueError(f"{n_dim=}, must be 1, 2, or 3.")

        # build arguments dict for the MetadataLUTXD constructor.
        kwargs = {"data": ds_arr, "name": ds_path}

        if self.is_geocoded:
            names = ("xCoordinates", "yCoordinates")
        else:
            names = ("slantRange", "zeroDopplerTime")

        # In all L2 products, the coordinate datasets exist in the same group
        # as the dataset itself. However, in L1 products, some coordinate
        # datasets exist in a predecessor group, so we must recursively scan
        # parent directories until finding the coordinate dataset.
        kwargs["x_coord_vector"] = f[
            _get_path_to_nearest_dataset(
                h5_file=f,
                starting_path=ds_path,
                dataset_to_find=names[0],
            )
        ]
        if n_dim >= 2:
            kwargs["y_coord_vector"] = f[
                _get_path_to_nearest_dataset(
                    h5_file=f,
                    starting_path=ds_path,
                    dataset_to_find=names[1],
                )
            ]
        if n_dim == 3:
            kwargs["z_coord_vector"] = f[
                _get_path_to_nearest_dataset(
                    h5_file=f,
                    starting_path=ds_path,
                    dataset_to_find="heightAboveEllipsoid",
                )
            ]
        if n_dim == 1:
            lut_cls = nisarqa.MetadataLUT1D
        elif n_dim == 2:
            lut_cls = nisarqa.MetadataLUT2D
        else:
            lut_cls = nisarqa.MetadataLUT3D

        try:
            return lut_cls(**kwargs)
        except nisarqa.InvalidRasterError as e:
            if nisarqa.Version.from_string(
                self.product_spec_version
            ) < nisarqa.Version(1, 1, 0):
                # Older products sometimes had filler metadata.
                # log, and quiet the exception.
                nisarqa.get_logger().error(
                    f"Could not build MetadataLUT{n_dim}D for"
                    f" Dataset {ds_path}"
                )
            else:
                # Newer products should have complete metadata
                raise

    @cached_property
    def _processing_info_metadata_group_path(self) -> str:
        """
        Path in the input file to the `../metadata/processingInformation` Group.

        Returns
        -------
        path : str
            Path in input file to the ../metadata/processingInformation Group.
        """
        return "/".join([self._metadata_group_path, "processingInformation"])

    @cached_property
    def _algorithms_metadata_group_path(self) -> str:
        """
        Path in input file to `../processingInformation/algorithms` Group.

        Returns
        -------
        path : str
            Path in input file to the ../processingInformation/algorithms Group.
        """
        return "/".join(
            [self._processing_info_metadata_group_path, "algorithms"]
        )

    @cached_property
    def software_version(self) -> str:
        """
        The software version used to generate the HDF5 granule.

        For NISAR at JPL, this will typically be the version of ISCE3 used to
        generate the granule.

        Returns
        -------
        software_version : str
            The software version used to generate the HDF5 granule.
        """
        log = nisarqa.get_logger()

        path = f"{self._algorithms_metadata_group_path}/softwareVersion"

        try:
            with h5py.File(self.filepath) as in_f:
                isce3_version = in_f[path][()]
        except KeyError:
            return_val = "not available"
            msg = (
                f"Returning placeholder software version of {return_val!r}."
                f" `softwareVersion` does not exist at path: {path}"
            )
            spec = nisarqa.Version.from_string(self.product_spec_version)
            if spec < nisarqa.Version(1, 1, 0):
                log.warning(
                    f"Input product generated with an old product spec. {msg}"
                )
            else:
                log.error(msg)
            return return_val

        return nisarqa.byte_string_to_python_str(isce3_version)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
