import os
import warnings
from dataclasses import fields

import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

# List of objects from the import statements that
# should not be included when importing this module
objects_to_skip = nisarqa.get_all(name=__name__)


def verify_gcov(user_rncfg):
    """
    Verify an GCOV product based on the input file, parameters, etc.
    specified in the input runconfig file.

    This is the main function for running the entire QA workflow for this
    product. It will run based on the options supplied in the
    input runconfig file.
    The input runconfig file must follow the standard QA runconfig format
    for this product. Run the command line command:
            nisar_qa dumpconfig <product name>
    to generate an example template with default parameters for this product.

    Parameters
    ----------
    user_rncfg : dict
        A nested dict whose structure matches this product's QA runconfig
        yaml file and which contains the parameters needed to run its QA SAS.
    """

    # Build the GCOVRootParamGroup parameters per the runconfig
    try:
        root_params = nisarqa.build_root_params(
            product_type="gcov", user_rncfg=user_rncfg
        )
    except nisarqa.ExitEarly:
        # No workflows were requested. Exit early.
        print(
            "All `workflows` set to `False` in the runconfig, "
            "so no QA outputs will be generated. This is not an error."
        )
        return

    # Start logger
    # TODO get logger from Brian's code and implement here
    # For now, output the stub log file.
    nisarqa.output_stub_files(
        output_dir=root_params.get_output_dir(), stub_files="log_txt"
    )

    # Log the values of the parameters.
    # Currently, this prints to stdout. Once the logger is implemented,
    # it should log the values directly to the log file.
    root_params.log_parameters()

    # For readibility, store possible output filenames in variables.
    input_file = root_params.input_f.qa_input_file
    out_dir = root_params.get_output_dir()
    browse_file_png = out_dir / root_params.get_browse_png_filename()
    browse_file_kml = out_dir / root_params.get_kml_browse_filename()
    report_file = out_dir / root_params.get_report_pdf_filename()
    stats_file = out_dir / root_params.get_stats_h5_filename()
    summary_file = out_dir / root_params.get_summary_csv_filename()

    print(f"Starting Quality Assurance for input file: {input_file}")

    if root_params.workflows.validate:
        # TODO Validate file structure
        # (After this, we can assume the file structure for all
        # subsequent accesses to it)
        # NOTE: Refer to the original 'get_bands()' to check that in_file
        # contains metadata, swaths, Identification groups, and that it
        # is SLC/RSLC compliant. These should trigger a fatal error!
        # NOTE: Refer to the original get_freq_pol() for the verification
        # checks. This could trigger a fatal error!

        # These reports will be saved to the SUMMARY.csv file.
        # For now, output the stub file
        nisarqa.output_stub_files(output_dir=out_dir, stub_files="summary_csv")
        print(f"Input file validation PASS/FAIL checks saved: {summary_file}")
        print(f"Input file validation complete.")

        # TODO - this GCOV validation check should be integrated into
        # the actual product validation. For now, we'll leave it here.
        with nisarqa.open_h5_file(input_file, mode="r") as in_file:
            # Run the requested workflows
            pols = nisarqa.rslc.get_pols(in_file)
            for band in pols:
                for freq in pols[band]:
                    for pol in pols[band][freq]:
                        if pol in nisarqa.GCOV_DIAG_POLS:
                            continue
                        elif pol in nisarqa.GCOV_OFF_DIAG_POLS:
                            warnings.warn(
                                f"GCOV product contains off-diagonal term {pol}.",
                                RuntimeWarning,
                            )

    if root_params.workflows.qa_reports:
        # TODO qa_reports will add to the SUMMARY.csv file.
        # For now, make sure that the stub file is output
        if not os.path.isfile(summary_file):
            nisarqa.output_stub_files(
                output_dir=out_dir,
                stub_files="summary_csv",
            )
            print(
                f"Input file validation PASS/FAIL checks saved: {summary_file}"
            )
            print(f"Input file validation complete.")

        # TODO qa_reports will create the BROWSE.kml file.
        # For now, make sure that the stub file is output
        nisarqa.output_stub_files(
            output_dir=out_dir,
            stub_files="browse_kml",
        )
        print("Processing of browse image kml complete.")
        print(f"Browse image kml file saved to {browse_file_kml}")

        with nisarqa.open_h5_file(
            input_file, mode="r"
        ) as in_file, nisarqa.open_h5_file(
            stats_file, mode="w"
        ) as stats_h5, PdfPages(
            report_file
        ) as report_pdf:
            print("Beginning processing of `qa_reports` items...")

            # Note: `pols` contains references to datasets in the open input file.
            # All processing with `pols` must be done within this context manager,
            # or the references will be closed and inaccessible.
            pols = nisarqa.rslc.get_pols(in_file)

            # Save frequency/polarization info from `pols` to stats file
            nisarqa.rslc.save_nisar_freq_metadata_to_h5(
                stats_h5=stats_h5, pols=pols
            )

            # Save the processing parameters to the stats.h5 file
            root_params.save_params_to_stats_file(
                h5_file=stats_h5, bands=tuple(pols.keys())
            )
            print(f"QA Processing Parameters saved to {stats_file}")

            # Copy the Product identification group to STATS.h5
            nisarqa.rslc.save_NISAR_identification_group_to_h5(
                nisar_h5=in_file, stats_h5=stats_h5
            )
            print(f"Input file Identification group copied to {stats_file}")

            input_raster_represents_power = True
            name_of_backscatter_content = (
                r"GCOV Backscatter Coefficient ($\gamma^0$)"
            )

            # Generate the Backscatter Image and Browse Image
            nisarqa.rslc.process_backscatter_imgs_and_browse(
                pols=pols,
                params=root_params.backscatter_img,
                stats_h5=stats_h5,
                report_pdf=report_pdf,
                product_type="gcov",
                plot_title_prefix=name_of_backscatter_content,
                input_raster_represents_power=input_raster_represents_power,
                browse_filename=browse_file_png,
            )
            print("Processing of Backscatter images complete.")
            print(f"Browse image PNG file saved to {browse_file_png}")

            # Generate the Backscatter and Phase Histograms
            nisarqa.rslc.process_backscatter_and_phase_histograms(
                pols=pols,
                params=root_params.histogram,
                stats_h5=stats_h5,
                report_pdf=report_pdf,
                plot_title_prefix=name_of_backscatter_content,
                input_raster_represents_power=input_raster_represents_power,
            )
            print("Processing of backscatter and phase histograms complete.")

            # Check for invalid values

            # Compute metrics for stats.h5

            print(f"PDF reports saved to {report_file}")
            print(f"HDF5 statistics saved to {stats_file}")
            print(f"CSV Summary PASS/FAIL checks saved to {summary_file}")
            print("`qa_reports` processing complete.")

    print(
        "Successful completion of QA SAS. Check log file for validation warnings and errors."
    )


def select_layers_for_gcov_browse(pols):
    """
    Assign the polarization layers in the input file to grayscale or
    RGBA channels for the GCOV Browse Image.

    Only on-diagonal terms will be used to create the browse image.
    See `Notes` for details on the possible NISAR modes and assigned channels
    for LSAR band.
    SSAR is currently only minimally supported, so only a grayscale image
    will be created. Prioritization order to select the freq/pol to use:
        For frequency: Freq A then Freq B.
        For polarization: 'HHHH', then 'VVVV', then the first polarization found.


    Parameters
    ----------
    pols : nested dict of GeoRaster
        Nested dict of GeoRaster objects, where each object represents
        a polarization dataset in `h5_file`.
        Format: pols[<band>][<freq>][<pol>] -> a GeoRaster
        Ex: pols['LSAR']['A']['HHHH'] -> the HHHH dataset, stored
                                       in a GeoRaster object

    Returns
    -------
    layers_for_browse : dict
        A dictionary containing the channel assignments.
        For GCOV, either `layers_for_browse['A']` or `layers_for_browse['B']`
        will exist, but not both. Its structure is:

        layers_for_browse['band']  : str
                                        Either 'LSAR' or 'SSAR'
        layers_for_browse['A']     : list of str, optional
                                        List of the Freq A polarization(s)
                                        required to create the browse image.
                                        Warning: Only on-diag terms supported.
        layers_for_browse['B']     : list of str, optional
                                        List of the Freq B polarizations
                                        required to create the browse image.
                                        Warning: Only on-diag terms supported.

    Notes
    -----
    Unlike RSLC products, the polarizations contained within a GCOV product
    do not map to the NISAR mode table. For GCOV, The user selects a subset
    of polarizations of the RSLC to process. With that subset, the GCOV
    SAS workflow verifies if it should symmetrize the cross-polarimetric
    channels (HV and VH) into a single cross-polarimetric channel (HV),
    and also verifies if it should generate the full covariance or only
    the diagonal terms.

    Usually polarimetric symmetrization is applied; symmetrization
    joins HV and VH into a single polarimetric channel HV.

    Layer selection for LSAR GCOV Browse:
     - Frequency A is used if available. Otherwise, Frequency B.
     - If only one polarization is available, or if the images are cross-pol,
     make one layer into grayscale. This function selects that layer.
     - Otherwise, generate an RGB color composition, per the algorithm
    described in `save_gcov_browse_img()`. This function will gather the
    largest subset of: {HHHH, VVVV, (HVHV or VHVH)}, in prep for that function.

    GCOV and RTC-S1 pixels are square on the ground, so the multilooking factor
    is the same in both directions, depending only in the expected output dimensions.

    See Also
    --------
    save_gcov_browse_img : Assigns color channels and generates the browse PNG

    """

    layers_for_browse = {}

    # Determine which band to use. LSAR has priority over SSAR.
    for b in ("LSAR", "SSAR"):
        if b in pols:
            layers_for_browse["band"] = b
            band = b
            break
    else:
        raise ValueError(
            f'Only "LSAR" and "SSAR" bands are supported: {list(pols)}'
        )

    # Check that the correct frequencies are available
    if not set(pols[band].keys()).issubset({"A", "B"}):
        raise ValueError(
            f"`pols['{band}']` contains {set(pols[band].keys())}"
            ", but must be a subset of {'A', 'B'}"
        )

    # Get the frequency sub-band containing science mode data.
    # This is always frequency A if present, otherwise B.
    freq = "A" if ("A" in pols[band]) else "B"

    # SSAR is not fully supported by QA, so just make a simple grayscale
    if band == "SSAR":
        # Prioritize Co-Pol
        if "HHHH" in pols[band][freq]:
            layers_for_browse[freq] = ["HHHH"]
        elif "VVVV" in pols[band][freq]:
            layers_for_browse[freq] = ["VVVV"]
        else:
            # Take the first available on-diagonal term
            for pol in pols[band][freq]:
                if pol[0:2] == pol[2:4]:
                    layers_for_browse[freq] = [pol]
                    break
            else:
                # Take first available pol, even if it is an off-diagonal term
                layers_for_browse[freq] = [pols[band][freq][0]]

        return layers_for_browse

    # The input file contains LSAR data. Will need to make
    # grayscale/RGB channel assignments

    # Get the available polarizations
    available_pols = list(pols[band][freq])

    # Keep only the on-diagonal polarizations
    # (On-diagonal terms have the same first two letters as second two letters,
    # e.g. HVHV or VVVV.)
    available_pols = [p for p in available_pols if (p[0:2] == p[2:4])]
    n_pols = len(available_pols)

    # Sanity check: There should always be on-diag pols for GCOV
    if n_pols == 0:
        raise ValueError("No on-diagonal polarizations found in input GCOV.")

    elif n_pols == 1:
        # Only one image; it will be grayscale
        layers_for_browse[freq] = available_pols

    elif all(p.startswith(("R", "L")) for p in available_pols):
        # Only compact pol(s) are available. Create grayscale.
        # Per the Prioritization Order, use first available polarization
        for pol in ("RHRH", "RVRV", "LHLH", "LVLV"):
            if pol in available_pols:
                layers_for_browse[freq] = [pol]
                break
        else:
            # Use first available pol
            layers_for_browse[freq] = [available_pols[0]]

        assert len(layers_for_browse[freq]) == 1

    else:
        # Only keep "HHHH", "HVHV", "VHVH", "VVVV".
        keep = [
            p
            for p in available_pols
            if (p in ("HHHH", "HVHV", "VHVH", "VVVV"))
        ]

        # Sanity Check
        assert len(keep) >= 1

        # If both cross-pol terms are available, only keep one
        if ("HVHV" in keep) and ("VHVH" in keep):
            if ("VVVV" in keep) and not ("HHHH" in keep):
                # Only VVVV is in keep, and not HHHH. So, prioritize
                # keeping VHVH with VVVV.
                keep.remove("HVHV")
            else:
                # prioritize keeping "HVHV"
                keep.remove("VHVH")

        layers_for_browse[freq] = keep

    # Sanity Checks
    if ("A" not in layers_for_browse) and ("B" not in layers_for_browse):
        raise ValueError(
            "Input file must contain either Frequency A or Frequency B iamges."
        )

    if len(layers_for_browse[freq]) == 0:
        raise ValueError(
            f"The input file's Frequency {freq} group does not contain "
            "the expected polarization names."
        )

    return layers_for_browse


def save_gcov_browse_img(pol_imgs, filepath):
    """
    Save the given polarization images to a RGB or Grayscale PNG with
    transparency.

    Dimensions of the output PNG (in pixels) will be the same as the dimensions
    of the input polarization image array(s). (No scaling will occur.)
    Non-finite values will be made transparent.

    Color Channels will be assigned per the following pseudocode:

        If pol_imgs.keys() contains only one image, then:
            grayscale = <that image>

        Else:
            Red: first available co-pol of the list [HHHH, VVVV]
            Green: first of the list [HVHV, VHVH, VVVV]
            if Green is VVVV:
                Blue: HHHH
            else:
                Blue: first co-pol of the list [VVVV, HHHH]

    Parameters
    ----------
    pol_imgs : dict of numpy.ndarray
        Dictionary of 2D array(s) that will be mapped to specific color
        channel(s) for the output browse PNG.
        If there are multiple image arrays, they must have identical shape.
        Format of dictionary:
            pol_imgs[<polarization>] : <2D numpy.ndarray image>, where
                <polarization> is a subset of: 'HHHH', 'HVHV', 'VVVV', 'VHVH',
                                               'RHRH', 'RVRV', 'LVLV', 'LHLH'
        Example:
            pol_imgs['HHHH'] : <2D numpy.ndarray image>
            pol_imgs['VVVV'] : <2D numpy.ndarray image>
    filepath : str
        Full filepath for where to save the browse image PNG.

    Notes
    -----
    Provided image array(s) must previously be image-corrected. This
    function will take the image array(s) as-is and will not apply additional
    image correction processing to them. This function directly combines
    the image(s) into a single browse image.

    If there are multiple input images, they must be thoughtfully prepared and
    standardized relative to each other prior to use by this function.
    For example, trying to combine a Freq A 20 MHz image
    and a Freq B 5 MHz image into the same output browse image might not go
    well, unless the image arrays were properly prepared and standardized
    in advance.

    See Also
    --------
    select_layers_for_gcov_browse : Function to select the layers
    """

    # WLOG, get the shape of the image arrays
    # They should all be the same shape; the check for this is below.
    first_img = next(iter(pol_imgs.values()))
    img_2D_shape = np.shape(first_img)
    for img in pol_imgs.values():
        # Input validation check
        if np.shape(img) != img_2D_shape:
            raise ValueError(
                "All image arrays in `pol_imgs` must have the same shape."
            )

    # Only on-diagonal terms are supported.
    if not set(pol_imgs.keys()).issubset(set(nisarqa.GCOV_DIAG_POLS)):
        raise ValueError(
            f"{pol_imgs.keys()=}, must be a subset of {nisarqa.GCOV_DIAG_POLS}"
        )

    # Assign channels

    if len(pol_imgs) == 1:
        # Single pol. Make a grayscale image.
        nisarqa.products.rslc.plot_to_grayscale_png(
            img_arr=first_img, filepath=filepath
        )

        # Return early, so that we do not try to plot to RGB
        return

    # Initialize variables. Later, check to ensure they were all used.
    red = None
    blue = None
    green = None

    for pol in ["HHHH", "VVVV"]:
        if pol in pol_imgs:
            red = pol_imgs[pol]
            break

    # There should only be one cross-pol in the input
    if ("HVHV" in pol_imgs) and ("VHVH" in pol_imgs):
        raise ValueError(
            "`pol_imgs` should only contain one cross-pol image."
            f"It contains {pol_imgs.keys()}. Please update logic in "
            "`_select_layers_for_gcov_browse()`"
        )

    for pol in ["HVHV", "VHVH", "VVVV"]:
        if pol in pol_imgs:
            green = pol_imgs[pol]

            if pol == "VVVV":
                # If we get here, this means two things:
                #   1: no cross-pol images were available
                #   2: only HHHH and VVVV are available
                # So, final assignment should be R: HHHH, G: VVVV, B: HHHH
                blue = pol_imgs["HHHH"]
            else:
                for pol2 in ["VVVV", "HHHH"]:
                    if pol2 in pol_imgs:
                        blue = pol_imgs[pol2]
                        break
            break

    # Sanity Check, and catch-all logic to make a browse image
    if any(arr is None for arr in (red, green, blue)):
        # If we get here, then the images provided are not one of the
        # expected cases. WLOG plot one of the image(s) in `pol_imgs`.
        warnings.warn(
            f"The images provided are not one of the expected cases to form "
            "the GCOV browse image. Grayscale image will be created by default."
        )

        for gray_img in pol_imgs.values():
            nisarqa.products.rslc.plot_to_grayscale_png(
                img_arr=gray_img, filepath=filepath
            )

    else:
        # Output the RGB Browse Image
        nisarqa.products.rslc.plot_to_rgb_png(
            red=red, green=green, blue=blue, filepath=filepath
        )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
