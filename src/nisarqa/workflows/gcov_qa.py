import h5py
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


def gcov_qa(
    root_params: nisarqa.GCOVRootParamGroup, verbose: bool = False
) -> None:
    """
    Perform verification checks and quality assurance on a NISAR GCOV product.

    This is the main function for running the entire QA workflow. It will
    run based on the options supplied in the input parameters.

    Parameters
    ----------
    root_params : nisarqa.GCOVRootParamGroup
        Input parameters to run this QA SAS.
    verbose : bool, optional
        True to stream log messages to console (stderr) in addition to the
        log file. False to only stream to the log file. (Initial log messages
        during setup will stream to console regardless.) Defaults to False.
    """
    log = nisarqa.get_logger()

    # Start logging in the log file
    out_dir = root_params.get_output_dir()
    log_file_txt = out_dir / root_params.get_log_filename()
    log.info(f"Log messages now directed to the log file: {log_file_txt}")
    nisarqa.set_logger_handler(log_file=log_file_txt, verbose=verbose)

    # Log the values of the parameters.
    root_params.log_parameters()

    # For readibility, store possible output filenames in variables.
    input_file = root_params.input_f.qa_input_file
    out_dir = root_params.get_output_dir()
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
        product = nisarqa.GCOV(
            filepath=input_file,
            use_cache=root_params.software_config.use_cache,
        )
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

        # Build list of polarizations (terms)
        freq_cov: dict[str, list[str]] = {}
        for freq in product.list_of_frequencies:
            freq_cov[freq] = product.get_list_of_covariance_terms(freq=freq)

        nisarqa.verify_file_against_xml(
            input_file=product.filepath,
            product_type=product.product_type.lower(),
            product_spec_version=product.product_spec_version,
            freq_pols=freq_cov,
        )

        nisarqa.verify_metadata_cubes(
            product=product,
            fail_if_all_nan=root_params.validation.metadata_luts_fail_if_all_nan,
        )

        nisarqa.verify_calibration_metadata_luts(
            product=product,
            fail_if_all_nan=root_params.validation.metadata_luts_fail_if_all_nan,
        )

        nisarqa.dataset_sanity_checks(product=product)

        msg = "Input file validation complete."
        log.info(msg)
        if not verbose:
            print(msg)

        # TODO - this GCOV validation check should be integrated into
        # the actual product validation. For now, we'll leave it here.
        for freq in product.freqs:
            for pol in product.get_pols(freq=freq):
                if pol in nisarqa.GCOV_DIAG_POLS:
                    continue
                elif pol in nisarqa.GCOV_OFF_DIAG_POLS:
                    log.warning(
                        f"GCOV product contains off-diagonal term {pol}."
                    )
                else:
                    raise nisarqa.InvalidNISARProductError(
                        f"Polzarization '{pol}' was found in input product."
                        " GCOV products can only contain polarizations: "
                        f" {nisarqa.GCOV_DIAG_POLS + nisarqa.GCOV_OFF_DIAG_POLS}."
                    )

    if root_params.workflows.qa_reports:
        log.info(f"Beginning `qa_reports` processing...")

        with (
            h5py.File(stats_file, mode="w") as stats_h5,
            PdfPages(report_file) as report_pdf,
        ):
            # Add file metadata and title page to report PDF.
            nisarqa.setup_report_pdf(product=product, report_pdf=report_pdf)

            nisarqa.setup_stats_h5_non_insar_products(
                product=product, stats_h5=stats_h5, root_params=root_params
            )

            input_raster_represents_power = True
            name_of_backscatter_content = (
                r"GCOV Backscatter Coefficient ($\gamma^0$)"
            )

            # Generate the Backscatter Image and Browse Image
            nisarqa.process_backscatter_imgs_and_browse(
                product=product,
                params=root_params.backscatter_img,
                stats_h5=stats_h5,
                report_pdf=report_pdf,
                plot_title_prefix=name_of_backscatter_content,
                input_raster_represents_power=input_raster_represents_power,
                out_dir=out_dir,
                browse_filename=root_params.get_browse_png_filename(),
                kml_filename=root_params.get_kml_browse_filename(),
            )
            log.info("Processing of Backscatter images complete.")

            # Generate the Backscatter and Phase Histograms
            nisarqa.process_backscatter_and_phase_histograms(
                product=product,
                params=root_params.histogram,
                stats_h5=stats_h5,
                report_pdf=report_pdf,
                plot_title_prefix=name_of_backscatter_content,
                input_raster_represents_power=input_raster_represents_power,
            )
            log.info("Processing of backscatter and phase histograms complete.")

            # Check for invalid values

            # Compute metrics for stats.h5

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
