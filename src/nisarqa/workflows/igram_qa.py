from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, Optional, Union, overload

import h5py
import isce3
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


def igram_qa(
    root_params: (
        nisarqa.RIFGRootParamGroup
        | nisarqa.RUNWRootParamGroup
        | nisarqa.GUNWRootParamGroup
    ),
    verbose: bool = False,
) -> None:
    """
    Perform verification checks and quality assurance on a NISAR InSAR product.

    This is the main function for running the entire QA workflow for one of
    a NISAR RIFG, RUNW, or GUNW product.
    It will run based on the options supplied in the input parameters.

    Parameters
    ----------
    root_params : nisarqa.RIFGRootParamGroup or nisarqa.RUNWRootParamGroup
                        or nisarqa.GUNWRootParamGroup
        Input parameters to run this QA SAS. The type of the input product
        to be verified (RIFG, RUNW, or GUNW) will be inferred from the type
        of this argument.
    verbose : bool, optional
        True to stream log messages to console (stderr) in addition to the
        log file. False to only stream to the log file. (Initial log messages
        during setup will stream to console regardless.) Defaults to False.
    """
    if isinstance(root_params, nisarqa.RIFGRootParamGroup):
        product_type = "rifg"
    elif isinstance(root_params, nisarqa.RUNWRootParamGroup):
        product_type = "runw"
    elif isinstance(root_params, nisarqa.GUNWRootParamGroup):
        product_type = "gunw"
    else:
        raise TypeError(
            f"`root_params` has type {type(root_params)}, must be one of"
            " RIFGRootParamGroup, RUNWRootParamGroup, or GUNWRootParamGroup."
        )

    log = nisarqa.get_logger()

    # Start logging in the log file
    out_dir = root_params.get_output_dir()
    log_file_txt = out_dir / root_params.get_log_filename()
    log.info(f"Log messages now directed to the log file: {log_file_txt}")
    nisarqa.set_logger_handler(log_file=log_file_txt, verbose=verbose)

    # Log the values of the parameters.
    root_params.log_parameters()

    # For readibility, store output filenames in variables.
    # Depending on which workflows are set to True, not all filename
    # variables will be used.
    input_file = root_params.input_f.qa_input_file
    out_dir = root_params.get_output_dir()
    browse_file_png = out_dir / root_params.get_browse_png_filename()
    browse_file_kml = out_dir / root_params.get_kml_browse_filename()
    report_file = out_dir / root_params.get_report_pdf_filename()
    stats_file = out_dir / root_params.get_stats_h5_filename()
    summary_file = out_dir / root_params.get_summary_csv_filename()
    use_cache = root_params.software_config.use_cache

    msg = f"Starting Quality Assurance for input file: {input_file}"
    log.info(msg)
    if not verbose:
        print(msg)

    # Initialize the PASS/FAIL checks summary file
    nisarqa.setup_summary_csv(summary_file)
    summary = nisarqa.get_summary()

    try:
        if product_type == "rifg":
            product = nisarqa.RIFG(input_file, use_cache=use_cache)
        elif product_type == "runw":
            product = nisarqa.RUNW(input_file, use_cache=use_cache)
        else:
            assert product_type == "gunw"
            product = nisarqa.GUNW(input_file, use_cache=use_cache)
    except:
        # Input product could not be opened via the product reader.
        summary.check_can_open_input_file(result="FAIL")
        raise
    else:
        # Input product could be opened via the product reader.
        summary.check_can_open_input_file(result="PASS")

    if root_params.workflows.validate:
        msg = f"Beginning validation of input file against XML Product Spec..."
        log.info(msg)

        # Build list of polarizations
        freq_pol: dict[str, list[str]] = {}
        for freq in product.list_of_frequencies:
            freq_pol[freq] = product.get_list_of_polarizations(freq=freq)

        nisarqa.verify_file_against_xml(
            input_file=product.filepath,
            product_type=product.product_type.lower(),
            product_spec_version=product.product_spec_version,
            freq_pols=freq_pol,
        )

        nisarqa.verify_metadata_cubes(
            product=product,
            fail_if_all_nan=root_params.validation.metadata_luts_fail_if_all_nan,
        )

        nisarqa.dataset_sanity_checks(product=product)

        msg = "Input file validation complete."
        log.info(msg)
        if not verbose:
            print(msg)

    if root_params.workflows.qa_reports:
        log.info("Beginning processing of `qa_reports` items...")

        with (
            h5py.File(stats_file, mode="w") as stats_h5,
            PdfPages(report_file) as report_pdf,
        ):
            # Add file metadata and title page to report PDF.
            nisarqa.setup_report_pdf(product=product, report_pdf=report_pdf)

            nisarqa.setup_stats_h5_insar_products(
                product=product, stats_h5=stats_h5, root_params=root_params
            )

            # Save frequency/polarization info to stats file
            product.save_qa_metadata_to_h5(stats_h5=stats_h5)

            # Generate the browse products (PNG+KML)
            log.info("Generating browse products...")
            dem = None
            if (
                hasattr(root_params, "anc_files")
                and root_params.anc_files is not None
            ):
                dem = root_params.anc_files.dem_file
            save_igram_product_browse(
                product=product,
                params=root_params.browse,
                browse_paths=root_params.get_browse_paths(),
                dem_file=dem,
            )

            if isinstance(product, nisarqa.UnwrappedGroup):
                nisarqa.process_phase_image_unwrapped(
                    product=product,
                    params=root_params.unw_phs_img,
                    report_pdf=report_pdf,
                    stats_h5=stats_h5,
                )

                nisarqa.process_connected_components(
                    product=product,
                    params=root_params.connected_components,
                    report_pdf=report_pdf,
                    stats_h5=stats_h5,
                )

                nisarqa.process_unw_coh_mag(
                    product=product,
                    params=root_params.coh_mag,
                    report_pdf=report_pdf,
                    stats_h5=stats_h5,
                )

            if isinstance(product, nisarqa.WrappedGroup):
                nisarqa.process_phase_image_wrapped(
                    product=product,
                    params_wrapped_igram=root_params.wrapped_igram,
                    params_coh_mag=root_params.coh_mag,
                    report_pdf=report_pdf,
                    stats_h5=stats_h5,
                )

            if isinstance(product, nisarqa.UnwrappedGroup):
                nisarqa.process_ionosphere_phase_screen(
                    product=product,
                    params_iono_phs_screen=root_params.iono_phs_screen,
                    params_iono_phs_uncert=root_params.iono_phs_uncert,
                    report_pdf=report_pdf,
                    stats_h5=stats_h5,
                )

            # Plot azimuth offsets and slant range offsets (RIFG, RUNW, & GUNW)
            nisarqa.process_az_and_slant_rg_offsets_from_igram_product(
                product=product,
                params=root_params.az_rng_offsets,
                report_pdf=report_pdf,
                stats_h5=stats_h5,
            )

            nisarqa.process_surface_peak(
                product=product,
                params_surface_peak=root_params.corr_surface_peak,
                report_pdf=report_pdf,
                stats_h5=stats_h5,
            )

        log.info(f"PDF reports saved to {report_file}")
        log.info(f"HDF5 statistics saved to {stats_file}")
        log.info(f"CSV Summary PASS/FAIL checks saved to {summary_file}")
        msg = "`qa_reports` processing complete."
        log.info(msg)
        if not verbose:
            print(msg)

    msg = (
        "QA SAS complete. For details, warnings, and errors see output log"
        " file."
    )
    log.info(msg)
    if not verbose:
        print(msg)


def save_igram_product_browse(
    product: nisarqa.WrappedGroup | nisarqa.UnwrappedGroup,
    params: Any,  # will be type-narrowed in the function
    *,
    browse_paths: nisarqa.BrowseOutputPaths,
    dem_file: str | os.PathLike | None = None,
) -> None:
    """
    Save browse PNG and KML for interferogram products (RIFG, RUNW, GUNW).

    This function generates the browse PNG image and its corresponding KML file
    with accurate corner coordinates. It also generates EPSG 4326 (lat/lon)
    browse products if configured.

    Parameters
    ----------
    product : nisarqa.WrappedGroup or nisarqa.UnwrappedGroup
        Input NISAR product. Must be either a RIFG, RUNW, or GUNW product.
    params : nisarqa.IgramBrowseParamGroup or nisarqa.UNWIgramBrowseParamGroup,
            and nisarqa.L1RadarBrowseLatLonParamGroup or nisarqa.L2GeoBrowseLatLonParamGroup
        A structure containing the processing parameters for the browse PNG.
        Must be an instance of either:
            IgramBrowseParamGroup or UNWIgramBrowseParamGroup
        and (via multiple inheritance) also an instance of either:
            L1RadarBrowseLatLonParamGroup or L2GeoBrowseLatLonParamGroup
    browse_paths : nisarqa.BrowseOutputPaths
        Container with output directory and browse/KML filenames.
    dem_file : path-like or None, optional
        Path to a Digital Elevation Model (DEM) file in a GDAL-compatible
        raster format which will be used for computing accurate geolocation.
        Used for radar products (RIFG, RUNW); ignored for geocoded products.
        If None, a zero-height DEM will be used.
        Defaults to None.
    """
    product_type = product.product_type
    if product_type not in ("RIFG", "RUNW", "GUNW"):
        raise ValueError(
            f"{product.product_type=}, must be one of ('RIFG', 'RUNW', 'GUNW')."
        )

    # XXX - Python's type annotations do not currently have a good syntax
    # for multiple inheritance in combination with a Union.
    # Instead, use type narrowing to assist type checkers:
    t = nisarqa.IgramBrowseParamGroup | nisarqa.UNWIgramBrowseParamGroup
    if not isinstance(params, t):
        msg = f"{type(params)=}, must be IgramBrowseParamGroup or UNWIgramBrowseParamGroup"
        raise TypeError(msg)
    t = (
        nisarqa.L1RadarBrowseLatLonParamGroup
        | nisarqa.L2GeoBrowseLatLonParamGroup
    )
    if not isinstance(params, t):
        msg = f"{type(params)=}, must be L1RadarBrowseLatLonParamGroup or L2GeoBrowseLatLonParamGroup"
        raise TypeError(msg)

    if isinstance(product, nisarqa.WrappedGroup):
        if not isinstance(params, nisarqa.IgramBrowseParamGroup):
            raise TypeError(
                f"{type(product)=} which is an instance of WrappedGroup, but"
                f" {type(params)=} which is not an instance of IgramBrowseParamGroup"
            )
    if isinstance(product, nisarqa.UnwrappedGroup):
        if not isinstance(params, nisarqa.UNWIgramBrowseParamGroup):
            raise TypeError(
                f"{type(product)=} which is an instance of UnwrappedGroup, but"
                f" {type(params)=} which is not an instance of UNWIgramBrowseParamGroup"
            )

    freq, pol = product.get_browse_freq_pol()

    # Generate the browse PNG and get decimation info
    if product_type == "RIFG":
        nisarqa.make_wrapped_phase_browse(
            product=product,
            freq=freq,
            pol=pol,
            params=params,
            browse_paths=browse_paths,
            dem_file=dem_file,
        )
    else:
        nisarqa.make_unwrapped_phase_browse(
            product=product,
            freq=freq,
            pol=pol,
            params=params,
            browse_paths=browse_paths,
            dem_file=dem_file,
        )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
