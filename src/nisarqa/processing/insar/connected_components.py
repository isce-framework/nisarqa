from __future__ import annotations

import h5py
import matplotlib.colors as colors
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nisarqa

from ..plotting_utils import format_axes_ticks_and_labels

objects_to_skip = nisarqa.get_all(name=__name__)


def process_connected_components(
    product: nisarqa.UnwrappedGroup,
    params: nisarqa.ConnectedComponentsParamGroup,
    report_pdf: PdfPages,
    stats_h5: h5py.File,
) -> None:
    """
    Process connected components layer: metrics to STATS h5, plots to PDF.

    Parameters
    ----------
    product : nisarqa.UnwrappedGroup
        Input NISAR product.
    params : nisarqa.ConnectedComponentsParamGroup
        A structure containing processing parameters to generate the
        connected components layer plots and metrics.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        The output PDF file to append the unwrapped phase image plots to.
    stats_h5 : h5py.File
        The output file to save QA metrics, etc. to.
    """
    for freq in product.freqs:
        for pol in product.get_pols(freq=freq):
            with product.get_connected_components(freq=freq, pol=pol) as cc:
                # Compute % NaN, % Inf, % Fill, % near-zero, % invalid,
                # metrics first in case of malformed layers (which could cause
                # plotting to fail).
                nisarqa.compute_percentage_metrics(
                    raster=cc,
                    stats_h5=stats_h5,
                    params=params,
                )

                plot_connected_components_layer(
                    cc_raster=cc, report_pdf=report_pdf
                )

                # Compute the Connected Components metrics last. None of these
                # metrics should trigger the plotting to fail, so let's try to
                # finish the plots beforehand.
                nisarqa.connected_components_metrics(
                    cc_raster=cc,
                    stats_h5=stats_h5,
                    max_num_cc=params.max_num_cc,
                )


def plot_connected_components_layer(
    cc_raster: nisarqa.RadarRaster | nisarqa.GeoRaster,
    report_pdf: PdfPages,
) -> None:
    """
    Plot a connected components layer and a bar chart of percentages on PDF.

    Parameters
    ----------
    cc_raster : nisarqa.RadarRaster or nisarqa.GeoRaster
        *Raster of connected components data.
    report_pdf : matplotlib.backends.backend_pdf.PdfPages
        Output PDF file to append the generated plots to.
    """

    # Setup PDF page
    fig, (ax1, ax2) = plt.subplots(
        ncols=2,
        nrows=1,
        constrained_layout="tight",
        figsize=nisarqa.FIG_SIZE_TWO_PLOTS_PER_PAGE,
    )

    # Construct title for the overall PDF page.
    title = f"Connected Components Mask\n{cc_raster.name}"
    fig.suptitle(title)

    # Step 1: Compute metrics on full raster (We should not skip any CC!):
    cc_full = cc_raster.data[()]

    labels, percentages = nisarqa.get_unique_elements_and_percentages(cc_full)
    num_features = len(labels)

    # Step 2: Setup colormap and boundaries between integer values.
    # Note: `labels` is guaranteed to be sorted and unique values, but
    # depending on how the CC layer was created, there might be skipped values
    # in the labels, e.g. the CC layer only contains labels [0, 1, 3, 4].

    # Create a color map with distinct color for each connected component
    # If there are more than 10 connected components, simply repeat the colors.
    # (Per the product lead, it will likely be an edge case if more than
    # 10 connected components.)
    # Kludge: We need to ensure that the "fill value" color is white.
    # colors.ListedColormap is able to do the repeating automatically using
    # the `N` parameter, however, I don't know a clever way to then make
    # only fill value white. For now, simply constuct the full list manually.
    quot, rem = divmod(num_features, len(nisarqa.SEABORN_COLORBLIND))
    colors_list = nisarqa.SEABORN_COLORBLIND * quot
    colors_list += nisarqa.SEABORN_COLORBLIND[:rem]

    # If the raster contains any fill value pixels, set them to white
    # so they look "transparent" in the PDF
    fill_idx = np.where(labels == cc_raster.fill_value)[0]
    if fill_idx.size > 0:
        colors_list[fill_idx[0]] = (1.0, 1.0, 1.0, 0.0)  # transparent white

    # To create the colorbar for the CC image raster, we'll use a
    # a ListedColormap for the discrete colors, and use a BoundaryNorm for
    # to create a colormap based on discrete intervals. (BoundaryNorm maps
    # values to integers, instead of to e.g. the interval [0, 1].)
    # Reference:
    # https://www.geeksforgeeks.org/matplotlib-colors-listedcolormap-class-in-python/

    cmap = colors.ListedColormap(colors=colors_list)

    # Create a list of the boundaries (aka the halfway points) between
    # each integer label; also include the very max and min values
    # of the interval for the colorbar.
    # Hint: Visually, the "boundary" between two integer labels is where the
    # colorbar changes from one color to the next color.

    # Kludge: the `labels` returned above use the same dtype as `cc_full`.
    # As of March 2024, the product spec for the CC layer specifies a
    # dtype of unsigned int16 with a fill value of 65535. For the CC layer,
    # `0` designates pixels with invalid unwrapping, so `labels` will
    # typically be [0, ..., 65535].
    # Because 0 and 65535 are the min and max values for uint16, when
    # we try to subtract 1 and add 1 to those values below when creating the
    # `boundaries` variable, we'll run into overflow errors.
    # Prior to NumPy 2.0 (e.g. NumPy 1.26), the datatype would automatically
    # be promoted to avoid overflow. Starting with NumPy 2.0, datatypes were
    # no longer promoted. So, manually promote the datatype to avoid overflow.
    # Sources:
    #     [1] https://numpy.org/doc/stable/numpy_2_0_migration_guide.html#changes-to-numpy-data-type-promotion
    #     [2] https://numpy.org/neps/nep-0050-scalar-promotion.html
    info = np.iinfo(np.int64)
    if (np.min(labels) <= info.min) or (np.max(labels) >= info.max):
        # The label values fall outside the permissible interval of NumPy's
        # int64, +/- 1 to account for the algorithm below.
        # This could happen if e.g. the CC layer has dtype uint64 and the
        # fill value is set to 2 ** 63 - 1.
        # However, this should not occur in nominal products, so simply raise
        # an error for now.
        raise NotImplementedError(
            f"Connected components label value(s) fall outside of the"
            " permissible interval for QA's plotting tools. Please update QA."
        )
    else:
        labels_promoted = labels.astype(np.int64)

    # This assumes that `labels` is in sorted, ascending order.
    boundaries = np.concatenate(
        (
            [labels_promoted[0] - 1],
            labels_promoted[:-1] + np.diff(labels_promoted) / 2.0,
            [labels_promoted[-1] + 1],
        )
    )
    norm = colors.BoundaryNorm(boundaries, len(boundaries) - 1)

    # Step 3: Decimate Connected Components array to square pixels and plot
    # Note: We do not need to decimate again to a smaller size to fit nicely
    # on the axes in order to reduce PDF file size. PdfPages defaults to
    # using Flate compression, a lossless compression method that works well
    # on images with large areas of single colors or repeating patterns.
    cc_decimated = nisarqa.decimate_raster_array_to_square_pixels(cc_raster)

    # Plot connected components mask
    im1 = ax1.imshow(cc_decimated, cmap=cmap, norm=norm, interpolation="none")

    cax1 = fig.colorbar(im1, cmap=cmap, norm=norm)

    # The CC image plot visualizes discrete data; the colorbar ticks are
    # for the integer CC labels.
    # Set colorbar ticks to appear at the midpoint between each `boundaries`
    # transition:
    cax1.set_ticks(boundaries[:-1] + np.diff(boundaries) / 2.0)
    # Labels the tick marks with the `labels`
    cax1.ax.set_yticklabels(labels)
    # Hide the ticks at the boundaries
    cax1.ax.minorticks_off()

    format_axes_ticks_and_labels(
        ax=ax1,
        xlim=cc_raster.x_axis_limits,
        ylim=cc_raster.y_axis_limits,
        img_arr_shape=np.shape(cc_decimated),
        xlabel=cc_raster.x_axis_label,
        ylabel=cc_raster.y_axis_label,
        title=f"{(cc_raster.name.split('_')[-1])} Layer",
    )

    # Step 4: Create a bar chart of the connected components on ax2
    ax2.set_title("Percentage of Pixels per Connected Component", fontsize=10)

    x_locations_of_bars = range(len(percentages))

    ax2.bar(
        x_locations_of_bars,
        percentages,
        color=cmap.colors,
        edgecolor="black",
        linewidth=0.5,
    )
    ax2.set_ylabel("Percentage of Pixels")
    ax2.xaxis.set_ticks(x_locations_of_bars)
    xlabel = (
        "Connected Component Label\n(0 denotes pixels with invalid unwrapping"
    )
    if cc_raster.fill_value in labels:
        xlabel += f",\n{cc_raster.fill_value} is fill value from geocoding)"
    else:
        xlabel += ")"
    ax2.set_xlabel(xlabel)

    rotation = 45 if len(labels) > 10 else 0
    ax2.xaxis.set_ticklabels(labels, rotation=rotation)

    if num_features < 25:
        # Note the percentage at the top of each bar. (Cap this at 25. If there
        # are too many bars, it will be too cluttered to read the percentages.)
        font_size = 8 if num_features < 12 else 6

        for i, val in enumerate(percentages):
            ax2.text(
                x_locations_of_bars[i],  # location on x-axis
                val,  # location on y-axis
                f"{val:.1f}",
                fontsize=font_size,
                horizontalalignment="center",
                verticalalignment="bottom",
            )

    # Append figure to the output PDF
    report_pdf.savefig(fig)

    # Close the plot
    plt.close(fig)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
