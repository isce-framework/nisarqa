from __future__ import annotations

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


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
