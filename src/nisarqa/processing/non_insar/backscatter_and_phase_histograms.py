from __future__ import annotations

import h5py
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from ..plotting_utils import add_hist_to_axis

objects_to_skip = nisarqa.get_all(name=__name__)


@nisarqa.log_function_runtime
def process_backscatter_and_phase_histograms(
    product: nisarqa.NonInsarProduct,
    params: nisarqa.HistogramParamGroup,
    stats_h5: h5py.File,
    report_pdf: PdfPages,
    plot_title_prefix: str = "Backscatter Coefficient",
    input_raster_represents_power: bool = False,
):
    """
    Generate the Backscatter and Phase Histograms and save their plots
    to the graphical summary PDF file.

    Backscatter histogram will be computed in decibel units.
    Phase histogram defaults to being computed in radians,
    configurable to be computed in degrees by setting
    `params.phs_in_radians` to False.
    NaN values will be excluded from Histograms.

    Parameters
    ----------
    product : nisarqa.NonInsarProduct
        Input NISAR product
    params : HistogramParams
        A structure containing the parameters for processing
        and outputting the backscatter and phase histograms.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the backscatter image plot to
    plot_title_prefix : str, optional
        Prefix for the title of the backscatter plots.
        Suggestions: "RSLC Backscatter Coefficient (beta-0)" or
        "GCOV Backscatter Coefficient (gamma-0)".
        Defaults to "Backscatter Coefficient".
    input_raster_represents_power : bool, optional
        The input dataset rasters associated with these histogram parameters
        should have their pixel values represent either power or root power.
        If `True`, then QA SAS assumes the input data already represents
        power and uses the pixels' magnitudes for computations.
        If `False`, then QA SAS assumes the input data represents root power
        aka magnitude and will handle the full computation to power using
        the formula:  power = abs(<magnitude>)^2 .
        Defaults to False (root power).
    """

    # Generate and store the histograms

    for freq in product.freqs:
        with nisarqa.log_runtime(
            "`generate_backscatter_image_histogram_single_freq` for"
            f" Frequency {freq}"
        ):
            generate_backscatter_image_histogram_single_freq(
                product=product,
                freq=freq,
                params=params,
                stats_h5=stats_h5,
                report_pdf=report_pdf,
                input_raster_represents_power=input_raster_represents_power,
                plot_title_prefix=plot_title_prefix,
            )

        with nisarqa.log_runtime(
            f"`generate_phase_histogram_single_freq` for Frequency {freq}"
        ):
            generate_phase_histogram_single_freq(
                product=product,
                freq=freq,
                params=params,
                stats_h5=stats_h5,
                report_pdf=report_pdf,
            )


def generate_backscatter_image_histogram_single_freq(
    product: nisarqa.NonInsarProduct,
    freq: str,
    params: nisarqa.HistogramParamGroup,
    stats_h5: h5py.File,
    report_pdf: PdfPages,
    plot_title_prefix: str = "Backscatter Coefficient",
    input_raster_represents_power: bool = False,
) -> None:
    """
    Generate Backscatter Image Histogram for a single frequency.

    The histogram's plot will be appended to the graphical
    summary file `report_pdf`, and its data will be
    stored in the statistics .h5 file `stats_h5`.
    Backscatter histogram will be computed in decibel units.

    Parameters
    ----------
    product : nisarqa.NonInsarProduct
        Input NISAR product
    freq : str
        Frequency name for the histograms to be processed,
        e.g. 'A' or 'B'
    params : HistogramParamGroup
        A structure containing the parameters for processing
        and outputting the histograms.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the backscatter image plot to
    plot_title_prefix : str
        Prefix for the title of the backscatter plots.
        Suggestions: "RSLC Backscatter Coefficient (beta-0)" or
        "GCOV Backscatter Coefficient (gamma-0)"
        Defaults to "Backscatter Coefficient"
    input_raster_represents_power : bool, optional
        The input dataset rasters associated with these histogram parameters
        should have their pixel values represent either power or root power.
        If `True`, then QA SAS assumes the input data already represents
        power and uses the pixels' magnitudes for computations.
        If `False`, then QA SAS assumes the input data represents root power
        aka magnitude and will handle the full computation to power using
        the formula:  power = abs(<magnitude>)^2 .
        Defaults to False (root power).
    """
    log = nisarqa.get_logger()

    log.info(f"Generating Backscatter Image Histograms for Frequency {freq}...")

    # Open one figure+axes.
    # Each band+frequency will have a distinct plot, with all of the
    # polarization images for that setup plotted together on the same plot.
    fig, ax = plt.subplots(
        nrows=1, ncols=1, figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE
    )

    # Use custom cycler for accessibility
    ax.set_prop_cycle(nisarqa.CUSTOM_CYCLER)

    def img_prep(arr):
        # Convert to backscatter.
        # For Backscatter Histogram, do not mask out zeros.
        power = (
            np.abs(arr)
            if input_raster_represents_power
            else nisarqa.arr2pow(arr)
        )

        with nisarqa.ignore_runtime_warnings():
            # This line throws these warnings:
            #   "RuntimeWarning: divide by zero encountered in log10"
            # when there are zero values. Ignore those warnings.
            power = nisarqa.pow2db(power)

        return power

    for pol_name in product.get_pols(freq=freq):
        with product.get_raster(freq=freq, pol=pol_name) as pol_data:
            # Get histogram probability density
            with nisarqa.log_runtime(
                f"`compute_histogram_by_tiling` for backscatter histogram for"
                f" Frequency {freq}, Polarization {pol_name} with"
                f" raster shape {pol_data.data.shape} using decimation ratio"
                f" {params.decimation_ratio} and tile shape {params.tile_shape}"
            ):
                hist_density = nisarqa.compute_histogram_by_tiling(
                    arr=pol_data.data,
                    arr_name=f"{pol_data.name} backscatter",
                    bin_edges=params.backscatter_bin_edges,
                    data_prep_func=img_prep,
                    density=True,
                    decimation_ratio=params.decimation_ratio,
                    tile_shape=params.tile_shape,
                )

            # Save to stats.h5 file
            grp_path = f"{nisarqa.STATS_H5_QA_FREQ_GROUP}/{pol_name}/" % (
                product.band,
                freq,
            )

            # Save Backscatter Histogram Counts to HDF5 file
            backscatter_units = params.get_units_from_hdf5_metadata(
                "backscatter_bin_edges"
            )

            nisarqa.create_dataset_in_h5group(
                h5_file=stats_h5,
                grp_path=grp_path,
                ds_name="backscatterHistogramDensity",
                ds_data=hist_density,
                ds_units=f"1/{backscatter_units}",
                ds_description=(
                    "Normalized density of the backscatter image histogram"
                ),
            )

            # Add backscatter histogram density to the figure
            add_hist_to_axis(
                ax,
                counts=hist_density,
                edges=params.backscatter_bin_edges,
                label=pol_name,
            )

    # Label the backscatter histogram Figure
    title = (
        f"{plot_title_prefix} Histograms\n{product.band}-band Frequency {freq}"
    )
    ax.set_title(title)

    ax.legend(loc="upper right")
    ax.set_xlabel(f"Backscatter ({backscatter_units})")
    ax.set_ylabel(f"Density (1/{backscatter_units})")

    # Per ADT, let the top limit float for Backscatter Histogram
    ax.set_ylim(bottom=0.0)
    ax.grid(visible=True)

    # Save complete plots to graphical summary PDF file
    report_pdf.savefig(fig)

    # Close figure
    plt.close(fig)

    log.info(f"Backscatter Image Histograms for Frequency {freq} complete.")


def generate_phase_histogram_single_freq(
    product: nisarqa.NonInsarProduct,
    freq: str,
    params: nisarqa.HistogramParamGroup,
    stats_h5: h5py.File,
    report_pdf: PdfPages,
) -> None:
    """
    Generate Phase Histograms for a single frequency.

    The histograms' plots will be appended to the graphical
    summary file `report_pdf`, and their data will be
    stored in the statistics .h5 file `stats_h5`.
    Phase histogram defaults to being computed in radians,
    configurable to be computed in degrees per `params.phs_in_radians`.
    NOTE: Only if the dtype of a polarization raster is complex-valued
    (e.g. complex32) will it be included in the Phase histogram(s).
    NaN values will be excluded from the histograms.

    Parameters
    ----------
    product : nisarqa.NonInsarProduct
        The input NISAR product
    freq : str
        Frequency name for the histograms to be processed,
        e.g. 'A' or 'B'
    params : HistogramParamGroup
        A structure containing the parameters for processing
        and outputting the backscatter and phase histograms.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the backscatter image plot to
    """
    log = nisarqa.get_logger()

    band = product.band

    # flag for if any phase histogram densities are generated
    # (We expect this flag to be set to True if any polarization contains
    # phase information. But for example, if a GCOV product only has
    # on-diagonal terms which are real-valued and lack phase information,
    # this will remain False.)
    save_phase_histogram = False

    log.info(f"Generating Phase Histograms for Frequency {freq}...")

    # Open one figure+axes.
    # Each band+frequency will have a distinct plot, with all of the
    # polarization images for that setup plotted together on the same plot.
    fig, ax = plt.subplots(
        nrows=1, ncols=1, figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE
    )

    # Use custom cycler for accessibility
    ax.set_prop_cycle(nisarqa.CUSTOM_CYCLER)

    def img_prep(arr):
        # Remove zero values (and nans) in case of 0 magnitude vectors, etc.
        # Note: There will be no need to clip phase values; the output of
        # np.angle() is always in the range (-pi, pi] (or (-180, 180]).
        if params.phs_in_radians:
            return np.angle(arr[np.abs(arr) >= 1.0e-05], deg=False)
        else:
            # phase in degrees
            return np.angle(arr[np.abs(arr) >= 1.0e-05], deg=True)

    for pol_name in product.get_pols(freq=freq):
        with product.get_raster(freq=freq, pol=pol_name) as pol_data:
            # Only create phase histograms for complex datasets. Examples of
            # complex datasets include RSLC, GSLC, and GCOV off-diagonal rasters.
            if not pol_data.is_complex:
                continue

            save_phase_histogram = True

            with nisarqa.log_runtime(
                f"`compute_histogram_by_tiling` for phase histogram for"
                f" Frequency {freq}, Polarization {pol_name} with"
                f" raster shape {pol_data.data.shape} using decimation ratio"
                f" {params.decimation_ratio} and tile shape {params.tile_shape}"
            ):
                # Get histogram probability densities
                hist_density = nisarqa.compute_histogram_by_tiling(
                    arr=pol_data.data,
                    arr_name=f"{pol_data.name} phase",
                    bin_edges=params.phs_bin_edges,
                    data_prep_func=img_prep,
                    density=True,
                    decimation_ratio=params.decimation_ratio,
                    tile_shape=params.tile_shape,
                )

            # Save to stats.h5 file
            freq_path = nisarqa.STATS_H5_QA_FREQ_GROUP % (band, freq)
            grp_path = f"{freq_path}/{pol_name}/"

            phs_units = params.get_units_from_hdf5_metadata("phs_bin_edges")

            nisarqa.create_dataset_in_h5group(
                h5_file=stats_h5,
                grp_path=grp_path,
                ds_name="phaseHistogramDensity",
                ds_data=hist_density,
                ds_units=f"1/{phs_units}",
                ds_description="Normalized density of the phase histogram",
            )

            # Add phase histogram density to the figure
            add_hist_to_axis(
                ax,
                counts=hist_density,
                edges=params.phs_bin_edges,
                label=pol_name,
            )

    # Label and output the Phase Histogram Figure
    if save_phase_histogram:
        ax.set_title(f"{band}SAR Frequency {freq} Phase Histograms")
        ax.legend(loc="upper right")
        ax.set_xlabel(f"Phase ({phs_units})")
        ax.set_ylabel(f"Density (1/{phs_units})")
        if params.phase_histogram_y_axis_range is not None:
            # Fix bottom and/or top of y axis interval
            kwargs = {}
            if params.phase_histogram_y_axis_range[0] is not None:
                kwargs["bottom"] = params.phase_histogram_y_axis_range[0]
            if params.phase_histogram_y_axis_range[1] is not None:
                kwargs["top"] = params.phase_histogram_y_axis_range[1]
            ax.set_ylim(**kwargs)

        ax.grid(visible=True)

        # Save complete plots to graphical summary PDF file
        report_pdf.savefig(fig)

        # Close figure
        plt.close(fig)
    else:
        # Remove unused dataset from STATS.h5 because no phase histogram was
        # generated.

        # Get param attribute for the extraneous group
        metadata = nisarqa.HistogramParamGroup.get_attribute_metadata(
            "phs_bin_edges"
        )

        # Get the instance of the HDF5Attrs object for this parameter
        hdf5_attrs_instance = metadata["hdf5_attrs_func"](params)

        # Form the path in output STATS.h5 file to the group to be deleted
        path = hdf5_attrs_instance.group_path % band
        path += f"/{hdf5_attrs_instance.name}"

        # Delete the unnecessary dataset
        if path in stats_h5:
            del stats_h5[path]

    log.info(f"Phase Histograms for Frequency {freq} complete.")


__all__ = nisarqa.get_all(__name__, objects_to_skip)
