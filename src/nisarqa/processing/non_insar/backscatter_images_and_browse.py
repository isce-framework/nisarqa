from __future__ import annotations

import functools
import os
from pathlib import Path

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
    *,
    out_dir: str | os.Pathlike,
    browse_filename: str,
    kml_filename: str,
    input_raster_represents_power: bool = False,
    plot_title_prefix: str = "Backscatter Coefficient",
) -> None:
    """
    Generate Backscatter Image plots for the Report PDF and browse product.

    This function generates both the PNG and KML components of the
    browse product.

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
    out_dir : path-like
        The directory to write the output PNG and KML file(s) to. This
        directory must already exist.
    browse_filename : str
        The basename of the output browse image PNG file. The file will be
        created in `out_dir`. Example: "BROWSE.png".
    kml_filename : str
        The basename of the output browse image KML file. The file will be
        created in `out_dir`. Example: "BROWSE.kml".
    input_raster_represents_power : bool, optional
        The input dataset rasters associated with these histogram parameters
        should have their pixel values represent either power or root power.
        If `True`, then QA SAS assumes the input data already represents
        power and uses the pixels' magnitudes for computations.
        If `False`, then QA SAS assumes the input data represents root power
        aka magnitude and will handle the full computation to power using
        the formula:  power = abs(<magnitude>)^2 .
        Defaults to False (root power).
    plot_title_prefix : str, optional
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

                if params.output_individual_pngs:

                    def _indiv_path(
                        basename: str | os.PathLike,
                    ) -> str:
                        base = Path(basename)
                        return f"{base.stem}_{freq}_{pol}{base.suffix}"

                    nisarqa.plot_to_grayscale_png(
                        img_arr=corrected_img,
                        filepath=Path(out_dir, _indiv_path(browse_filename)),
                    )

                    # Generate the KML that corresponds to the individual PNG
                    nisarqa.write_latlonquad_to_kml(
                        llq=product.get_browse_latlonquad(),
                        output_dir=out_dir,
                        kml_filename=_indiv_path(kml_filename),
                        png_filename=_indiv_path(browse_filename),
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
    browse_path = Path(out_dir, browse_filename)
    product.save_browse(pol_imgs=pol_imgs_for_browse, filepath=browse_path)

    # Generate the KML that corresponds to the browse image
    nisarqa.write_latlonquad_to_kml(
        llq=product.get_browse_latlonquad(),
        output_dir=out_dir,
        kml_filename=kml_filename,
        png_filename=browse_filename,
    )
    log = nisarqa.get_logger()
    log.info(f"Browse image PNG file saved to {browse_path}")
    log.info(f"Browse image KML file saved to {Path(out_dir, kml_filename)}")


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


def compute_multilooked_backscatter_by_tiling(
    arr, nlooks, input_raster_represents_power=False, tile_shape=(512, -1)
):
    """
    Compute the multilooked backscatter array (linear units) by tiling.

    Parameters
    ----------
    arr : array_like
        The input 2D array
    nlooks : tuple of ints
        Number of looks along each axis of the input array to be
        averaged during multilooking.
        Format: (num_rows, num_cols)
    input_raster_represents_power : bool, optional
        The input dataset rasters associated with these histogram parameters
        should have their pixel values represent either power or root power.
        If `True`, then QA SAS assumes the input data already represents
        power and uses the pixels' magnitudes for computations.
        If `False`, then QA SAS assumes the input data represents root power
        aka magnitude and will handle the full computation to power using
        the formula:  power = abs(<magnitude>)^2 .
        Defaults to False (root power).
    tile_shape : tuple of ints
        Shape of each tile to be processed. If `tile_shape` is
        larger than the shape of `arr`, or if the dimensions of `arr`
        are not integer multiples of the dimensions of `tile_shape`,
        then smaller tiles may be used.
        -1 to use all rows / all columns (respectively).
        Format: (num_rows, num_cols)
        Defaults to (512, -1) to use all columns (i.e. full rows of data)
        and leverage Python's row-major ordering.

    Returns
    -------
    multilook_img : numpy.ndarray
        The multilooked backscatter image in linear units

    Notes
    -----
    If the length of the input array along a given axis is not evenly divisible by the
    specified number of looks, any remainder samples from the end of the array will be
    discarded in the output.

    If a cell in the input array is nan (invalid), then the corresponding cell in the
    output array will also be nan.

    """
    arr_shape = np.shape(arr)

    if len(arr_shape) != 2:
        raise ValueError(
            f"Input array has shape {arr_shape} but can only have 2 dimensions."
        )

    if (arr_shape[0] < nlooks[0]) or (arr_shape[1] < nlooks[1]):
        raise ValueError(
            f"{nlooks=} but the array has has dimensions {arr_shape}. For each "
            "dimension, `nlooks` must be <= the length of that dimension."
        )

    if tile_shape[0] == -1:
        tile_shape = (arr_shape[0], tile_shape[1])
    if tile_shape[1] == -1:
        tile_shape = (tile_shape[0], arr_shape[1])

    if len(nlooks) != 2:
        raise ValueError(f"`nlooks` must be a tuple of length 2: {nlooks}")
    if not all(isinstance(x, int) for x in nlooks):
        raise ValueError(f"`nlooks` must contain only ints: {nlooks}")

    # Compute the portion (shape) of the input array
    # that is integer multiples of nlooks.
    # This will be used to trim off (discard) the 'uneven edges' of the image,
    # i.e. the pixels beyond the largest integer multiples of nlooks.
    in_arr_valid_shape = tuple(
        [(m // n) * n for m, n in zip(arr_shape, nlooks)]
    )

    # Compute the shape of the output multilooked array
    final_out_arr_shape = tuple([m // n for m, n in zip(arr_shape, nlooks)])

    # Adjust the tiling shape to be integer multiples of nlooks
    # Otherwise, the tiling will get messy to book-keep.

    # If a tile dimension is smaller than nlooks, grow it to be the same length
    if tile_shape[0] < nlooks[0]:
        tile_shape = (nlooks[0], tile_shape[1])
    if tile_shape[1] < nlooks[1]:
        tile_shape = (tile_shape[0], nlooks[1])

    # Next, shrink the tile shape to be an integer multiple of nlooks
    in_tiling_shape = tuple([(m // n) * n for m, n in zip(tile_shape, nlooks)])

    out_tiling_shape = tuple([m // n for m, n in zip(tile_shape, nlooks)])

    # Create the Iterators
    input_iter = nisarqa.TileIterator(
        arr_shape=in_arr_valid_shape,
        axis_0_tile_dim=in_tiling_shape[0],
        axis_1_tile_dim=in_tiling_shape[1],
    )
    out_iter = nisarqa.TileIterator(
        arr_shape=final_out_arr_shape,
        axis_0_tile_dim=out_tiling_shape[0],
        axis_1_tile_dim=out_tiling_shape[1],
    )

    # Create an inner function for this use case.
    def calc_backscatter_and_multilook(arr):
        # square the pixel values (e.g to convert from magnitude to power),
        # if requested.
        # Otherwise, take the absolute value to ensure we're using the
        # magnitude for either real or complex values
        out = (
            np.abs(arr)
            if input_raster_represents_power
            else nisarqa.arr2pow(arr)
        )

        # Multilook
        out = nisarqa.multilook(out, nlooks)

        return out

    # Instantiate the output array
    multilook_img = np.zeros(
        final_out_arr_shape, dtype=np.float32
    )  # 32 bit precision

    # Ok to pass the full input array; the tiling iterators
    # are constrained such that the 'uneven edges' will be ignored.
    nisarqa.process_arr_by_tiles(
        arr,
        multilook_img,
        calc_backscatter_and_multilook,
        input_batches=input_iter,
        output_batches=out_iter,
    )

    return multilook_img


__all__ = nisarqa.get_all(__name__, objects_to_skip)
