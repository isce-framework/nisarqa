from __future__ import annotations

import os
from typing import Any, overload

import isce3
import numpy as np

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


def get_phase_array(
    phs_or_complex_raster: nisarqa.GeoRaster | nisarqa.RadarRaster,
    make_square_pixels: bool,
    rewrap: Optional[float] = None,
) -> tuple[np.ndarray, list[float]]:
    """
    Get the phase image from the input *Raster.

    Parameters
    ----------
    phs_or_complex_raster : nisarqa.GeoRaster | nisarqa.RadarRaster
        *Raster of complex interferogram or unwrapped phase data.
        If *Raster is complex valued, numpy.angle() will be used to compute
        the phase image (float-valued).
    make_square_pixels : bool
        True to decimate the image to have square pixels.
        False for `phs_img` to always keep the same shape as
        `phs_or_complex_raster.data`
    rewrap : float or None, optional
        The multiple of pi to rewrap the unwrapped phase image.
        If None, no rewrapping will occur.
        If `phs_or_complex_raster` is complex valued, this will be ignored.
        Ex: If 3 is provided, the image is rewrapped to the interval [0, 3pi).
        Defaults to None.

    Returns
    -------
    phs_img : numpy.ndarray
        Copy of the phase image from the input raster, processed
        according to the input parameters.
    cbar_min_max : pair of float
        The suggested range to use for plotting the phase image.
        If `phs_or_complex_raster` has complex valued data, then `cbar_min_max`
        will be the range (-pi, +pi].
        If `rewrap` is a float, the range will be [0, <rewrap * pi>).
        If `rewrap` is a None, the range will be [<array min>, <array max>].
    """

    # Validate rewrap parameter for complex data
    if phs_or_complex_raster.is_complex and rewrap is not None:
        raise ValueError(
            "Input raster has a complex dtype (implying a wrapped"
            f" interferogram), but input parameter {rewrap=}. `rewrap` is"
            " only used in the case of real-valued data (implying an"
            " unwrapped phase image). Please check that this is intended."
        )

    # Extract phase
    phs_img = extract_phase_from_raster(phs_or_complex_raster)

    # Apply rewrapping if needed (only for real-valued/unwrapped data)
    if not phs_or_complex_raster.is_complex and rewrap is not None:
        phs_img = rewrap_phase(phs_img, rewrap)

    # Determine colorbar
    cbar_min_max = determine_phase_colorbar(
        is_complex=phs_or_complex_raster.is_complex,
        rewrap=rewrap if not phs_or_complex_raster.is_complex else None,
        phase=phs_img,
    )

    # Decimate to square pixels if requested
    if make_square_pixels:
        raster_shape = phs_img.shape

        ky, kx = nisarqa.compute_square_pixel_nlooks(
            img_shape=raster_shape,
            sample_spacing=[
                phs_or_complex_raster.y_ground_spacing,
                phs_or_complex_raster.x_ground_spacing,
            ],
            # Only make square pixels. Use `max()` to not "shrink" the rasters.
            longest_side_max=max(raster_shape),
        )

        # Decimate to square pixels.
        phs_img = phs_img[::ky, ::kx]

    return phs_img, cbar_min_max


def extract_phase_from_raster(
    phs_or_complex_raster: nisarqa.GeoRaster | nisarqa.RadarRaster,
) -> np.ndarray:
    """
    Extract the phase image from the input *Raster.

    If the raster is complex-valued, applies np.angle() to compute phase.
    If the raster is real-valued, returns a copy of the data.

    Parameters
    ----------
    phs_or_complex_raster : nisarqa.GeoRaster | nisarqa.RadarRaster
        *Raster of complex interferogram or unwrapped phase data.

    Returns
    -------
    phs_img : numpy.ndarray
        Phase image (float-valued). For complex input, this is the result
        of np.angle(). For real input, this is a copy of the data.
    """
    phs_img = np.array(phs_or_complex_raster.data, copy=True)

    if phs_or_complex_raster.is_complex:
        phs_img = np.angle(phs_img)

    return phs_img


def rewrap_phase(
    phase: np.ndarray,
    rewrap: float,
) -> np.ndarray:
    """
    Rewrap a phase array to [0, rewrap*pi).

    Parameters
    ----------
    phase : np.ndarray
        Input phase array (in radians).
    rewrap : float
        The multiple of pi to rewrap to.
        Ex: If 3 is provided, the output is rewrapped to [0, 3π).

    Returns
    -------
    rewrapped_phase : np.ndarray
        Phase array rewrapped to [0, rewrap*pi).
    """
    rewrap_final = rewrap * np.pi
    # The modulo operator puts the output into range [0, rewrap_final)
    return phase % rewrap_final


def determine_phase_colorbar(
    is_complex: bool,
    rewrap: float | None,
    phase: np.ndarray,
) -> tuple[float, float]:
    """
    Determine the colorbar range for a phase image.

    Parameters
    ----------
    is_complex : bool
        True if the original raster was complex-valued (wrapped interferogram).
        False if it was real-valued (unwrapped phase).
    rewrap : float or None
        The multiple of pi used for rewrapping, or None if not rewrapped.
        Only applicable when is_complex=False.
    phase : np.ndarray
        The phase array. Only used if is_complex=False and rewrap=None
        (to compute min/max for colorbar).

    Returns
    -------
    cbar_min, cbar_max : tuple of float
        The (min, max) values for the colorbar range.
    """
    if is_complex:
        # Complex data: phase is in (-pi, pi] from np.angle()
        return (-np.pi, np.pi)
    elif rewrap is not None:
        # Rewrapped: [0, rewrap*pi)
        return (0.0, rewrap * np.pi)
    else:
        # Unwrapped without rewrapping: use actual data range
        return (float(np.nanmin(phase)), float(np.nanmax(phase)))


@overload
def make_phase_browse(
    raster: nisarqa.RadarRaster,
    *,
    rewrap: float | None,
    longest_side_max: int | None,
    resample: str,
    browse_paths: nisarqa.BrowseOutputPaths,
    save_latlon_browse: bool,
    orbit: isce3.core.Orbit,
    wavelength: float,
    look_side: isce3.core.LookSide | str,
    dem_file: str | os.PathLike | None = None,
) -> None: ...


@overload
def make_phase_browse(
    raster: nisarqa.GeoRaster,
    *,
    rewrap: float | None,
    longest_side_max: int | None,
    resample: str,
    browse_paths: nisarqa.BrowseOutputPaths,
    save_latlon_browse: bool,
) -> None: ...


def make_phase_browse(
    raster: nisarqa.GeoRaster | nisarqa.RadarRaster,
    *,
    rewrap: float | None,
    longest_side_max: int | None,
    resample: str,
    browse_paths: nisarqa.BrowseOutputPaths,
    save_latlon_browse: bool,
    # Level-1 (RadarRaster) parameters:
    orbit: Any | None = None,
    wavelength: float | None = None,
    look_side: Any | None = None,
    dem_file: str | os.PathLike | None = None,
) -> None:
    """
    Helper function to create and save phase browse products as PNG+KML.

    This function handles both Level-1 (radar coordinates) and Level-2 (geocoded)
    phase rasters. It extracts the phase, decimates to square pixels, applies
    rewrapping at the appropriate stage, and saves the browse products.

    For the primary browse: decimates → rewraps (if needed) → saves PNG+KML
    For the EPSG 4326 browse: decimates → geocodes/reprojects → rewraps (if needed) → saves PNG+KML

    Parameters
    ----------
    raster : nisarqa.GeoRaster or nisarqa.RadarRaster
        Input phase raster (complex-valued wrapped interferogram or
        real-valued unwrapped phase).
    rewrap : float or None
        The multiple of pi to rewrap the phase image.
        If None, no rewrapping will occur.
        Only applicable for unwrapped phase (real-valued rasters).
        If the raster is complex-valued and rewrap is not None, an error is raised.
    longest_side_max : int or None
        Maximum number of pixels for the longest side of the decimated array.
        If None, no maximum is enforced.
    resample : str
        Resampling method for EPSG 4326 (lat/lon) browse generation.
        Common options: 'bilinear', 'cubic', 'nearest', etc.
    browse_paths : nisarqa.BrowseOutputPaths
        Container with output directory and browse/KML filenames.
    save_latlon_browse : bool
        If False, only save the primary browse PNG+KML in the raster's native grid.
        If True, additionally save a version of the browse PNG+KML in
        EPSG 4326 (lat/lon).
    orbit : isce3.core.Orbit or None, optional
        **Required for Level-1 (RadarRaster). Ignored for Level-2.**
        The trajectory of the radar antenna phase center.
        Defaults to None.
    wavelength : float or None, optional
        **Required for Level-1 (RadarRaster). Ignored for Level-2.**
        The radar central wavelength, in meters.
        Defaults to None.
    look_side : isce3.core.LookSide or {'left', 'right'} or None, optional
        **Required for Level-1 (RadarRaster). Ignored for Level-2.**
        The look direction of the radar (left-looking or right-looking).
        Defaults to None.
    dem_file : str, os.PathLike, or None, optional
        **Required for Level-1 (RadarRaster). Ignored for Level-2.**
        Digital Elevation Model (DEM) file path in a GDAL-compatible raster
        format. Used when geocoding the EPSG 4326 (lat/lon) browse.
        If None, a zero-height DEM will be used.
        Defaults to None.
    """
    log = nisarqa.get_logger()

    # Validate rewrap parameter
    if raster.is_complex and rewrap is not None:
        raise ValueError(
            f"Raster is complex-valued (wrapped interferogram) but {rewrap=}. "
            "Rewrapping is only applicable to unwrapped phase (real-valued rasters)."
        )

    # Extract phase from the raster
    phase = extract_phase_from_raster(raster)

    # Get sample spacing from the raster
    sample_spacing = (raster.y_ground_spacing, raster.x_ground_spacing)

    # Decimate the phase array to square pixels
    decimated_phase, ky, kx = (
        nisarqa.decimate_array_to_square_pixels_with_strides(
            arr=phase,
            y_axis_spacing=sample_spacing[0],
            x_axis_spacing=sample_spacing[1],
            longest_side_max=longest_side_max,
        )
    )

    # === PRIMARY BROWSE ===
    # Apply rewrapping if needed for primary browse
    if raster.is_complex or rewrap is None:
        primary_phase = decimated_phase
    else:
        primary_phase = rewrap_phase(decimated_phase, rewrap)

    # Determine colorbar for primary browse
    primary_cbar = determine_phase_colorbar(
        is_complex=raster.is_complex,
        rewrap=rewrap if not raster.is_complex else None,
        phase=primary_phase,
    )

    # Save primary browse PNG
    nisarqa.plot_2d_array_and_save_to_png(
        arr=primary_phase,
        cmap="twilight_shifted",
        png_filepath=browse_paths.primary_browse_path,
        vmin=primary_cbar[0],
        vmax=primary_cbar[1],
    )

    # Downsample the grid to match the decimated phase array
    browse_grid = raster.grid.downsample(
        y_stride=ky, x_stride=kx, mode="decimate"
    )

    # Assert grid and phase have matching dimensions
    assert (
        np.shape(decimated_phase)[0] == np.shape(browse_grid.y_pixel_centers)[0]
    ), (
        f"Must be equal: {np.shape(decimated_phase)[0]=} but"
        f" {np.shape(browse_grid.y_pixel_centers)[0]=}."
    )
    assert np.shape(decimated_phase)[1] == len(browse_grid.x_pixel_centers), (
        f"Must be equal: {np.shape(decimated_phase)[1]=} but"
        f" {len(browse_grid.x_pixel_centers)=}."
    )

    # Save KML for the primary browse PNG
    if isinstance(raster.grid, nisarqa.GeoGrid):
        # Level-2: Geocoded product
        browse_grid.save_kml(browse_paths=browse_paths)
    else:
        # Level-1: Radar product
        assert isinstance(raster.grid, nisarqa.RadarGrid)
        browse_grid.save_kml(
            browse_paths=browse_paths,
            orbit=orbit,
            wavelength=wavelength,
            look_side=look_side,
            dem_file=dem_file,
        )

    # === EPSG 4326 BROWSE (if requested) ===
    if save_latlon_browse:
        # Geocode or reproject the decimated (but NOT rewrapped) phase
        if isinstance(raster.grid, nisarqa.GeoGrid):
            # Ensure fill_value is float (take real part if complex)
            fill_val = (
                np.real(raster.fill_value)
                if np.iscomplexobj(raster.fill_value)
                else raster.fill_value
            )

            # Level-2: Reproject using GDAL
            geocoded_arr, qa_geogrid_4326 = nisarqa.reproject_geo_raster(
                image_array=decimated_phase,
                fill_value=fill_val,
                geogrid=browse_grid,
                output_epsg=4326,
                resample=resample,
            )
        else:
            # Level-1: Geocode using ISCE3
            geocoded_arr, qa_geogrid_4326 = nisarqa.geocode_radar_raster(
                radar_array=decimated_phase,
                radargrid=browse_grid,
                orbit=orbit,
                wavelength=wavelength,
                look_side=look_side,
                epsg=4326,
                dem_file=dem_file,
                resample=resample,
            )

        # Apply rewrapping to the geocoded array if needed
        if raster.is_complex or rewrap is None:
            epsg4326_phase = geocoded_arr
        else:
            epsg4326_phase = rewrap_phase(geocoded_arr, rewrap)

        # Determine colorbar for EPSG 4326 browse
        epsg4326_cbar = determine_phase_colorbar(
            is_complex=raster.is_complex,
            rewrap=rewrap if not raster.is_complex else None,
            phase=epsg4326_phase,
        )

        # Save EPSG 4326 browse PNG
        suffix = nisarqa.LATLON_SUFFIX
        png_4326_path = browse_paths.get_browse_path(suffix=suffix)

        nisarqa.plot_2d_array_and_save_to_png(
            arr=epsg4326_phase,
            cmap="twilight_shifted",
            png_filepath=png_4326_path,
            vmin=epsg4326_cbar[0],
            vmax=epsg4326_cbar[1],
        )
        log.info(f"EPSG 4326 (lat/lon) browse PNG saved to {png_4326_path}")

        # Save EPSG 4326 KML
        qa_geogrid_4326.save_kml(browse_paths=browse_paths, suffix=suffix)

        kml_4326_path = browse_paths.get_kml_path(suffix=suffix)
        log.info(f"EPSG 4326 (lat/lon) browse KML saved to {kml_4326_path}")


__all__ = nisarqa.get_all(__name__, objects_to_skip)
