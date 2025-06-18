from datetime import datetime, timezone
from itertools import product
from pathlib import Path

import numpy as np
from cycler import cycler

# List of first 6 Seaborn colorblind colors:
# Hardcode these so that we do not add another dependency of `seaborn`
# Source for values: output from seaborn.color_palette(palette='colorblind', n_colors=10)
SEABORN_COLORBLIND = [
    (0.00392156862745098, 0.45098039215686275, 0.6980392156862745),
    (0.8705882352941177, 0.5607843137254902, 0.0196078431372549),
    (0.00784313725490196, 0.6196078431372549, 0.45098039215686275),
    (0.8352941176470589, 0.3686274509803922, 0.0),
    (0.8, 0.47058823529411764, 0.7372549019607844),
    (0.792156862745098, 0.5686274509803921, 0.3803921568627451),
    (0.984313725490196, 0.6862745098039216, 0.8941176470588236),
    (0.5803921568627451, 0.5803921568627451, 0.5803921568627451),
    (0.9254901960784314, 0.8823529411764706, 0.2),
    (0.33725490196078434, 0.7058823529411765, 0.9137254901960784),
]
CUSTOM_CYCLER = (
    cycler(color=SEABORN_COLORBLIND[:6])
    + cycler(
        linestyle=[
            "-",
            "-.",
            "--",
            (0, (3, 1, 1, 1)),
            (0, (3, 5, 1, 5, 1, 5)),
            ":",
        ]
    )
    + cycler(lw=np.linspace(3, 1, 6))
)


#: The UTC time at which this module was first loaded, in ISO 8601 format with
#: integer seconds precision.
QA_PROCESSING_DATETIME = datetime.now(timezone.utc).isoformat()[:19]

FIG_SIZE_ONE_PLOT_PER_PAGE = (6.4, 4.8)
FIG_SIZE_TWO_PLOTS_PER_PAGE = (10.0, 4.8)
FIG_SIZE_THREE_PLOTS_PER_PAGE_STACKED = (6.4, 9.6)

PI_UNICODE = "\u03c0"

# This is used for logging errors during computation of statistics.
# Ex: if a raster has greater than `STATISTICS_THRESHOLD` percent NaN values,
# an error should be logged.
STATISTICS_THRESHOLD_PERCENTAGE = 95.0

# Total number of tracks and frames (inclusive) for NISAR during operations
NUM_TRACKS = 173  # valid range of [1, 173] confirmed on 2024-07-24
NUM_FRAMES = 176  # valid range of [1, 176] confirmed on 2024-07-24

LIST_OF_NISAR_PRODUCTS = [
    "rslc",
    "gslc",
    "gcov",
    "rifg",
    "runw",
    "gunw",
    "roff",
    "goff",
]

NISAR_BANDS = ("L", "S")
NISAR_FREQS = ("A", "B")
NISAR_LAYERS = ("layer1", "layer2", "layer3")


LIST_OF_INSAR_PRODUCTS = ["rifg", "roff", "runw", "goff", "gunw"]


# As of June 2023, baseline for GCOV NISAR products is to only include
# on-diagonal terms. However, the ISCE3 GCOV processor is capable of processing
# both on-diagonal and off-diagonal terms. There is an ongoing push from
# some NISAR Science Team members to include the off-diagonal terms
# in the baseline GCOV product, so P. Rosen requested that QA handle both
# on-diag and off-diag terms. But, they need to be handled differently
# in the code, so have these lists be independent.
GCOV_DIAG_POLS = []
GCOV_OFF_DIAG_POLS = []


def _append_gcov_terms(txrx_iterable):
    # For global GCOV*_POLS variables, we should include all possible
    # polarizations.
    # ISCE3 GCOV processor can output e.g. either HHVV or VVHH, depending
    # on the order the user typed the polarizations into the runconfig.
    # So, use `product()` to list the full matrix, and not only the upper
    # triangle or the lower triangle of the matrix.
    for term in product(txrx_iterable, repeat=2):
        if term[0] == term[1]:
            # On-diag term
            GCOV_DIAG_POLS.append(term[0] + term[1])
        else:
            GCOV_OFF_DIAG_POLS.append(term[0] + term[1])


_append_gcov_terms(("HH", "HV", "VH", "VV"))
_append_gcov_terms(("RH", "RV"))
_append_gcov_terms(("LH", "LV"))


def get_possible_pols(product_type):
    """
    Return all possible polarizations for the requested product type.

    Parameters
    ----------
    product_type : str
        One of: 'rslc', 'gslc', 'gcov', 'rifg',
                'runw', 'gunw', 'roff', 'goff'
    Returns
    -------
    polarization_list : tuple of str
        Tuple of all possible polarizations for the given product type.
        Ex: ('HH', 'VV', 'HV', 'VH')

    """
    if product_type not in LIST_OF_NISAR_PRODUCTS:
        raise ValueError(
            f"`{product_type=}`, but must be one of: {LIST_OF_NISAR_PRODUCTS}"
        )

    if product_type.endswith("slc"):
        return ("HH", "VV", "HV", "VH", "RH", "RV", "LH", "LV")
    elif product_type == "gcov":
        return GCOV_DIAG_POLS + GCOV_OFF_DIAG_POLS
    elif product_type in LIST_OF_INSAR_PRODUCTS:
        # As of 6/21/2023, baseline for NISAR InSAR mission processing
        # is to produce only HH and/or VV.
        # ISCE3 can also handle HV and/or VH. Compact Pol not supported.
        return ("HH", "VV", "HV", "VH")
    else:
        raise NotImplementedError


PRODUCT_SPECS_PATH = Path(__file__).parent / "product_specs"

complex32 = np.dtype([("r", np.float16), ("i", np.float16)])


# The are global constants and not functions nor classes,
# so manually create the __all__ attribute.
__all__ = [
    "CUSTOM_CYCLER",
    "LIST_OF_NISAR_PRODUCTS",
    "LIST_OF_INSAR_PRODUCTS",
    "NISAR_BANDS",
    "NISAR_FREQS",
    "NISAR_LAYERS",
    "QA_PROCESSING_DATETIME",
    "FIG_SIZE_ONE_PLOT_PER_PAGE",
    "FIG_SIZE_TWO_PLOTS_PER_PAGE",
    "FIG_SIZE_THREE_PLOTS_PER_PAGE_STACKED",
    "PI_UNICODE",
    "NUM_TRACKS",
    "NUM_FRAMES",
    "PRODUCT_SPECS_PATH",
    "STATISTICS_THRESHOLD_PERCENTAGE",
    "get_possible_pols",
    "GCOV_DIAG_POLS",
    "GCOV_OFF_DIAG_POLS",
    "SEABORN_COLORBLIND",
    "complex32",
]
