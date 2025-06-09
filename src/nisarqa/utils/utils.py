from __future__ import annotations

import logging
import os
import warnings
from collections.abc import Callable, Generator, Iterator, Mapping, Sequence
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from typing import Optional

import h5py
import numpy as np
from numpy.typing import ArrayLike
from ruamel.yaml import YAML

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


class InvalidRasterError(Exception):
    """
    Raster is invalid.

    This exception can be used when a raster was improperly formed.
    A common example is when the raster is filled with all NaN values
    (or nearly 100% NaN values).

    Parameters
    ----------
    msg : str, optional
        Error message.
        Default: "Raster is invalid.".
    """

    def __init__(
        self,
        msg: str = "Raster is invalid.",
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


def create_dataset_in_h5group(
    h5_file: h5py.File,
    grp_path: str,
    ds_name: str,
    ds_data: ArrayLike | str,
    ds_description: str,
    ds_units: Optional[str] = None,
    ds_attrs: Optional[Mapping[str, ArrayLike | str]] = None,
) -> None:
    """
    Add a Dataset with attributes to the provided group.

    Parameters
    ----------
    h5_file : h5py.File
        HDF5 File handle to save this dataset to
    grp_path : str
        Path to h5py Group to add the dataset and attributes to
    ds_name : str
        Name (key) for the Dataset in the `grp_path`
    ds_data : array_like or str or bool
        Data to be stored as a Dataset in `grp_path`. If data is a boolean
        value, then per NISAR conventions it will be saved as its "True" or
        "False" string representation.
    ds_description : str
        Description of `ds_data`; will be stored in a `description`
        attribute for the new Dataset.
    ds_units : str or None, optional
        Units of `ds_data`; will be stored in a `units` attribute
        for the new Dataset.
        NISAR datasets use this convention:
            - If values have dimensions, use CF- and UDUNITS-compliant names.
              Units should be spelled out:
                  Correct: "meters"
                  Incorrect: "m"
              Units should favor math symbols:
                  Correct: "meters / second ^ 2"
                  Incorrect: "meters per second squared"
            - If values are numeric but dimensionless (e.g. ratios),
              set `ds_units` to "1" (the string "1").
            - If values are inherently descriptive and have no units
              (e.g. a file name, or a list of frequency names like: ['A', 'B'],
              or data which is categorical in nature),
              then set `ds_units` to None so that no units attribute
              is created.
        Defaults to None (no units attribute will be created)
    ds_attrs : mapping of str to array_like or str, or None; optional
        Additional metadata to attach as attributes to the new Dataset.
        If None, no additional Attributes will be added.
        Format:     { <Attribute name> : <Attribute value> }
        Example:    { "subswathStartIndex" : 45,
                      "subswathStopIndex" : 65,
                      "freqBins" : "science/LSAR/QA/data/freqA/azSpectraFreq"}
        Defaults to None.

    Notes
    -----
    Please supply Python strings for arguments. This function handles the
    conversion to fixed-length byte strings to meet ISCE3 conventions for R4.
    """
    if not (isinstance(ds_units, str) or (ds_units is None)):
        raise TypeError(
            f"`{ds_units=}` and has type `{type(ds_units)}`, but must be a"
            " string or None."
        )

    if ds_units == "unitless":
        raise ValueError(
            f"{ds_units=}. As of R4, please use the string '1' as the"
            " `ds_units` for numeric but unitless datasets."
        )

    grp = h5_file.require_group(grp_path)

    # If a string or a list of strings, convert to fixed-length byte strings
    def _to_fixed_length_str(
        data: ArrayLike | str | bool,
    ) -> ArrayLike | np.bytes_:
        # If `data` is an e.g. numpy array with a numeric dtype,
        # do not alter it.
        if isinstance(data, str):
            data = np.bytes_(data)
        elif isinstance(data, Sequence) and all(
            isinstance(s, str) for s in data
        ):
            data = np.bytes_(data)
        elif isinstance(data, np.ndarray) and (
            np.issubdtype(data.dtype, np.object_)
            or np.issubdtype(data.dtype, np.str_)
        ):
            raise NotImplementedError(
                f"`{data=}` and has dtype `{data.dtype}`, which is not"
                " currently supported. Suggestion: Make `ds_data` a list or tuple"
                " of Python strings, or an ndarray of fixed-length byte strings."
            )
        elif isinstance(data, bool):
            data = "True" if data else "False"
            data = np.bytes_(data)
        elif (
            isinstance(data, Sequence)
            and all(isinstance(b, bool) for b in data)
        ) or (
            isinstance(data, np.ndarray)
            and (np.issubdtype(data.dtype, np.bool_))
        ):
            raise NotImplementedError(
                f"`{data=}` is a sequence or array of boolean values"
                " which is not currently supported"
            )
        return data

    # Create dataset and add attributes
    ds = grp.create_dataset(ds_name, data=_to_fixed_length_str(ds_data))
    if ds_units is not None:
        ds.attrs.create(name="units", data=np.bytes_(ds_units))

    ds.attrs.create(name="description", data=np.bytes_(ds_description))

    if ds_attrs is not None:
        for name, val in ds_attrs.items():
            ds.attrs.create(name=name, data=_to_fixed_length_str(val))


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
    # Step 1: Use .astype(np.str_) to cast from numpy byte string
    # to numpy unicode (UTF-32)
    out = byte_str.astype(np.str_)

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


def set_logger_handler(
    log_file: Optional[str | os.PathLike] = None,
    mode: str = "w",
    verbose: bool = False,
) -> None:
    """
    Configure the 'QA' logger with correct message format and output location.

    Parameters
    ----------
    log_file : path-like or None, optional
        If path-like, log messages will be directed to this log file; use
        `mode` to control how the log file is opened.
        If None, log messages will only be directed to sys.stderr.
        Defaults to None.
    mode : str, optional
        The mode to setup the log file. Options:
            "w"         - Create file, truncate if exists
            "a"         - Read/write if exists, create otherwise
        Defaults to "w", which means that if `log_file` is an existing
        file, it will be overwritten.
        Note: `mode` will only be used if `log_file` is path-like.
    verbose : bool, optional
        True to stream log messages to console (stderr) in addition to the
        log file. False to only stream to the log file. Defaults to False.
        Note: `verbose` will only be used if `log_file` is path-like.

    See Also
    --------
    get_logger : Preferred nisarqa API to get the 'QA' logger.
    """
    if (not isinstance(log_file, (str, os.PathLike))) and (
        log_file is not None
    ):
        raise TypeError(
            f"`{log_file=}` and has type {type(log_file)}, but must be"
            " path-like or None."
        )

    if mode not in ("w", "a"):
        raise ValueError(f"{mode=}, must be either 'w' or 'a'.")

    # Setup the QA logger
    log = logging.getLogger("QA")
    # remove all existing (old) handlers
    for hdlr in log.handlers:
        log.removeHandler(hdlr)

    # Set minimum log level for the root logger; this sets the minimum
    # possible log level for all handlers. (It typically defaults to WARNING.)
    # Later, set the minimum log level for individual handlers.
    log_level = logging.DEBUG
    log.setLevel(log_level)

    # Set log message format
    # Format from L0B PGE Design Document, section 9. Kludging error code.
    # Nov 2023: Use "999998", so that QA is distinct from RSLC (999999).
    msgfmt = (
        f"%(asctime)s.%(msecs)03d, %(levelname)s, QA, "
        f'999998, %(pathname)s:%(lineno)d, "%(message)s"'
    )
    fmt = logging.Formatter(msgfmt, "%Y-%m-%d %H:%M:%S")

    # Use the requested handler(s)
    if (log_file is None) or verbose:
        # direct log messages to sys.stderr
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        handler.setFormatter(fmt)
        log.addHandler(handler)

    if isinstance(log_file, (str, os.PathLike)):
        # validate/clean the filepath
        log_file = os.fspath(log_file)

        # direct log messages to the specified file
        handler = logging.FileHandler(filename=log_file, mode=mode)
        handler.setLevel(log_level)
        handler.setFormatter(fmt)
        log.addHandler(handler)


@contextmanager
def log_runtime(msg: str) -> Generator[None, None, None]:
    """
    Log the runtime of the context manager's block with microsecond precision.

    Parameters
    ----------
    msg : str
        Prefix for the log message. Format of logged message will be:
            "Runtime: <msg> took <duration>".

    See Also
    --------
    log_function_runtime :
        Function decorator to log runtime of a function.
    """
    tic = datetime.now()
    yield
    toc = datetime.now()
    nisarqa.get_logger().info(f"Runtime: {msg} took {toc - tic}")


def log_function_runtime(
    func: Callable[..., nisarqa.typing.T],
) -> Callable[..., nisarqa.typing.T]:
    """
    Function decorator to log the runtime of a function.

    Parameters
    ----------
    func : callable
        Function that will have its runtime logged.

    See Also
    --------
    log_runtime :
        Context manager to log runtime of a code block with a custom message.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        with log_runtime(f"`{func.__name__}`"):
            return func(*args, **kwargs)

    return wrapper


@contextmanager
def ignore_runtime_warnings() -> Iterator[None]:
    """
    Context manager to ignore and silence RuntimeWarnings generated inside it.
    """
    with warnings.catch_warnings():
        warnings.simplefilter(
            action="ignore",
            category=RuntimeWarning,
        )
        yield


def load_user_runconfig(
    runconfig_yaml: str | os.PathLike,
) -> nisarqa.typing.RunConfigDict:
    """
    Load a QA runconfig YAML file into a dict format.

    Parameters
    ----------
    runconfig_yaml : path-like
        Filename (with path) to a QA runconfig YAML file.

    Returns
    -------
    user_rncfg : nisarqa.typing.RunConfigDict
        `runconfig_yaml` loaded into a dict format
    """
    # parse runconfig into a dict structure
    parser = YAML(typ="safe")
    with open(runconfig_yaml, "r") as f:
        user_rncfg = parser.load(f)
    return user_rncfg


__all__ = nisarqa.get_all(__name__, objects_to_skip)
