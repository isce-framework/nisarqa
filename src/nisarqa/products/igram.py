from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Optional, overload

import h5py
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

# List of objects from the import statements that
# should not be included when importing this module
objects_to_skip = nisarqa.get_all(name=__name__)


def verify_igram(
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

    msg = f"Starting Quality Assurance for input file: {input_file}"
    log.info(msg)
    if not verbose:
        print(msg)

    # Initialize the PASS/FAIL checks summary file
    nisarqa.setup_summary_csv(summary_file)
    summary = nisarqa.get_summary()

    try:
        if product_type == "rifg":
            product = nisarqa.RIFG(input_file)
        elif product_type == "runw":
            product = nisarqa.RUNW(input_file)
        else:
            assert product_type == "gunw"
            product = nisarqa.GUNW(input_file)
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
            fail_if_all_nan=root_params.validation.metadata_cubes_fail_if_all_nan,
        )

        nisarqa.dataset_sanity_checks(product=product)

        msg = "Input file validation complete."
        log.info(msg)
        if not verbose:
            print(msg)

    if root_params.workflows.qa_reports:
        log.info("Beginning processing of `qa_reports` items...")

        log.info(f"Beginning processing of browse KML...")
        nisarqa.write_latlonquad_to_kml(
            llq=product.get_browse_latlonquad(),
            output_dir=out_dir,
            kml_filename=root_params.get_kml_browse_filename(),
            png_filename=root_params.get_browse_png_filename(),
        )
        log.info(f"Browse image kml file saved to {browse_file_kml}")

        with (
            h5py.File(stats_file, mode="w") as stats_h5,
            PdfPages(report_file) as report_pdf,
        ):
            # Add file metadata and title page to report PDF.
            nisarqa.setup_report_pdf(product=product, report_pdf=report_pdf)

            # Save the processing parameters to the stats.h5 file
            root_params.save_processing_params_to_stats_h5(
                h5_file=stats_h5, band=product.band
            )
            log.info(f"QA Processing Parameters saved to {stats_file}")

            nisarqa.rslc.copy_identification_group_to_stats_h5(
                product=product, stats_h5=stats_h5
            )
            log.info(f"Input file Identification group copied to {stats_file}")

            # Save frequency/polarization info to stats file
            product.save_qa_metadata_to_h5(stats_h5=stats_h5)

            save_igram_product_browse_png(
                product=product,
                params=root_params.browse,
                browse_png=browse_file_png,
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

            # Save HSI Plots to PDF
            if product_type == "rifg":
                nisarqa.hsi_images_to_pdf_wrapped(
                    product=product, report_pdf=report_pdf
                )
            else:
                # RUNW or GUNW
                nisarqa.hsi_images_to_pdf_unwrapped(
                    product=product,
                    report_pdf=report_pdf,
                    rewrap=root_params.unw_phs_img.rewrap,
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


@overload
def save_igram_product_browse_png(
    product: nisarqa.WrappedGroup,
    params: nisarqa.IgramBrowseParamGroup,
    browse_png: str | os.PathLike,
) -> None: ...


@overload
def save_igram_product_browse_png(
    product: nisarqa.UnwrappedGroup,
    params: nisarqa.UNWIgramBrowseParamGroup,
    browse_png: str | os.PathLike,
) -> None: ...


def save_igram_product_browse_png(product, params, browse_png):
    """
    Save the browse PNG for interferogram products (RIFG, RUNW, GUNW).

    Parameters
    ----------
    product : nisarqa.WrappedGroup or nisarqa.UnwrappedGroup
        Input NISAR product. Must be either a RIFG, RUNW, or GUNW product.
    params : nisarqa.IgramBrowseParamGroup or nisarqa.UNWIgramBrowseParamGroup
        A structure containing the processing parameters for the browse PNG.
    browse_png : path-like
        Filename (with path) for the browse image PNG.
    """

    product_type = product.product_type
    if product_type not in ("RIFG", "RUNW", "GUNW"):
        raise ValueError(
            f"{product.product_type=}, must be one of ('RIFG', 'RUNW', 'GUNW')."
        )

    freq, pol = product.get_browse_freq_pol()

    if params.browse_image == "phase":
        if product_type == "RIFG":
            nisarqa.make_wrapped_phase_png(
                product=product,
                freq=freq,
                pol=pol,
                png_filepath=browse_png,
                longest_side_max=params.longest_side_max,
            )
        else:
            nisarqa.make_unwrapped_phase_png(
                product=product,
                freq=freq,
                pol=pol,
                params=params,
                png_filepath=browse_png,
            )

    elif params.browse_image == "hsi":
        if product_type == "RIFG":
            nisarqa.make_hsi_png_with_wrapped_phase(
                product=product,
                freq=freq,
                pol=pol,
                params=params,
                png_filepath=browse_png,
            )

        else:
            nisarqa.make_hsi_png_with_unwrapped_phase(
                product=product,
                freq=freq,
                pol=pol,
                params=params,
                png_filepath=browse_png,
            )
    else:
        raise ValueError(
            f"`{params.browse_image=}`, only 'phase' or 'hsi' supported."
        )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
