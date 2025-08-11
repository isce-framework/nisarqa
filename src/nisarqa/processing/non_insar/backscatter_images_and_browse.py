from __future__ import annotations

import functools

import h5py
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter

import nisarqa

from ..plotting_utils import apply_image_correction, invert_gamma_correction

objects_to_skip = nisarqa.get_all(name=__name__)


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

                nisarqa.img2pdf_grayscale(
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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
