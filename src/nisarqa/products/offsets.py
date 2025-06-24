from __future__ import annotations

import h5py
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


def verify_offset(
    root_params: nisarqa.ROFFRootParamGroup | nisarqa.GOFFRootParamGroup,
    verbose: bool = False,
) -> None:
    """
    Perform verification checks and quality assurance on a NISAR Offset product.

    This is the main function for running the entire QA workflow for one of
    a NISAR ROFF or GOFF product.
    It will run based on the options supplied in the input parameters.

    Parameters
    ----------
    root_params : nisarqa.ROFFRootParamGroup or nisarqa.GOFFRootParamGroup
        Input parameters to run this QA SAS. The type of the input product
        to be verified (ROFF or GOFF) will be inferred from the type
        of this argument.
    verbose : bool, optional
        True to stream log messages to console (stderr) in addition to the
        log file. False to only stream to the log file. (Initial log messages
        during setup will stream to console regardless.) Defaults to False.
    """
    if isinstance(root_params, nisarqa.ROFFRootParamGroup):
        product_type = "roff"
    elif isinstance(root_params, nisarqa.GOFFRootParamGroup):
        product_type = "goff"
    else:
        raise TypeError(
            f"`root_params` has type {type(root_params)}, must be one of"
            " ROFFRootParamGroup or GOFFRootParamGroup."
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
        if product_type == "roff":
            product = nisarqa.ROFF(input_file, use_cache=use_cache)
        else:
            assert product_type == "goff"
            product = nisarqa.GOFF(input_file, use_cache=use_cache)
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

        layer_groups = [
            f"layer{num}" for num in product.available_layer_numbers
        ]

        nisarqa.verify_file_against_xml(
            input_file=product.filepath,
            product_type=product.product_type.lower(),
            product_spec_version=product.product_spec_version,
            freq_pols=freq_pol,
            # TODO - create a new function in the product reader
            # called "get_list_of_layers(freq)" to extract the contents of
            # the `listOfLayers` dataset
            layer_groups=layer_groups,
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

            nisarqa.setup_stats_h5_all_products(
                product=product, stats_h5=stats_h5, root_params=root_params
            )

            # Save frequency/polarization info to stats file
            product.save_qa_metadata_to_h5(stats_h5=stats_h5)

            # Generate along track + slant range browse image, quiver plots,
            # and side-by-side plots for PDF
            nisarqa.process_az_and_slant_rg_offsets_from_offset_product(
                product=product,
                params_quiver=root_params.quiver,
                params_offsets=root_params.az_rng_offsets,
                report_pdf=report_pdf,
                stats_h5=stats_h5,
                browse_png=browse_file_png,
            )

            nisarqa.process_az_and_slant_rg_variances_from_offset_product(
                product=product,
                params=root_params.variances,
                report_pdf=report_pdf,
                stats_h5=stats_h5,
            )

            nisarqa.process_cross_variance_and_surface_peak(
                product=product,
                params_cross_offset=root_params.cross_variance,
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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
