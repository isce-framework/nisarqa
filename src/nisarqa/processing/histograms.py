from __future__ import annotations

from collections.abc import Callable

import h5py
import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from .plotting_utils import add_hist_to_axis
from .processing_utils import clip_array

objects_to_skip = nisarqa.get_all(name=__name__)


def generate_histogram_to_axes_and_h5(
    raster: nisarqa.RadarRaster | nisarqa.GeoRaster,
    ax: mpl.axes.Axes,
    stats_h5: h5py.File,
    *,
    xlabel=str,
    include_axes_title: bool = True,
    percentile_for_clipping: tuple[float, float] | None = None,
    data_prep_func: Callable | None = None,
) -> None:
    """
    Compute histogram and save to PDF and STATS HDF5 file.

    Parameters
    ----------
    raster : nisarqa.RadarRaster or nisarqa.GeoRaster
        *Raster to generate the histogram for. Non-finite values are ignored.
    ax : matplotlib.axes.Axes
        Axes object.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    xlabel : str
        Label to use for the x-axis histogram bins, not including units.
            Correct: "InSAR Phase"
            Wrong: "InSAR Phase (radians)"
        The units for this label will be set per `raster.units`.
    include_axes_title : bool, optional
        True to include a title on the axes itself; False to exclude it.
        Defaults to True.
    percentile_for_clipping : None or pair of float, optional
        Percentile range that the finite raster values will be clipped to prior
        to creating the histogram. If None, no clipping will occur.
        Must be in range [0.0, 100.0] or None. Defaults to None.
    data_prep_func : Callable or None, optional
        Function to transform the raster data before applying
        `percentile_for_clipping` and before computing
        the histogram counts. For example, this function could be
        `numpy.angle` to convert complex values into float values,
        or it could be `numpy.sqrt` for converting variances
        into standard deviation.
        If `None`, then histogram will be computed on the raster as-is,
        and no pre-processing of the data will occur.
        Defaults to None.
    """
    # Get histogram probability density
    arr = np.asanyarray(raster.data)
    arr = arr[np.isfinite(arr)]
    if data_prep_func is not None:
        arr = data_prep_func(arr)

    if percentile_for_clipping is not None:
        arr = clip_array(arr=arr, percentile_range=percentile_for_clipping)

    # Fix the number of bins to keep the output file size small
    # NOTE: InSAR phase histograms were observed to have a spike at 0 radians,
    # likely due to imperfect overlap between the reference and secondary
    # SLC footprints.
    # This histogram feature may be masked if the number of bins is too low.
    density, bin_edges = np.histogram(arr, bins=200, density=True)

    # Append to Axes
    if include_axes_title:
        # Get the layer name. (`*raster.name` has a format
        # like "RUNW_L_A_pixelOffsets_HH_slantRangeOffset". We need to
        # get the last component, e.g. "slantRangeOffset".)
        ax_title = raster.name.split("_")[-1]
    else:
        ax_title = None

    add_histogram_to_axes(
        ax=ax,
        density=density,
        bin_edges=bin_edges,
        xlabel=xlabel,
        units=raster.units,
        axes_title=ax_title,
        percentile_for_clipping=percentile_for_clipping,
    )

    # Save to stats HDF5
    add_histogram_data_to_h5(
        stats_h5=stats_h5,
        stats_h5_group_path=raster.stats_h5_group_path,
        density=density,
        bin_edges=bin_edges,
        units=raster.units,
    )


def add_histogram_to_axes(
    density: np.ndarray,
    bin_edges: np.ndarray,
    ax: mpl.axes.Axes,
    *,
    xlabel: str,
    units: str,
    axes_title: str | None = None,
    percentile_for_clipping: tuple[float, float] | None = None,
) -> None:
    """
    Plot a histogram on a Matplotlib Axes.

    Parameters
    ----------
    density: np.ndarray
        The normalized density values for the histogram.
    bin_edges: np.ndarray
        The bin edges for the histogram.
    ax : matplotlib.axes.Axes
        Axes object to plot the histogram on.
    xlabel : str
        Label to use for the x-axis histogram bins, not including units.
            Correct: "InSAR Phase"
            Wrong: "InSAR Phase (radians)"
        The units for this label will be set per `units`.
    units : str
        Units which will be used for labeling axes.
        The x-axis bins will be labeled with units of "`units`", and
        the y-axis densities will be labeled with units of "1/`units`".
    axes_title : str or None, optional
        Title for the Axes. If None, no title will be added. Defaults to None.
    percentile_for_clipping : None or pair of float, optional
        Percentile range that the finite raster values will be clipped to prior
        to creating the histogram. If None, no clipping will occur.
        Must be in range [0.0, 100.0] or None. Defaults to None.
    """
    # Use custom cycler for accessibility
    ax.set_prop_cycle(nisarqa.CUSTOM_CYCLER)

    # Add backscatter histogram density to the figure
    add_hist_to_axis(
        ax,
        counts=density,
        edges=bin_edges,
        label=None,
    )

    # Construct the axes title
    final_axes_title = None
    if axes_title is not None:
        final_axes_title = axes_title
    if percentile_for_clipping is not None:
        txt = (
            f"clipped to percentile range"
            f" [{percentile_for_clipping[0]}, {percentile_for_clipping[1]}]"
        )
        if axes_title is None:
            final_axes_title = txt
        else:
            final_axes_title += f"\n{txt}"
    ax.set_title(final_axes_title, fontsize=10)

    if units == "1":
        units = "unitless"
    ax.set_xlabel(f"{xlabel} ({units})")
    ax.set_ylabel(f"Density (1/{units})")

    # TODO: For RSLC/GSLC/GCOV, the top limit floats. Do the same for InSAR?
    # Let the top limit float
    ax.set_ylim(bottom=0.0)
    ax.grid(visible=True)


def add_histogram_data_to_h5(
    density: np.ndarray,
    bin_edges: np.ndarray,
    stats_h5: h5py.File,
    *,
    units: str,
    stats_h5_group_path: str,
) -> None:
    """
    Add histogram data to the STATS HDF5 file.

    Parameters
    ----------
    density : numpy.ndarray
        The normalized density values for the histogram.
    bin_edges : numpy.ndarray
        The bin edges for the histogram.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    units : str
        Units which will be used for labeling axes.
        The bin edges will be denoted with units of "`units`", and
        the densities will be denoted with units of "1/`units`".
    stats_h5_group_path : str
        Path in the STATS.h5 file for the group where all metrics and
        statistics re: this raster should be saved.
        If calling function has a *Raster, suggest using the *Raster's
        `stats_h5_group_path` attribute.
        Examples:
            RSLC/GSLC/GCOV: "/science/LSAR/QA/data/frequencyA/HH"
            RUNW/GUNW: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset"
            ROFF/GOFF: "/science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset"
    """
    # Save density values to stats.h5 file
    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=stats_h5_group_path,
        ds_name="histogramDensity",
        ds_data=density,
        ds_units=f"1/{units}",
        ds_description="Normalized density of the histogram",
    )

    # Save bins to stats.h5 file
    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=stats_h5_group_path,
        ds_name="histogramBins",
        ds_data=bin_edges,
        ds_units=units,
        ds_description="Histogram bin edges",
    )


def process_single_histogram(
    raster: nisarqa.GeoRaster | nisarqa.RadarRaster,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
    *,
    xlabel: str,
    name_of_histogram: str,
    percentile_for_clipping: tuple[float, float] | None = None,
) -> None:
    """
    Make histogram of a *Raster; plot to single PDF page and add metrics to HDF5.

    Parameters
    ----------
    raster : nisarqa.GeoRaster | nisarqa.RadarRaster
        *Raster to generate the histogram for.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the histogram to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    xlabel : str
        Label to use for the x-axis histogram bins, not including units.
            Correct: "InSAR Phase"
            Wrong: "InSAR Phase (radians)"
        The units for this label will be set per `raster.units`.
    name_of_histogram : str
        What is this histogram of? This string will be used in the main title
        of the PDF page, like this: "Histogram of <name_of_histogram>".
    percentile_for_clipping : None or pair of float, optional
        Percentile range that the finite raster values will be clipped to prior
        to creating the histogram. If None, no clipping will occur.
        Must be in range [0.0, 100.0] or None. Defaults to None.

    Warnings
    --------
    The entire input array will be read into memory and processed.
    Only use this function for small datasets.
    """
    fig, ax = plt.subplots(
        ncols=1,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE,
    )

    # Form the plot title
    title = f"Histogram of {name_of_histogram}\n{raster.name}"
    fig.suptitle(title)

    generate_histogram_to_axes_and_h5(
        raster=raster,
        ax=ax,
        stats_h5=stats_h5,
        xlabel=xlabel,
        include_axes_title=False,
        percentile_for_clipping=percentile_for_clipping,
    )

    # Save complete plots to graphical summary PDF file
    report_pdf.savefig(fig)

    # Close figure
    plt.close(fig)


def process_two_histograms(
    raster1: nisarqa.GeoRaster | nisarqa.RadarRaster,
    raster2: nisarqa.GeoRaster | nisarqa.RadarRaster,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
    *,
    name_of_histogram_pair: str,
    r1_xlabel: str,
    r2_xlabel: str,
    r1_clip_percentile: tuple[float, float] | None = None,
    r2_clip_percentile: tuple[float, float] | None = None,
    sharey: bool = False,
    r1_data_prep_func: Callable | None = None,
    r2_data_prep_func: Callable | None = None,
) -> None:
    """
    Make histograms of two *Rasters; plot to PDF page and add metrics to HDF5.

    The histograms of the two rasters will be plotted side-by-side on a
    single PDF page.

    Parameters
    ----------
    raster1, raster2 : nisarqa.GeoRaster | nisarqa.RadarRaster
        *Rasters to generate the histograms for. Non-finite values are ignored.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the histogram plots to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    name_of_histogram_pair : str
        What are these histograms of? This string will be used in the main title
        of the PDF page, like this: "Histograms of <name_of_histogram_pair>".
    r1_xlabel, r2_xlabel : str
        Label to use for the x-axis histogram bins for `raster1` and `raster2`
        (respectively), not including units.
            Correct: "InSAR Phase"
            Wrong: "InSAR Phase (radians)"
        The units for this label will be set per `raster.units`.
    r1_clip_percentile, r2_clip_percentile : None or pair of float, optional
        Percentile range that the finite raster values will be clipped to prior
        to creating the histogram for `raster1` and `raster2`, respectively.
        If None, no clipping will occur. Must be in range [0.0, 100.0] or None.
        Defaults to None.
    sharey : bool, optional
        True to have the plots share a y-axes; False otherwise.
    r1_data_prep_func, r2_data_prep_func : Callable or None, optional
        Function to transform the raster1 and raster2 (respectively) data
        before clipping outliers and before computing
        the histogram counts. For example, this function could be
        `numpy.angle` to convert complex values into float values,
        or it could be `numpy.sqrt` for converting variances
        into standard deviation.
        If `None`, then histogram will be computed on the rasters as-is,
        and no pre-processing of the data will occur.
        Defaults to None.

    Warnings
    --------
    The entire input arrays will be read into memory and processed.
    Only use this function for small datasets.
    """
    fig, (ax1, ax2) = plt.subplots(
        ncols=2,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_TWO_PLOTS_PER_PAGE,
        sharey=sharey,
    )

    # Construct title for the overall PDF page. (`*raster.name` has a format
    # like "RUNW_L_A_pixelOffsets_HH_slantRangeOffset". We need to
    # remove the final layer name of e.g. "_slantRangeOffset".)
    name = "_".join(raster1.name.split("_")[:-1])
    title = f"Histograms of {name_of_histogram_pair}\n{name}"
    fig.suptitle(title)

    generate_histogram_to_axes_and_h5(
        raster=raster1,
        ax=ax1,
        stats_h5=stats_h5,
        xlabel=r1_xlabel,
        include_axes_title=True,
        percentile_for_clipping=r1_clip_percentile,
        data_prep_func=r1_data_prep_func,
    )

    generate_histogram_to_axes_and_h5(
        raster=raster2,
        ax=ax2,
        stats_h5=stats_h5,
        xlabel=r2_xlabel,
        include_axes_title=True,
        percentile_for_clipping=r2_clip_percentile,
        data_prep_func=r2_data_prep_func,
    )

    if sharey:
        ax2.set_ylabel("")

    # Save complete plots to graphical summary PDF file
    report_pdf.savefig(fig)

    # Close figure
    plt.close(fig)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
