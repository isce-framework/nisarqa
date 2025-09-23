from __future__ import annotations

import functools
import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import overload

import isce3
import matplotlib as mpl
import matplotlib.colors as colors
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from ..plotting_utils import (
    downsample_img_to_size_of_axes_with_stride,
    format_axes_ticks_and_labels,
    save_mpl_plot_to_png,
)

objects_to_skip = nisarqa.get_all(name=__name__)


@overload
def plot_offsets_quiver_plot_to_pdf(
    az_offset: nisarqa.RadarRaster,
    rg_offset: nisarqa.RadarRaster,
    params: nisarqa.QuiverParamGroup,
    report_pdf: PdfPages,
) -> tuple[float, float]: ...


@overload
def plot_offsets_quiver_plot_to_pdf(
    az_offset: nisarqa.GeoRaster,
    rg_offset: nisarqa.GeoRaster,
    params: nisarqa.QuiverParamGroup,
    report_pdf: PdfPages,
    quiver_projection_params: None | nisarqa.ParamsForAzRgOffsetsToProjected,
) -> tuple[float, float]: ...


def plot_offsets_quiver_plot_to_pdf(
    az_offset, rg_offset, params, report_pdf, quiver_projection_params=None
):
    """
    Process and save a single quiver plot to PDF.

    Parameters
    ----------
    az_offset : nisarqa.RadarRaster or nisarqa.GeoRaster
        Along track offset layer to be processed. Must correspond to
        `rg_offset`.
    rg_offset : nisarqa.RadarRaster or nisarqa.GeoRaster
        Slant range offset layer to be processed. Must correspond to
        `az_offset`.
    params : nisarqa.QuiverParamGroup
        A structure containing processing parameters to generate quiver plots.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the quiver plot to.
    quiver_projection_params : None or ParamsForAzRgOffsetsToProjected, optional
        ** Strongly recommend providing parameters for GOFF and GUNW **
        Set to None if the contents of the offset rasters use the same
        coordinate grid as the raster image (e.g. both are
        azimuth/range grid, such as for ROFF, RIFG, and RUNW).
        If offsets arrays are nisarqa.GeoRaster and these parameters are
        provided, they will be used to modify the quiver arrows to
        represent displacement direction and relative magnitude in
        projected coordinates. Note: the plotted image (and colorbar) will
        represent displacement magnitude in radar coordinates;
        only the quiver arrows will be projected.
        Defaults to None.

    Returns
    -------
    cbar_min, cbar_max : float
        The vmin and vmax (respectively) used for the colorbar and clipping
        the pixel offset displacement image.

    Notes
    -----
    NISAR GOFF and GUNW along track and slant range offsets rasters are
    geocoded to projected coordinates, but their pixel values represent the
    offset in azimuth and slant range directions (respectively).
    Because of this, if `az_offset` and `rg_offset` come from GOFF or GUNW,
    and if `quiver_projection_params` is set to None, then the quiver arrows
    will not be plotted in the correct direction/magnitude for the projected
    X/Y image grid (i.e. they'll appear to point the wrong direction).
    """
    # Validate input rasters
    nisarqa.compare_raster_metadata(az_offset, rg_offset, almost_identical=True)

    if quiver_projection_params is not None:
        if isinstance(az_offset, nisarqa.RadarRaster):
            raise TypeError(
                "Input az and rg offset rasters are instances of"
                f" nisarqa.RadarRaster, but {type(quiver_projection_params)=}."
                " It should be set to None for rasters on the radar grid."
            )
        reproject_arrows = True
    else:
        reproject_arrows = False

    fig, ax = plt.subplots(
        ncols=1,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE,
    )

    # Form the plot title (Remove the layer name from the layer's `name`)
    # Because of the constrained layout (which optimizes for all Artists in
    # the Figure), let's add the title before decimating the rasters.
    # (`az_offset.name` is formatted like "ROFF_L_A_HH_layer1_alongTrackOffset".
    # The PDF page has two rasters, so remove the final layer name for title.)
    title = (
        "Combined Azimuth and Slant Range Displacement (meters)\n"
        f"{'_'.join(az_offset.name.split('_')[:-1])}"
    )
    if isinstance(az_offset, nisarqa.GeoRaster):
        title = "Geocoded " + title
    fig.suptitle(title)

    # Grab the datasets into arrays in memory (with square pixels).
    az_off, ky1, kx1 = (
        nisarqa.decimate_raster_array_to_square_pixels_with_strides(
            raster_obj=az_offset
        )
    )
    rg_off, ky2, kx2 = (
        nisarqa.decimate_raster_array_to_square_pixels_with_strides(
            raster_obj=rg_offset
        )
    )
    assert ky1 == ky2
    assert kx1 == kx2

    # `downsample_img_to_size_of_axes_with_stride()` retains the aspect ratio
    # of the source raster, so the stride is the same for along both X and Y.
    az_off, stride1 = downsample_img_to_size_of_axes_with_stride(
        ax=ax, arr=az_off, mode="decimate"
    )
    rg_off, stride2 = downsample_img_to_size_of_axes_with_stride(
        ax=ax, arr=rg_off, mode="decimate"
    )
    assert stride1 == stride2

    # Construct coordinate grid parameters to match our
    # freshly-decimated `az_off` and `rg_off`
    kwargs = {}
    if isinstance(az_offset, nisarqa.GeoRaster):
        # `nisarqa.compare_raster_metadata` ensures that the `rg_offset`
        # has the same coordinate grid as `az_offset`.
        y_coordinates = az_offset.y_coordinates
        x_coordinates = az_offset.x_coordinates

        # Modify with same strides as used above to decimate to square pixels
        # and size of axes
        y_coords = y_coordinates[::ky1][::stride1]
        x_coords = x_coordinates[::kx1][::stride1]

        assert az_off.shape[0] == len(y_coords)
        assert az_off.shape[1] == len(x_coords)

        x_posting = az_offset.x_posting * kx1 * stride1
        y_posting = az_offset.y_posting * ky1 * stride1

        kwargs["coord_grid"] = nisarqa.GeoGrid(
            epsg=az_offset.epsg,
            x_axis_posting=x_posting,
            x_coordinates=x_coords,
            y_axis_posting=y_posting,
            y_coordinates=y_coords,
        )

        kwargs["quiver_projection_params"] = quiver_projection_params

    else:
        assert isinstance(az_offset, nisarqa.RadarRaster)

        zero_dop_spacing = az_offset.zero_doppler_time_spacing * ky1 * stride1

        kwargs["coord_grid"] = nisarqa.RadarGrid(
            zero_doppler_time=az_offset.zero_doppler_time[::ky1][::stride1],
            zero_doppler_time_spacing=zero_dop_spacing,
            slant_range=az_offset.slant_range[::kx1][::stride1],
            slant_range_spacing=az_offset.slant_range_spacing * kx1 * stride1,
            ground_az_spacing=az_offset.ground_az_spacing * ky1 * stride1,
            ground_range_spacing=az_offset.ground_range_spacing * kx1 * stride1,
            epoch=az_offset.epoch,
        )

    im, cbar_min, cbar_max = add_magnitude_image_and_quiver_plot_to_axes(
        ax=ax,
        az_off=az_off,
        rg_off=rg_off,
        params=params,
        **kwargs,
    )

    # Add a colorbar to the figure
    cax = fig.colorbar(im)
    cax.ax.set_ylabel(ylabel="Displacement (m)", rotation=270, labelpad=10.0)

    format_axes_ticks_and_labels(
        ax=ax,
        xlim=az_offset.x_axis_limits,
        ylim=az_offset.y_axis_limits,
        img_arr_shape=np.shape(az_off),
        xlabel=az_offset.x_axis_label,
        ylabel=az_offset.y_axis_label,
    )

    if reproject_arrows:
        note = (
            "* Arrows represent direction and relative magnitude\n"
            "of the combined X and Y displacement on the geocoded grid"
        )
        ax.set_title(note, loc="right", color="blue", size=6, pad=1)

    # Append figure to the output PDF
    report_pdf.savefig(fig)

    # Close the plot
    plt.close(fig)

    return cbar_min, cbar_max


@overload
def plot_single_quiver_plot_to_png(
    az_offset: nisarqa.RadarRaster,
    rg_offset: nisarqa.RadarRaster,
    params: nisarqa.QuiverParamGroup,
    png_filepath: str | os.PathLike,
) -> tuple[int, int]: ...


@overload
def plot_single_quiver_plot_to_png(
    az_offset: nisarqa.GeoRaster,
    rg_offset: nisarqa.GeoRaster,
    params: nisarqa.QuiverParamGroup,
    png_filepath: str | os.PathLike,
    quiver_projection_params: None | nisarqa.ParamsForAzRgOffsetsToProjected,
) -> tuple[int, int]: ...


def plot_single_quiver_plot_to_png(
    az_offset, rg_offset, params, png_filepath, quiver_projection_params=None
):
    """
    Process and save a single quiver plot to PDF and (optional) PNG.

    Parameters
    ----------
    az_offset : nisarqa.RadarRaster or nisarqa.GeoRaster
        Along track offset layer to be processed. Must correspond to
        `rg_offset`.
    rg_offset : nisarqa.RadarRaster or nisarqa.GeoRaster
        Slant range offset layer to be processed. Must correspond to
        `az_offset`.
    params : nisarqa.QuiverParamGroup
        A structure containing processing parameters to generate quiver plots.
    png_filepath : path-like
        Filename (with path) for the image PNG.
    quiver_projection_params : None or ParamsForAzRgOffsetsToProjected, optional
        ** Strongly recommend providing parameters for GOFF and GUNW **
        Set to None if the contents of the offset rasters use the same
        coordinate grid as the raster image (e.g. both are
        azimuth/range grid, such as for ROFF, RIFG, and RUNW).
        If offsets arrays are nisarqa.GeoRaster and these parameters are
        provided, they will be used to modify the quiver arrows to
        represent displacement direction and relative magnitude in
        projected coordinates. Note: the plotted image (and colorbar) will
        represent displacement magnitude in radar coordinates;
        only the quiver arrows will be projected.
        Defaults to None.

    Returns
    -------
    y_dec, x_dec : int
        The decimation stride value used in the Y axis direction and X axis
        direction (respectively).

    Notes
    -----
    NISAR GOFF and GUNW along track and slant range offsets rasters are
    geocoded to projected coordinates, but their pixel values represent the
    offset in azimuth and slant range directions (respectively).
    Because of this, if `az_offset` and `rg_offset` come from GOFF or GUNW,
    and if `quiver_projection_params` is set to None, then the quiver arrows
    will not be plotted in the correct direction/magnitude for the projected
    X/Y image grid (i.e. they'll appear to point the wrong direction).
    """
    # Validate input rasters
    nisarqa.compare_raster_metadata(az_offset, rg_offset, almost_identical=True)

    # Compute decimation values for the browse image PNG.
    if (az_offset.freq == "A") and (params.browse_decimation_freqa is not None):
        y_decimation, x_decimation = params.browse_decimation_freqa
    elif (az_offset.freq == "B") and (
        params.browse_decimation_freqb is not None
    ):
        y_decimation, x_decimation = params.browse_decimation_freqb
    else:
        # Square the pixels. Decimate if needed to stay within longest side max.
        longest_side_max = params.longest_side_max

        if longest_side_max is None:
            # Update to be the longest side of the array. This way no downsizing
            # of the image will occur, but we can still output square pixels.
            longest_side_max = max(np.shape(rg_offset.data))

        y_decimation, x_decimation = nisarqa.compute_square_pixel_nlooks(
            img_shape=np.shape(az_offset.data),
            sample_spacing=[
                az_offset.y_ground_spacing,
                az_offset.x_ground_spacing,
            ],
            longest_side_max=longest_side_max,
        )

    # Grab the datasets into arrays in memory.
    # While doing this, convert to square pixels and correct pixel dimensions.
    az_off = az_offset.data[::y_decimation, ::x_decimation]
    rg_off = rg_offset.data[::y_decimation, ::x_decimation]

    # Construct coordinate grid parameters to match our
    # freshly-decimated `az_off` and `rg_off`
    kwargs = {}
    if quiver_projection_params is not None:
        if isinstance(az_offset, nisarqa.RadarRaster):
            raise TypeError(
                "Input az and rg offset rasters are instances of"
                f" nisarqa.RadarRaster, but {type(quiver_projection_params)=}."
                " It should be set to None for rasters on the radar grid."
            )
        kwargs["quiver_projection_params"] = quiver_projection_params

    if isinstance(az_offset, nisarqa.GeoRaster):
        x_coordinates = az_offset.x_coordinates
        y_coordinates = az_offset.y_coordinates
        x_coords = x_coordinates[::x_decimation]
        y_coords = y_coordinates[::y_decimation]

        assert az_off.shape[1] == len(x_coords)
        assert az_off.shape[0] == len(y_coords)

        x_posting = az_offset.x_posting * x_decimation
        y_posting = az_offset.y_posting * y_decimation

        kwargs["coord_grid"] = nisarqa.GeoGrid(
            epsg=az_offset.epsg,
            x_axis_posting=x_posting,
            x_coordinates=x_coords,
            y_axis_posting=y_posting,
            y_coordinates=y_coords,
        )
    else:
        assert isinstance(az_offset, nisarqa.RadarRaster)

        zero_dop_spacing = az_offset.zero_doppler_time_spacing * y_decimation

        kwargs["coord_grid"] = nisarqa.RadarGrid(
            zero_doppler_time=az_offset.zero_doppler_time[::y_decimation],
            zero_doppler_time_spacing=zero_dop_spacing,
            slant_range=az_offset.slant_range[::x_decimation],
            slant_range_spacing=az_offset.slant_range_spacing * x_decimation,
            ground_az_spacing=az_offset.ground_az_spacing * y_decimation,
            ground_range_spacing=az_offset.ground_range_spacing * x_decimation,
            epoch=az_offset.epoch,
        )

    # Next, we need to add the background image + quiver plot arrows onto
    # an Axes, and then save this to a PNG with exact pixel dimensions as
    # `az_off` and `rg_off`.
    quiver_func = functools.partial(
        add_magnitude_image_and_quiver_plot_to_axes,
        az_off=az_off,
        rg_off=rg_off,
        params=params,
        **kwargs,
    )

    save_mpl_plot_to_png(
        axes_partial_func=quiver_func,
        raster_shape=az_off.shape,
        png_filepath=png_filepath,
    )

    return y_decimation, x_decimation


def add_magnitude_image_and_quiver_plot_to_axes(
    ax: mpl.axes.Axes,
    az_off: np.ndarray,
    rg_off: np.ndarray,
    params: nisarqa.QuiverParamGroup,
    coord_grid: nisarqa.RadarGrid | nisarqa.GeoGrid,
    quiver_projection_params: (
        None | nisarqa.ParamsForAzRgOffsetsToProjected
    ) = None,
) -> tuple[mpl.AxesImage, float, float]:
    """
    Compute the total offset magnitude and add as a quiver plot to an Axes.

    This function computes the total offset magnitude via this formula:
        total_offset = sqrt(rg_off**2 + az_off**2)
    `total_offset` is used as the background image, with the magma color map.
    The quiver arrows (vector arrows) are added to the Axes on top of the
    `total_offset` image.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes object that will be modified; the total offset magnitude image
        and the quiver plot arrows will be added to this axes.
    az_off : numpy.ndarray
        Along track offset raster array.
    rg_off : numpy.ndarray
        Slant range offset raster array.
    params : nisarqa.QuiverParamGroup
        A structure containing processing parameters to generate quiver plots.
    coord_grid : nisarqa.RadarGrid or nisarqa.GeoGrid
        Coordinate grid for `az_off` and `rg_off`.
    quiver_projection_params : None or ParamsForAzRgOffsetsToProjected
        ** Strongly Recommend `None` for ROFF, RIFG, RUNW **
        ** Strongly Recommend providing parameters for GOFF and GUNW **
        Set to None if the contents of the offset rasters use the same
        coordinate grid as the raster image (e.g. both are
        azimuth/range grid, such as for ROFF, RIFG, and RUNW).
        If provided, function assumes `az_off` and `rg_off` are in projected
        coordinates but their contents represent offsets in azimuth and slant
        range (respectively); this is the case for GOFF and GUNW.
        These parameters will be used to modify the quiver arrows to
        represent displacement direction and relative magnitude in
        projected coordinates. Note: the plotted image (and colorbar) will
        represent displacement magnitude in radar coordinates;
        only the quiver arrows will be projected.
        These parameters should correspond to `az_off` and `rg_off`.
        Defaults to None.

    Returns
    -------
    im : matplotlib.AxesImage
        AxesImage containing the final plotted image (including quiver arrows).
    vmin, vmax : float
        The vmin and vmax (respectively) used for clipping the pixel offset
        displacement image and for the colorbar interval.

    Notes
    -----
    No decimation occurs in this function, and the image arrays are
    plotted on `ax` with interpolation set to "none". This is to maintain the
    same pixel dimensions of the input arrays.

    Prior to calling this function, it is suggested that the user size the
    axes and the input arrays to have matching dimensions. This helps to
    ensure that the aspect ratio of `im` is as expected.

    Warnings
    --------
    If `az_off` and `rg_off` are in projected coordinates, but their
    contents represent offsets in azimuth and slant range (respectively),
    and if `quiver_projection_params` is set to None, then the quiver arrows
    will not be plotted in the correct direction/magnitude for the projected
    X/Y image grid (i.e. they'll point the wrong direction w/r/t the image).
    """

    # Use the full resolution image as the colorful background image of the plot
    total_offset = np.sqrt(rg_off**2 + az_off**2)

    # Compute the vmin and vmax for the colorbar range
    # Note: because we're getting `cbar_min_max` from the `params`, the values
    # have already been validated. No further checks needed.
    cbar_min_max = params.cbar_min_max
    if cbar_min_max is None:
        # Dynamically compute the colorbar interval to be [0, max].
        # (`total_offset` represents magnitude; these are positive values)
        vmin, vmax = 0, np.nanmax(total_offset)
    else:
        vmin, vmax = cbar_min_max

    # Truncate the magma cmap to only use the top half of the magma colormap
    # Adapted from: https://stackoverflow.com/a/18926541
    def truncate_colormap(
        cmap: colors.ListedColormap,
        minval: float = 0.0,
        maxval: float = 1.0,
        n: int = -1,
    ) -> colors.LinearSegmentedColormap:
        """
        Truncate a colormap to only use a subset of the colormap.

        A colormap maps values in the interval [0.0, 1.0] to specific visual
        colors. For a known colormap, sometimes we only want to use a
        sub-interval of its visual color range for our plot. This function
        allows the user to specify the sub-interval of the existing colorbar
        that they want to use, and returns a new colormap with the
        visual colors from that sub-interval "stretched" to fill the entire
        [0.0, 1.0] colormap range.

        Parameters
        ----------
        cmap : colors.ListedColormap
            An existing colormap. This can be fetched by calling e.g.
            matplotlib.pyplot.get_cmap("magma").
        minval : float, optional
            Minimum value of the sub-interval of `cmap` to use. Must be >= 0.0.
            Defaults to 0.0.
        maxval : float, optional
            Maximum value of the sub-interval of `cmap` to use. Must be <= 1.0.
            Defaults to 1.0.
        n : int, optional
            Number of entries to generate in the truncated colormap. (256 is
            a typical value.) -1 to use the same numbers of entries as `cmap`.
            Defaults to -1.

        Returns
        -------
        truncated_cmap : matplotlib.colors.LinearSegmentedColormap
            A new colormap with the visual colors from the sub-interval
            [`minval`, `maxval`] of `cmap`'s colormap "stretched" to
            fill the entire colormap range.
        """
        if (minval < 0.0) or (maxval > 1.0):
            raise ValueError(
                f"{minval=} and {maxval=}, but must be in range [0.0, 1.0]."
            )
        if n == -1:
            n = cmap.N
        new_cmap = colors.LinearSegmentedColormap.from_list(
            "trunc({name},{a:.2f},{b:.2f})".format(
                name=cmap.name, a=minval, b=maxval
            ),
            cmap(np.linspace(minval, maxval, n)),
        )
        return new_cmap

    # Use interval from [0.5, 1.0] to truncate to the top half of the magma
    # colormap range. (We do not want to use the very-dark lower half
    # for these quiver plots.)
    # Definitions: the colormap range is different than the colorbar range.
    # Colorbar range refers to the range of tick label values, while the
    # colormap determines the mapping of those values to actual visual colors.
    magma_cmap = truncate_colormap(plt.get_cmap("magma"), 0.5, 1.0)

    # Add the background image to the axes
    im = ax.imshow(
        total_offset,
        vmin=vmin,
        vmax=vmax,
        cmap=magma_cmap,
        interpolation="none",
    )

    # Now, prepare and add the quiver plot arrows to the axes
    arrow_stride = int(max(np.shape(total_offset)) / params.arrow_density)

    # Only plot the arrows at the requested strides.
    arrow_az_offsets = az_off[::arrow_stride, ::arrow_stride]
    arrow_rg_offsets = rg_off[::arrow_stride, ::arrow_stride]

    num_arrows_x = arrow_az_offsets.shape[1]
    num_arrows_y = arrow_az_offsets.shape[0]
    x = np.arange(num_arrows_x)
    y = np.arange(num_arrows_y)
    X, Y = np.meshgrid(x, y)

    # 2D grid of the starting x pixel indices in the image arrays for each arrow
    arrow_tails_x_indices = X * arrow_stride

    # 2D grid of the starting y pixel indices in the image arrays for each arrow
    arrow_tails_y_indices = Y * arrow_stride

    # Determine the offsets in the image grid's X and Y directions

    if quiver_projection_params is None:
        # For L1 (ROFF, etc), `arrow_az_offsets` indicates how many
        # meters to offset in the image grid's y-direction (aka along-track).
        # (Similar reasoning for slant range offsets and the x-direction.)

        # For L2 (GOFF, etc), because `quiver_projection_params` was not
        # provided, use the offsets values as-is, with no modifications.
        arrow_y_offsets = arrow_az_offsets
        arrow_x_offsets = arrow_rg_offsets
    else:
        # For L2 (GOFF, etc), `arrow_az_offsets` indicates how many
        # meters to offset in the satellite's along-track direction, which
        # is NOT the same as the image grid's y-direction. So, do conversion.

        arrow_x_offsets, arrow_y_offsets = (
            get_offset_values_in_projected_coordinates(
                az_offsets=arrow_az_offsets,
                rg_offsets=arrow_rg_offsets,
                geo_grid=nisarqa.GeoGrid(
                    epsg=coord_grid.epsg,
                    x_coordinates=coord_grid.x_coordinates[::arrow_stride],
                    x_axis_posting=coord_grid.x_posting * arrow_stride,
                    y_coordinates=coord_grid.y_coordinates[::arrow_stride],
                    y_axis_posting=coord_grid.y_posting * arrow_stride,
                ),
                projection_params=quiver_projection_params,
            )
        )

    # Arrow tail locations are in pixels. Arrow head offsets are in
    # meters. Convert from meters to pixels.

    # Note: The y-coordinate posting of the coordinate grid of NISAR L2
    # products is negative (the positive y-axis points up in the plot).
    # That is, a postive-valued offset in meters will be a negative-valued
    # offset in pixels. So, when you divide the offsets by the pixel
    # posting, it should flip the sign of the y component of the offsets.

    # Conversely, the y-coordinate posting of NISAR L1 products is
    # positive (the positive y-axis points down in the plot).
    # So dividing by the pixel posting should not flip the sign of the
    # y component of the offsets when making quiver plots for L1 products.

    if isinstance(coord_grid, nisarqa.RadarGrid):
        # TODO - improve me!
        # Ideally, for correct y offsets in pixels we would compute:
        #   <azimuth offset (m)> /
        #       (ground track velocity (m/s) * azimuth pixel spacing (sec))
        # However, this would require computing the ground track velocity
        # for each quiver arrow in L1 products.
        # For now, use `sceneCenterAlongTrackSpacing` as an approximation.
        # (The approximation is because the spacing will vary in different
        # parts of the image.)
        tmp_y_posting = coord_grid.ground_az_spacing
    else:
        assert isinstance(coord_grid, nisarqa.GeoGrid)
        tmp_y_posting = coord_grid.y_posting

    arrow_y_offsets_in_pixels = arrow_y_offsets / tmp_y_posting
    arrow_x_offsets_in_pixels = arrow_x_offsets / coord_grid.x_posting

    # Add the quiver arrows to the plot.
    # Multiply the start and end points for each arrow by the decimation factor;
    # this is to ensure that each arrow is placed on the correct pixel on
    # the full-resolution `total_offset` background image.
    ax.quiver(
        # starting pixel index in x direction for each arrow tail
        arrow_tails_x_indices,
        # starting pixel index in y direction for each arrow tail
        arrow_tails_y_indices,
        # x offset direction for each arrow tip (autoscaling handles magnitude)
        arrow_x_offsets_in_pixels,
        # y offset direction for each arrow tip (autoscaling handles magnitude)
        arrow_y_offsets_in_pixels,
        # When you pass angles='xy', the arrow offsets are in the same
        # coordinates as the arrow tail locations: "Arrow direction in
        # data coordinates, i.e. the arrows point from (x, y) to (x+u, y+v).
        # This is ideal for vector fields or gradient plots where the arrows
        # should directly represent movements or gradients in the
        # x and y directions.""
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.quiver.html
        angles="xy",
        scale_units="xy",
        # Use a scale less that 1 to exaggerate the arrows.
        scale=params.arrow_scaling,
        color="b",
    )

    return im, vmin, vmax


@dataclass
class ParamsForAzRgOffsetsToProjected:
    """
    Parameters to convert geocoded offsets values from az/range to projected.

    For e.g. GOFF and GUNW, the along track offsets and slant range offsets
    rasters are geocoded to projected coordinates, but their pixels'
    values represent offsets in azimuth and slant range directions (in meters).
    These parameters are needed to rotate/scale the pixel values from
    azimuth and slant range directions into the X/Y directions of the projected
    coordinates.

    Parameters
    ----------
    orbit : isce3.core.Orbit
        The trajectory of the radar antenna phase center over a time interval
        that includes the observation times of each point offset pixel.
    look_side : isce3.core.LookSide or {'left', 'right'}
        The look direction of the input product (left-looking or right-looking).
    wavelength : float
        The radar central wavelength for the frequency subband of the offset,
        in meters.
    geo2rdr_params : dict of [str, float] or None, optional
        An optional dict of parameters configuring the behavior of the
        root-finding routine used in geo2rdr (bracketing implementation).
        The following keys are supported:
        'tol_aztime':
           Azimuth time convergence tolerance, in seconds. Defaults to 1e-7.
        'time_start':
           Start of search interval, in seconds. Defaults to `orbit.start_time`.
        'time_end':
           End of search interval, in seconds. Defaults to `orbit.end_time`.
        Defaults to None.
    """

    orbit: isce3.core.Orbit
    wavelength: float
    look_side: isce3.core.LookSide | str
    geo2rdr_params: Mapping[str, float] | None = None


def get_offset_values_in_projected_coordinates(
    az_offsets: np.ndarray,
    rg_offsets: np.ndarray,
    geo_grid: nisarqa.GeoGrid,
    projection_params: nisarqa.ParamsForAzRgOffsetsToProjected,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert pixel values from offset in az/range to offset in projected X/Y.

    For the along-track and slant range offsets raster in NISAR GOFF and GUNW
    products, the raster images are geocoded to projected coordinates but
    their pixel values represent offsets in azimuth and slant range directions
    (respectively) in meters.
    This function will convert the values from offset amount in azimuth
    and slant range directions to the offset in the X and Y directions
    of the projected image grid.

    Parameters
    ----------
    az_offsets : numpy.ndarray
        2D array of the values of the along track offsets.
        Array should be geocoded, but the pixel values should represent
        offset in along azimuth direction (in meters).
    rg_offsets : numpy.ndarray
        2D array of the values of the slant range offsets.
        Array should be geocoded, but the pixel values should represent
        offset in slant range direction (in meters).
    geo_grid : nisarqa.GeoGrid
        Geocoded coordinate grid on which `rg_offsets` and `az_offsets` are sampled.
    projection_params : ParamsForAzRgOffsetsToProjected
        Parameters used to convert the offsets rasters' pixel values from
        azimuth/range offset values (in meters) to values in the
        rasters' projected coordinate grid.

    Returns
    -------
    offset_in_x_direction, offset_in_y_direction : numpy.ndarray
        2D array of the offset values in X and Y direction (respectively)
        of the projected coordinate grid.
    """

    # Variable renaming and unpacking
    arrow_rg_offsets = rg_offsets
    arrow_az_offsets = az_offsets
    epsg = geo_grid.epsg
    arrow_tails_x = geo_grid.x_coordinates
    arrow_tails_y = geo_grid.y_coordinates
    orbit = projection_params.orbit
    wavelength = projection_params.wavelength
    look_side = projection_params.look_side
    geo2rdr_params = projection_params.geo2rdr_params
    geo2rdr_params = {} if (geo2rdr_params is None) else geo2rdr_params

    # Useful variables for the algorithm
    num_arrows_x = len(arrow_tails_x)
    num_arrows_y = len(arrow_tails_y)

    if arrow_rg_offsets.shape != arrow_az_offsets.shape:
        raise ValueError(
            f"{rg_offsets.shape=}, but it must have the same shape"
            f" as {az_offsets.shape=}"
        )

    if (arrow_rg_offsets.shape[1] != num_arrows_x) or (
        arrow_rg_offsets.shape[0] != num_arrows_y
    ):
        raise ValueError(
            f"{arrow_rg_offsets.shape=}, but its dimensions must"
            " correspond to the provided coordinate vectors where"
            f" {len(geo_grid.y_coordinates)=} and"
            f" {len(geo_grid.x_coordinates)=}"
        )

    arrow_x_offsets = np.zeros(
        (num_arrows_y, num_arrows_x),
        dtype=arrow_tails_y.dtype,
    )
    arrow_y_offsets = np.zeros(
        (num_arrows_y, num_arrows_x),
        dtype=arrow_tails_y.dtype,
    )

    # For projected coordinate point (x_0, y_0) at each arrow tail,
    # the basic algorithm to convert is:
    # 1) Convert (x_0, y_0) from projected coordinates into LLH
    # 2) Run geo2rdr on the (x_0, y_0) LLH
    # 3) Use the az/rng offset values (in meters) at the coordinate
    #    to offset ("shift") the point in the radar grid
    # 4) Run rdr2geo to convert back to (x_1, y_1) LLH
    # 5) Convert (x_1, y_1) LLH back into projected coordinates
    # 6) Compute new offset values in projected coordinates:
    #    (x_1 - x_0, y_1 - y_0)

    # Make the ISCE3 projection
    proj = isce3.core.make_projection(epsg)

    for i, y_coord in enumerate(arrow_tails_y):
        for j, x_coord in enumerate(arrow_tails_x):

            # Skip NaN pixels (this is usually geocoding fill)
            if (np.isnan(arrow_rg_offsets[i, j])) or (
                np.isnan(arrow_az_offsets[i, j])
            ):
                arrow_x_offsets[i, j] = np.nan
                arrow_y_offsets[i, j] = np.nan
                continue

            # 1) Convert (x_0, y_0) arrow tail from projected coordinates to LLH

            # Use a dummy height value of 0 in computing the inverse projection.
            # ISCE3 projections are always 2-D transformations -- the height
            # has no effect on lon/lat. In ISCE3, the height value is simply
            # passed through and copied to the output height value, so we
            # can ignore it.
            lon, lat, _ = proj.inverse([x_coord, y_coord, 0])

            # 2) Run geo2rdr on the (x_0, y_0) LLH

            # Get target (x,y,z) position of arrow tails in ECEF coordinates.
            # (ECEF = Earth-centered, Earth-fixed coordinate frame.)
            # Get the ellipsoid to convert the target position from LLH to ECEF
            # Since we do not have a DEM, as an approximation, assume that
            # each target falls on the surface of the WGS 84 ellipsoid.
            # (Ideally, we'd use the target height rather than assuming zero
            # height. But we don't have access to this information in the GOFF
            # input product, so a reasonable approx. is to use zero height.)
            ellipsoid = isce3.core.WGS84_ELLIPSOID

            # When we used `proj.inverse()` above, we did not care
            # about height because the height was simply passed through.
            # Here, for `ellipsoid.lon_lat_to_xyz()` we do care about height,
            # but we do not have a DEM in GOFF nor GUNW products.
            # So, assume each target falls on the WGS 84 ellipsoid.
            target_xyz = ellipsoid.lon_lat_to_xyz([lon, lat, 0])

            # Run geo2rdr to get the target position in radar coordinates.
            aztime, srange = isce3.geometry.geo2rdr_bracket(
                xyz=target_xyz,
                orbit=orbit,
                # NISAR products are zero-Doppler, so construct a zero-Doppler LUT
                doppler=isce3.core.LUT2d(),
                wavelength=wavelength,
                side=look_side,
                **geo2rdr_params,
            )

            # 3) Use the az/rng offset values (in meters) at the coordinate
            #    to offset ("shift") the point in the radar grid

            # Azimuth Offsets are in meters, but azimuth on the radar grid is in
            # seconds. So, convert `arrow_az_offsets` from meters to
            # seconds by using the ground track velocity (meters/second).

            # Use the aztime of each target in radar coordinates to
            # interpolate the orbit in order to get the
            # platform position and velocity in ECEF coordinates.
            platform_pos, platform_vel = orbit.interpolate(aztime)

            grd_trk_vel_at_arrow_tail = nisarqa.get_ground_track_velocity(
                target_xyz,  # ECEF position of target on the ground
                platform_pos,
                platform_vel,
            )

            az_off_val_at_arrow_tail_in_seconds = (
                arrow_az_offsets[i, j] / grd_trk_vel_at_arrow_tail
            )

            # Shift the radar grid's azimuth values
            aztime += az_off_val_at_arrow_tail_in_seconds

            # Shift the radar grid's range values
            # Note: range offset values were already in meters, so just add them
            srange += arrow_rg_offsets[i, j]

            # 4) Run rdr2geo to convert back to (x_1, y_1) LLH

            xyz = isce3.geometry.rdr2geo_bracket(
                # az time in seconds since orbit.reference_epoch
                aztime=aztime,
                # slant range in meters
                slant_range=srange,
                orbit=orbit,
                side=look_side,
                # Here, doppler is a scalar value -- not a LUT. Because
                # we know the target azimuth/range coordinates so we don't
                # need Doppler as a function of range & azimuth, it can
                # just be a scalar value. Since we care about the Doppler
                # of the image grid, use 0.0.
                doppler=0.0,
                # Technically the wavelength is not needed here since
                # Doppler is zero and the wavelength is just multiplied
                # by the Doppler. But since we already need the wavelength
                # for geo2rdr, might as well use it.
                wavelength=wavelength,
                # Ideally we would use the actual DEM, but we don't have
                # this information available so use a zero-height DEM.
                # Pass `epsg=4326` to ensure the DEM is referenced to the
                # WGS 84 ellipsoid.
                dem=isce3.geometry.DEMInterpolator(epsg=4326),
            )

            # Once again, ignore the returned height
            lon, lat, _ = ellipsoid.xyz_to_lon_lat(xyz)

            # 5) Convert shifted LLH (x_1, y_1) back into projected
            #    coordinates
            # To convert from LLH back to the projected coordinates of the
            # input arrays, use the forward() method of the same `proj`
            # object we created above.
            x_shift, y_shift, _ = proj.forward([lon, lat, 0])

            # 6) Compute new offset values in projected coordinates:
            #       (x_1 - x_0, y_1 - y_0)
            arrow_x_offsets[i, j] = x_shift - x_coord
            arrow_y_offsets[i, j] = y_shift - y_coord

    return arrow_x_offsets, arrow_y_offsets


__all__ = nisarqa.get_all(__name__, objects_to_skip)
