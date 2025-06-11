from __future__ import annotations

import os
import textwrap
from collections.abc import Generator, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

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

    unwrapped = [lons_180[0]]

    for prev_lon, curr_lon in nisarqa.pairwise(lons_180):

        delta = curr_lon - prev_lon

        # If it's a large jump to the west, subtract 360
        if delta > 180:
            curr_lon -= 360
        # If it's a large jump to the east, add 360
        elif delta < -180:
            curr_lon += 360

        unwrapped.append(curr_lon)

    return unwrapped


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
        in degrees.
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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
