import h5py
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


def verify_gslc(
    root_params: nisarqa.GSLCRootParamGroup, verbose: bool = False
) -> None:
    """
    Perform verification checks and quality assurance on a NISAR GSLC product.

    This is the main function for running the entire QA workflow. It will
    run based on the options supplied in the input parameters.

    Parameters
    ----------
    root_params : nisarqa.GSLCRootParamGroup
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
        product = nisarqa.GSLC(
            filepath=input_file,
            use_cache=root_params.software_config.use_cache,
            # prime_the_cache=True,  # we analyze all images, so prime the cache
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

        nisarqa.verify_calibration_metadata_luts(
            product=product,
            fail_if_all_nan=root_params.validation.metadata_luts_fail_if_all_nan,
        )

        nisarqa.dataset_sanity_checks(product=product)

        msg = "Input file validation complete."
        log.info(msg)
        if not verbose:
            print(msg)

    # Both the `qa_reports` and/or `point_target` steps may generate a report
    # PDF. If both are workflows are enabled, this can cause an issue, since
    # closing and re-opening a `PdfPages` object causes the file to be
    # overwritten, discarding the previous contents. The current solution is to
    # unconditionally create the `PdfPages` object and keep it open during both
    # steps. The file is automatically deleted upon closing if nothing was
    # written to it.
    with PdfPages(report_file, keep_empty=False) as report_pdf:

        if (
            root_params.workflows.qa_reports
            or root_params.workflows.point_target
        ):
            # This is the first time opening the STATS.h5 file for GSLC
            # workflow, so open in 'w' mode.
            # After this, always open STATS.h5 in 'r+' mode.
            with h5py.File(stats_file, mode="w") as stats_h5:
                nisarqa.setup_stats_h5_non_insar_products(
                    product=product, stats_h5=stats_h5, root_params=root_params
                )

            # Add file metadata and title page to report PDF.
            nisarqa.setup_report_pdf(product=product, report_pdf=report_pdf)

        if root_params.workflows.qa_reports:
            log.info(f"Beginning `qa_reports` processing...")

            log.info(f"Beginning processing of browse KML...")
            nisarqa.write_latlonquad_to_kml(
                llq=product.get_browse_latlonquad(),
                output_dir=root_params.get_output_dir(),
                kml_filename=root_params.get_kml_browse_filename(),
                png_filename=root_params.get_browse_png_filename(),
            )
            log.info(f"Browse image kml file saved to {browse_file_kml}")

            with h5py.File(stats_file, mode="r+") as stats_h5:

                input_raster_represents_power = False
                name_of_backscatter_content = (
                    r"GSLC Backscatter Coefficient ($\beta^0$)"
                )

                # Generate the GSLC Power Image and Browse Image
                nisarqa.process_backscatter_imgs_and_browse(
                    product=product,
                    params=root_params.backscatter_img,
                    stats_h5=stats_h5,
                    report_pdf=report_pdf,
                    plot_title_prefix=name_of_backscatter_content,
                    input_raster_represents_power=input_raster_represents_power,
                    browse_filename=browse_file_png,
                )
                log.info("Processing of Backscatter images complete.")
                log.info(f"Browse image PNG file saved to {browse_file_png}")

                # Generate the GSLC Power and Phase Histograms
                nisarqa.process_backscatter_and_phase_histograms(
                    product=product,
                    params=root_params.histogram,
                    stats_h5=stats_h5,
                    report_pdf=report_pdf,
                    plot_title_prefix=name_of_backscatter_content,
                    input_raster_represents_power=input_raster_represents_power,
                )
                log.info(
                    "Processing of backscatter and phase histograms complete."
                )

                # Process Interferograms

                # Check for invalid values

                # Compute metrics for stats.h5

                log.info(f"PDF reports saved to {report_file}")
                log.info(f"HDF5 statistics saved to {stats_file}")
                log.info(
                    f"CSV Summary PASS/FAIL checks saved to {summary_file}"
                )
                msg = "`qa_reports` processing complete."
                log.info(msg)
                if not verbose:
                    print(msg)

        if root_params.workflows.point_target:
            log.info("Beginning Point Target Analyzer CalTool...")

            # Run Point Target Analyzer tool
            nisarqa.caltools.run_gslc_pta_tool(
                pta_params=root_params.pta,
                dyn_anc_params=root_params.anc_files,
                gslc=product,
                stats_filename=stats_file,
            )
            log.info(
                f"Point Target Analyzer CalTool results saved to {stats_file}."
            )

            # Read the PTA results from `stats_file`, generate plots of
            # azimuth/range cuts, and add them to the PDF report.
            with h5py.File(stats_file, mode="r") as stats_h5:
                nisarqa.caltools.plot_cr_offsets_to_pdf(
                    product, stats_h5, report_pdf
                )
                nisarqa.caltools.add_pta_plots_to_report(stats_h5, report_pdf)
            log.info(
                f"Point Target Analyzer CalTool plots saved to {report_file}."
            )

            msg = "Point Target Analyzer CalTool complete."
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
