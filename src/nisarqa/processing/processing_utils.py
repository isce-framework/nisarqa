from __future__ import annotations

from typing import Optional

import numpy as np

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
