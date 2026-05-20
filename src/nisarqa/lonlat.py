from __future__ import annotations

import os
import textwrap
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import isce3
import numpy as np
from numpy.typing import ArrayLike

import nisarqa

objects_to_skip = nisarqa.get_all(__name__)


def unwrap_longitudes(lons: Iterable[float]) -> list[float]:
    """
    Unwrap longitudes if the values cross the antimeridian.

    Specifically, longitudes are normalized so that the absolute difference
    between any adjacent pair of longitude values is <= 180 degrees.

    All given longitude values are first wrapped to +/-180 degrees, and
    then in the case of an antimeridian crossing they are "unwrapped"
    to extend beyond the interval of +/-180 degrees for the crossing.

    Arguments
    ---------
    lons : iterable of float
        Sequence of longitude values (in degrees).

    Returns
    -------
    unwrapped : list of float
        Copy of `lons`, but unwrapped so that the absolute difference
        between any adjacent pair of longitude values is <= 180 degrees.
        The ordering of the points is preserved.
    """
    # since `lons` is an iterable, `wrap_to_interval` returns an iterator
    lons_180 = list(nisarqa.wrap_to_interval(val=lons, start=-180, stop=180))

    return list(unwrap_degrees(angles=lons_180))


def unwrap_degrees(angles: ArrayLike) -> np.ndarray:
    """
    Unwrap a sequence of angles in degrees.

    Unwraps the input angles such that the absolute differences between
    adjacent elements are never greater than 180 degrees by adding a
    multiple of 360 degrees to each element.

    Parameters
    ----------
    angles : array_like
        The input sequence of angles, in degrees.

    Returns
    -------
    numpy.ndarray
        The unwrapped angles, in degrees.
    """
    # `numpy.unwrap` doesn't correctly unwrap inputs in degrees prior
    # to NumPy 1.21.0. See https://github.com/numpy/numpy/pull/16987.
    # nisarqa currently supports NumPy >=1.20.
    return np.rad2deg(np.unwrap(np.deg2rad(angles)))


def normalize_lon_lat_pts(lon_lat_points: Sequence[LonLat]) -> list[LonLat]:
    """
    Normalize so that longitudes's are <= +/-360 and unwrapped at antimeridian.

    Specifically, longitudes are normalized so that the absolute difference
    between any adjacent pair of longitude values is <= 180 degrees.

    All given longitude values are first wrapped to +/-180 degrees, and
    then in the case of an antimeridian crossing they are "unwrapped"
    to extend beyond the interval of +/-180 degrees for the crossing.

    Parameters
    ----------
    lon_lat_points : iterable of nisarqa.LonLat
        Iterable of nisarqa.LonLat (in degrees); must be able to support
        multi-pass iteration (such as a list or sequence).

    Returns
    -------
    normalized : list of nisarqa.LonLat
        Copy of `lon_lat_points`, but normalized so that the absolute difference
        between any adjacent pair of longitude values is <= 180 degrees.
        The ordering of the points is preserved.
    """

    lons = unwrap_longitudes(pt.lon for pt in lon_lat_points)
    lats = (pt.lat for pt in lon_lat_points)

    return [nisarqa.LonLat(lon=lon, lat=lat) for lon, lat in zip(lons, lats)]


@dataclass
class LonLat:
    """
    A point in Lon/Lat space (units of degrees).

    Attributes
    ----------
    lon, lat : float
        The geodetic longitude and latitude, in degrees.
    """

    lon: float
    lat: float


@dataclass(frozen=True)
class LatLonQuad:
    """
    A quadrilateral defined by four Lon/Lat corner points (in degrees).

    This class represents a KML gx:LatLonQuad, as described in
    https://developers.google.com/kml/documentation/kmlreference#gx:latlonquad

    The corners are provided as follows:
        * ul - upper-left
        * ur - upper-right
        * ll - lower-left
        * lr - lower-right

    Note that "upper", "lower", "left" and "right" are given from the image's
    native perspective prior to transformation to lon/lat coordinates, so e.g.
    the "upper-left" coordinate of a radar image is not necessarily the
    upper-left in lon/lat space, but in the un-geocoded radar image. This is
    done to provide the proper orientation of the overlay image.

    Attributes
    ----------
    ul, ur, ll, lr : LonLat
        The upper-left, upper-right, lower-left, and lower-right corners,
        in degrees, for the entire extent of the image.
    normalize_longitudes : bool, optional
        True to modify the longitudes values during post init so the absolute
        difference between any adjacent pair of longitudes is <= 180 degrees.
        This prepares the coordinates for use in the KML's gx:LatLonQuad.
        Defaults to True.
    """

    ul: LonLat
    ur: LonLat
    ll: LonLat
    lr: LonLat

    normalize_longitudes: bool = True

    def __post_init__(self):
        if self.normalize_longitudes:
            unwrapped = normalize_lon_lat_pts(
                (self.ul, self.ur, self.lr, self.ll)
            )
            object.__setattr__(self, "ul", unwrapped[0])
            object.__setattr__(self, "ur", unwrapped[1])
            object.__setattr__(self, "lr", unwrapped[2])
            object.__setattr__(self, "ll", unwrapped[3])

    def bounds(self) -> tuple[float, float, float, float]:
        """
        Get the bounding box of this LatLonQuad.

        Returns
        -------
        tuple of float
            Bounding box as (minx, miny, maxx, maxy), where:
            - minx: minimum longitude (degrees)
            - miny: minimum latitude (degrees)
            - maxx: maximum longitude (degrees)
            - maxy: maximum latitude (degrees)

        Notes
        -----
        For LatLonQuad objects with normalized longitudes (which may extend
        beyond [-180, 180] to handle antimeridian crossings), this method
        correctly computes the bounds using the unwrapped longitude values.
        """
        # Extract all longitudes and latitudes
        lons = [self.ul.lon, self.ur.lon, self.ll.lon, self.lr.lon]
        lats = [self.ul.lat, self.ur.lat, self.ll.lat, self.lr.lat]

        # Compute bounds
        minx = min(lons)
        maxx = max(lons)
        miny = min(lats)
        maxy = max(lats)

        return minx, miny, maxx, maxy


def write_latlonquad_to_kml(
    llq: LatLonQuad,
    output_dir: str | os.PathLike[str],
    *,
    kml_filename: str,
    png_filename: str,
) -> None:
    """
    Generate a KML file containing geolocation info of the corresponding
    browse image.

    Parameters
    ----------
    llq : LatLonQuad
        The LatLonQuad object containing the corner coordinates that will be
        serialized to KML.
    output_dir : path-like
        The directory to write the output KML file to. This directory
        must already exist. The PNG file that the KML corresponds to is
        expected to be placed in the same directory.
    kml_filename : str, optional
        The output filename of the KML file, specified relative to
        `output_dir`. Defaults to 'BROWSE.kml'.
    png_filename : str, optional
        The filename of the corresponding PNG file, specified relative
        to `output_dir`. Defaults to 'BROWSE.png'.
    """

    # Construct LatLonQuad coordinates string in correct format for KML.
    # The coordinates are specified in counter-clockwise order with the first
    # point corresponding to the lower-left corner of the overlayed image.
    # (https://developers.google.com/kml/documentation/kmlreference#gx:latlonquad)
    kml_lat_lon_quad = " ".join(
        [f"{p.lon},{p.lat}" for p in (llq.ll, llq.lr, llq.ur, llq.ul)]
    )

    kml_file = textwrap.dedent(
        f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns:gx="http://www.google.com/kml/ext/2.2">
          <Document>
            <name>overlay image</name>
            <GroundOverlay>
              <name>overlay image</name>
              <Icon>
                <href>{png_filename}</href>
              </Icon>
              <gx:LatLonQuad>
                <coordinates>{kml_lat_lon_quad}</coordinates>
              </gx:LatLonQuad>
            </GroundOverlay>
          </Document>
        </kml>
        """
    ).strip()
    with open(Path(output_dir, kml_filename), "w") as f:
        f.write(kml_file)


def compute_latlonquad_from_radar_coords(
    slant_range: np.ndarray,
    zero_doppler_time: np.ndarray,
    orbit: isce3.core.Orbit,
    wavelength: float,
    look_side: isce3.core.LookSide | str,
    dem_file: str | os.PathLike | None = None,
    ellipsoid: Optional[isce3.core.Ellipsoid] = None,
) -> LatLonQuad:
    """
    Compute LatLonQuad for a range-Doppler raster.

    The provided arguements should all be consistent with each other for a
    given raster on the range Doppler grid (e.g. NISAR Level-1 products).

    Parameters
    ----------
    slant_range : numpy.ndarray
        1D array of slant range values (in meters) for the given raster.
        Values should correspond to pixel centers.
    zero_doppler_time : numpy.ndarray
        1D array of zero Doppler time values (in seconds since orbit reference
        epoch) for the given raster.
        Values should correspond to pixel centers.
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
        A LatLonQuad object for the given raster with longitude normalization
        applied for proper antimeridian handling.
    """
    if ellipsoid is None:
        ellipsoid = isce3.core.WGS84_ELLIPSOID

    # Use provided DEM file or default to zero-height DEM
    if dem_file is None:
        # Per specification, KML lonlatquads use EPSG 4326
        dem = isce3.geometry.DEMInterpolator(epsg=4326)
    else:
        dem_raster = isce3.io.Raster(str(dem_file))
        dem = isce3.geometry.DEMInterpolator(dem_raster)

    # NISAR products are zero-Doppler
    doppler = 0.0

    # Define the four corners in radar coordinates
    # NISAR coordinate vectors provide values for pixel-centers.
    # KMLs require values for pixel edges. Adjust:
    half_az_spacing = (zero_doppler_time[1] - zero_doppler_time[0]) / 2
    half_rg_spacing = (slant_range[1] - slant_range[0]) / 2

    first_az = zero_doppler_time[0] - half_az_spacing
    first_rg = slant_range[0] - half_rg_spacing
    last_az = zero_doppler_time[-1] + half_az_spacing
    last_rg = slant_range[-1] + half_rg_spacing

    corners_radar = {
        "ul": (first_az, first_rg),  # upper-left corner
        "ur": (first_az, last_rg),  # upper-right corner
        "ll": (last_az, first_rg),  # lower-left corner
        "lr": (last_az, last_rg),  # lower-right corner
    }

    corners_lonlat = {}

    for corner_name, (aztime, srange) in corners_radar.items():
        # Convert from radar coordinates (aztime, slant_range) to ECEF XYZ
        xyz = isce3.geometry.rdr2geo_bracket(
            aztime=aztime,
            slant_range=srange,
            orbit=orbit,
            side=look_side,
            doppler=doppler,
            wavelength=wavelength,
            dem=dem,
        )

        # Convert from ECEF XYZ to geodetic lon/lat (in radians)
        lon_rad, lat_rad, _ = ellipsoid.xyz_to_lon_lat(xyz)

        # Convert from radians to degrees
        lon_deg = np.rad2deg(lon_rad)
        lat_deg = np.rad2deg(lat_rad)

        corners_lonlat[corner_name] = LonLat(lon=lon_deg, lat=lat_deg)

    if dem_file is not None:
        # Explicitly close the ISCE3 Raster
        dem_raster.close_dataset()  # Explicitly flush caches and close file handle
        dem_raster = None  # Then remove the Python reference

    # Create and return LatLonQuad with longitude normalization
    return LatLonQuad(
        ul=corners_lonlat["ul"],
        ur=corners_lonlat["ur"],
        ll=corners_lonlat["ll"],
        lr=corners_lonlat["lr"],
        normalize_longitudes=True,
    )


def compute_latlonquad_from_geo_coords(
    x_coords: np.ndarray,
    y_coords: np.ndarray,
    epsg: int,
) -> LatLonQuad:
    """
    Compute LatLonQuad for a geocoded raster.

    The provided arguements should all be consistent with each other for a
    given raster on a geocoded grid (e.g. NISAR Level-2 products).

    Parameters
    ----------
    x_coords : numpy.ndarray
        1D array of X coordinate values (in units corresponding to `epsg`)
        for the given raster. Values should correspond to pixel centers.
    y_coords : numpy.ndarray
        1D array of Y coordinate values (in units corresponding to `epsg`)
        for the given raster. Values should correspond to pixel centers.
    epsg : int
        The EPSG code of the projected coordinate system for the given raster
        (e.g., 32610 for UTM Zone 10N, or 3413 for NSIDC Sea Ice Polar
        Stereographic North).

    Returns
    -------
    LatLonQuad
        A LatLonQuad object for the given raster, with longitude normalization
        applied for proper antimeridian handling.

    Notes
    -----
    - For EPSG 4326 (already in lon/lat), this function still works correctly
      as the projection inverse is essentially a pass-through.
    """
    # Create the ISCE3 projection object for the given EPSG code
    proj = isce3.core.make_projection(epsg)

    # NISAR coordinate vectors provide values for pixel-centers.
    # KMLs require values for pixel edges. Adjust:
    geogrid = nisarqa.GeoGrid.from_coordinates(
        x_coords=x_coords, y_coords=y_coords, epsg=epsg
    )
    corners_proj = {
        "ul": (geogrid.x_start, geogrid.y_start),  # upper-left corner
        "ur": (geogrid.x_stop, geogrid.y_start),  # upper-right corner
        "ll": (geogrid.x_start, geogrid.y_stop),  # lower-left corner
        "lr": (geogrid.x_stop, geogrid.y_stop),  # lower-right corner
    }

    corners_lonlat = {}

    for corner_name, (x, y) in corners_proj.items():
        # Convert to lon/lat
        # Use dummy height of 0; ISCE3 projections are 2-D tranformations --
        # the height has no effect on lon/lat
        lon_rad, lat_rad, _ = proj.inverse([x, y, 0])

        # Convert from radians to degrees
        lon_deg = np.rad2deg(lon_rad)
        lat_deg = np.rad2deg(lat_rad)

        corners_lonlat[corner_name] = LonLat(lon=lon_deg, lat=lat_deg)

    # Create and return LatLonQuad with longitude normalization
    return LatLonQuad(
        ul=corners_lonlat["ul"],
        ur=corners_lonlat["ur"],
        ll=corners_lonlat["ll"],
        lr=corners_lonlat["lr"],
        normalize_longitudes=True,
    )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
