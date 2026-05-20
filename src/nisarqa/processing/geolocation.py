from __future__ import annotations

from datetime import datetime, timezone
import os
import pathlib
import tempfile
from contextlib import contextmanager
from typing import Generator

import isce3
import numpy as np
from numpy.typing import ArrayLike
from osgeo import gdal, osr

import nisarqa

objects_to_skip = nisarqa.get_all(__name__)


@contextmanager
def dem_file_manager(
    dem_file: str | os.PathLike | None = None,
) -> Generator[pathlib.Path, None, None]:
    """
    Context manager for DEM file handling.

    If a DEM file is provided, yields it without cleanup.
    If None, creates a temporary zero-height DEM (global coverage in EPSG 4326
    lat/lon with 1 degree resolution) and automatically cleans it up on exit.

    Parameters
    ----------
    dem_file : path-like or None, optional
        Digital Elevation Model (DEM) file path. If None, a temporary
        zero-height DEM will be created (global coverage in EPSG 4326 lat/lon
        with 1 degree resolution) and automatically cleaned up when exiting the
        context manager. Defaults to None.

    Yields
    ------
    pathlib.Path
        Path to the DEM file, as determined by the input `dem_file`.

    Examples
    --------
    >>> # Use temporary zero-height DEM (auto-cleanup)
    >>> with dem_file_manager(dem_file=None) as dem_path:
    ...     dem = isce3.io.Raster(str(dem_path))
    ...     # ... use dem ...
    ...     # Temporary DEM automatically deleted after this block

    >>> # Use provided DEM (no cleanup)
    >>> with dem_file_manager(dem_file="/path/to/real_dem.tif") as dem_path:
    ...     dem = isce3.io.Raster(str(dem_path))
    ...     # ... use dem ...
    ...     # Provided DEM is NOT deleted
    """
    if dem_file is None:
        # Create temporary zero-height DEM
        temp_dem_path = _create_zero_height_dem()
        try:
            yield temp_dem_path
        finally:
            # Cleanup temporary DEM
            temp_dem_path.unlink(missing_ok=True)
    else:
        # Use provided DEM (no cleanup)
        yield pathlib.Path(dem_file)


def _create_zero_height_dem() -> pathlib.Path:
    """
    Create a zero-height DEM TIF file in the scratch directory.

    Creates a GeoTIFF file containing an array of zeros with global coverage
    in EPSG 4326 (lon/lat) with 1 degree resolution.

    The file is uniquely named with a timestamp to avoid collisions. This is
    useful for geocoding operations where a DEM is required but high accuracy
    is not critical (e.g., for browse image generation).

    Returns
    -------
    pathlib.Path
        Path to the created zero-height DEM file with global coverage
        in EPSG 4326 (lat/lon) with 1 degree resolution, located in the
        nisarqa global scratch directory.

    Notes
    -----
    This is a private helper function. The file is NOT automatically cleaned up.
    Use dem_file_manager() context manager for automatic cleanup.
    """
    # Create a uniquely-named file in the scratch directory
    scratch = nisarqa.get_global_scratch_dir()
    _, dem_file = tempfile.mkstemp(
        prefix="zero_height_dem_", suffix=".tif", dir=scratch
    )

    # 1. Define resolution
    res = 1.0  # 1 degree resolution

    # Calculate dimensions (360x180 for 1-degree resolution)
    width = int(360 / res)
    height = int(180 / res)

    # 2. Create the dataset
    driver = gdal.GetDriverByName("GTiff")
    # GDT_Int16 is common for DEMs; use GDT_Float32 for precision
    ds = driver.Create(dem_file, width, height, 1, gdal.GDT_Int16)

    # 3. Set GeoTransform:
    #   [Upper Left X, X Resolution, Rotation,
    #       Upper Left Y, Rotation, Y Resolution]
    # Note: Y resolution must be negative for North-up images
    ds.SetGeoTransform([-180, res, 0, 90, 0, -res])

    # 4. Set Spatial Reference (WGS 84)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    ds.SetProjection(srs.ExportToWkt())

    # 5. Fill with zeros
    band = ds.GetRasterBand(1)
    zeros = np.zeros((height, width), dtype=np.int16)
    band.WriteArray(zeros)

    # Finalize and save
    band.FlushCache()
    ds = None

    return pathlib.Path(dem_file)


def geocode_radar_raster(
    radar_array: ArrayLike,
    radargrid: nisarqa.RadarGrid,
    orbit: isce3.core.Orbit,
    wavelength: float,
    look_side: isce3.core.LookSide | str,
    epsg: int,
    dem_file: str | os.PathLike | None = None,
    resample: str = "bilinear",
) -> np.ndarray:
    """
    Geocode a range-Doppler grid image array onto a given geogrid.

    This function geocodes data from range-Doppler coordinates
    to geographic/projected coordinates.

    Parameters
    ----------
    radar_array : array-like
        Input range-Doppler image array (e.g. NISAR Level-1) to be geocoded.
        Must be real-valued (float).
    radargrid : nisarqa.RadarGrid
        Radar grid parameters specifying the range-Doppler grid associated
        with the input `radar_array`.
    orbit : isce3.core.Orbit
        The trajectory of the radar antenna phase center.
    wavelength : float
        The radar central wavelength, in meters.
    look_side : isce3.core.LookSide or {'left', 'right'}
        The look direction of the radar (left-looking or right-looking).
    epsg : int
        The EPSG code for the output geocoded raster. Supports any valid EPSG
        (e.g., 4326 for lat/lon, 32610 for UTM Zone 10N, 3413 for polar
        stereographic) that is supported by isce3::core::createProj.
    dem_file : path-like or None, optional
        Path to a DEM file; required for accurate geolocation of the pixels.
        If None, a temporary zero-height DEM will be used (global coverage
        in EPSG 4326 lat/lon with 1 degree resolution).
        Defaults to None.
    resample : str, optional
        Resampling method for ISCE3 geocoding. Options: 'sinc', 'bilinear',
        'bicubic', 'nearest', 'biquintic'. Default: 'bilinear'.

    Returns
    -------
    geocoded_array : numpy.ndarray
        2D array of geocoded data. The length of the longest side of
        `geocoded_array` will be no greater than the length of the
        longest side of the input `radar_array`.
    output_geogrid : nisarqa.GeoGrid
        GeoGrid object describing the coordinate system and grid of the
        geocoded array.

    Warnings
    --------
    This function is not tested for large, full-size NISAR rasters.
    Recommend only using it to geocode relatively small rasters, such as
    browse image arrays. To geocode full-size NISAR rasters, suggest using
    ISCE3 directly.
    """

    if np.iscomplexobj(radar_array):
        raise ValueError(
            f"{type(radar_array)=} which is complex-valued. Only real-valued"
            " data currently supported."
        )

    # Use scratch directory with temporary files for ISCE3 raster I/O.
    # GDAL's in-memory option has potential security issues.
    scratch = nisarqa.get_global_scratch_dir()

    gdal_dtype = gdal.GDT_Float64
    output_dtype = np.float64

    with (
        dem_file_manager(dem_file) as dem_filepath,
        tempfile.NamedTemporaryFile(
            prefix="browse4326_in_", suffix=".tif", dir=scratch, delete=True
        ) as input_temp,
        tempfile.NamedTemporaryFile(
            prefix="browse4326_out_", suffix=".tif", dir=scratch, delete=True
        ) as output_temp,
    ):
        # Note: Keep input_temp and output_temp file handles open throughout.
        # On Unix systems, GDAL can work with files that have open handles.
        input_file = input_temp.name
        output_file = output_temp.name

        # Setup temporary input raster file, so that it can be converted to
        # the correct format for ISCE3 geocoding
        input_ds = gdal.GetDriverByName("GTiff").Create(
            input_file,
            radar_array.shape[1],
            radar_array.shape[0],
            1,
            gdal_dtype,
        )

        # Ensure float type
        raster_array = radar_array.astype(np.float64)

        # Convert nisarqa.RadarGrid to isce3.product.RadarGridParameters
        isce3_radargrid = radargrid.get_isce3_radar_grid_parameters(
            wavelength=wavelength,
            look_side=look_side,
        )

        input_ds.GetRasterBand(1).WriteArray(raster_array)
        input_ds.FlushCache()
        input_ds = None  # Close
        input_raster = isce3.io.Raster(str(input_file))

        # Next, setup temporary output raster file, which the input raster
        # file will be geocoded to.

        # Get lon/lat corners from radar grid.
        # Note: The returned lat/lon quad was generated with longitude
        # normalization applied for proper antimeridian handling. This means
        # that longitude coordinates will not jump from e.g. -179.5 to 179.5;
        # instead, they would be returned as e.g. -179.5 to -180.5, or
        # 180.5 to 179.5.
        llq = radargrid.get_latlonquad(
            orbit=orbit,
            wavelength=wavelength,
            look_side=look_side,
            dem_file=dem_filepath,
        )

        # Transform lon/lat corners to target projection
        proj = isce3.core.make_projection(epsg)
        corners_proj = []
        for corner in [llq.ul, llq.ur, llq.ll, llq.lr]:
            lon_rad = np.deg2rad(corner.lon)
            lat_rad = np.deg2rad(corner.lat)
            # Forward transform: lon/lat -> target projection
            # Returns coordinates in projection's native units
            # (degrees for EPSG 4326 lat/lon, meters for UTM, etc.)
            # Note: for EPSG 4326, will not re-wrap longitudes to [-180, 180].
            x, y, _ = proj.forward([lon_rad, lat_rad, 0])
            corners_proj.append((x, y))

        # Get bounding box in target projection's native units
        xs = [c[0] for c in corners_proj]

        # Create a SpatialReference object to check output projection type
        srs_out = osr.SpatialReference()
        srs_out.ImportFromEPSG(epsg)

        if srs_out.IsGeographic:
            # Ensure that longitudes are unwrapped
            xs = nisarqa.unwrap_longitudes(xs)

        ys = [c[1] for c in corners_proj]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)

        # Because longitude values were normalized, `width = maxx - minx`
        # works correctly for all frames, including antimeridian crossings.
        width = maxx - minx
        height = maxy - miny

        # Determine resolution to preserve aspect ratio and enforce size
        # constraint.
        # Goal: output image size <= max(input dimensions) along each axis,
        # while maintaining similar spatial resolution as input.
        maxdim = max(radar_array.shape)

        # Earth Equatorial Radius (Semi-major Axis) in meters (WGS 84)
        a = 6378137.0

        # ISCE3's update_geogrid() dynamically adds a margin when determining
        # the geogrid to ensure that the swath's corners are all contained.
        # To compensate and meet the maxdim constraint, use a two-step approach:
        # 1. Initial geogrid call to determine actual bounds (including margin)
        # 2. Create fresh geocode object with refined resolution based on actual bounds

        def compute_resolution(
            span_width: float,
            span_height: float,
            target_dim: int,
            avg_latitude: float | None = None,
        ) -> tuple[float, float]:
            """
            Compute x and y resolution for geocoding.

            Parameters
            ----------
            span_width : float
                Width span in native projection units (degrees for EPSG 4326,
                meters for UTM/polar stereo).
            span_height : float
                Height span in native projection units.
            target_dim : int
                Target dimension in pixels to constrain output size.
            avg_latitude : float or None, optional
                Average latitude in degrees. Required for geographic
                projections only; will be ignored otherwise.
                Defaults to None (for non-geographic projections).

            Returns
            -------
            resolution_x, resolution_y : float, float
                Pixel spacing in native projection units.
            """
            if srs_out.IsGeographic():
                if not isinstance(avg_latitude, (float, int)):
                    raise ValueError(f"{avg_latitude=}, must be a float.")

                # For lat/lon (EPSG 4326), spacing varies by latitude
                radius_at_lat = a * np.cos(np.deg2rad(avg_latitude))
                lon_distance_meters = (
                    (span_width / 360) * 2 * np.pi * radius_at_lat
                )
                dx_meters = lon_distance_meters / target_dim
                lat_distance_meters = (span_height / 360) * 2 * np.pi * a
                dy_meters = lat_distance_meters / target_dim
                spacing_m = max(dx_meters, dy_meters)
                res_x = np.rad2deg(spacing_m / radius_at_lat)
                res_y = np.rad2deg(spacing_m / a)
            else:
                # Assume dx/dy ≈ 1 (polar stereo or UTM with spacing in meters)
                dx = span_width / target_dim
                dy = span_height / target_dim
                res_x = res_y = max(dx, dy)
            return res_x, res_y

        def create_geocode_obj(
            res_x: float,
            res_y: float,
            x_start: float | None = None,
            y_start: float | None = None,
            grid_width: int | None = None,
            grid_length: int | None = None,
        ) -> isce3.geocode.GeocodeFloat64:
            """
            Create and configure a fresh GeocodeFloat64 object.

            Parameters
            ----------
            res_x, res_y : float
                Pixel spacing in x and y directions.
            x_start, y_start : float or None, optional
                Starting coordinates. If None, will be computed by update_geogrid.
            grid_width, grid_length : int or None, optional
                Grid dimensions in pixels. If None, will be computed by update_geogrid.

            Returns
            -------
            isce3.geocode.GeocodeFloat64
                Configured geocode object with geogrid set.
            """
            geo_obj = isce3.geocode.GeocodeFloat64()
            geo_obj.orbit = orbit
            geo_obj.ellipsoid = isce3.core.WGS84_ELLIPSOID
            geo_obj.doppler = isce3.core.LUT2d()  # Zero-Doppler for NISAR
            geo_obj.threshold_geo2rdr = 1.0e-8
            geo_obj.numiter_geo2rdr = 25
            geo_obj.data_interpolator = resample

            geo_obj.geogrid(
                x_start=x_start if x_start is not None else np.nan,
                y_start=y_start if y_start is not None else np.nan,
                x_spacing=res_x,
                y_spacing=-res_y,
                width=grid_width if grid_width is not None else 0,
                length=grid_length if grid_length is not None else 0,
                epsg=epsg,
            )

            return geo_obj

        # Step 1: Compute initial resolution based on estimated bounds
        avg_lat = (miny + maxy) / 2
        resolution_x, resolution_y = compute_resolution(
            width, height, maxdim, avg_lat
        )

        # Create initial geocode object to determine actual bounds with margin
        geocode_obj_initial = create_geocode_obj(resolution_x, resolution_y)

        # Create DEM fresh for update_geogrid to avoid corruption issues with VRT files.
        # The DEM raster object can become corrupted when used across multiple
        # ISCE3/GDAL operations, so we create it fresh for each use and close
        # it immediately after.
        dem_for_update = isce3.io.Raster(str(dem_filepath))
        geocode_obj_initial.update_geogrid(isce3_radargrid, dem_for_update)
        dem_for_update.close_dataset()
        dem_for_update = None

        # Step 2: Recompute resolution using actual bounds from update_geogrid
        # to ensure output dimensions <= maxdim

        # Get start coordinates
        final_x_start = geocode_obj_initial.geogrid_start_x
        final_y_start = geocode_obj_initial.geogrid_start_y

        # Compute end coordinates from initial grid
        final_x_end = final_x_start + (
            geocode_obj_initial.geogrid_width
            * geocode_obj_initial.geogrid_spacing_x
        )
        final_y_end = final_y_start + (
            geocode_obj_initial.geogrid_length
            * geocode_obj_initial.geogrid_spacing_y
        )

        # Compute spans
        final_width_span = abs(final_x_end - final_x_start)
        final_height_span = abs(final_y_end - final_y_start)

        # Compute final center latitude from actual bounds
        final_miny = min(final_y_start, final_y_end)
        final_maxy = max(final_y_start, final_y_end)
        avg_lat_final = (final_miny + final_maxy) / 2

        # Recompute resolution with actual bounds
        final_resolution_x, final_resolution_y = compute_resolution(
            final_width_span, final_height_span, maxdim, avg_lat_final
        )

        # Compute final dimensions based on new resolution and actual bounds
        final_width = int(np.round(final_width_span / final_resolution_x))
        final_length = int(np.round(final_height_span / final_resolution_y))

        # Create fresh geocode object with refined resolution and explicit bounds.
        # Pass ALL parameters - do NOT call update_geogrid() again.
        final_geocode_obj = create_geocode_obj(
            final_resolution_x,
            final_resolution_y,
            x_start=final_x_start,
            y_start=final_y_start,
            grid_width=final_width,
            grid_length=final_length,
        )

        # Create temporary output raster file
        output_ds = gdal.GetDriverByName("GTiff").Create(
            output_file,
            final_geocode_obj.geogrid_width,
            final_geocode_obj.geogrid_length,
            1,
            gdal_dtype,
        )

        # Set output file's projection and geotransform
        output_ds.SetProjection(srs_out.ExportToWkt())

        output_geotransform = [
            final_geocode_obj.geogrid_start_x,
            final_geocode_obj.geogrid_spacing_x,
            0,
            final_geocode_obj.geogrid_start_y,
            0,
            final_geocode_obj.geogrid_spacing_y,
        ]

        output_ds.SetGeoTransform(output_geotransform)

        output_ds.FlushCache()
        output_ds = None  # Close
        output_raster = isce3.io.Raster(str(output_file), update=True)

        # Create DEM fresh for geocode to avoid corruption issues with VRT files
        dem_for_geocode = isce3.io.Raster(str(dem_filepath))

        # Perform geocoding
        final_geocode_obj.geocode(
            radar_grid=isce3_radargrid,
            input_raster=input_raster,
            output_raster=output_raster,
            dem_raster=dem_for_geocode,
            output_mode=isce3.geocode.GeocodeOutputMode.INTERP,
        )

        # Explicitly close the ISCE3 Rasters
        # ISCE3's Raster class wraps around GDAL datasets. So, we need to:
        #   1) close_dataset() to explicitly flush caches and close file handle
        #   2) set to None to remove the Python reference
        input_raster.close_dataset()
        input_raster = None
        output_raster.close_dataset()
        output_raster = None
        dem_for_geocode.close_dataset()
        dem_for_geocode = None

        # Read geocoded result
        output_ds = gdal.Open(output_file)
        geocoded_array = (
            output_ds.GetRasterBand(1).ReadAsArray().astype(output_dtype)
        )
        output_gt = list(output_ds.GetGeoTransform())
        output_ds = None

        # Create GeoGrid for the output
        # GDAL geotransform uses upper-left corner convention,
        # but nisarqa.GeoGrid uses pixel center convention.
        # Convert from corner to center coordinates:
        # GT(0) = x-coordinate of upper-left corner of upper-left pixel
        # GT(3) = y-coordinate of upper-left corner of upper-left pixel
        # GT(1) = pixel width (x spacing)
        # GT(5) = pixel height (y spacing, negative for north-up)

        # Calculate pixel center coordinates
        reproj_height, reproj_width = geocoded_array.shape

        x_coords = output_gt[0] + (np.arange(reproj_width) + 0.5) * output_gt[1]
        y_coords = (
            output_gt[3] + (np.arange(reproj_height) + 0.5) * output_gt[5]
        )

        output_geogrid = nisarqa.GeoGrid(
            epsg=epsg,
            x_axis_posting=output_gt[1],
            x_coordinates=x_coords,
            y_axis_posting=output_gt[5],
            y_coordinates=y_coords,
        )

        # All context managers exit here - temp files and DEM cleaned up automatically
        return geocoded_array, output_geogrid


def reproject_geo_raster(
    image_array: np.ndarray,
    fill_value: float,
    geogrid: nisarqa.GeoGrid,
    *,
    output_epsg: int,
    resample: str = "average",
) -> tuple[np.ndarray, nisarqa.GeoGrid]:
    """
    Reproject a geocoded raster array.

    Parameters
    ----------
    image_array : numpy.ndarray
        2D array of image data to be reprojected.
        Should be real-valued (float). Complex data is not supported.
    fill_value : float or None
        Fill value for `image_array`.
    geogrid : nisarqa.GeoGrid
        GeoGrid defining the coordinate system and spacing of `image_array`.
    output_epsg : int
        EPSG to reproject the raster to. Example: 4326 for lat/lon.
    resample : str, optional
        Resampling algorithm for GDAL reprojection. Options: 'near', 'bilinear',
        'cubic', 'cubicspline', 'lanczos', 'average', 'mode'.
        Default: 'average'.

    Returns
    -------
    reprojected_array : numpy.ndarray
        2D array of reprojected data in the output EPSG.
        The output dimensions will match the input dimensions (height and width
        in pixels are preserved), which may introduce geometric distortion when
        reprojecting between coordinate systems with different scale factors.
    output_geogrid : nisarqa.GeoGrid
        GeoGrid object describing the coordinate system and grid of the
        reprojected array. Uses pixel center convention.

    Warnings
    --------
    This function is designed for visual browse image generation and
    prioritizes predictable output dimensions and visual appearance.
    The output dimensions are constrained to match the input dimensions, which
    may introduce non-square pixels when reprojecting between coordinate systems
    (e.g., from UTM meters to lat/lon degrees, or in regions near the poles).

    This function is not optimized for large, full-size NISAR rasters.
    Recommend only using it to reproject relatively small rasters, such as
    browse image arrays.
    """
    if np.iscomplexobj(image_array):
        raise ValueError(
            f"image_array is complex-valued. Only real-valued data"
            " currently supported."
        )

    if np.iscomplexobj(fill_value):
        raise TypeError(
            f"fill_value must be real-valued, but received complex: {fill_value}. "
            "Convert to float (e.g., using np.real()) before calling this function."
        )

    # Use scratch directory with temporary files for ISCE3 raster I/O.
    # GDAL's in-memory option has potential security issues.
    scratch = nisarqa.get_global_scratch_dir()

    # Ensure float type
    raster_array = image_array.astype(np.float64)

    source_epsg = geogrid.epsg

    # Calculate geotransform for the source raster
    # GDAL geotransform: [x_origin, x_pixel_size, 0, y_origin, 0, y_pixel_size]
    # GeoGrid uses pixel centers, so we need x_start/y_start which are the edges
    geotransform = [
        geogrid.x_start,
        geogrid.x_axis_posting,
        0,
        geogrid.y_start,
        0,
        geogrid.y_axis_posting,
    ]

    # Use nested context managers for temporary TIF files
    with (
        tempfile.NamedTemporaryFile(
            prefix="browse4326_in_", suffix=".tif", dir=scratch, delete=True
        ) as source_temp,
        tempfile.NamedTemporaryFile(
            prefix="browse4326_vrt_", suffix=".vrt", dir=scratch, delete=True
        ) as temporary_vrt,
        tempfile.NamedTemporaryFile(
            prefix="browse4326_reproj_", suffix=".tif", dir=scratch, delete=True
        ) as reproj_temp,
    ):
        source_file = source_temp.name
        reprojected_file = reproj_temp.name
        temp_vrt = temporary_vrt.name

        # Note: Keep source_temp and reproj_temp file handles open throughout.
        # On Unix systems, GDAL can work with files that have open handles.

        # Create temporary input source GeoTIFF
        driver = gdal.GetDriverByName("GTiff")
        src_height, src_width = raster_array.shape
        source_ds = driver.Create(
            source_file, src_width, src_height, 1, gdal.GDT_Float64
        )

        # Set projection and geotransform
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(source_epsg)
        source_ds.SetProjection(srs.ExportToWkt())
        source_ds.SetGeoTransform(geotransform)

        # Write data
        source_ds.GetRasterBand(1).WriteArray(raster_array)
        # Make sure to set the fill value
        # Reason: GDAL uses all non-NODATA pixels during resampling.
        # If the fill value is not designated, then the fill value pixels will
        # (unfortunately) be used in the resampling.
        source_ds.GetRasterBand(1).SetNoDataValue(float(fill_value))

        source_ds.FlushCache()
        source_ds = None  # Close

        # Specify warp options; handle antimeridian crossings.
        warp_options = {
            "srcSRS": f"EPSG:{source_epsg}",
            "resampleAlg": resample,
            "dstNodata": fill_value,
        }

        srs_out = osr.SpatialReference()
        srs_out.ImportFromEPSG(output_epsg)

        if srs_out.IsGeographic() and geogrid.crosses_antimeridian:
            # For antimeridian crossing, use +lon_wrap=180 to shift the
            # coordinate system center to 180 degrees (dateline) instead
            # of 0 degrees (prime meridian).
            # This avoids the discontinuity at -180/+180 and allows GDAL to
            # properly handle data that spans the dateline.
            warp_options["dstSRS"] = "+proj=longlat +datum=WGS84 +lon_wrap=180"
        else:
            # Standard reprojection for non-dateline-crossing data
            warp_options["dstSRS"] = f"EPSG:{output_epsg}"

        # Do initial warp to get extent; use a VRT to avoid warping each pixel.
        # Then we can calculate the sizes/spacings that will give
        # square-ish pixels while obeying the max size constraint.
        maxdim = max(src_height, src_width)
        vrt = gdal.Warp(
            temp_vrt,
            source_file,
            format="VRT",
            height=maxdim,
            width=maxdim,
            **warp_options,
        )

        # Calculate extents in output projection.
        gt = vrt.GetGeoTransform()
        left, top, dx, dy = gt[0], gt[3], gt[1], gt[5]
        right = left + vrt.RasterXSize * dx
        bottom = top + vrt.RasterYSize * dy
        x_extent = right - left  # already unwrapped via dstSRS if needed
        y_extent = top - bottom

        # Calculate aspect ratio, taking care of dy/dx=cos(lat) for longlat.
        # Assume other projections have dy/dx=1.
        if srs_out.IsGeographic():
            # Compute the ratio of ground distance (per degree of longitude)
            # at this raster's average latitude vs. at the equator
            longitude_scale_factor = np.cos(np.deg2rad((top + bottom) / 2))
            aspect_ratio = x_extent * longitude_scale_factor / y_extent
        else:
            aspect_ratio = x_extent / y_extent

        # Assign maxdim to largest extent and scale the other dimension to
        # preserve aspect ratio.
        if aspect_ratio > 1.0:
            width = maxdim
            height = round(maxdim / aspect_ratio)
        else:
            height = maxdim
            width = round(maxdim * aspect_ratio)

        gdal.Warp(
            reprojected_file,
            source_file,
            format="GTiff",
            height=height,
            width=width,
            **warp_options,
        )

        # Open reprojected image
        reprojected_ds = gdal.Open(reprojected_file)
        reproj_data = reprojected_ds.GetRasterBand(1).ReadAsArray()
        reproj_gt = list(reprojected_ds.GetGeoTransform())
        reprojected_ds = None  # Close

        # Create GeoGrid for the output
        # GDAL geotransform uses upper-left corner convention,
        # but nisarqa.GeoGrid uses pixel center convention.
        # Convert from corner to center coordinates:
        # GT(0) = x-coordinate of upper-left corner of upper-left pixel
        # GT(3) = y-coordinate of upper-left corner of upper-left pixel
        # GT(1) = pixel width (x spacing)
        # GT(5) = pixel height (y spacing, negative for north-up)

        # Calculate pixel center coordinates
        reproj_height, reproj_width = reproj_data.shape

        x_coords = reproj_gt[0] + (np.arange(reproj_width) + 0.5) * reproj_gt[1]
        y_coords = (
            reproj_gt[3] + (np.arange(reproj_height) + 0.5) * reproj_gt[5]
        )

        output_geogrid = nisarqa.GeoGrid(
            epsg=output_epsg,
            x_axis_posting=reproj_gt[1],
            x_coordinates=x_coords,
            y_axis_posting=reproj_gt[5],
            y_coordinates=y_coords,
        )

        # All context managers exit here - temp files cleaned up automatically
        return reproj_data, output_geogrid


__all__ = nisarqa.get_all(__name__, objects_to_skip)
