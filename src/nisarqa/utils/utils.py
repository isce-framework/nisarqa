from __future__ import annotations

import numpy as np
import logging
import os
from typing import Optional

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


class DatasetNotFoundError(Exception):
    """
    Custom exception for when a dataset is not found in an e.g. HDF5 file.

    Parameters
    ----------
    msg : str, optional
        Error message. Default: "Dataset not found.".
    """

    def __init__(self, msg: str = "Dataset not found.") -> None:
        super().__init__(msg)


class ExitEarly(Exception):
    """
    Custom exception for when logic is nominal but the QA-SAS should exit early.
    This should be used such as for when all `workflows` are set to
    `False` and so no QA processing should be performed.
    """

    pass


class InvalidNISARProductError(Exception):
    """
    Input NISAR HDF5 file does not match the product spec structure.

    Parameters
    ----------
    msg : str, optional
        Error message.
        Default: "Input file does not match expected product spec structure.".
    """

    def __init__(
        self,
        msg: str = "Input file does not match expected product spec structure.",
    ) -> None:
        super().__init__(msg)


def raise_(exc):
    """
    Wrapper to raise an Exception for use in e.g. lambda functions.

    Parameters
    ----------
    exc : Exception
        An Exception or a subclass of Exception that can be re-raised.

    Examples
    --------
    >>> raise_(Exception('mayday'))
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 2, in raise_
    Exception: mayday

    >>> raise_(TypeError('Input has incorrect type'))
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 2, in raise_
    TypeError: Input has incorrect type

    >>> out = lambda x: (x + 1) if (x > 1) else raise_(Exception('error'))
    >>> my_func = lambda x: (x + 1) if (x > 1) else raise_(Exception('error'))
    >>> my_func(3)
    4

    >>> my_func(-1)
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
      File "<stdin>", line 1, in <lambda>
      File "<stdin>", line 2, in raise_
    Exception: error
    """
    raise exc


def compute_non_zero_mask(arr, epsilon=1.0e-05):
    """
    Create a mask of the non-zero pixels in the input array.

    Elements in the input array that are approximately equal to zero,
    based on the specified tolerance, are masked out.
    TODO - after development of the RSLC QA code is complete,
    check that this function is used. If not, delete.

    Parameters
    ----------
    arr : array_like
        The input array.
    epsilon : float, optional
        Absolute tolerance for determining if an element in `arr`
        is nearly zero.

    Returns
    -------
    mask : Boolean array
        Array with same shape as `arr`.
        True for non-zero entries. False where the absolute
        value of the entry is less than `epsilon`.
    """
    zero_real = np.abs(arr) < epsilon
    return ~zero_real


def compute_mask_ok(arr, epsilon=1.0e-05):
    """
    Create a mask of the valid (finite, non-zero) pixels in arr.

    TODO - after development of the RSLC QA code is complete,
    check that this function is used. If not, delete.

    Parameters
    ----------
    arr : array_like
        The input array
    epsilon : float, optional
        Tolerance for if an element in `arr` is considered 'zero'

    Returns
    -------
    mask_ok : array_like
        Array with same shape as `arr`.
        True for valid entries. Valid entries are finite values that are
        not approximately equal to zero.
        False for entries that have a nan or inf in either the real
        or imaginary component, or a zero in both real and imag components.
    """

    finite_mask = np.isfinite(arr)
    non_zero_mask = compute_non_zero_mask(arr, epsilon)
    mask_ok = finite_mask & non_zero_mask

    return mask_ok


def create_dataset_in_h5group(
    h5_file, grp_path, ds_name, ds_data, ds_description, ds_units=None
):
    """
    Add a dataset with attributes to the provided group.

    Parameters
    ----------
    h5_file : h5py.File
        HDF5 File handle to save this dataset to
    grp_path : str
        Path to h5py Group to add the dataset and attributes to
    ds_name : str
        Name (key) for the Dataset in the `grp_path`
    ds_data : array_like or str
        Data to be stored as a Dataset in `grp_path`.
    ds_description : str
        Description of `ds_data`; will be stored in a `description`
        attribute for the new Dataset
    ds_units : str or None, optional
        Units of `ds_data`; will be stored in a `units` attribute
        for the new Dataset.
        For NISAR datasets, use this convention:
            - If values have dimensions, use CF-compliant names (e.g. 'meters')
            - If values are numeric but dimensionless (e.g. ratios),
              set `ds_units` to 'unitless'
            - If values are inherently descriptive and have no units
              (e.g. a file name, or a list of frequency names like: ['A', 'B']),
              then set `ds_units` to None so that no units attribute
              is created.
        Defaults to None (no units attribute will be created)
    """
    grp = h5_file.require_group(grp_path)

    ds = grp.create_dataset(ds_name, data=ds_data)
    if ds_units is not None:
        ds.attrs.create(name="units", data=ds_units, dtype=f"<S{len(ds_units)}")

    ds.attrs.create(
        name="description",
        data=ds_description,
        dtype=f"<S{len(ds_description)}",
    )


def multi_line_string_iter(multiline_str):
    """
    Iterator for a multi-line string.

    Strips leading and trailing whitespace, and returns one line at a time.

    Parameters
    ----------
    multiline_str : str
        The string to be iterated over

    Yields
    ------
    line : str
        The next line in `multiline_str`, with the leading and trailing
        whitespace stripped.
    """
    return (x.strip() for x in multiline_str.splitlines())


def get_nested_element_in_dict(source_dict, path_to_element):
    """
    Return the value of the last key in the `path_to_element`.

    Parameters
    ----------
    source_dict : dict
        Nested dictionary to be parsed
    path_to_element : sequence
        Sequence which define a nested path in `source_dict` to
        the desired value.

    Returns
    -------
    element : Any
        The value of the final key in the `path_to_element` sequence

    Example
    -------
    >>> src = {'a' : 'dog', 'b' : {'cat':'lulu', 'toy':'mouse'}}
    >>> path = ['b']
    >>> get_nested_element_in_dict(src, path)
    {'cat': 'lulu', 'toy': 'mouse'}
    >>> path = ['b', 'toy']
    >>> get_nested_element_in_dict(src, path)
    'mouse'
    """
    element = source_dict
    for nested_dict in path_to_element:
        element = element[nested_dict]
    return element


def m2km(m):
    """Convert meters to kilometers."""
    return m / 1000.0


def byte_string_to_python_str(byte_str: np.bytes_) -> str:
    """Convert Numpy byte string to Python string object."""
    # Step 1: Use .astype(np.unicode_) to cast from numpy byte string
    # to numpy unicode (UTF-32)
    out = byte_str.astype(np.unicode_)

    # Step 2: Use str(...) to cast from numpy string to normal python string
    out = str(out)

    return out


def get_logger() -> logging.Logger:
    """
    Get the 'QA' logger.

    Returns
    -------
    log : logging.Logger
        The global 'QA' logger.

    See Also
    --------
    set_logger_handler : Update the output destination for the log messages.
    """
    log = logging.getLogger("QA")

    # Ensure the logging handler (formatter) is setup.
    # (The first time logging.getLogger("QA") is invoked, logging module will
    # generate the "QA" logger with no handlers.
    # But, if `set_logger_handler()` was called prior to `get_logger()`, then
    # that function will have already generated the "QA" logger and
    # added a handler. We should not override that existing handler.)
    if not log.handlers:
        set_logger_handler()

    return log


def set_logger_handler(log_file: Optional[str | os.PathLike] = None, mode: str = "w") -> None:
    """
    Configure the 'QA' logger with correct message format and output location.

    Parameters
    ----------
    log_file : path-like or None, optional
        If None, log messages will be directed to sys.stderr.
        If path-like, log messages will be directed to the log file.
        Defaults to None.
    mode : str, optional
        The mode to setup the log file. Options:
            "r"         - Readonly, file must exist (default)
            "r+"        - Read/write, file must exist
            "w"         - Create file, truncate if exists
            "w-" or "x" - Create file, fail if exists
            "a"         - Read/write if exists, create otherwise
        Defaults to "w", which means that if `log_file` is an existing
        file, it will be overwritten.
        Note: `mode` will only be used if `log_file` is path-like.

    See Also
    --------
    get_logger : Preferred nisarqa API to get the 'QA' logger.
    """
    # Setup the QA logger
    log = logging.getLogger("QA")
    # remove all existing (old) handlers
    for hdlr in log.handlers:
        log.removeHandler(hdlr)

    # Get the correct handler
    if log_file is None:
        # direct log messages to sys.stderr
        handler = logging.StreamHandler()
    elif isinstance(log_file, (str, os.PathLike)):
        # validate/clean the filepath
        log_file = os.fspath(log_file)

        # direct log messages to the specified file
        handler = logging.FileHandler(filename=log_file, mode=mode)
    else:
        raise TypeError(
            f"`{log_file=}` and has type {type(log_file)}, but must be"
            " path-like or None."
        )

    # Set log level to be reported
    log_level = logging.DEBUG
    log.setLevel(log_level)
    handler.setLevel(log_level)

    # Set log message format
    # Format from L0B PGE Design Document, section 9. Kludging error code.
    msgfmt = (
        f"%(asctime)s.%(msecs)03d, %(levelname)s, QA, "
        f'999998, %(pathname)s:%(lineno)d, "%(message)s"'
    )
    fmt = logging.Formatter(msgfmt, "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(fmt)

    # set the new handler
    log.addHandler(handler)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
