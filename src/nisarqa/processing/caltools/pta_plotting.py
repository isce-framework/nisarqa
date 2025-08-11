from __future__ import annotations

import itertools
from collections.abc import Iterator
from dataclasses import dataclass

import h5py
import isce3
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import to_rgba
from matplotlib.figure import Figure
from numpy.typing import ArrayLike

import nisarqa

from ._utils import get_valid_freqs, get_valid_pols

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass(frozen=True)
class IPRCut:
    """
    1-D cut of a point-like target's impulse response (IPR).

    Each cut is a 1-D cross-section of the target's impulse response through the
    center of the target along either azimuth or range. Both magnitude and phase
    information are stored.

    Parameters
    ----------
    index : (N,) numpy.ndarray
        A 1-D array of sample indices on which the impulse response function is
        sampled, relative to the approximate location of the peak.
    magnitude : (N,) numpy.ndarray
        The magnitude (linear) of the impulse response. Must have the same shape
        as `index`.
    phase : (N,) numpy.ndarray
        The phase of the impulse response, in radians. Must have the same shape
        as `index`.
    pslr : float
        The peak-to-sidelobe ratio (PSLR) of the impulse response, in dB.
    islr : float
        The integrated sidelobe ratio (ISLR) of the impulse response, in dB.
    """

    index: np.ndarray
    magnitude: np.ndarray
    phase: np.ndarray
    pslr: float
    islr: float

    def __post_init__(self) -> None:
        # Check that the `index` array is 1-D.
        if self.index.ndim != 1:
            raise ValueError(
                f"index must be a 1-D array, instead got ndim={self.index.ndim}"
            )

        # A helper function used to check that `magnitude` and `phase` each have the
        # same shape as `index`.
        def check_shape(name: str, shape: tuple[int, ...]) -> None:
            if shape != self.index.shape:
                raise ValueError(
                    f"Shape mismatch: index and {name} must have the same"
                    f" shape, instead got {shape} != {self.index.shape}"
                )

        check_shape("magnitude", self.magnitude.shape)
        check_shape("phase", self.phase.shape)


@dataclass
class CornerReflectorIPRCuts:
    """
    Azimuth & range impulse response (IPR) cuts for a single corner reflector.

    Parameters
    ----------
    id : str
        Unique corner reflector ID.
    observation_time : isce3.core.DateTime
        The UTC date and time that the corner reflector was observed by the
        radar (in zero-Doppler geometry).
    el_angle : float
        Antenna elevation angle of the corner reflector, in radians.
    az_cut : IPRCut
        The azimuth impulse response cut.
    rg_cut : IPRCut
        The range impulse response cut.
    """

    id: str
    observation_time: isce3.core.DateTime
    el_angle: float
    az_cut: IPRCut
    rg_cut: IPRCut


def get_pta_data_group(stats_h5: h5py.File) -> h5py.Group:
    """
    Get the 'pointTargetAnalyzer' data group in an RSLC QA STATS.h5 file.

    Returns the group in the input HDF5 file containing the outputs of the Point
    Target Analyzer (PTA) CalTool. The group name is expected to match the
    pattern '/science/{L|S}SAR/pointTargetAnalyzer/data/'.

    Parameters
    ----------
    stats_h5 : h5py.File
        The input HDF5 file. Must be a valid STATS.h5 file created by the RSLC
        QA workflow with the PTA tool enabled.

    Returns
    -------
    pta_data_group : h5py.Group
        The HDF5 Group containing the PTA tool output.

    Raises
    ------
    nisarqa.DatasetNotFoundError
        If not such group was found in the input HDF5 file.

    Notes
    -----
    Even if the PTA tool is enabled during RSLC QA, it still may not produce an
    output 'data' group in the STATS.h5 file if the RSLC product did not contain
    any valid corner reflectors. This is a requirement imposed on the PTA tool
    in order to simplify processing rules for the NISAR RSLC PGE.
    """
    for band in nisarqa.NISAR_BANDS:
        path = nisarqa.STATS_H5_PTA_DATA_GROUP % band
        if path in stats_h5:
            return stats_h5[path]

    raise nisarqa.DatasetNotFoundError(
        "Input STATS.h5 file did not contain a group matching"
        f" '{nisarqa.STATS_H5_PTA_DATA_GROUP % '(L|S)'}' "
    )


def get_ipr_cut_data(group: h5py.Group) -> Iterator[CornerReflectorIPRCuts]:
    """
    Extract corner reflector IPR cuts from a group in an RSLC QA STATS.h5 file.

    Get azimuth & range impulse response (IPR) cut data for each corner
    reflector in a single RSLC image raster (i.e. a single freq/pol pair).

    Parameters
    ----------
    group : h5py.Group
        The group in the RSLC QA STATS.h5 file containing the Point Target
        Analysis (PTA) results for a single frequency & polarization, e.g.
        '/science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/'.

    Yields
    ------
    cuts : CornerReflectorIPRCuts
        Azimuth and range cuts for a single corner reflector.
    """
    # Get 1-D array of corner reflector IDs and decode from
    # np.bytes_ -> np.str_.
    ids = group["cornerReflectorId"][()].astype(np.str_)

    # Total number of corner reflectors.
    num_corners = len(ids)

    # A helper function to check that elevationAngle/PSLR/ISLR datasets are
    # valid and return their contents. Each dataset should be 1-D array with
    # length equal to the number of corner reflectors.
    def ensure_valid_1d_dataset(dataset: h5py.Dataset) -> np.ndarray:
        # Check dataset shape.
        if dataset.shape != (num_corners,):
            raise ValueError(
                "Expected dataset to be a 1-D array with length equal to the"
                f" number of corner reflectors ({num_corners}), but instead got"
                f" {dataset.shape=} for dataset {dataset.name}"
            )

        # Return the contents.
        return dataset[()]

    # A helper function to check that each corner reflector IPR cut dataset is
    # valid and return its contents. Each dataset should contain an MxN array of
    # impulse response azimuth/range cuts, where M is the total number of corner
    # reflectors and N is the number of samples per cut. In general, N could be
    # different for azimuth vs. range cuts but M should be the same for all
    # datasets.
    def ensure_valid_2d_dataset(dataset: h5py.Dataset) -> np.ndarray:
        # The dataset must be 2-D and its number of rows must be equal to the
        # number of corner reflectors.
        if dataset.ndim != 2:
            raise ValueError(
                f"Expected dataset {dataset.name} to contain a 2-D array,"
                f" instead got ndim={dataset.ndim}"
            )
        if dataset.shape[0] != num_corners:
            raise ValueError(
                "Expected the length (the number of rows) of dataset"
                f" {dataset.name} to be equal to the number of corner"
                f" reflectors ({num_corners}), but instead got"
                f" len={dataset.shape[0]}"
            )

        # Return the contents.
        return dataset[()]

    observation_times = ensure_valid_1d_dataset(group["radarObservationDate"])
    el_angles = ensure_valid_1d_dataset(group["elevationAngle"])

    az_index = ensure_valid_2d_dataset(group["azimuthIRF/cut/index"])
    az_magnitude = ensure_valid_2d_dataset(group["azimuthIRF/cut/magnitude"])
    az_phase = ensure_valid_2d_dataset(group["azimuthIRF/cut/phase"])

    rg_index = ensure_valid_2d_dataset(group["rangeIRF/cut/index"])
    rg_magnitude = ensure_valid_2d_dataset(group["rangeIRF/cut/magnitude"])
    rg_phase = ensure_valid_2d_dataset(group["rangeIRF/cut/phase"])

    az_pslr = ensure_valid_1d_dataset(group["azimuthIRF/PSLR"])
    az_islr = ensure_valid_1d_dataset(group["azimuthIRF/ISLR"])

    rg_pslr = ensure_valid_1d_dataset(group["rangeIRF/PSLR"])
    rg_islr = ensure_valid_1d_dataset(group["rangeIRF/ISLR"])

    # Iterate over corner reflectors.
    for i in range(num_corners):
        id_ = ids[i]
        observation_time = isce3.core.DateTime(observation_times[i])
        el_angle = el_angles[i]
        az_cut = IPRCut(
            index=az_index[i],
            magnitude=az_magnitude[i],
            phase=az_phase[i],
            pslr=az_pslr[i],
            islr=az_islr[i],
        )
        rg_cut = IPRCut(
            index=rg_index[i],
            magnitude=rg_magnitude[i],
            phase=rg_phase[i],
            pslr=rg_pslr[i],
            islr=rg_islr[i],
        )
        yield CornerReflectorIPRCuts(
            id=id_,
            observation_time=observation_time,
            el_angle=el_angle,
            az_cut=az_cut,
            rg_cut=rg_cut,
        )


def plot_ipr_cuts(
    cuts: CornerReflectorIPRCuts,
    freq: str,
    pol: str,
    *,
    xlim: tuple[float, float] | None = (-15.0, 15.0),
) -> Figure:
    """
    Plot corner reflector impulse response cuts.

    Parameters
    ----------
    cuts : CornerReflectorIPRCuts
        The corner reflector azimuth & range impulse response cuts.
    freq : str
        The frequency sub-band of the RSLC image data (e.g. 'A', 'B').
    pol : str
        The polarization of the RSLC image data (e.g. 'HH', 'HV').
    xlim : (float, float) or None, optional
        X-axis limits of the plots. Defines the range of sample indices,
        relative to the approximate location of the impulse response peak, to
        display in each plot. Use a smaller range to include fewer sidelobes or
        a wider range to include more sidelobes. If None, uses Matplotlib's
        default limits. Defaults to (-15, 15).

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure.
    """
    # Create two side-by-side sub-plots to plot azimuth & range impulse response
    # cuts.
    figsize = nisarqa.FIG_SIZE_TWO_PLOTS_PER_PAGE
    fig, axes = plt.subplots(figsize=figsize, ncols=2)

    # Set figure title.
    fig.suptitle(f"Corner Reflector {cuts.id!r} (freq={freq!r}, pol={pol!r})")

    # Set sub-plot titles.
    axes[0].set_title("Azimuth Impulse Response")
    axes[1].set_title("Range Impulse Response")

    # Each sub-plot should have both a left-edge y-axis and a right-edge y-axis.
    # The two left-edge y-axes represent power, and are independent of the
    # right-edge y-axes which represent phase.
    raxes = [ax.twinx() for ax in axes]

    # Share both (left & right) y-axes between both sub-plots.
    axes[0].sharey(axes[1])
    raxes[0].sharey(raxes[1])

    # Set y-axis labels. Only label the left axis on the left sub-plot and only
    # label the right axis on the right sub-plot.
    axes[0].set_ylabel("Power (dB)")
    raxes[1].set_ylabel("Phase (rad)")

    # Get styling properties for power & phase curves. Power info should be most
    # salient -- use a thinner line for the phase plot.
    palette = nisarqa.SEABORN_COLORBLIND
    power_props = dict(color=palette[0], linewidth=2.0)
    phase_props = dict(color=palette[1], linewidth=1.0)

    for ax, rax, cut in zip(axes, raxes, [cuts.az_cut, cuts.rg_cut]):
        # Stack the power/phase plots so that power has higher precedence
        # (https://stackoverflow.com/a/30506077).
        ax.set_zorder(rax.get_zorder() + 1)
        ax.set_frame_on(False)

        # Set x-axis limits/label.
        ax.set_xlim(xlim)
        ax.set_xlabel("Rel. Sample Index")

        # Plot impulse response power, in dB.
        power_db = nisarqa.amp2db(cut.magnitude)
        lines = ax.plot(cut.index, power_db, label="power", **power_props)

        # Plot impulse response phase, in radians.
        lines += rax.plot(cut.index, cut.phase, label="phase", **phase_props)

        # Constrain the left y-axis (power) lower limit to 50dB below the peak.
        # Otherwise, the nulls tend to stretch the y-axis range too much. (Note
        # that the azimuth & range cuts both have the same peak value.)
        # Use `nanmax` since GSLC impulse response cuts may contain NaN values.
        peak_power = np.nanmax(power_db)
        ax.set_ylim([peak_power - 50.0, None])

        # Set right y-axis (phase) limits. Note: don't use fixed limits for the
        # left y-axis (power) -- let Matplotlib choose limits appropriate for
        # the data.
        rax.set_ylim([-np.pi, np.pi])

        # Add a text box in the upper-right corner of each plot with PSLR & ISLR
        # info.
        ax.text(
            x=0.97,
            y=0.97,
            s=f"PSLR = {cut.pslr:.3f} dB\nISLR = {cut.islr:.3f} dB",
            transform=ax.transAxes,
            horizontalalignment="right",
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.7),
        )

    # Add a legend to the left sub-plot.
    labels = [line.get_label() for line in lines]
    axes[0].legend(lines, labels, loc="upper left")

    # Get the datetime string in ISO 8601 format.
    # NOTE: `isce3.core.DateTime.isoformat()` currently produces output with
    # nanosecond precision, although this isn't necessarily guaranteed by the
    # API. If this changes in the future, we'll need to update some descriptions
    # in the output STATS.h5 file.
    obs_time_str = cuts.observation_time.isoformat()

    # Annotate figure with the radar observation time and elevation angle of the
    # corner reflector.
    fig.text(
        x=0.03, y=0.03, s=f"$\\bf{{Observation\ time\ (UTC):}}$\n{obs_time_str}"
    )
    el_angle_deg = np.rad2deg(cuts.el_angle)
    fig.text(
        x=0.53, y=0.03, s=f"$\\bf{{Elevation\ angle\ (deg):}}$\n{el_angle_deg}"
    )

    # Tighten figure layout to leave some margin at the bottom to avoid
    # overlapping annotations with axis labels.
    plt.tight_layout(rect=[0.0, 0.1, 1.0, 1.0])

    return fig


def add_pta_plots_to_report(stats_h5: h5py.File, report_pdf: PdfPages) -> None:
    """
    Add plots of PTA results to the RSLC/GSLC QA PDF report.

    Extract the Point Target Analysis (PTA) results from `stats_h5`, use them to
    generate plots of azimuth & range impulse response for each corner reflector
    in the scene and add them to QA PDF report.

    This function has no effect if the input STATS.h5 file did not contain a PTA
    data group (for example, in the case where the RSLC/GSLC product did not
    contain any corner reflectors).

    Parameters
    ----------
    stats_h5 : h5py.File
        The input RSLC or GSLC QA STATS.h5 file.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF report.
    """
    # Get the group in the HDF5 file containing the output from the PTA tool. If
    # the group does not exist, we assume that the RSLC product did not contain
    # any valid corner reflectors, so there is nothing to do here.
    try:
        pta_data_group = get_pta_data_group(stats_h5)
    except nisarqa.DatasetNotFoundError:
        return

    # Get valid frequency groups within `.../data/`. If the data group exists,
    # it must contain at least one frequency sub-group.
    freqs = get_valid_freqs(pta_data_group)
    if not freqs:
        raise RuntimeError(
            f"No frequency groups found in {pta_data_group.name}. The STATS.h5"
            " file is ill-formed."
        )

    for freq in freqs:
        freq_group = pta_data_group[f"frequency{freq}"]

        # Get polarization sub-groups. Each frequency group must contain at
        # least one polarization sub-group.
        pols = get_valid_pols(freq_group)
        if not pols:
            raise RuntimeError(
                f"No polarization groups found in {freq_group.name}. The"
                " STATS.h5 file is ill-formed."
            )

        for pol in pols:
            pol_group = freq_group[pol]

            # Loop over corner reflectors. Generate azimuth & range cut plots
            # for each and add them to the report.
            for cuts in get_ipr_cut_data(pol_group):
                fig = plot_ipr_cuts(cuts, freq, pol)
                report_pdf.savefig(fig)

                # Close the plot.
                plt.close(fig)


@dataclass
class CRPlotAxisAttrs:
    """
    Descriptive metadata used for labeling plots of corner reflector offsets.

    Each `CRPlotAxisAttrs` describes a single axis of a raster image in a NISAR
    product.

    Attributes
    ----------
    name : str
        The name of the axis (e.g. 'Easting', 'Northing', for geocoded images or
        'Slant Range', 'Azimuth' for range-Doppler images).
    spacing : float
        The signed pixel spacing of the image axis, in units described by the
        `units` attribute. (Note that North-up raster images in geodetic or
        projected coordinates typically have negative-valued y-spacing.)
    units : str
        The units of the image axis coordinate space (e.g. 'meters',
        'seconds').

    See Also
    --------
    get_cr_plot_axis_attrs
    """

    name: str
    spacing: float
    units: str

    def __post_init__(self) -> None:
        if self.spacing == 0.0:
            raise ValueError(
                f"pixel spacing must be nonzero; got {self.spacing}"
            )


def get_cr_plot_axis_attrs(
    slc: nisarqa.RSLC | nisarqa.GSLC,
    freq: str,
    pol: str,
) -> tuple[CRPlotAxisAttrs, CRPlotAxisAttrs]:
    """
    Get metadata describing each axis of a raster image.

    Parameters
    ----------
    slc : RSLC or GSLC
        The product containing the raster image dataset.
    freq : str
        The frequency sub-band of the raster image (e.g. 'A', 'B').
    pol : str
        The polarization of the raster image (e.g. 'HH', 'HV').

    Returns
    -------
    x_attrs, y_attrs : CRPlotAxisAttrs
        Descriptive metadata corresponding to the X & Y axes of the raster
        image.
    """
    if isinstance(slc, nisarqa.RSLC):
        x_attrs = CRPlotAxisAttrs(
            name="Slant Range",
            spacing=slc.get_slant_range_spacing(freq),
            units="meters",
        )
        y_attrs = CRPlotAxisAttrs(
            name="Azimuth",
            spacing=1e6 * slc.get_zero_doppler_time_spacing(),
            units="microsec.",
        )
    elif isinstance(slc, nisarqa.GSLC):
        with slc.get_raster(freq, pol) as raster:
            x_attrs = CRPlotAxisAttrs(
                name="Easting",
                spacing=raster.x_spacing,
                units="meters",
            )
            y_attrs = CRPlotAxisAttrs(
                name="Northing",
                spacing=raster.y_spacing,
                units="meters",
            )
    else:
        raise TypeError(
            "input slc must be of type `nisarqa.RSLC` or `nisarqa.GSLC`; got"
            f" `{type(slc)}`"
        )

    return x_attrs, y_attrs


def make_cr_offsets_scatterplot(
    ax: Axes,
    x_offsets: ArrayLike,
    y_offsets: ArrayLike,
    x_attrs: CRPlotAxisAttrs,
    y_attrs: CRPlotAxisAttrs,
) -> None:
    """
    Create a scatterplot of corner reflector offsets.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to add the plot to.
    x_offsets, y_offsets : (N,) array_like
        Arrays of X & Y (for geocoded datasets) or slant range & azimuth (for
        range-Doppler datasets) position offsets of each corner reflector w.r.t.
        the expected locations, in pixels. Must be 1-D arrays with length equal
        to the number of corner reflectors.
    x_attrs, y_attrs : CRPlotAxisAttrs
        Descriptive metadata corresponding to the X & Y axes of the raster image
        that the corner reflector measurements were derived from. Used for
        labeling the plot.
    """
    x_offsets = np.asanyarray(x_offsets)
    y_offsets = np.asanyarray(y_offsets)

    if (x_offsets.ndim != 1) or (y_offsets.ndim != 1):
        raise ValueError(
            f"x_offsets and y_offsets must be 1-D arrays; got {x_offsets.ndim=}"
            f" and {y_offsets.ndim=}"
        )

    if len(x_offsets) != len(y_offsets):
        raise ValueError(
            "size mismatch: x_offsets and y_offsets must have the same size;"
            f" got {len(x_offsets)=} and {len(y_offsets)=}"
        )

    # Plot x & y (range & azimuth) offsets.
    colors = itertools.cycle(nisarqa.SEABORN_COLORBLIND)
    for x_offset, y_offset in zip(x_offsets, y_offsets):
        ax.scatter(
            x=x_offset,
            y=y_offset,
            marker="x",
            s=100.0,
            color=next(colors),
        )

    # We want to center the subplot axes (like crosshairs). Move the left and
    # bottom spines to x=0 and y=0, respectively. Hide the top and right spines.
    ax.spines["left"].set_position(("data", 0.0))
    ax.spines["bottom"].set_position(("data", 0.0))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Draw arrows as black triangles at the end of each axis spine. Disable
    # clipping (clip_on=False) as the marker actually spills out of the axes.
    ax.plot(0.0, 0.0, "<k", transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(1.0, 0.0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0.0, 0.0, "vk", transform=ax.get_xaxis_transform(), clip_on=False)
    ax.plot(0.0, 1.0, "^k", transform=ax.get_xaxis_transform(), clip_on=False)

    # Update axis limits as follows:
    #  - Center the axis limits at the origin (0, 0)
    #  - Use the same axis limits for both x & y
    #  - Pad the axis limits by 25% (to make more room for axis labels)
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    xymax = 1.25 * np.max(np.abs([xmin, xmax, ymin, ymax]))
    ax.set_xlim([-xymax, xymax])
    ax.set_ylim([-xymax, xymax])

    # Force the aspect ratio to be 1:1.
    ax.set_aspect("equal")

    # Plot concentric circles with radii equal to each positive tick position
    # (except the outermost ticks, which are at or beyond the axis limits).
    inner_ticks = ax.get_xticks()[1:-1]
    for tick in filter(lambda x: x > 0.0, inner_ticks):
        circle = plt.Circle(
            xy=(0.0, 0.0),
            radius=tick,
            edgecolor=to_rgba("black", alpha=0.2),
            fill=False,
        )
        ax.add_patch(circle)

    # Add axis labels.
    # Depending on the orientation of the image, x-spacing or y-spacing
    # may be negative (e.g. y-spacing is negative in a North-up image)
    # so take the absolute value to get the magnitude of the spacing.
    xlabel = (
        f"{x_attrs.name}, pixels\n"
        f"1 pixel = {abs(x_attrs.spacing):.4g} {x_attrs.units}"
    )
    ylabel = (
        f"{y_attrs.name}, pixels\n"
        f"1 pixel = {abs(y_attrs.spacing):.4g} {y_attrs.units}"
    )
    ax.set_xlabel(xlabel, loc="right")
    ax.set_ylabel(ylabel, loc="top", rotation=0.0, verticalalignment="top")


def make_cr_offsets_stats_table(
    ax: Axes, offsets: ArrayLike, attrs: CRPlotAxisAttrs
) -> None:
    """
    Make a table of corner reflector offsets statistics.

    Compute summary statistics (mean, standard deviation, min, and max) of the
    corner reflector offsets corresponding to a single image axis. Make a table
    containing the results and add it to the specified axis.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to add the table to.
    offsets : array_like
        Array of position offsets of each corner reflector w.r.t. the expected
        locations along a single axis of the image, in pixels. Must be a 1-D
        array with length equal to the number of corner reflectors.
    attrs : CRPlotAxisAttrs
        Metadata describing the axis of the raster image that the `offsets`
        measurements were derived from.
    """
    # Row & column headers.
    row_labels = ["Mean", "Std. Dev.", "Min", "Max"]
    col_labels = ["in pixels", f"in {attrs.units}"]

    # Get CR offsets in pixels and in real time/space coordinates.
    offsets = np.asanyarray(offsets)
    offsets = np.vstack([offsets, attrs.spacing * offsets])

    # Get CR offset statistics.
    # Note that we don't expect NaN values -- `offsets` should only contain
    # valid CR measurements. We deliberately don't use e.g. `np.nanmean()` to
    # avoid hiding NaN values in the PDF report.
    stats = np.vstack(
        [
            np.mean(offsets, axis=1),
            np.std(offsets, axis=1),
            np.min(offsets, axis=1),
            np.max(offsets, axis=1),
        ]
    )

    # Add the table to the specified axes.
    ax.table(
        cellText=stats,
        rowLabels=row_labels,
        rowColours=["lightgray"] * len(row_labels),
        colLabels=col_labels,
        colColours=["lightgray"] * len(col_labels),
        loc="center",
    )

    # Hide the axis itself.
    ax.axis("off")

    # Add table title.
    # XXX: There doesn't seem to be a good way to dynamically position the title
    # at the top of the table, so the y-position is hard-coded based on the
    # table size and may need to be adjusted if the table contents change.
    ax.set_title(f"{attrs.name} CR Offsets", y=0.75)


def make_cr_offsets_figure(
    x_offsets: ArrayLike,
    y_offsets: ArrayLike,
    x_attrs: CRPlotAxisAttrs,
    y_attrs: CRPlotAxisAttrs,
    freq: str,
    pol: str,
) -> Figure:
    """
    Make a plot of corner reflector position errors.

    Parameters
    ----------
    x_offsets, y_offsets : (N,) array_like
        Arrays of X & Y (for geocoded datasets) or slant range & azimuth (for
        range-Doppler datasets) position offsets of each corner reflector w.r.t.
        the expected locations, in pixels. Must be 1-D arrays with length equal
        to the number of corner reflectors.
    x_attrs, y_attrs : CRPlotAxisAttrs
        Descriptive metadata corresponding to the X & Y axes of the raster image
        that the corner reflector measurements were derived from. Used for
        labeling the plot.
    freq : str
        The frequency sub-band of the raster image that corner reflector
        measurements were derived from (e.g. 'A', 'B').
    pol : str
        The polarization of the raster image that corner reflector measurements
        were derived from (e.g. 'HH', 'HV').

    Returns
    -------
    fig : matplotlib.figure.Figure
        The created figure.
    """
    # Make a figure with 3 sub-plots: a scatterplot of corner reflector offsets
    # on the left, and two vertically stacked tables of summary statistics on
    # the right.
    fig, axes = plt.subplot_mosaic(
        [
            ["offsets_plot", "y_stats_table"],
            ["offsets_plot", "x_stats_table"],
        ],
        figsize=nisarqa.FIG_SIZE_TWO_PLOTS_PER_PAGE,
    )

    # Add the corner reflector offsets scatterplot.
    make_cr_offsets_scatterplot(
        ax=axes["offsets_plot"],
        x_offsets=x_offsets,
        y_offsets=y_offsets,
        x_attrs=x_attrs,
        y_attrs=y_attrs,
    )

    # Add tables of corner reflector offset statistics to the figure.
    make_cr_offsets_stats_table(axes["y_stats_table"], y_offsets, y_attrs)
    make_cr_offsets_stats_table(axes["x_stats_table"], x_offsets, x_attrs)

    # Add figure title.
    title = (
        f"Corner Reflector (CR) {x_attrs.name}/{y_attrs.name} Position Error\n"
        f"freq={freq!r}, pol={pol!r}"
    )
    fig.suptitle(title)

    # Update figure layout to increase margins around the borders.
    fig.tight_layout(pad=2.0)

    return fig


def plot_cr_offsets_to_pdf(
    slc: nisarqa.RSLC | nisarqa.GSLC, stats_h5: h5py.File, report_pdf: PdfPages
) -> None:
    """
    Plot RSLC/GSLC corner reflector geometric position errors to PDF.

    Extract the Point Target Analysis (PTA) results from `stats_h5`, use them to
    generate plots of azimuth & range (for RSLC) or easting & northing (for
    GSLC) peak offsets for each corner reflector in the scene and add them to
    QA PDF report. A single figure is generated for each available
    frequency/polarization pair.

    This function has no effect if the input STATS.h5 file did not contain a PTA
    data group (for example, in the case where the input product did not contain
    any corner reflectors).

    Parameters
    ----------
    slc : RSLC or GSLC
        The NISAR product that the PTA results were generated from.
    stats_h5 : h5py.File
        The input RSLC/GSLC QA STATS.h5 file.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF report.
    """
    # Get the names of the groups in the STATS.h5 file that contain corner
    # reflector peak offsets data. The group names correspond to the axes of the
    # RSLC/GSLC image data.
    if isinstance(slc, nisarqa.RSLC):
        assert not isinstance(slc, nisarqa.GSLC)
        x_axis = "range"
        y_axis = "azimuth"
    elif isinstance(slc, nisarqa.GSLC):
        x_axis = "x"
        y_axis = "y"
    else:
        raise TypeError(
            "Input product must be RSLC or GSLC, instead got"
            f" {slc.product_type}"
        )

    # Get the group in the HDF5 file containing the output from the PTA tool. If
    # the group does not exist, we assume that the RSLC product did not contain
    # any valid corner reflectors, so there is nothing to do here.
    try:
        pta_data_group = get_pta_data_group(stats_h5)
    except nisarqa.DatasetNotFoundError:
        return

    # Get valid frequency groups within `.../data/`. If the data group exists,
    # it must contain at least one frequency sub-group.
    freqs = get_valid_freqs(pta_data_group)
    if not freqs:
        raise RuntimeError(
            f"No frequency groups found in {pta_data_group.name}. The STATS.h5"
            " file is ill-formed."
        )

    for freq in freqs:
        freq_group = pta_data_group[f"frequency{freq}"]

        # Get polarization sub-groups. Each frequency group must contain at
        # least one polarization sub-group.
        pols = get_valid_pols(freq_group)
        if not pols:
            raise RuntimeError(
                f"No polarization groups found in {freq_group.name}. The"
                " STATS.h5 file is ill-formed."
            )

        for pol in pols:
            pol_group = freq_group[pol]

            # Extract range & azimuth (easting & northing) peak offsets data
            # from STATS.h5.
            x_offsets = pol_group[f"{x_axis}Position/peakOffset"]
            y_offsets = pol_group[f"{y_axis}Position/peakOffset"]

            # Check that both datasets contain 1-D arrays with the same shape.
            for dataset in [x_offsets, y_offsets]:
                if dataset.ndim != 1:
                    raise ValueError(
                        f"Expected dataset {dataset.name} to contain a 1-D"
                        f" array, instead got ndim={dataset.ndim}"
                    )
            if x_offsets.shape != y_offsets.shape:
                raise ValueError(
                    f"Corner reflector peak offsets in {x_axis} and {y_axis}"
                    " must have the same shape, instead got"
                    f" {x_axis}_offsets.shape={x_offsets.shape} and"
                    f" {y_axis}_offsets.shape={y_offsets.shape}"
                )

            # Get descriptive metadata corresponding to the X & Y axes of the
            # raster image.
            x_attrs, y_attrs = get_cr_plot_axis_attrs(slc, freq, pol)

            # Make a plot of corner reflector position offsets for the current
            # freq/pol and append it to the PDF report.
            fig = make_cr_offsets_figure(
                x_offsets=x_offsets,
                y_offsets=y_offsets,
                x_attrs=x_attrs,
                y_attrs=y_attrs,
                freq=freq,
                pol=pol,
            )
            report_pdf.savefig(fig)

            # Close the figure.
            plt.close(fig)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
