from __future__ import annotations

import os

import h5py

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


def get_copols(rslc: nisarqa.RSLC, freq: str) -> list[str]:
    """
    Get a list of co-pol channels in a sub-band of an RSLC product.

    Returns a list of strings identifying the transmit (Tx) & receive (Rx)
    polarizations of each co-pol channel (e.g. 'HH' or 'VV') found in the
    specified sub-band of the product.

    Parameters
    ----------
    rslc : RSLC
        The RSLC product.
    freq : {'A', 'B'}
        The frequency sub-band to check for co-pols. Must be a valid sub-band in the
        input product.

    Returns
    -------
    copols : list of str
        The list of co-pols.
    """
    return [pol for pol in rslc.get_pols(freq) if pol[0] == pol[1]]


def file_is_empty(filepath: str | os.PathLike) -> bool:
    """
    Check if a file is empty.

    Parameters
    ----------
    filepath : path-like
        The path of an existing file.

    Returns
    -------
    is_empty : bool
        True if the file was empty; false otherwise.
    """
    # Check if the file size is zero.
    return os.stat(filepath).st_size == 0


def get_valid_freqs(group: h5py.Group) -> list[str]:
    """
    Get a list of frequency sub-bands contained within the input HDF5 Group.

    The group is assumed to contain child groups corresponding to each sub-band,
    with names 'frequencyA' and/or 'frequencyB'.

    Parameters
    ----------
    group : h5py.Group
        The input HDF5 Group.

    Returns
    -------
    freqs : list of str
        A list of frequency sub-bands found in the group. Each sub-band in the
        list is denoted by its single-character identifier (e.g. 'A', 'B').
    """
    return [freq for freq in nisarqa.NISAR_FREQS if f"frequency{freq}" in group]


def get_valid_pols(group: h5py.File) -> list[str]:
    """
    Get a list of polarization channels contained within the input HDF5 Group.

    The group is assumed to contain child groups corresponding to each
    polarization, with names like 'HH', 'HV', etc.

    Parameters
    ----------
    group : h5py.Group
        The input HDF5 Group.

    Returns
    -------
    pols : list of str
        A list of polarizations found in the group.
    """
    pols = ("HH", "HV", "VH", "VV", "LH", "LV", "RH", "RV")
    return [pol for pol in pols if pol in group]


__all__ = nisarqa.get_all(__name__, objects_to_skip)
