from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from typing import overload

import isce3
import numpy as np
from numpy.typing import ArrayLike
from osgeo import osr


import nisarqa
from nisarqa.utils.typing import CoordinateGridT

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass
class CoordinateGrid(ABC):
    """Abstract Base Class for raster grid dataclasses."""

    @property
    @abstractmethod
    def x_posting(self):
        """
        Posting in X direction of raster grid.

        Notes
        -----
        "Spacing" refers to the (positive-valued) width of a pixel while
        "posting" refers to the (positive- or negative-valued) stride between
        points in a grid. (The spacing is the absolute value of the posting.)
        """
        pass

    @property
    def x_spacing(self):
        """
        Spacing in X direction of raster grid.

        Notes
        -----
        "Spacing" refers to the (positive-valued) width of a pixel while
        "posting" refers to the (positive- or negative-valued) stride between
        points in a grid. (The spacing is the absolute value of the posting.)
        """
        return abs(self.x_posting)

    @property
    @abstractmethod
    def x_pixel_centers(self):
        """
        1D vector of the raster grid's pixel center locations in X direction.
        """
        pass

    @property
    @abstractmethod
    def y_posting(self):
        """
        Posting in Y direction of raster grid.

        Notes
        -----
        "Spacing" refers to the (positive-valued) width of a pixel while
        "posting" refers to the (positive- or negative-valued) stride between
        points in a grid. (The spacing is the absolute value of the posting.)

        For NISAR L2 products, the y-coordinate posting of the
        coordinate grid is negative (the positive y-axis points up in QA plots).
        For NISAR L1 products (i.e. radar grids), the y-coordinate posting
        is positive (the positive y-axis points down in QA plots).
        """
        pass

    @property
    def y_spacing(self):
        """
        Spacing in Y direction of raster grid.

        Notes
        -----
        "Spacing" refers to the (positive-valued) width of a pixel while
        "posting" refers to the (positive- or negative-valued) stride between
        points in a grid. (The spacing is the absolute value of the posting.)
        """
        return abs(self.y_posting)

    @property
    @abstractmethod
    def y_pixel_centers(self):
        """
        1D vector of the raster grid's pixel center locations in Y direction.
        """
        pass

    @abstractmethod
    def downsample(
        self: CoordinateGridT, y_stride: int, x_stride: int, mode: str
    ) -> CoordinateGridT:
        """
        Downsample grid by the given strides and mode.

        Parameters
        ----------
        y_stride, x_stride : int
            Stride for downsampling along the Y (azimuth) or X (slant range)
            axis, respectively.
        mode : str, optional
            Downsampling algorithm. One of:
                "decimate" : Pure decimation. For example, if
                    `y_stride` is 3 and `x_stride` is 4, then rows 0, 3, ...,
                    and columns 0, 4, ... will be extracted to form
                    the downsampled grid.
                "multilook" : Naive, unweighted multilooking. For example, if
                    `y_stride` is 3 and `x_stride` is 4,
                    then every 3-by-4 window (12 pixels total) will be averaged
                    to form the output pixel.
                    Note that if any of those 12 input pixels is NaN, then the
                    output pixel will be NaN.

        Returns
        -------
        downsampled_grid : nisarqa.typing.CoordinateGridT:
            Copy of this instance which has been downsampled.
            If instance is a RadarGrid, then a RadarGrid will be returned.
            If instance is a GeoGrid, then a GeoGrid will be returned.

        Notes
        -----
        Coordinates whose index is greater than the largest integer
        multiple of the Y and X stride (along their respective axis)
        will be truncated/ignored.
        """
        pass

    def _downsample(
        self, y_stride: int, x_stride: int, mode: str
    ) -> tuple[np.ndarray, np.ndarray, float, float]:
        """
        Downsample this CoordinateGrid's properties by given strides and mode.

        Parameters
        ----------
        y_stride, x_stride : int
            Stride for downsampling along the Y (azimuth) or X (slant range)
            axis, respectively.
        mode : str, optional
            Downsampling algorithm. One of:
                "decimate" : (default) Pure decimation. For example, if
                    `y_stride` is 3 and `x_stride` is 4, then rows 0, 3, ...,
                    and columns 0, 4, ... will be extracted to form
                    the downsampled grid.
                "multilook" : Naive, unweighted multilooking. For example, if
                    `y_stride` is 3 and `x_stride` is 4,
                    then every 3-by-4 window (12 pixels total) will be averaged
                    to form the output pixel.
                    Note that if any of those 12 input pixels is NaN, then the
                    output pixel will be NaN.

        Returns
        -------
        y_coords, x_coords, y_posting, x_posting :
            Downsampled copies of the instance's properties.

        Notes
        -----
        - Coordinates whose index is greater than the largest integer
        multiple of the Y and X stride (along their respective axis)
        will be truncated/ignored.
        """
        if y_stride < 1:
            raise ValueError(f"{y_stride=}, must be >= 1.")
        if x_stride < 1:
            raise ValueError(f"{x_stride=}, must be >= 1.")

        # Downsample to the correct size along the X and Y directions.
        if mode == "decimate":
            y_coords = self.y_pixel_centers[::y_stride]
            x_coords = self.x_pixel_centers[::x_stride]

        elif mode == "multilook":
            y_coords = _get_multilooked_center_coordinates(
                coords=self.y_pixel_centers, nlooks=y_stride
            )
            x_coords = _get_multilooked_center_coordinates(
                coords=self.x_pixel_centers, nlooks=x_stride
            )
        else:
            raise ValueError(
                f"`{mode=}`, only 'decimate' and 'multilook' supported."
            )

        y_post = self.y_posting * y_stride
        assert np.isclose(
            y_post, y_coords[1] - y_coords[0]
        ), f"{y_post=}, {y_coords[1] - y_coords[0]=}"

        x_post = self.x_posting * x_stride
        assert np.isclose(x_post, x_coords[1] - x_coords[0])

        return y_coords, x_coords, y_post, x_post


@dataclass
class RadarGrid(CoordinateGrid):
    """
    Uniformly-spaced 2D grid in radar (azimuth time, slant range) coordinates.

    The attributes specified here are based on the needs of the QA code
    for generating and labeling plots, etc.

    Parameters
    ----------
    zero_doppler_time : numpy.ndarray
        1D vector of zero Doppler azimuth times (in seconds) measured relative
        to a UTC epoch. These correspond to the center of each pixel
        of the raster grid in the Y direction.
    zero_doppler_time_spacing : float
        Time interval in the along-track direction of the raster, in seconds.
        This is same as the spacing between consecutive entries in the
        `zero_doppler_time` array.
    slant_range : numpy.ndarray
        1D vector of the slant range values (in meters), corresponding to
        the center of each pixel of the raster grid in the X direction.
    slant_range_spacing : float
        Slant range spacing of grid, in meters. Same as difference between
        consecutive samples in `slant_range` array.
    ground_az_spacing : float
        Scene center azimuth spacing of pixels of the grid, in meters.
    ground_range_spacing : float
        Scene center ground range spacing of pixels of the grid, in meters.
    epoch : str
        The reference epoch for time coordinates in the grid,
        in the format 'YYYY-MM-DDTHH:MM:SS'.

    Attributes
    ----------
    az_start : float
        The start time of the radar grid.
        This corresponds to the upper edge of the top pixels.
        Units: seconds since epoch
    az_stop : float
        The stopping time of the radar grid.
        This corresponds to the lower side of the bottom pixels.
        Units: seconds since epoch
    rng_start : float
        Start (near) range of the radar grid.
        This corresponds to the left side of the left-most pixels.
        Units: meters
    rng_stop : float
        End (far) range of the radar grid.
        This corresponds to the right side of the right-most pixels.
        Units: meters

    Notes
    -----
    Provided initialization parameters will also be stored as attributes.
    """

    # Attributes of the input array
    zero_doppler_time: np.ndarray
    zero_doppler_time_spacing: float

    slant_range: np.ndarray
    slant_range_spacing: float

    ground_az_spacing: float
    ground_range_spacing: float

    epoch: str

    az_start: float = field(init=False)
    az_stop: float = field(init=False)
    rng_start: float = field(init=False)
    rng_stop: float = field(init=False)

    def __post_init__(self):

        self.zero_doppler_time_spacing = float(self.zero_doppler_time_spacing)
        self.slant_range_spacing = float(self.slant_range_spacing)
        self.ground_az_spacing = float(self.ground_az_spacing)
        self.ground_range_spacing = float(self.ground_range_spacing)

        # Infer start and stop values

        # For NISAR, radar-domain grids are referenced by the center of the
        # pixel, so +/- half the distance of the pixel's side to capture
        # the entire range.
        self.az_start = (
            float(self.zero_doppler_time[0])
            - 0.5 * self.zero_doppler_time_spacing
        )
        self.az_stop = (
            float(self.zero_doppler_time[-1])
            + 0.5 * self.zero_doppler_time_spacing
        )

        # For NISAR, radar-domain grids are referenced by the center of the
        # pixel, so +/- half the distance of the pixel's side to capture
        # the entire range.
        self.rng_start = (
            float(self.slant_range[0]) - 0.5 * self.slant_range_spacing
        )
        self.rng_stop = (
            float(self.slant_range[-1]) + 0.5 * self.slant_range_spacing
        )

    @property
    def x_posting(self):
        return self.slant_range_spacing

    @property
    def x_pixel_centers(self):
        return self.slant_range

    @property
    def y_posting(self):
        return self.zero_doppler_time_spacing

    @property
    def y_pixel_centers(self):
        return self.zero_doppler_time

    def get_isce3_radar_grid_parameters(
        self,
        wavelength: float,
        look_side: isce3.core.LookSide | str,
    ) -> isce3.product.RadarGridParameters:
        """
        Generate ISCE3 RadarGridParameters for this RadarRaster.

        This method constructs an isce3.product.RadarGridParameters object
        from the radar coordinate information stored in this RadarRaster.

        Parameters
        ----------
        wavelength : float
            The radar central wavelength, in meters.
        look_side : isce3.core.LookSide or {'left', 'right'}
            The look direction of the radar (left-looking or right-looking).

        Returns
        -------
        isce3.product.RadarGridParameters
            ISCE3 radar grid parameters object representing this raster's
            coordinate system.
        """

        # Parse the epoch string to create an ISCE3 DateTime object
        ref_epoch = isce3.core.DateTime(self.epoch)

        # Convert look_side to ISCE3 LookSide enum
        # XXX - ISCE3's RadarGridParameters constructor has multiple interfaces:
        # If the look side is a str, then the parameter name is `look_side`.
        # If the look side is an isce3.core.LookSide, then the parameter
        # name is lookside (no underscore).
        if isinstance(look_side, str):
            if look_side.lower() == "left":
                look_side = isce3.core.LookSide.Left
            elif look_side.lower() == "right":
                look_side = isce3.core.LookSide.Right
            else:
                raise ValueError(f"Invalid look_side string: {look_side}")

        # Compute PRF from zero doppler time spacing
        prf = 1.0 / self.zero_doppler_time_spacing

        # Create the RadarGridParameters object
        radar_grid = isce3.product.RadarGridParameters(
            sensing_start=float(self.zero_doppler_time[0]),
            wavelength=float(wavelength),
            prf=float(prf),
            starting_range=float(self.slant_range[0]),
            range_pixel_spacing=float(self.slant_range_spacing),
            lookside=look_side,
            length=len(self.zero_doppler_time),
            width=len(self.slant_range),
            ref_epoch=ref_epoch,
        )

        return radar_grid

    def downsample(self, y_stride: int, x_stride: int, mode: str) -> RadarGrid:

        zdt_coords, sr_coords, zdt_spacing, sr_spacing = self._downsample(
            y_stride=y_stride, x_stride=x_stride, mode=mode
        )

        grd_az_spacing = self.ground_az_spacing * y_stride
        grd_rg_spacing = self.ground_range_spacing * x_stride

        return RadarGrid(
            zero_doppler_time=zdt_coords,
            zero_doppler_time_spacing=zdt_spacing,
            slant_range=sr_coords,
            slant_range_spacing=sr_spacing,
            ground_az_spacing=grd_az_spacing,
            ground_range_spacing=grd_rg_spacing,
            epoch=self.epoch,
        )

    def get_latlonquad(
        self,
        orbit: isce3.core.Orbit,
        wavelength: float,
        look_side: isce3.core.LookSide | str,
        dem_file: str | os.PathLike | None = None,
        ellipsoid: isce3.core.Ellipsoid | None = None,
    ) -> nisarqa.LatLonQuad:
        """
        Get the LatLonQuad for this RadarGrid.

        Wrapper around nisarqa.compute_latlonquad_from_radar_coords().

        Parameters
        ----------
        orbit : isce3.core.Orbit
            The trajectory of the radar antenna phase center.
        wavelength : float
            The radar central wavelength, in meters.
        look_side : isce3.core.LookSide or {'left', 'right'}
            The look direction of the radar (left-looking or right-looking).
        dem_file : path-like or None, optional
            Digital Elevation Model (DEM) file path in a GDAL-compatible raster
            format. If None, a zero-height DEM will be used. Defaults to None.
        ellipsoid : isce3.core.Ellipsoid, optional
            The reference ellipsoid. If None, defaults to WGS84.

        Returns
        -------
        LatLonQuad
            A LatLonQuad object for this RadarGrid instance, with longitude
            normalization applied for proper antimeridian handling.
        """
        return nisarqa.compute_latlonquad_from_radar_coords(
            slant_range=self.slant_range,
            zero_doppler_time=self.zero_doppler_time,
            orbit=orbit,
            wavelength=wavelength,
            look_side=look_side,
            ellipsoid=ellipsoid,
            dem_file=dem_file,
        )

    def save_kml(
        self,
        *,
        browse_paths: nisarqa.BrowseOutputPaths,
        orbit: isce3.core.Orbit,
        wavelength: float,
        look_side: str,
        dem_file: str,
        suffix: str | None = None,
    ) -> None:
        """
        Save a KML with a lonlatquad corresponding to this RadarGrid.

        Parameters
        ----------
        browse_paths : nisarqa.BrowseOutputPaths
            Container with output directory and browse/KML filenames.
        orbit : nisarqa.Orbit
            Orbit object for radar geometry calculations.
        wavelength : float
            Radar wavelength in meters.
        look_side : str
            Look direction of the radar ('Left' or 'Right').
        dem_file : path-like or None
            Digital Elevation Model file path for geolocation. If None,
            a zero-height DEM will be used.
        suffix : str or None, optional
            If provided, this suffix will be appended to the filenames
            (e.g., "A_HH" produces "BROWSE_A_HH.png"). If None, use the
            primary browse/KML filenames. Defaults to None.
        """

        llq = self.get_latlonquad(
            orbit=orbit,
            wavelength=wavelength,
            look_side=look_side,
            dem_file=dem_file,
        )

        nisarqa.write_latlonquad_to_kml(
            llq=llq,
            output_dir=browse_paths.output_dir,
            kml_filename=browse_paths.get_kml_filename(suffix=suffix),
            png_filename=browse_paths.get_browse_filename(suffix=suffix),
        )


@dataclass
class GeoGrid(CoordinateGrid):
    """
    Uniformly-spaced 2D grid in geocoded (e.g. projected) coordinates.

    The attributes specified here are based on the needs of the QA code
    for generating and labeling plots, etc.

    Parameters
    ----------
    epsg : int
        The EPSG code of the coordinate system.
    x_axis_posting : float
        X posting of pixels of the grid, in units matching `x_coordinates`.
    x_coordinates : numpy.ndarray
        1D vector of the coordinate values of the center of each pixel
        of the raster grid in the X direction, in the units of the
        coordinate reference system represented by `epsg`.
    y_axis_posting : float
        Y posting of pixels of the grid, in units matching `y_coordinates`.
        Note: For NISAR L2 products, the y-coordinate posting of the
        coordinate grid is negative (the positive y-axis points up in QA plots).
    y_coordinates : numpy.ndarray
        1D vector of the coordinate values of the center of each pixel
        of the raster grid in the Y direction, in the units of the
        coordinate reference system represented by `epsg`.

    Attributes
    ----------
    x_start : float
        The starting (typically West) X position of the grid.
        This corresponds to the left side of the left-most pixels.
    x_stop : float
        The stopping (typically East) X position of the grid.
        This corresponds to the right side of the right-most pixels.
    y_start : float
        The starting (typically North) Y position of the grid.
        This corresponds to the upper edge of the top pixels.
    y_stop : float
        The stopping (typically South) Y position of the grid.
        This corresponds to the lower side of the bottom pixels.

    Notes
    -----
    Provided initialization parameters will also be stored as attributes.
    """

    epsg: int

    # Call this `x_axis_posting` instead of simply `x_posting` to avoid
    # name collisions with the property in the base class.
    x_axis_posting: float
    x_coordinates: np.ndarray

    # Call this `y_axis_posting` per reasoning above
    y_axis_posting: float
    y_coordinates: np.ndarray

    x_start: float = field(init=False)
    x_stop: float = field(init=False)
    y_start: float = field(init=False)
    y_stop: float = field(init=False)

    def __post_init__(self):
        self.epsg = int(self.epsg)
        self.x_axis_posting = float(self.x_axis_posting)
        self.y_axis_posting = float(self.y_axis_posting)

        # Infer start and stop values

        # For NISAR, geocoded grids are referenced by the center
        # of the pixel (different from GDAL conventions!). So add half
        # of the pixels' spacing to get the grid's far edges.
        # Note: `isce3.product.GeoGridParameters` adopts the GDAL convention
        # of referencing by the upper-left corner of the pixel, but the
        # NISAR L2 product writers construct `xCoordinates` and `yCoordinates`
        # to refer to the location of the center of the pixels.
        self.x_start = float(self.x_coordinates[0] - 0.5 * self.x_posting)
        self.x_stop = float(self.x_coordinates[-1] + 0.5 * self.x_posting)

        # Use the posting (not the spacing) to capture the
        # negative-valued stride of the y-coordinates for NISAR L2 products.
        self.y_start = float(self.y_coordinates[0] - 0.5 * self.y_posting)
        self.y_stop = float(self.y_coordinates[-1] + 0.5 * self.y_posting)

    @property
    def x_posting(self):
        return self.x_axis_posting

    @property
    def x_pixel_centers(self):
        return self.x_coordinates

    @property
    def y_posting(self):
        return self.y_axis_posting

    @property
    def y_pixel_centers(self):
        return self.y_coordinates

    def to_isce3_geo_grid_parameters(self) -> isce3.product.GeoGridParameters:
        """
        Generate ISCE3 GeoGridParameters for this GeoRaster.

        This method constructs an isce3.product.GeoGridParameters object
        from the geocoded coordinate information stored in this GeoRaster.

        Returns
        -------
        isce3.product.GeoGridParameters
            ISCE3 geo grid parameters object representing this raster's
            coordinate system.

        Notes
        -----
        ISCE3's GeoGridParameters uses the GDAL convention where coordinate
        values reference the upper-left corner of pixels, while NISAR products
        reference pixel centers.
        """

        # ISCE3 GeoGridParameters expects the starting coordinates to represent
        # the upper-left corner of the first pixel (GDAL convention).
        geogrid = isce3.product.GeoGridParameters(
            start_x=self.x_start,
            start_y=self.y_start,
            spacing_x=float(self.x_posting),
            spacing_y=float(self.y_posting),
            width=len(self.x_coordinates),
            length=len(self.y_coordinates),
            epsg=int(self.epsg),
        )

        return geogrid

    @classmethod
    def from_isce3_geo_grid(
        cls, isce3_geogrid: isce3.product.GeoGridParameters
    ) -> GeoGrid:
        """
        Construct a nisarqa.GeoGrid from a ISCE3 GeoGridParameters instance.

        ISCE3 GeoGridParameters uses upper-left corner convention (like GDAL),
        but nisarqa.GeoGrid uses pixel center convention.

        Parameters
        ----------
        isce3_geogrid : isce3.product.GeoGridParameters
            An ISCE3 GeoGridParameters instance, which uses the upper-left
            corner convention (like GDAL).

        Returns
        -------
        qa_geogrid : nisarqa.GeoGrid
            A nisarqa GeoGridParameters instance, which uses the pixel center
            convention.
        """
        # Convert from corner to center coordinates:
        # geogrid.start_x = x-coordinate of upper-left corner of upper-left pixel
        # geogrid.start_y = y-coordinate of upper-left corner of upper-left pixel
        # geogrid.spacing_x = pixel width (x spacing)
        # geogrid.spacing_y = pixel height (y spacing, negative for north-up)

        # Calculate pixel center coordinates
        x_coords = (
            isce3_geogrid.start_x
            + (np.arange(isce3_geogrid.width) + 0.5) * isce3_geogrid.spacing_x
        )
        y_coords = (
            isce3_geogrid.start_y
            + (np.arange(isce3_geogrid.length) + 0.5) * isce3_geogrid.spacing_y
        )

        epsg = str(isce3_geogrid.epsg)

        return cls(
            epsg=epsg,
            x_axis_posting=isce3_geogrid.spacing_x,
            x_coordinates=x_coords,
            y_axis_posting=isce3_geogrid.spacing_y,
            y_coordinates=y_coords,
        )

    @classmethod
    def from_coordinates(
        cls,
        x_coords: ArrayLike,
        y_coords: ArrayLike,
        epsg: int,
    ) -> GeoGrid:
        """
        Construct a GeoGrid from coordinate vectors.

        The provided arguements should all be consistent with each other for a
        given raster on a geocoded grid (e.g. NISAR Level-2 products).

        Parameters
        ----------
        x_coords : array-like
            1D array of X coordinate values (in units corresponding to `epsg`)
            for the given raster. Values should correspond to pixel centers.
        y_coords : array-like
            1D array of Y coordinate values (in units corresponding to `epsg`)
            for the given raster. Values should correspond to pixel centers.
        epsg : int
            The EPSG code of the projected coordinate system for the given raster
            (e.g., 32610 for UTM Zone 10N, or 3413 for NSIDC Sea Ice Polar
            Stereographic North).

        Returns
        -------
        qa_geogrid : nisarqa.GeoGrid
            A nisarqa GeoGrid instance, which uses the pixel center
            convention.
        """
        x_coordinates = np.asarray(x_coords)
        y_coordinates = np.asarray(y_coords)

        return cls(
            epsg=epsg,
            x_axis_posting=x_coordinates[1] - x_coordinates[0],
            x_coordinates=x_coordinates,
            y_axis_posting=y_coordinates[1] - y_coordinates[0],
            y_coordinates=y_coordinates,
        )

    def downsample(self, y_stride: int, x_stride: int, mode: str) -> GeoGrid:

        y_coords, x_coords, y_posting, x_posting = self._downsample(
            y_stride=y_stride, x_stride=x_stride, mode=mode
        )

        return GeoGrid(
            epsg=self.epsg,
            x_axis_posting=x_posting,
            x_coordinates=x_coords,
            y_axis_posting=y_posting,
            y_coordinates=y_coords,
        )

    def get_latlonquad(self) -> nisarqa.LatLonQuad:
        """
        Get the LatLonQuad for this GeoGrid.

        Wrapper around nisarqa.compute_latlonquad_from_geo_coords().

        Returns
        -------
        LatLonQuad
            A LatLonQuad object for this GeoGrid instance, with longitude
            normalization applied for proper antimeridian handling.
        """
        return nisarqa.compute_latlonquad_from_geo_coords(
            x_coords=self.x_coordinates,
            y_coords=self.y_coordinates,
            epsg=self.epsg,
        )

    def save_kml(
        self,
        *,
        browse_paths: nisarqa.BrowseOutputPaths,
        suffix: str | None = None,
    ) -> None:
        """
        Save a KML with a lonlatquad corresponding to this GeoGrid.

        Parameters
        ----------
        browse_paths : nisarqa.BrowseOutputPaths
            Container with output directory and browse/KML filenames.
        suffix : str or None, optional
            If provided, this suffix will be appended to the filenames
            (e.g., "LATLON" produces "BROWSE_LATLON.png"). If None, use the
            primary browse/KML filenames. Defaults to None.
        """

        nisarqa.write_latlonquad_to_kml(
            llq=self.get_latlonquad(),
            output_dir=browse_paths.output_dir,
            kml_filename=browse_paths.get_kml_filename(suffix=suffix),
            png_filename=browse_paths.get_browse_filename(suffix=suffix),
        )

    @property
    def is_geographic(self) -> bool:
        """
        True if this GeoGrid's SRS is a geographic coordinate system.

        Returns
        -------
        is_geographic : bool
            True if this GeoGrid's SRS is a geographic coordinate system
            (e.g. EPSG 4326 lat/lon), False otherwise.
        """

        srs = osr.SpatialReference()
        srs.ImportFromEPSG(self.epsg)
        return bool(srs.IsGeographic())

    @property
    def crosses_antimeridian(self) -> bool:
        """
        True if this GeoGrid crosses the EPSG 4326 antimeridian.

        This geogrid's extents will be converted to EPSG 4326 to determine
        whether it crosses the antimeridian.

        Returns
        -------
        crosses : bool
            True if the grid crosses the antimeridian, False otherwise.

        Examples
        --------
        A grid with lon_start=-181 and lon_stop=-147 crosses the antimeridian.
        A grid with corner longitudes [179, 180, -179, -178] crosses
        the antimeridian.
        """

        # Implementation plan:
        # Step 1: Convert the grid's corner coordinates to EPSG:4326 (lon/lat).
        # Step 2: Wrap all longitudes to [-180, 180) to normalize any unwrapped
        #    coordinates (e.g., 181 degrees or -181 degrees).
        # Step 3: Determine if there is an antimeridian crossing by examining
        #    whether there are large discontinuous jumps (>180) between
        #    wrapped corner longitude values, which indicate a dateline crossing

        # Create projection object for this grid's EPSG
        proj = isce3.core.make_projection(self.epsg)

        # Get corner coordinates in the grid's native projection
        # Use a dummy z-coordinate of 0 for 2D projections
        corners = [
            [self.x_start, self.y_start, 0],  # upper-left
            [self.x_stop, self.y_start, 0],  # upper-right
            [self.x_start, self.y_stop, 0],  # lower-left
            [self.x_stop, self.y_stop, 0],  # lower-right
        ]

        # Convert corners to lon/lat (EPSG:4326)
        corner_lons = []
        for corner in corners:
            lon_rad, lat_rad, h = proj.inverse(corner)
            lon_deg = np.rad2deg(lon_rad)
            corner_lons.append(lon_deg)

        # Ensure all longitudes are wrapped to [-180, 180) to normalize
        # unwrapped coordinates
        wrapped_lons = list(
            nisarqa.wrap_to_interval(corner_lons, start=-180, stop=180)
        )

        # Check for discontinuous jumps between wrapped corner longitudes
        # A jump > 180 indicates wrapping across the dateline
        for i in range(len(wrapped_lons)):
            for j in range(i + 1, len(wrapped_lons)):
                if abs(wrapped_lons[i] - wrapped_lons[j]) > 180:
                    return True

        return False


def _get_multilooked_center_coordinates(coords: ArrayLike, nlooks: int):
    """
    Get the vector of center coordinates for a multilooked array.

    For odd nlooks, the center falls on a pixel. For even nlooks, the center
    falls between two pixels and requires interpolation.

    Parameters
    ----------
    coords : array_like
        1D array of coordinate values (e.g., x_coordinates, slant_range)
        where values correspond to pixel center.
    nlooks : int
        Number of looks (multilook window size).

    Returns
    -------
    numpy.ndarray
        Coordinate values at the centers of the multilooked blocks
    """
    coords = coords.copy()

    # truncate the coords array
    truncation_amount = len(coords) % nlooks
    if truncation_amount > 0:
        trunc_coords = coords[:-truncation_amount]
    else:
        trunc_coords = coords

    if nlooks % 2 == 1:
        # Odd nlooks: center falls exactly on a pixel
        center_idx = nlooks // 2
        decimated = trunc_coords[center_idx::nlooks]
    else:
        # Even nlooks: center falls between two pixels, need to interpolate
        left_idx = nlooks // 2 - 1
        right_idx = nlooks // 2
        left_coords = trunc_coords[left_idx::nlooks]
        right_coords = trunc_coords[right_idx::nlooks]
        decimated = (left_coords + right_coords) / 2.0

    return decimated


@overload
def compare_raster_metadata(
    grid1: nisarqa.RadarGrid,
    grid2: nisarqa.RadarGrid,
) -> None: ...


@overload
def compare_grid_metadata(
    grid1: nisarqa.GeoGrid,
    grid2: nisarqa.GeoGrid,
) -> None: ...


def compare_grid_metadata(grid1, grid2):
    """
    Compare the metadata of two *Grid instances.

    Compare metadata fields for two *Grid instances.
    This is useful for checking that two raster images have approximately
    equal grids, which will allow the rasters to be combined smoothly
    into a single image. For example, this is a useful check prior to
    combining a phase image raster and a coherence magnitude raster
    to create an HSI image.
    Raises a ValueError if two fields do not match.

    Parameters
    ----------
    grid1, grid2 : nisarqa.RadarGrid | nisarqa.GeoGrid
        *Grid to compare. `grid1` and `grid2` must either both be
        instances of RadarGrids or both be instances of GeoGrids.

    Raises
    ------
    ValueError
        If metadata does not match

    See Also
    --------
    compare_raster_metadata : Compare the metadata for two *Raster instances.
    """
    r_grid = nisarqa.RadarGrid
    g_grid = nisarqa.GeoGrid
    if isinstance(grid1, r_grid) and isinstance(grid2, r_grid):
        raster_class = r_grid
    elif isinstance(grid1, g_grid) and isinstance(grid2, g_grid):
        raster_class = g_grid
    else:
        raise TypeError(
            f"{type(grid1)=} and {type(grid2)=}, must both be instances"
            " of either RadarGrid or of GeoGrid."
        )

    for f in fields(raster_class):
        field_name = f.name
        r1_val = getattr(grid1, field_name)
        r2_val = getattr(grid2, field_name)

        if isinstance(r1_val, str):
            if r1_val != r2_val:
                raise ValueError(
                    f"Values do not match for `{field_name}` field. `grid1`"
                    f" has value {r1_val}, but `grid2` has value {r2_val}."
                )
        else:
            if np.any(np.abs(r1_val - r2_val) > 1e-6):
                raise ValueError(
                    f"Values do not match for `{field_name}` field. `grid1`"
                    f" has value {r1_val}, but `grid2` has value {r2_val}."
                )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
