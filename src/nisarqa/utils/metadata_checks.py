from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import TypeVar

import h5py
import numpy as np
from osgeo import gdal, osr

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass
class MetadataDataset1D:
    """
    1D metadata dataset.

    Parameters
    ----------
    data : array_like
        Metadata dataset with shape (X,). Can be a numpy.ndarray, h5py.Dataset,
        etc. The dataset will be coerced to and stored as a NumPy array.
    name : str
        Name for this Dataset. If source data is from an HDF5 file, suggest
        using the full path to the Dataset for `name`.
    x_coord_vector : array_like
        1D vector with shape (X,) containing the coordinate values for the
        x axis of the dataset.
        For L1 products, this is the `slantRange` corresponding to `data`.
        For L2 products, this is the `xCoordinates` corresponding to `data`.
    """

    data: np.ndarray
    name: str
    x_coord_vector: np.ndarray

    def __post_init__(self):

        # Metadata datasets are, by design, very small in size. So, coerce these
        # input ArrayLike objects to NumPy arrays during init.
        # Otherwise, they may be repeatedly converted to (temporary) NumPy
        # arrays as we pass them to NumPy functions, matplotlib, etc.
        self.data = np.asanyarray(self.data)
        self.x_coord_vector = np.asanyarray(self.x_coord_vector)

        if self.shape[-1] != len(self.x_coord_vector):
            raise ValueError(
                f"Dataset {self.name} has x dimension {self.shape[-1]},"
                f" which should match the length of the cooresponding x-axis"
                f" coordinate vector which is {len(self.x_coord_vector)}."
            )

    @property
    def shape(self) -> tuple[int, ...]:
        """Shape of the metadata dataset."""
        return self.data.shape


@dataclass
class MetadataDataset2D(MetadataDataset1D):
    """
    2D metadata dataset.

    Parameters
    ----------
    data : array_like
        Metadata dataset with shape (Y, X). Can be a numpy.ndarray, h5py.Dataset,
        etc. The dataset will be coerced to and stored as a NumPy array.
    name : str
        Name for this Dataset. If data is from an HDF5 file, suggest using
        the full path to the Dataset for `name`.
    x_coord_vector : array_like
        1D vector with shape (X,) containing the coordinate values for the
        x axis of the dataset.
        For L1 products, this is the `slantRange` corresponding to `data`.
        For L2 products, this is the `xCoordinates` corresponding to `data`.
    y_coord_vector : array_like
        1D vector with shape (Y,) containing the coordinate values for the
        y axis of the dataset.
        For L1 products, this is the `zeroDopplerTime` corresponding to `data`.
        For L2 products, this is the `yCoordinates` corresponding to `data`.
    """

    y_coord_vector: np.ndarray

    def __post_init__(self):

        super().__post_init__()

        self.y_coord_vector = np.asanyarray(self.y_coord_vector)

        if self.shape[-2] != len(self.y_coord_vector):
            raise ValueError(
                f"Dataset {self.name} has y dimension {self.shape[-2]},"
                f" which should match the length of the cooresponding y-axis"
                f" coordinate vector which is {len(self.y_coord_vector)}."
            )


@dataclass
class MetadataDataset3D(MetadataDataset2D):
    """
    3D metadata dataset.

    Parameters
    ----------
    data : array_like
        Metadata dataset with shape (Z, Y, X). Can be a numpy.ndarray,
        h5py.Dataset, etc. The dataset will be coerced to and stored as
        a NumPy array.
    name : str
        Name for this Dataset. If data is from an HDF5 file, suggest using
        the full path to the Dataset for `name`. If `name` ends with 'Baseline',
        the dataset will be assumed to be a parallel baseline or perpendicular
        baseline dataset, which may have a z-dimension of 2 regardless of the
        size of `z_coord_vector`.
    x_coord_vector : array_like
        1D vector with shape (X,) containing the coordinate values for the
        x axis of the dataset.
        For L1 products, this is the `slantRange` corresponding to `data`.
        For L2 products, this is the `xCoordinates` corresponding to `data`.
    y_coord_vector : array_like
        1D vector with shape (Y,) containing the coordinate values for the
        y axis of the dataset.
        For L1 products, this is the `zeroDopplerTime` corresponding to `data`.
        For L2 products, this is the `yCoordinates` corresponding to `data`.
    z_coord_vector : array_like
        1D vector with shape (Z,) containing the coordinate values for the
        z axis of the dataset.
        For NISAR, this is `heightAboveEllipsoid` corresponding to `data`.
    """

    z_coord_vector: np.ndarray

    def __post_init__(self):

        super().__post_init__()
        self.z_coord_vector = np.asanyarray(self.z_coord_vector)

        len_z = len(self.z_coord_vector)
        if self.shape[-3] != len_z:
            if self.name.endswith("Baseline"):
                # `parallelBaseline` and `perpendicularBaseline` Datasets
                # either have a height of 2 or the length of the z coordinates
                if self.shape[-3] != 2:
                    raise nisarqa.InvalidRasterError(
                        f"Dataset {self.name} has z dimension {self.shape[-3]},"
                        " which should either be 2 or match the length of the"
                        " cooresponding z-axis coordinate vector which is"
                        f" {len_z}."
                    )
                else:
                    len_z = 2
            else:
                raise nisarqa.InvalidRasterError(
                    f"Dataset {self.name} has z dimension {self.shape[-3]},"
                    f" which should match the length of the cooresponding"
                    f" z-axis coordinate vector which is {len_z}."
                )


def verify_metadata_cubes(
    product: nisarqa.NisarProduct, fail_if_all_nan: bool = True
) -> None:
    """
    Verify the input product's coordinate grid metadata cubes are valid.

    Coordinate grid metadata cubes are the 3D datasets in the input product's
    coordinate grid (e.g. `geolocationGrid` or `radarGrid`) metadata group.

    Parameters
    ----------
    product : nisarqa.NisarProduct
        Instance of the input product.
    fail_if_all_nan : bool, optional
        True to raise an exception if one of the metadata cubes contains
        all non-finite (e.g. Nan, +/- Inf) values, or if one of the
        z-dimension height layers in a 3D dataset has all non-finite values.
        False to quiet the exception, although it will still be logged.
        Defaults to True.

    Raises
    ------
    nisarqa.InvalidRasterError
        If `fail_if_all_nan` is True and if one or more metadata datasets
        contains all non-finite (e.g. Nan, +/- Inf) values, or if one of
        the z-dimension height layers in a 3D dataset has all non-finite values.
    """

    # Flag indicating if metadata datasets pass all verification checks; used
    # for Summary CSV reporting
    passes = True
    has_finite = True

    # Check metadata datasets in metadata Group
    try:
        # Note: During the __post_init__ of constructing each metadata dataset,
        # several validation checks are performed, including ensuring that
        # there are corresponding datasets with x coordinates and y coordinates
        # of the correct length. If these elements are missing, exceptions
        # will get thrown.
        for cube in product.coordinate_grid_metadata_cubes():
            has_finite &= _dataset_has_finite_pixels(cube)
            passes &= has_finite
            passes &= _dataset_is_not_all_zeros(cube)
            passes &= _check_gdal(product=product, ds=cube)

    except (nisarqa.DatasetNotFoundError, ValueError):
        nisarqa.get_logger().error(traceback.format_exc())
        passes = False

    # SUMMARY LOG
    summary = nisarqa.get_summary()
    summary.check_metadata_cubes(result="PASS" if passes else "FAIL")

    if fail_if_all_nan and (not has_finite):
        raise nisarqa.InvalidRasterError(
            "One or more metadata cubes contains all non-finite"
            " (e.g. NaN, +/- Inf) values or one of the z-dimension height"
            " layers in a cube has all non-finite values. See log file"
            " for details and names of the failing dataset(s)."
        )


def verify_calibration_metadata(
    product: nisarqa.NonInsarProduct, fail_if_all_nan: bool = True
) -> None:
    """
    Verify if the input product's calibration metadata datasets are valid.

    Parameters
    ----------
    product : nisarqa.NonInsarProduct
        Instance of the input product.
    fail_if_all_nan : bool, optional
        True to raise an exception if one of the metadata datasets contains
        all non-finite (e.g. Nan, +/- Inf) values.
        False to quiet the exception, although it will still be logged.
        Defaults to True.

    Raises
    ------
    nisarqa.InvalidRasterError
        If `fail_if_all_nan` is True and if one or more metadata datasets
        contains all non-finite (e.g. Nan, +/- Inf) values.
    """
    log = nisarqa.get_logger()
    # Flag indicating if metadata datasets pass all verification checks; used
    # for Summary CSV reporting
    passes = True
    has_finite = True

    # Check metadata datasets in metadata Group
    try:
        # Note: During the __post_init__ of constructing each metadata dataset,
        # several validation checks are performed, including ensuring that
        # there are corresponding datasets with x coordinates and y coordinates
        # of the correct length. If these elements are missing, exceptions
        # will get thrown.
        spec = nisarqa.Version.from_string(product.product_spec_version)

        for freq in product.freqs:

            if spec < nisarqa.Version(1, 1, 0):
                break

            for ds in product.metadata_neb_datasets(freq):
                has_finite &= _dataset_has_finite_pixels(ds)
                passes &= has_finite
                passes &= _dataset_is_not_all_zeros(ds)
                passes &= _check_gdal(product=product, ds=ds)

            for ds in product.metadata_elevation_antenna_pat_datasets(freq):
                has_finite &= _dataset_has_finite_pixels(ds)
                passes &= has_finite
                passes &= _dataset_is_not_all_zeros(ds)
                passes &= _check_gdal(product=product, ds=ds)

            if isinstance(product, nisarqa.SLC):
                for ds in product.metadata_geometry_datasets():
                    has_finite &= _dataset_has_finite_pixels(ds)
                    passes &= has_finite
                    passes &= _dataset_is_not_all_zeros(ds)
                    passes &= _check_gdal(product=product, ds=ds)

            if isinstance(product, nisarqa.RSLC):
                for ds in product.metadata_crosstalk_datasets():
                    has_finite &= _dataset_has_finite_pixels(ds)
                    passes &= has_finite
                    passes &= _dataset_is_not_all_zeros(ds)
                summary_notes = ""
            else:
                # GSLC and GCOV products contain the `crosstalk` Group with
                # datasets copied directly from the input RSLC product,
                # but these are neither geocoded nor georeferenced.
                # This means that that there is no corresponding
                # e.g. `xCoordinates` datasets, so it is not possible to
                # build/test a MetadataDataset.
                log.warning(
                    "Verification of calibration information `crosstalk`"
                    " metadata datasets was skipped by QA. Please update QA"
                    " code once these datasets become georeferenced."
                )
                summary_notes = "`crosstalk` datasets skipped."

    except (nisarqa.DatasetNotFoundError, ValueError):
        log.error(traceback.format_exc())
        passes = False

    # SUMMARY LOG
    summary = nisarqa.get_summary()
    summary.check_calibration_metadata(
        result="PASS" if passes else "FAIL", notes=summary_notes
    )

    if fail_if_all_nan and (not has_finite):
        raise nisarqa.InvalidRasterError(
            "One or more calibration metadata datasets contains all non-finite"
            " (e.g. NaN, +/- Inf) values. See log file"
            " for details and names of the failing dataset(s)."
        )


def _check_gdal(
    product: nisarqa.NisarProduct,
    ds: nisarqa.MetadataDataset2D | nisarqa.MetadataDataset3D,
) -> bool:
    """
    Check if product and member dataset are either L1, or L2 and GDAL-friendly.

    Always returns `True` if the dataset is not geocoded and/or not an
    h5py.Dataset.

    Parameters
    ----------
    product : nisarqa.NisarProduct
        Instance of the input product. If product is not geocoded (e.g. it
        is an L1 product), the function will always return True.
    ds : nisarqa.MetadataDataset2D or nisarqa.MetadataDataset3D
        Metadata Dataset to be checked. If `ds.data` is not an h5py.Dataset,
        the function will always return True.

    Returns
    -------
    passes : bool
        True if the dataset contains at least one finite pixel (meaning, it is
        considered a valid dataset), or if input product is not geocoded,
         or if `ds` is not an h5py.Dataset.
        False if the given metadata dataset contains all non-finite (e.g. NaN,
        +/- Inf) values.
        Or, if the dataset is 3D, and if any of the z-dimension
        height layers is all non-finite, it is also considered malformed and we
        return False.
    """
    if product.is_geocoded and isinstance(ds.data, h5py.Dataset):
        return is_gdal_friendly(
            input_filepath=product.filepath, ds_path=ds.data.name
        )
    else:
        return True


def is_gdal_friendly(input_filepath: str, ds_path: str) -> bool:
    """
    Return True if the Dataset is GDAL-friendly; False if not.

    This function uses GDAL to open the file and test if the specified
    Dataset is georeferenced in a way that GDAL can read. For example, this
    function tests if that Dataset has a valid `grid_mapping` attribute, if
    it has a valid spatial reference and projection, etc.

    Parameters
    ----------
    input_filepath : str
        Full filepath to the input NISAR product.
    ds_path : str
        HDF5 Path in `input_filepath` to a (hopefully) georeferenced Dataset.

    Returns
    -------
    passes : bool
        True if the Dataset at `ds_path` is GDAL-friendly; False if GDAL
        cannot successfully georeference the Dataset.
    """

    log = nisarqa.get_logger()

    good_msg = f"Dataset is GDAL-friendly: {ds_path}"
    bad_msg = good_msg.replace("is ", "is not ")

    gdal_ds = gdal.Open(f'NETCDF:"{input_filepath}":{ds_path}')

    # If Dataset does not have a `grid_mapping` attribute, then GetProjection()
    # returns an empty string. However, GDAL will still construct a spatial
    # reference from that empty string, which has a valid EPSG code.

    # However, if, for example, the Dataset's corresponding `xCoordinates`
    # Dataset is the incorrect length, then GetProjection() raises an
    # AttributeError.

    try:
        wkt = gdal_ds.GetProjection()
    except AttributeError:
        log.error(bad_msg)
        return False

    if wkt == "":
        log.error(bad_msg)
        return False

    proj = osr.SpatialReference(wkt=wkt)

    # If Dataset's corresponding "projection" Dataset is set to a bad EPSG
    # code (e.g. 9999), then `proj.GetAttrValue("AUTHORITY", 1)` returns None.
    # Otherwise, it returns the EPSG code, e.g. 32645
    epsg = proj.GetAttrValue("AUTHORITY", 1)

    # If Dataset does not have a `grid_mapping` attribute, then GetSpatialRef()
    # returns None.
    crs = gdal_ds.GetSpatialRef()

    if (crs is None) or (epsg is None):
        log.error(bad_msg)
        return False
    # Note: this is specifically checking that the dataset used a map
    # projection (e.g. UTM, UPS)
    # It is *not* checking that the dataset contained a projection, which
    # just means that it stored coordinate system info.
    # If the dataset is Lon/Lat, this check will be false
    elif crs.IsProjected() == 1:
        log.info(good_msg)
        return True
    else:
        log.error(bad_msg)
        return False


def _dataset_has_finite_pixels(ds: nisarqa.MetadataDatasetT) -> bool:
    """
    Return False if dataset contains all non-finite values; True otherwise.

    Parameters
    ----------
    ds : nisarqa.MetadataDatasetT
        Metadata Dataset to be checked.

    Returns
    -------
    passes : bool
        True if the dataset contains at least one finite pixel. (Meaning, it is
        considered a valid dataset.)
        False if the given metadata dataset contains all non-finite (e.g. NaN,
        +/- Inf) values.
        Or, if the dataset is 3D, and if any of the z-dimension
        height layers is all non-finite, it is also considered malformed and we
        return False.
    """
    log = nisarqa.get_logger()

    if not np.isfinite(ds.data).any():
        log.error(
            f"Metadata dataset {ds.name} contains all non-finite"
            " (e.g. NaN) values."
        )
        return False

    # For 3-D datasets, check each z-layer individually for all-NaN values.
    if isinstance(ds, MetadataDataset3D):
        for z in range(ds.shape[0]):
            if not np.isfinite(ds.data[z, :, :]).any():
                log.error(
                    f"Metadata dataset {ds.name} z-axis layer number {z}"
                    " contains all non-finite (e.g. NaN) values."
                )
                return False

    return True


def _dataset_is_not_all_zeros(ds: nisarqa.MetadataDatasetT) -> bool:
    """
    Return False if metadata dataset contains all near-zeros; True otherwise.

    Parameters
    ----------
    ds : nisarqa.MetadataDatasetT
        Metadata Dataset to be checked.

    Returns
    -------
    Passes : bool
        True if the dataset contains at least one non-near-zero pixel. (Meaning,
        it is considered a valid dataset.)
        False if the given metadata dataset contain all near-zero ( <1e-12 )
        values, it is likely a malformed Dataset.
        Or, if the dataset is 3D, and if any of the z-dimension
        height layers is all near-zero, it is also considered malformed and we
        return False.
    """
    log = nisarqa.get_logger()

    if np.all(np.abs(ds.data) < 1e-12):
        # This check is likely to raise a lot of failures.
        # We do not want to halt processing during CalVal.
        # So, issue obnoxious warnings for now.
        # TODO - refine this check during CalVal once real data comes back.
        msg = (
            f"Metadata dataset {ds.name} contains all near-zero"
            " (<1e-12) values."
        )
        log.warning(msg)
        return False

    # For 3-D datasets, check each z-layer individually for all near-zero values.
    if isinstance(ds, MetadataDataset3D):
        for z in range(ds.shape[0]):
            if np.all(np.abs(ds.data[z, :, :]) < 1e-12):
                # This check is likely to raise a lot of failures.
                # We do not want to halt processing during CalVal.
                # So, issue obnoxious warnings for now.
                # TODO - refine this check during CalVal once real data comes back.
                msg = (
                    f"Metadata dataset {ds.name} z-axis layer number {z}"
                    " contains all near-zero (<1e-12) values."
                )
                log.warning(msg)
                return False
    return True


__all__ = nisarqa.get_all(__name__, objects_to_skip)
