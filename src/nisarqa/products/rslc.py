from __future__ import annotations

import functools
from collections.abc import Sequence
from typing import Optional

import h5py
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter
from numpy.typing import ArrayLike
from PIL import Image
from scipy import constants

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


def verify_rslc(
    root_params: nisarqa.RSLCRootParamGroup, verbose: bool = False
) -> None:
    """
    Perform verification checks and quality assurance on a NISAR RSLC product.

    This is the main function for running the entire QA workflow. It will
    run based on the options supplied in the input parameters.

    Parameters
    ----------
    root_params : nisarqa.RSLCRootParamGroup
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
        # All worksflows use the RSLC() product; only initialize once.
        product = nisarqa.RSLC(
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

    # Run validate first because it checks the product spec
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
        # If running these workflows, save the processing parameters and
        # identification group to STATS.h5
        if (
            root_params.workflows.qa_reports
            or root_params.workflows.abs_cal
            or root_params.workflows.neb
            or root_params.workflows.point_target
        ):
            # This is the first time opening the STATS.h5 file for RSLC
            # workflow, so open in 'w' mode.
            # After this, always open STATS.h5 in 'r+' mode.
            with h5py.File(stats_file, mode="w") as stats_h5:

                nisarqa.setup_stats_h5_all_products(
                    product=product, stats_h5=stats_h5, root_params=root_params
                )

                nisarqa.copy_rfi_metadata_to_stats_h5(
                    product=product, stats_h5=stats_h5
                )
                log.info(f"Input file RFI metadata copied to {stats_file}")

        if (
            root_params.workflows.qa_reports
            or root_params.workflows.point_target
        ):
            # Add file metadata and title page to report PDF.
            nisarqa.setup_report_pdf(product=product, report_pdf=report_pdf)

        if root_params.workflows.qa_reports:
            log.info(f"Beginning `qa_reports` processing...")

            log.info(f"Beginning processing of browse KML...")
            nisarqa.write_latlonquad_to_kml(
                llq=product.get_browse_latlonquad(),
                output_dir=out_dir,
                kml_filename=root_params.get_kml_browse_filename(),
                png_filename=root_params.get_browse_png_filename(),
            )
            log.info(f"Browse image kml file saved to {browse_file_kml}")

            with h5py.File(stats_file, mode="r+") as stats_h5:
                # Save frequency/polarization info to stats file
                nisarqa.save_nisar_freq_metadata_to_h5(
                    stats_h5=stats_h5, product=product
                )

                # Copy imagery metrics into stats.h5
                nisarqa.copy_non_insar_imagery_metrics(
                    product=product, stats_h5=stats_h5
                )
                log.info(f"Input file imagery metrics copied to {stats_file}")

                input_raster_represents_power = False
                name_of_backscatter_content = (
                    r"RSLC Backscatter Coefficient ($\beta^0$)"
                )

                log.info("Beginning processing of backscatter images...")
                process_backscatter_imgs_and_browse(
                    product=product,
                    params=root_params.backscatter_img,
                    stats_h5=stats_h5,
                    report_pdf=report_pdf,
                    plot_title_prefix=name_of_backscatter_content,
                    input_raster_represents_power=input_raster_represents_power,
                    browse_filename=browse_file_png,
                )
                log.info("Processing of backscatter images complete.")
                log.info(f"Browse image PNG file saved to {browse_file_png}")

                log.info(
                    "Beginning processing of backscatter and phase"
                    " histograms..."
                )
                process_backscatter_and_phase_histograms(
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

                log.info("Beginning processing of range power spectra...")
                process_range_spectra(
                    product=product,
                    params=root_params.range_spectra,
                    stats_h5=stats_h5,
                    report_pdf=report_pdf,
                )
                log.info("Processing of range power spectra complete.")

                log.info("Beginning processing of azimuth power spectra...")
                process_azimuth_spectra(
                    product=product,
                    params=root_params.az_spectra,
                    stats_h5=stats_h5,
                    report_pdf=report_pdf,
                )
                log.info("Processing of azimuth power spectra complete.")

                # Check for invalid values

                log.info(f"PDF reports saved to {report_file}")
                log.info(f"HDF5 statistics saved to {stats_file}")
                log.info(
                    f"CSV Summary PASS/FAIL checks saved to {summary_file}"
                )
                msg = "`qa_reports` processing complete."
                log.info(msg)
                if not verbose:
                    print(msg)

        if root_params.workflows.abs_cal:
            log.info("Beginning Absolute Radiometric Calibration CalTool...")

            # Run Absolute Radiometric Calibration tool
            nisarqa.caltools.run_abscal_tool(
                abscal_params=root_params.abs_cal,
                dyn_anc_params=root_params.anc_files,
                rslc=product,
                stats_filename=stats_file,
            )
            log.info(
                "Absolute Radiometric Calibration CalTool results saved to"
                f" {stats_file}."
            )
            msg = "Absolute Radiometric Calibration CalTool complete."
            log.info(msg)
            if not verbose:
                print(msg)

        if root_params.workflows.neb:
            log.info("Beginning Noise Equivalent Backscatter CalTool...")

            # Run NEB tool
            nisarqa.caltools.run_neb_tool(
                rslc=product,
                stats_filename=stats_file,
            )
            log.info(
                f"Noise Equivalent Backscatter CalTool results saved to {stats_file}."
            )
            msg = "Noise Equivalent Backscatter CalTool complete."
            log.info(msg)
            if not verbose:
                print(msg)

        if root_params.workflows.point_target:
            log.info("Beginning Point Target Analyzer CalTool...")

            # Run Point Target Analyzer tool
            nisarqa.caltools.run_rslc_pta_tool(
                pta_params=root_params.pta,
                dyn_anc_params=root_params.anc_files,
                rslc=product,
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


def process_backscatter_imgs_and_browse(
    product: nisarqa.NonInsarProduct,
    params: nisarqa.BackscatterImageParamGroup,
    stats_h5: h5py.File,
    report_pdf: PdfPages,
    browse_filename: str,
    input_raster_represents_power: bool = False,
    plot_title_prefix: str = "Backscatter Coefficient",
) -> None:
    """
    Generate Backscatter Image plots for the `report_pdf` and
    corresponding browse image product.

    Parameters
    ----------
    product : nisarqa.NonInsarProduct
        The input NISAR product
    params : BackscatterImageParamGroup
        A dataclass containing the parameters for processing
        and outputting backscatter image(s) and browse image.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the backscatter image plot to
    browse_filename : str
        Filename (with path) for the browse image PNG.
    input_raster_represents_power : bool, optional
        The input dataset rasters associated with these histogram parameters
        should have their pixel values represent either power or root power.
        If `True`, then QA SAS assumes the input data already represents
        power and uses the pixels' magnitudes for computations.
        If `False`, then QA SAS assumes the input data represents root power
        aka magnitude and will handle the full computation to power using
        the formula:  power = abs(<magnitude>)^2 .
        Defaults to False (root power).
    plot_title_prefix : str
        Prefix for the title of the backscatter plots.
        Suggestions: "RSLC Backscatter Coefficient (beta-0)" or
        "GCOV Backscatter Coefficient (gamma-0)".
        Defaults to "Backscatter Coefficient".
    """

    # Select which layers will be needed for the browse image.
    # Multilooking takes a long time, but each multilooked polarization image
    # should be less than ~4 MB (per the current requirements for NISAR),
    # so it's ok to store the necessary multilooked Backscatter Images in memory.
    # to combine them later into the Browse image. The memory costs are
    # less than the costs for re-computing the multilooking.
    layers_for_browse = product.get_layers_for_browse()

    # At the end of the loop below, the keys of this dict should exactly
    # match the set of TxRx polarizations needed to form the browse image
    pol_imgs_for_browse = {}

    # Process each image in the dataset

    for freq in product.freqs:
        for pol in product.get_pols(freq=freq):
            # Open the *SARRaster image

            with product.get_raster(freq=freq, pol=pol) as img:
                with nisarqa.log_runtime(
                    f"`get_multilooked_backscatter_img` for Frequency {freq}"
                    f" Polarization {pol}"
                ):
                    multilooked_img = get_multilooked_backscatter_img(
                        img=img,
                        params=params,
                        stats_h5=stats_h5,
                        input_raster_represents_power=input_raster_represents_power,
                    )

                corrected_img, orig_vmin, orig_vmax = apply_image_correction(
                    img_arr=multilooked_img, params=params
                )

                if params.gamma is not None:
                    inverse_func = functools.partial(
                        invert_gamma_correction,
                        gamma=params.gamma,
                        vmin=orig_vmin,
                        vmax=orig_vmax,
                    )

                    colorbar_formatter = FuncFormatter(
                        lambda x, pos: "{:.3f}".format(inverse_func(x))
                    )

                else:
                    colorbar_formatter = None

                # Label and Save Backscatter Image to PDF
                # Construct Figure title
                fig_title = f"{plot_title_prefix}\n{img.name}"

                # Construct the axes title. Add image correction notes
                # in the order specified in `apply_image_correction()`.
                ax_title = ""
                clip_interval = params.percentile_for_clipping
                if not np.allclose(clip_interval, [0.0, 100.0]):
                    ax_title += (
                        "clipped to percentile range"
                        f" [{clip_interval[0]}, {clip_interval[1]}]\n"
                    )

                ax_title += f"scale={params.backscatter_units}"

                if params.gamma is not None:
                    ax_title += rf", $\gamma$-correction={params.gamma}"

                nisarqa.rslc.img2pdf_grayscale(
                    img_arr=corrected_img,
                    fig_title=fig_title,
                    ax_title=ax_title,
                    ylim=img.y_axis_limits,
                    xlim=img.x_axis_limits,
                    colorbar_formatter=colorbar_formatter,
                    ylabel=img.y_axis_label,
                    xlabel=img.x_axis_label,
                    plots_pdf=report_pdf,
                    nan_color=params.nan_color,
                )

                # If this backscatter image is needed to construct the browse image...
                if (freq in layers_for_browse) and (
                    pol in layers_for_browse[freq]
                ):
                    # ...keep the multilooked, color-corrected image in memory
                    pol_imgs_for_browse[pol] = corrected_img

    # Construct the browse image
    product.save_browse(pol_imgs=pol_imgs_for_browse, filepath=browse_filename)


# TODO - move to generic location
def get_multilooked_backscatter_img(
    img, params, stats_h5, input_raster_represents_power=False
):
    """
    Generate the multilooked Backscatter Image array for a single
    polarization image.

    Parameters
    ----------
    img : RadarRaster or GeoRaster
        The raster to be processed
    params : BackscatterImageParamGroup
        A structure containing the parameters for processing
        and outputting the backscatter image(s).
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to
    input_raster_represents_power : bool, optional
        The input dataset rasters associated with these histogram parameters
        should have their pixel values represent either power or root power.
        If `True`, then QA SAS assumes the input data already represents
        power and uses the pixels' magnitudes for computations.
        If `False`, then QA SAS assumes the input data represents root power
        aka magnitude and will handle the full computation to power using
        the formula:  power = abs(<magnitude>)^2 .
        Defaults to False (root power).

    Returns
    -------
    out_img : numpy.ndarray
        The multilooked Backscatter Image
    """
    log = nisarqa.get_logger()
    log.info(f"Beginning multilooking for backscatter image {img.name}...")

    nlooks_freqa_arg = params.nlooks_freqa
    nlooks_freqb_arg = params.nlooks_freqb

    # Get the window size for multilooking
    if (img.freq == "A" and nlooks_freqa_arg is None) or (
        img.freq == "B" and nlooks_freqb_arg is None
    ):
        nlooks = nisarqa.compute_square_pixel_nlooks(
            img.data.shape,
            sample_spacing=(
                np.abs(img.y_axis_spacing),
                np.abs(img.x_axis_spacing),
            ),
            longest_side_max=params.longest_side_max,
        )

    elif img.freq == "A":
        nlooks = nlooks_freqa_arg
    elif img.freq == "B":
        nlooks = nlooks_freqb_arg
    else:
        raise ValueError(
            f"frequency is '{img.freq}', but only 'A' or 'B' are valid options."
        )

    # Save the final nlooks to the HDF5 dataset
    grp_path = nisarqa.STATS_H5_QA_PROCESSING_GROUP % img.band
    dataset_name = f"backscatterImageNlooksFreq{img.freq.upper()}"

    if isinstance(img, nisarqa.RadarRaster):
        axes = "[<azimuth>,<range>]"
    elif isinstance(img, nisarqa.GeoRaster):
        axes = "[<Y direction>,<X direction>]"
    else:
        raise TypeError(
            f"Input `img` must be RadarRaster or GeoRaster. It is {type(img)}"
        )

    # Create the nlooks dataset
    if dataset_name in stats_h5[grp_path]:
        assert tuple(stats_h5[grp_path][dataset_name][...]) == tuple(nlooks)
    else:
        nisarqa.create_dataset_in_h5group(
            h5_file=stats_h5,
            grp_path=grp_path,
            ds_name=dataset_name,
            ds_data=nlooks,
            ds_units="1",
            ds_description=(
                f"Number of looks along {axes} axes of "
                f"Frequency {img.freq.upper()} image arrays "
                "for multilooking the backscatter and browse images."
            ),
        )

    log.debug(
        f"Multilooking Image {img.name} with original shape: {img.data.shape}"
    )
    log.debug(f"Y direction (azimuth) ground spacing: {img.y_axis_spacing}")
    log.debug(f"X direction (range) ground spacing: {img.x_axis_spacing}")
    log.debug(f"Beginning Multilooking with nlooks window shape: {nlooks}")

    # Multilook
    with nisarqa.log_runtime(
        f"`compute_multilooked_backscatter_by_tiling` for {img.name} with"
        f" shape {img.data.shape} using {nlooks=} and tile"
        f" shape {params.tile_shape}"
    ):
        out_img = nisarqa.compute_multilooked_backscatter_by_tiling(
            arr=img.data,
            nlooks=nlooks,
            input_raster_represents_power=input_raster_represents_power,
            tile_shape=params.tile_shape,
        )

    log.debug(f"Final multilooked image shape: {out_img.shape}")
    log.info(f"Multilooking complete for backscatter image {img.name}.")

    return out_img


def apply_image_correction(img_arr, params):
    """
    Apply image correction in `img_arr` as specified in `params`.

    Image correction is applied in the following order:
        Step 1: Per `params.percentile_for_clipping`, clip the image array's outliers
        Step 2: Per `params.linear_units`, convert from linear units to dB
        Step 3: Per `params.gamma`, apply gamma correction

    Parameters
    ----------
    img_arr : numpy.ndarray
        2D image array to have image correction applied to.
        For example, for RSLC this is the multilooked image array.
    params : BackscatterImageParamGroup
        A structure containing the parameters for processing
        and outputting the backscatter image(s).

    Returns
    -------
    out_img : numpy.ndarray
        2D image array. If any image correction was specified via `params`
        and applied to `img_arr`, this returned array will include that
        image correction.
    vmin, vmax : float
        The min and max of the image array (excluding Nan), as computed
        after Step 2 but before Step 3. These can be used to set
        colorbar tick mark values; by computing vmin and vmax prior to
        gamma correction, the tick marks values retain physical meaning.
    """

    # Step 1: Clip the image array's outliers
    img_arr = clip_array(
        img_arr, percentile_range=params.percentile_for_clipping
    )

    # Step 2: Convert from linear units to dB
    if not params.linear_units:
        with nisarqa.ignore_runtime_warnings():
            # This line throws these warnings:
            #   "RuntimeWarning: divide by zero encountered in log10"
            # when there are zero values. Ignore those warnings.
            img_arr = nisarqa.pow2db(img_arr)

    # Get the vmin and vmax prior to applying gamma correction.
    # These can later be used for setting the colorbar's
    # tick mark values.
    vmin = np.nanmin(img_arr)
    vmax = np.nanmax(img_arr)

    # Step 3: Apply gamma correction
    if params.gamma is not None:
        img_arr = apply_gamma_correction(img_arr, gamma=params.gamma)

    return img_arr, vmin, vmax


def clip_array(arr, percentile_range=(0.0, 100.0)):
    """
    Clip input array to the provided percentile range.

    NaN values are excluded from the computation of the percentile.

    Parameters
    ----------
    arr : array_like
        Input array
    percentile_range : pair of numeric, optional
        Defines the percentile range of the `arr`
        that the colormap covers. Must be in the range [0.0, 100.0],
        inclusive.
        Defaults to (0.0, 100.0) (no clipping).

    Returns
    -------
    out_img : numpy.ndarray
        A copy of the input array with the values outside of the
        range defined by `percentile_range` clipped.
    """
    for p in percentile_range:
        nisarqa.verify_valid_percent(p)
    if len(percentile_range) != 2:
        raise ValueError(f"{percentile_range=} must have length of 2")

    # Get the value of the e.g. 5th percentile and the 95th percentile
    vmin, vmax = np.nanpercentile(arr, percentile_range)

    # Clip the image data and return
    return np.clip(arr, a_min=vmin, a_max=vmax)


def apply_gamma_correction(img_arr, gamma):
    """
    Apply gamma correction to the input array.

    Function will normalize the array and apply gamma correction.
    The returned output array will remain in range [0,1].

    Parameters
    ----------
    img_arr : array_like
        Input array
    gamma : float
        The gamma correction parameter.
        Gamma will be applied as follows:
            array_out = normalized_array ^ gamma
        where normalized_array is a copy of `img_arr` with values
        scaled to the range [0,1].

    Returns
    -------
    out_img : numpy.ndarray
        Copy of `img_arr` with the specified gamma correction applied.
        Due to normalization, values in `out_img` will be in range [0,1].

    Also See
    --------
    invert_gamma_correction : inverts this function
    """
    # Normalize to range [0,1]
    # Any zeros in the image array will cause an expected Runtime warning.
    # Ok to suppress.
    with nisarqa.ignore_runtime_warnings():
        # This line throws these warnings:
        #   "RuntimeWarning: divide by zero encountered in divide"
        #   "RuntimeWarning: invalid value encountered in divide"
        # when there are zero values. Ignore those warnings.
        out_img = nisarqa.normalize(img_arr)

    # Apply gamma correction
    out_img = np.power(out_img, gamma)

    return out_img


def invert_gamma_correction(img_arr, gamma, vmin, vmax):
    """
    Invert the gamma correction to the input array.

    Function will normalize the array and apply gamma correction.
    The returned output array will remain in range [0,1].

    Parameters
    ----------
    img_arr : array_like
        Input array
    gamma : float
        The gamma correction parameter.
        Gamma will be inverted as follows:
            array_out = img_arr ^ (1/gamma)
        The array will then be rescaled as follows, to "undo" normalization:
            array_out = (array_out * (vmax - vmin)) + vmin
    vmin, vmax : float
        The min and max of the source image array BEFORE gamma correction
        was applied.

    Returns
    -------
    out : numpy.ndarray
        Copy of `img_arr` with the specified gamma correction inverted
        and scaled to range [<vmin>, <vmax>]

    Also See
    --------
    apply_gamma_correction : inverts this function
    """
    # Invert the power
    out = np.power(img_arr, 1 / gamma)

    # Invert the normalization
    out = (out * (vmax - vmin)) + vmin

    return out


def plot_to_grayscale_png(img_arr, filepath):
    """
    Save the image array to a 1-channel grayscale PNG with transparency.

    Finite pixels will have their values scaled to 1-255. Non-finite pixels
    will be set to 0 and made to appear transparent in the PNG.
    The pixel value of 0 is reserved for the transparent pixels.

    Parameters
    ----------
    img_arr : array_like
        2D Image to plot
    filepath : str
        Full filepath the browse image product.

    Notes
    -----
    This function does not add a full alpha channel to the output png.
    It instead uses "cheap transparency" (palette-based transparency)
    to keep file size smaller.
    See: http://www.libpng.org/pub/png/book/chapter08.html#png.ch08.div.5.4
    """

    # Only use 2D arrays
    if len(np.shape(img_arr)) != 2:
        raise ValueError("Input image array must be 2D.")

    img_arr, transparency_val = prep_arr_for_png_with_transparency(img_arr)

    # Save as grayscale image using PIL.Image. 'L' is grayscale mode.
    # (Pyplot only saves png's as RGB, even if cmap=plt.cm.gray)
    im = Image.fromarray(img_arr, mode="L")
    im.save(filepath, transparency=transparency_val)  # default = 72 dpi


def plot_to_rgb_png(red, green, blue, filepath):
    """
    Combine and save RGB channel arrays to a browse PNG with transparency.

    Finite pixels will have their values scaled to 1-255. Non-finite pixels
    will be set to 0 and made to appear transparent in the PNG.
    The pixel value of 0 is reserved for the transparent pixels.

    Parameters
    ----------
    red, green, blue : numpy.ndarray
        2D arrays that will be mapped to the red, green, and blue
        channels (respectively) for the PNG. These three arrays must have
        identical shape.
    filepath : str
        Full filepath for where to save the browse image PNG.

    Notes
    -----
    This function does not add a full alpha channel to the output png.
    It instead uses "cheap transparency" (palette-based transparency)
    to keep file size smaller.
    See: http://www.libpng.org/pub/png/book/chapter08.html#png.ch08.div.5.4
    """

    # Only use 2D arrays
    for arr in (red, green, blue):
        if len(np.shape(arr)) != 2:
            raise ValueError("Input image array must be 2D.")

    # Concatenate into uint8 RGB array.
    nrow, ncol = np.shape(red)
    rgb_arr = np.zeros((nrow, ncol, 3), dtype=np.uint8)

    # transparency_val will be the same from all calls to this function;
    # only need to capture it once.
    rgb_arr[:, :, 0], transparency_val = prep_arr_for_png_with_transparency(red)
    rgb_arr[:, :, 1] = prep_arr_for_png_with_transparency(green)[0]
    rgb_arr[:, :, 2] = prep_arr_for_png_with_transparency(blue)[0]

    # make a tuple with length 3, where each entry denotes the transparent
    # value for R, G, and B channels (respectively)
    transparency_val = (transparency_val,) * 3

    im = Image.fromarray(rgb_arr, mode="RGB")

    im.save(filepath, transparency=transparency_val)  # default = 72 dpi


def prep_arr_for_png_with_transparency(img_arr):
    """
    Prepare a 2D image array for use in a uint8 PNG with palette-based
    transparency.

    Normalizes and then scales the array values to 1-255. Non-finite pixels
    (aka invalid pixels) are set to 0.

    Parameters
    ----------
    img_arr : array_like
        2D Image to plot

    Returns
    -------
    out : numpy.ndarray with dtype numpy.uint8
        Copy of the input image array that has been prepared for use in
        a PNG file.
        Input image array values were normalized to [0,1] and then
        scaled to [1,255]. Non-finite pixels are set to 0.
    transparency_value : int
        The pixel value denoting non-finite (invalid) pixels. This is currently always 0.

    Notes
    -----
    For PNGs with palette-based transparency, one value in 0-255 will need
    to be assigned to be the fill value (i.e. the value that will appear
    as transparent). For unsigned integer data, it's conventional to use
    the largest representable value. (For signed integer data you usually
    want the most negative value.)
    However, when using RGB mode + palette-based transparency in Python's
    PIL library, if a pixel in only e.g. one color channel is invalid,
    but the corresponding pixel in other channels is valid, then the
    resulting PNG image will make the color for the first channel appear
    dominant. For example, for a given pixel in an RGB image. If a red
    channel's value for that pixel is 255 (invalid), while the green and
    blue channels' values are 123 and 67 (valid), then in the output RGB
    that pixel will appear bright red -- even if the `transparency` parameter
    is assigned correctly. So, instead we'll use 0 to represent invalid
    pixels, so that the resulting PNG "looks" more representative of the
    underlying data.
    """

    # Normalize to range [0,1]. If the array is already normalized,
    # this should have no impact.
    out = nisarqa.normalize(img_arr)

    # After normalization to range [0,1], scale to 1-255 for unsigned int8
    # Reserve the value 0 for use as the transparency value.
    #   out = (<normalized array> * (target_max - target_min)) + target_min
    with nisarqa.ignore_runtime_warnings():
        # This line throws a "RuntimeWarning: invalid value encountered in cast"
        # when there are NaN values. Ignore those warnings.
        out = (np.uint8(out * (255 - 1))) + 1

    # Set transparency value so that the "alpha" is added to the image
    transparency_value = 0

    # Denote invalid pixels with 255, so that they output as transparent
    out[~np.isfinite(img_arr)] = transparency_value

    return out, transparency_value


# TODO - move to generic plotting.py
def img2pdf_grayscale(
    img_arr: ArrayLike,
    plots_pdf: PdfPages,
    fig_title: Optional[str] = None,
    ax_title: Optional[str] = None,
    xlim: Optional[Sequence[float]] = None,
    ylim: Optional[Sequence[float]] = None,
    colorbar_formatter: Optional[FuncFormatter] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    nan_color: str | Sequence[float] | None = "blue",
) -> None:
    """
    Plot the image array in grayscale, add a colorbar, and append to the PDF.

    Parameters
    ----------
    img_arr : array_like
        Image to plot in grayscale
    plots_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the backscatter image plot to
    fig_title : str or None, optional
        The title for the plot's figure. Defaults to None.
    ax_title : str or None, optional
        The title for the plot's axes. (Functionally akin to a subtitle.)
        Defaults to None.
    xlim, ylim : sequence of numeric or None, optional
        Lower and upper limits for the axes ticks for the plot.
        Format: xlim=[<x-axis lower limit>, <x-axis upper limit>],
                ylim=[<y-axis lower limit>, <y-axis upper limit>]
    colorbar_formatter : matplotlib.ticker.FuncFormatter or None, optional
        Tick formatter function to define how the numeric value
        associated with each tick on the colorbar axis is formatted
        as a string. `FuncFormatter`s take exactly two arguments:
        `x` for the tick value and `pos` for the tick position,
        and must return a `str`. The `pos` argument is used
        internally by Matplotlib.
        If None, then default tick values will be used. Defaults to None.
        See: https://matplotlib.org/2.0.2/examples/pylab_examples/custom_ticker1.html
        (Wrapping the function with FuncFormatter is optional.)
    xlabel, ylabel : str or None, optional
        Axes labels for the x-axis and y-axis (respectively)
    nan_color : str or Sequence of float or None, optional
        Color to plot NaN pixels for the PDF report.
        For transparent, set to None.
        The color should given in a format recognized by matplotlib:
        https://matplotlib.org/stable/users/explain/colors/colors.html
        Defaults to "blue".
    """

    # Instantiate the figure object
    # (Need to instantiate it outside of the plotting function
    # in order to later modify the plot for saving purposes.)
    f = plt.figure(figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE)
    ax = plt.gca()

    # Decimate image to a size that fits on the axes without interpolation
    # and without making the size (in MB) of the PDF explode.
    img_arr = nisarqa.downsample_img_to_size_of_axes(
        ax=ax, arr=img_arr, mode="multilook"
    )

    # grayscale
    cmap = plt.cm.gray

    if nan_color is not None:
        # set color of NaN pixels
        cmap.set_bad(nan_color)

    # Plot the img_arr image.
    ax_img = ax.imshow(X=img_arr, cmap=cmap, interpolation="none")

    # Add Colorbar
    cbar = plt.colorbar(ax_img, ax=ax)

    if colorbar_formatter is not None:
        cbar.ax.yaxis.set_major_formatter(colorbar_formatter)

    ## Label the plot
    f.suptitle(fig_title)
    format_axes_ticks_and_labels(
        ax=ax,
        xlim=xlim,
        ylim=ylim,
        img_arr_shape=np.shape(img_arr),
        title=ax_title,
        xlabel=xlabel,
        ylabel=ylabel,
    )

    # Make sure axes labels do not get cut off
    f.tight_layout()

    # Append figure to the output PDF
    plots_pdf.savefig(f)

    # Close the plot
    plt.close(f)


def format_axes_ticks_and_labels(
    ax: Axes,
    xlim: Optional[Sequence[float]] = None,
    ylim: Optional[Sequence[float]] = None,
    img_arr_shape: Optional[Sequence[int]] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
) -> None:
    """
    Format the tick marks and labels on the given axes object.

    Parameters
    ----------
    ax : matplotlib.axis.Axes
        The axes object to be modified. This axes' tick marks, labels, and
        title will be formatted as specified by the parameters provided to
        this function. `ax` should be the full size of `fig`.
    xlim, ylim : sequence of numeric or None, optional
        Lower and upper limits for the axes ticks for the plot.
        Format: xlim=[<x-axis lower limit>, <x-axis upper limit>],
                ylim=[<y-axis lower limit>, <y-axis upper limit>]
        If `xlim` is None, the x-axes ticks and labels will not be modified.
        Similar for `ylim`. (They are handled independently.) Defaults to None.
    img_arr_shape : pair of ints or None, optional
        The shape of the image which will be placed on `ax`. In practise, this
        establishes the aspect ratio for the axes.
        Required if `xlim` or `ylim` are specified; otherwise will be ignored.
    title : str or None, optional
        The title for the axes. Defaults to None (no title added).
    xlabel, ylabel : str or None, optional
        Axes labels for the x-axis and y-axis (respectively).
        Defaults to None (no labels added).
    """

    # If xlim or ylim are not provided, let Matplotlib auto-assign the ticks.
    # Otherwise, dynamically calculate and set the ticks w/ labels for
    # the x-axis and/or y-axis.
    # (Attempts to set the limits by using the `extent` argument for
    # matplotlib.imshow() caused significantly distorted images.
    # So, compute and set the ticks w/ labels manually.)
    if xlim is not None or ylim is not None:
        if img_arr_shape is None:
            raise ValueError("Must provide `img_arr_shape` input.")

        # Set the density of the ticks on the figure
        ticks_per_inch = 2.5

        # Get the dimensions of the figure object in inches
        fig_w, fig_h = ax.get_figure().get_size_inches()

        # Get the dimensions of the image array in pixels
        W = img_arr_shape[1]
        H = img_arr_shape[0]

        # Update variables to the actual, displayed image size
        # (The actual image will have a different aspect ratio
        # than the Matplotlib figure window's aspect ratio.
        # But, altering the Matplotlib figure window's aspect ratio
        # will lead to inconsistently-sized pages in the output PDF.)
        if H / W >= fig_h / fig_w:
            # image will be limited by its height, so
            # it will not use the full width of the figure
            fig_w = W * (fig_h / H)
        else:
            # image will be limited by its width, so
            # it will not use the full height of the figure
            fig_h = H * (fig_w / W)

    if xlim is not None:
        # Compute num of xticks to use
        num_xticks = int(ticks_per_inch * fig_w)

        # Always have a minimum of 2 labeled ticks
        num_xticks = max(num_xticks, 2)

        # Specify where we want the ticks, in pixel locations.
        xticks = np.linspace(0, img_arr_shape[1], num_xticks)
        ax.set_xticks(xticks)

        # Specify what those pixel locations correspond to in data coordinates.
        # By default, np.linspace is inclusive of the endpoint
        xticklabels = [
            "{:.1f}".format(i)
            for i in np.linspace(start=xlim[0], stop=xlim[1], num=num_xticks)
        ]
        ax.set_xticklabels(xticklabels, rotation=45)

    if ylim is not None:
        # Compute num of yticks to use
        num_yticks = int(ticks_per_inch * fig_h)

        # Always have a minimum of 2 labeled ticks
        num_yticks = max(num_yticks, 2)

        # Specify where we want the ticks, in pixel locations.
        yticks = np.linspace(0, img_arr_shape[0], num_yticks)
        ax.set_yticks(yticks)

        # Specify what those pixel locations correspond to in data coordinates.
        # By default, np.linspace is inclusive of the endpoint
        yticklabels = [
            "{:.1f}".format(i)
            for i in np.linspace(start=ylim[0], stop=ylim[1], num=num_yticks)
        ]
        ax.set_yticklabels(yticklabels)

    # Label the Axes
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)

    # Add title
    if title is not None:
        ax.set_title(title, fontsize=10)


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


def add_hist_to_axis(
    axis: Axes, counts: np.ndarray, edges: np.ndarray, label: str | None = None
) -> None:
    """Add the plot of the given counts and edges to the
    axis object. Points will be centered in each bin,
    and the plot will be denoted `label` in the legend.
    """
    bin_centers = 0.5 * (edges[:-1] + edges[1:])
    axis.plot(bin_centers, counts, label=label)


@nisarqa.log_function_runtime
def process_range_spectra(
    product: nisarqa.RSLC,
    params: nisarqa.RangeSpectraParamGroup,
    stats_h5: h5py.File,
    report_pdf: PdfPages,
) -> None:
    """
    Generate the RSLC Range Spectra plot(s) and save to PDF and stats.h5.

    Generate the RSLC Range Spectra; save the plot
    to the graphical summary .pdf file and the data to the
    statistics .h5 file.

    Power Spectral Density (PSD) is computed in decibels referenced to
    1/hertz (dB re 1/Hz) units, and Frequency in Hz or MHz (specified
    per `params.hz_to_mhz`).

    Parameters
    ----------
    product : nisarqa.RSLC
        Input RSLC product.
    params : nisarqa.RangeSpectraParamGroup
        A structure containing the parameters for processing
        and outputting the range spectra.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the range spectra plots plot to.
    """

    # Generate and store the range spectra plots
    for freq in product.freqs:
        with nisarqa.log_runtime(
            f"`generate_range_spectra_single_freq` for Frequency {freq}"
        ):
            generate_range_spectra_single_freq(
                product=product,
                freq=freq,
                params=params,
                stats_h5=stats_h5,
                report_pdf=report_pdf,
            )


def generate_range_spectra_single_freq(
    product: nisarqa.RSLC,
    freq: str,
    params: nisarqa.RangeSpectraParamGroup,
    stats_h5: h5py.File,
    report_pdf: PdfPages,
) -> None:
    """
    Generate the RSLC Range Spectra for a single frequency.

    Generate the RSLC Range Spectra; save the plot
    to the graphical summary .pdf file and the data to the
    statistics .h5 file.

    Power Spectral Density (PSD) is computed in decibels referenced to
    1/hertz (dB re 1/Hz) units, and Frequency in Hz or MHz (specified
    per `params.hz_to_mhz`).

    Parameters
    ----------
    product : nisarqa.RSLC
        Input RSLC product.
    freq : str
        Frequency name for the range power spectra to be processed,
        e.g. 'A' or 'B'
    params : RangeSpectraParamGroup
        A structure containing the parameters for processing
        and outputting the spectra.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the range spectra plots plot to.
    """
    log = nisarqa.get_logger()
    log.info(f"Generating Range Spectra for Frequency {freq}...")

    # Plot the range spectra using strictly increasing sample frequencies
    # (no discontinuity).
    fft_shift = True

    # Get the FFT spacing
    # Because `freq` is fixed, and all polarizations within
    # the same frequency will have the same `fft_freqs`.
    # So, we only need to do this computation one time.
    first_pol = product.get_pols(freq=freq)[0]
    with product.get_raster(freq, first_pol) as img:
        # Compute the sample rate
        # c/2 for radar energy round-trip; units for `sample_rate` will be Hz
        dr = product.get_slant_range_spacing(freq)
        sample_rate = (constants.c / 2.0) / dr

        fft_freqs = nisarqa.generate_fft_freqs(
            num_samples=img.data.shape[1],
            sampling_rate=sample_rate,
            fft_shift=fft_shift,
        )

        proc_center_freq = product.get_processed_center_frequency(freq)

        if params.hz_to_mhz:
            fft_freqs = nisarqa.hz2mhz(fft_freqs)
            proc_center_freq = nisarqa.hz2mhz(proc_center_freq)

        abbreviated_units, hdf5_units = _get_units_hz_or_mhz(params.hz_to_mhz)

    # Save x-axis values to stats.h5 file
    nisarqa.create_dataset_in_h5group(
        h5_file=stats_h5,
        grp_path=nisarqa.STATS_H5_QA_FREQ_GROUP % (product.band, freq),
        ds_name="rangeSpectraFrequencies",
        ds_data=fft_freqs,
        ds_units=hdf5_units,
        ds_description=(
            f"Frequency coordinates for Frequency {freq} range power spectra."
        ),
    )

    # Plot the Range Power Spectra for each pol onto the same axes.
    fig, ax = plt.subplots(
        nrows=1, ncols=1, figsize=nisarqa.FIG_SIZE_ONE_PLOT_PER_PAGE
    )

    # Use custom cycler for accessibility
    ax.set_prop_cycle(nisarqa.CUSTOM_CYCLER)

    rng_spec_units_pdf = "dB re 1/Hz"
    rng_spec_units_hdf5 = "decibel re 1/hertz"

    for pol in product.get_pols(freq):
        with product.get_raster(freq=freq, pol=pol) as img:
            with nisarqa.log_runtime(
                f"`compute_range_spectra_by_tiling` for Frequency {freq}"
                f" Polarization {pol} with shape {img.data.shape} using"
                f" azimuth decimation of {params.az_decimation} and tile"
                f" height of {params.tile_height}"
            ):
                # Get the Range Spectra
                # (The returned array is in dB re 1/Hz)
                rng_spectrum = nisarqa.compute_range_spectra_by_tiling(
                    arr=img.data,
                    sampling_rate=sample_rate,
                    az_decimation=params.az_decimation,
                    tile_height=params.tile_height,
                    fft_shift=fft_shift,
                )

            # Save normalized range power spectra values to stats.h5 file
            nisarqa.create_dataset_in_h5group(
                h5_file=stats_h5,
                grp_path=img.stats_h5_group_path,
                ds_name="rangePowerSpectralDensity",
                ds_data=rng_spectrum,
                ds_units=rng_spec_units_hdf5,
                ds_description=(
                    "Normalized range power spectral density for Frequency"
                    f" {freq}, Polarization {pol}."
                ),
            )

            # Add this power spectrum to the figure
            ax.plot(fft_freqs, rng_spectrum, label=pol)

    # Label the Plot
    ax.set_title(f"Range Power Spectra for Frequency {freq}\n")
    ax.set_xlabel(f"Frequency rel. {proc_center_freq} {abbreviated_units}")

    ax.set_ylabel(f"Power Spectral Density ({rng_spec_units_pdf})")

    ax.legend(loc="upper right")
    ax.grid(visible=True)

    # Save complete plots to graphical summary pdf file
    report_pdf.savefig(fig)

    # Close the plot
    plt.close()

    log.info(f"Range Power Spectra for Frequency {freq} complete.")


@nisarqa.log_function_runtime
def process_azimuth_spectra(
    product: nisarqa.RSLC,
    params: nisarqa.AzimuthSpectraParamGroup,
    stats_h5: h5py.File,
    report_pdf: PdfPages,
) -> None:
    """
    Generate the RSLC Azimuth Spectra plot(s) and save to PDF and stats.h5.

    Generate the RSLC Azimuth Spectra; save the plots to the PDF and
    statistics to the .h5 file. For each frequency+polarization, azimuth
    spectra plots are generated for three subswaths: one at near range,
    one at mid range, and one at far range.
    The size of the subswaths is specified in `params`; the azimuth spectra
    are formed by averaging the contiguous range samples in each subswath.

    Power Spectral Density (PSD) is computed in decibels referenced to
    1/hertz (dB re 1/Hz) units, and Frequency in Hz or MHz (specified
    per `params.hz_to_mhz`).

    Parameters
    ----------
    product : nisarqa.RSLC
        Input RSLC product.
    params : nisarqa.AzimuthSpectraParamGroup
        A structure containing the parameters for processing
        and outputting the azimuth spectra.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the range spectra plots plot to.
    """

    # Generate and store the az spectra plots
    for freq in product.freqs:
        with nisarqa.log_runtime(
            f"`generate_az_spectra_single_freq` for Frequency {freq}"
        ):
            generate_az_spectra_single_freq(
                product=product,
                freq=freq,
                params=params,
                stats_h5=stats_h5,
                report_pdf=report_pdf,
            )


def generate_az_spectra_single_freq(
    product: nisarqa.RSLC,
    freq: str,
    params: nisarqa.AzimuthSpectraParamGroup,
    stats_h5: h5py.File,
    report_pdf: PdfPages,
) -> None:
    """
    Generate the RSLC Azimuth Spectra for a single frequency.

    Generate the RSLC Azimuth Spectra; save the plots to the PDF and
    statistics to the .h5 file. An azimuth spectra plot is computed for
    each of three subswaths: near range, mid range, and far range.
    The size of the subswaths is specified in `params`; the azimuth spectra
    are formed by averaging the contiguous range samples in each subswath.

    Power Spectral Density (PSD) is computed in decibels referenced to
    1/hertz (dB re 1/Hz) units, and Frequency in Hz or MHz (specified
    per `params.hz_to_mhz`).

    Parameters
    ----------
    product : nisarqa.RSLC
        Input RSLC product.
    freq : str
        Frequency name for the azimuth power spectra to be processed,
        e.g. 'A' or 'B'
    params : AzimuthSpectraParamGroup
        A structure containing the parameters for processing
        and outputting the spectra.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the spectra plots plot to.
    """
    log = nisarqa.get_logger()
    log.info(f"Generating Azimuth Power Spectra for Frequency {freq}...")

    # Plot the az spectra using strictly increasing sample frequencies
    # (no discontinuity).
    fft_shift = True

    # TODO: Consider breaking this out into a separate function that returns
    # fft_freqs and fft freq units
    # Get the FFT spacing (will be the same for all product images):

    # Compute the sample rate
    # zero doppler time is in seconds; units for `sample_rate` will be Hz
    da = product.get_zero_doppler_time_spacing()
    sample_rate = 1 / da

    # Get the number of range lines
    first_pol = product.get_pols(freq=freq)[0]
    with product.get_raster(freq, first_pol) as img:
        num_range_lines = img.data.shape[0]

    # Compute fft_freqs
    fft_freqs = nisarqa.generate_fft_freqs(
        num_samples=num_range_lines,
        sampling_rate=sample_rate,
        fft_shift=fft_shift,
    )

    if params.hz_to_mhz:
        fft_freqs = nisarqa.hz2mhz(fft_freqs)

    abbreviated_units, hdf5_units = _get_units_hz_or_mhz(params.hz_to_mhz)

    # Save x-axis values to stats.h5 file
    grp_path = nisarqa.STATS_H5_QA_DATA_GROUP % product.band
    ds_name = "azimuthSpectraFrequencies"
    if f"{grp_path}/{ds_name}" not in stats_h5:
        nisarqa.create_dataset_in_h5group(
            h5_file=stats_h5,
            grp_path=grp_path,
            ds_name=ds_name,
            ds_data=fft_freqs,
            ds_units=hdf5_units,
            ds_description=(
                f"Frequency coordinates for azimuth power spectra."
            ),
        )

    # Plot the Azimuth Power Spectra for each pol+subswath onto the same axes
    fig, all_axes = plt.subplots(
        nrows=3, ncols=1, figsize=nisarqa.FIG_SIZE_THREE_PLOTS_PER_PAGE_STACKED
    )

    ax_near, ax_mid, ax_far = all_axes

    fig.suptitle(f"Azimuth Power Spectra for Frequency {freq}")

    # Use custom cycler for accessibility
    for ax in all_axes:
        ax.set_prop_cycle(nisarqa.CUSTOM_CYCLER)

    az_spec_units_pdf = "dB re 1/Hz"
    az_spec_units_hdf5 = "decibel re 1/hertz"

    # We want the y-axis label limits to be consistent for all three plots.
    # Initialize variables to track the limits.
    y_min = np.nan
    y_max = np.nan

    for pol in product.get_pols(freq):
        with product.get_raster(freq=freq, pol=pol) as img:

            for subswath, ax in zip(("Near", "Mid", "Far"), all_axes):
                img_width = np.shape(img.data)[1]
                num_col = params.num_columns

                # Get the start and stop column index for each subswath.
                if (num_col == -1) or (num_col >= img_width):
                    col_slice = slice(0, img_width)
                else:
                    if subswath == "Near":
                        col_slice = slice(0, num_col)
                    elif subswath == "Far":
                        col_slice = slice(img_width - num_col, img_width)
                    else:
                        assert subswath == "Mid"
                        mid_img = img_width // 2
                        mid_num_col = num_col // 2
                        start_idx = mid_img - mid_num_col
                        col_slice = slice(start_idx, start_idx + num_col)

                with nisarqa.log_runtime(
                    f"`compute_az_spectra_by_tiling` for Frequency {freq},"
                    f" Polarization {pol}, {subswath}-Range subswath"
                    f" (columns [{col_slice.start}:{col_slice.stop}],"
                    f" step={1 if col_slice.step is None else col_slice.step})"
                    f" using tile width {params.tile_width}"
                ):
                    # The returned array is in dB re 1/Hz
                    az_spectrum = nisarqa.compute_az_spectra_by_tiling(
                        arr=img.data,
                        sampling_rate=sample_rate,
                        subswath_slice=col_slice,
                        tile_width=params.tile_width,
                        fft_shift=fft_shift,
                    )

                # Save normalized power spectra values to stats.h5 file
                nisarqa.create_dataset_in_h5group(
                    h5_file=stats_h5,
                    grp_path=img.stats_h5_group_path,
                    ds_name=f"azimuthPowerSpectralDensity{subswath}Range",
                    ds_data=az_spectrum,
                    ds_units=az_spec_units_hdf5,
                    ds_description=(
                        "Normalized azimuth power spectral density for"
                        f" Frequency {freq}, Polarization {pol}"
                        f" {subswath}-Range."
                    ),
                    ds_attrs={
                        "subswathStartIndex": col_slice.start,
                        "subswathStopIndex": col_slice.stop,
                    },
                )

                # Add this power spectrum to the figure
                ax.plot(fft_freqs, az_spectrum, label=pol)
                ax.grid(visible=True)

                y_ax_min, y_ax_max = ax.get_ylim()
                y_min = np.nanmin([y_min, y_ax_min])
                y_max = np.nanmax([y_max, y_ax_max])

                # Label the Plot
                ax.set_title(
                    f"{subswath}-Range (columns {col_slice.start}-{col_slice.stop})",
                    fontsize=9,
                )

    # All axes can share the same y-label. Attach that label to the middle
    # axes, so that it is centered.
    ax_mid.set_ylabel(f"Power Spectral Density ({az_spec_units_pdf})")

    ax_near.xaxis.set_ticklabels([])
    ax_mid.xaxis.set_ticklabels([])
    ax_far.set_xlabel(f"Frequency ({abbreviated_units})")

    # Make the y axis labels consistent
    for ax in all_axes:
        ax.set_ylim([y_min, y_max])

    ax_near.legend(loc="upper right")

    # Save complete plots to graphical summary pdf file
    report_pdf.savefig(fig)

    # Close the plot
    plt.close()

    log.info(f"Azimuth Power Spectra for Frequency {freq} complete.")


def _get_units_hz_or_mhz(mhz: bool) -> tuple[str, str]:
    """
    Return the abbreviated and long units for Hz or MHz.

    Parameters
    ----------
    mhz : bool
        True for MHz units; False for Hz units.

    Returns
    -------
    abbreviated_units : str
        "MHz" if `mhz`, otherwise "Hz".
    long_units : str
        "megahertz" if `mhz`, otherwise "hertz".
    """
    if mhz:
        abbreviated_units = "MHz"
        long_units = "megahertz"
    else:
        abbreviated_units = "Hz"
        long_units = "hertz"

    return abbreviated_units, long_units


__all__ = nisarqa.get_all(__name__, objects_to_skip)
