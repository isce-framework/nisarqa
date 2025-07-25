from __future__ import annotations

import logging
import os
import shutil
import tempfile
import warnings
from collections.abc import (
    Callable,
    Generator,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
)
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Callable, Optional, overload

import h5py
import numpy as np
from numpy.typing import ArrayLike
from ruamel.yaml import YAML

import nisarqa
from nisarqa.utils.typing import RunConfigDict, T

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


def _prep_data_for_hdf5_using_nisar_conventions(
    data: ArrayLike | str | bool,
) -> ArrayLike | np.bytes_:
    """Prep data for writing to the STATS.h5 file, per NISAR conventions."""

    if isinstance(data, str) or (
        isinstance(data, Sequence) and all(isinstance(s, str) for s in data)
    ):
        # If a string or a list of strings, convert to fixed-length byte strings

        # If `data` is a scalar Python (Unicode) string,
        # numpy.char.encode() returns a 0D array of byte strings.
        # If a sequence of Python strings, numpy.char.encode() returns a
        # NumPy array of byte strings.
        # We want to use `np.char.encode()` to handle non-ASCII characters,
        # such as the copyright symbol.
        # (`numpy.bytes_()` can only handle ASCII characters.)
        data = np.char.encode(data, encoding="utf-8")
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
        data = np.bytes_("True" if data else "False")
    elif (
        isinstance(data, Sequence) and all(isinstance(b, bool) for b in data)
    ) or (
        isinstance(data, np.ndarray) and (np.issubdtype(data.dtype, np.bool_))
    ):
        raise NotImplementedError(
            f"`{data=}` is a sequence or array of boolean values"
            " which is not currently supported"
        )
    else:
        # If `data` is an e.g. NumPy array with a numeric dtype,
        # do not alter it.
        pass

    return data


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

    See Also
    --------
    add_attribute_to_h5_object :
        To add a new Attribute to an existing h5py Dataset, Group, or File
        following NISAR conventions.

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

    # Create Dataset
    ds = grp.create_dataset(
        ds_name, data=_prep_data_for_hdf5_using_nisar_conventions(ds_data)
    )

    # Add Attributes
    if ds_units is not None:
        add_attribute_to_h5_object(
            h5_object=ds, attr_key="units", attr_value=ds_units
        )

    add_attribute_to_h5_object(
        h5_object=ds, attr_key="description", attr_value=ds_description
    )

    if ds_attrs is not None:
        for name, val in ds_attrs.items():
            add_attribute_to_h5_object(
                h5_object=ds, attr_key=name, attr_value=val
            )


def add_attribute_to_h5_object(
    h5_object: h5py.Dataset | h5py.Group | h5py.File,
    attr_key: str,
    attr_value: ArrayLike | str | bool,
) -> None:
    """
    Add an Attribute to an existing HDF5 Dataset or Group.

    This function will prepare the Attribute value to follow NISAR conventions.
    For example, if the value is a boolean value, then per NISAR conventions
    it will be saved as its "True" or "False" byte string representation.

    Parameters
    ----------
    h5_object : h5py.Dataset or h5py.Group or h5py.File
        h5py object to write the new Attribute to.
        Per h5py documentation, "the File object does double duty as
        the HDF5 root group". So if `h5_object` is an h5py.File, the new
        Attribute will be written to the root Group.
    attr_key : str
        Name (key) for the new Attribute.
    attr_value : array_like or str or bool
        The data to be stored as the new Attribute's value.

    See Also
    --------
    create_dataset_in_h5group :
        To create a new Dataset (including Attributes) in the HDF5 file.
        Please use that function to ensure all NISAR conventions are followed,
        including adding a `description`, `units`, etc.

    Notes
    -----
    Please supply Python strings for arguments. This function handles the
    conversion to fixed-length byte strings to meet ISCE3 conventions for R4.0+.
    """
    h5_object.attrs.create(
        name=attr_key,
        data=_prep_data_for_hdf5_using_nisar_conventions(attr_value),
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


@overload
def byte_string_to_python_str(byte_str: np.bytes_) -> str:
    pass


@overload
def byte_string_to_python_str(byte_str: ArrayLike) -> list[str]:
    pass


def byte_string_to_python_str(byte_str):
    """
    Convert NumPy byte string(s) to Python string(s) (Unicode).

    Parameters
    ----------
    byte_str : numpy.bytes_ or array_like of numpy.bytes_
        A byte string or 1D array of byte strings.
        If `byte_str` is a scalar byte string, it is converted to a Python string.
        If `byte_str` is array_like of byte strings, it is converted
        element-wise to a Python strings and that are returned in a list.

    Returns
    -------
    python_str : str or list of str
        `byte_str` converted to a Python string or list of Python strings.

    Raises
    ------
    ValueError
        If `byte_str` is an N-dimensional (N>1) array of byte strings.
        As of June 2025, NISAR products contain no Datasets like this;
        handling these edge cases would cause unnecessary code complexity.
    """
    # Step 1: Decode from NumPy byte string to NumPy unicode (UTF-8)
    # Unlike casting via `my_string.as_type(np.str_)`, this method also
    # correctly decodes non-ASCII characters (such as the copyright symbol
    # found in the runconfigs)
    out = np.char.decode(byte_str, encoding="utf-8")

    # As of June 2025, InSAR products have a bug where `orbitFiles` was being
    # written with shape (1, 2), instead of shape (2,). Given the prevalence of
    # existing test data and sample products, QA should log and then attempt to
    # workaround this issue to continue processing.
    # If the squeezed array still fails below, then let it raise an exception.
    if out.ndim > 1:
        out_squeezed = np.squeeze(out)
        if out.ndim != out_squeezed.ndim:
            nisarqa.get_logger().error(
                f"Provided array of byte strings has shape {byte_str.shape}."
                f" QA will squeeze it to shape {out_squeezed.shape},"
                f" but the input product should be fixed. Array: {byte_str!r}"
            )
        out = out_squeezed

    # Step 2: Use str(...) to cast from NumPy string to Python string (Unicode)
    if out.ndim == 0:
        # scalar input
        return str(out)
    elif out.ndim == 1:
        # array input
        return [str(s) for s in out]
    else:
        raise ValueError(
            f"{byte_str.ndim=}; N-dimensional (N>1) arrays are not supported."
        )


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


def log_function_runtime(func: Callable[..., T]) -> Callable[..., T]:
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
) -> RunConfigDict:
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


@overload
def wrap_to_interval(val: float, start: float, stop: float) -> float:
    pass


@overload
def wrap_to_interval(
    val: Iterable[float], start: float, stop: float
) -> Iterator[float]:
    pass


def wrap_to_interval(val, *, start, stop):
    """
    Wrap float value(s) to the interval [start, stop).

    Parameters
    ----------
    val : float or Iterable of float
        Value(s) to wrap.
    start : float
        Start of the interval (inclusive).
    stop : float
        End of the interval (exclusive).

    Returns
    -------
    float or iterator of float
        Wrapped value(s) in the interval [start, stop).
        Returns a float if input is a scalar, otherwise returns an iterator.

    Examples
    --------
    >>> wrap_to_interval(190, start=-180, stop=180)
    -170.0

    >>> import numpy as np
    >>> wrap_to_interval(np.pi * 3, start=0, stop=2 * np.pi)
    3.141592653589793

    >>> x = wrap_to_interval([-370, 370], start=-180, stop=180)
    >>> x
    <generator object wrap_to_interval.<locals>.<genexpr> at 0x185f08040>
    >>> list(x)
    [-370.0, 10.0]
    """
    if not (stop > start):
        raise ValueError(f"{stop=} must be greater than {start=}")

    is_scalar = not nisarqa.is_iterable(val)
    width = stop - start

    # Python's `%` (modulo) operator computes the remainder with the same sign
    # as the right-hand side operand, so the result of the modulo operation
    # below is in the range [0, b-a), where b is the upper endpoint and a is
    # the lower endpoint. Then, if we add a, the result will be in the
    # range [a, b). See:
    # https://docs.python.org/3/reference/expressions.html#binary-arithmetic-operations.
    wrap = lambda v: (v - start) % width + start
    return wrap(val) if is_scalar else (wrap(v) for v in val)


def pairwise(iterable: Iterable[T]) -> Generator[tuple[T, T], None, None]:
    """
    Return successive overlapping pairs taken from the input iterable.

    Example: pairwise('ABCDEFG') -> AB BC CD DE EF FG

    Source: https://docs.python.org/3/library/itertools.html#itertools.pairwise

    Parameters
    ----------
    iterable : iterable of T
        The input iterable.

    Yields
    ------
    pair : pair of T
        Successive overlapping pairs taken from the input iterable.
        The number of 2-tuples in the output iterator will be one fewer than
        the number of inputs. It will be empty if the input iterable has
        fewer than two values.
    """

    iterator = iter(iterable)
    a = next(iterator, None)
    for b in iterator:
        yield a, b
        a = b


@contextmanager
def create_unique_subdirectory(
    parent_dir: str | os.PathLike | None = None,
    prefix: str | None = None,
    *,
    delete: bool = True,
) -> Generator[Path, None, None]:
    """
    Create a uniquely-named subdirectory or temporary directory.

    Parameters
    ----------
    parent_dir : path-like or None, optional
        Local file system path to a directory where a new, uniquely-named
        subdirectory will be created.
        If `parent_dir` is a path-like object, it will be created if it
        did not already exist.
        If `parent_dir` is None, a temporary directory will be created as
        though by `tempfile.mkdtemp()`.
        Defaults to None.
    prefix : str or None, optional
        If not None, the subdirectory name will begin with that prefix.
    delete : bool, optional
        If True, the directory and its contents are recursively removed from
        the file system upon exiting the context manager.
        Defaults to True.

    Yields
    ------
    pathlib.Path
        Path to the uniquely-named subdirectory. If `delete` was True,
        the directory will be removed from the file system upon exiting
        the context manager.
    """

    if parent_dir is None:
        # Make a temporary directory inside a default directory, which is
        # chosen from a platform-dependent list, but can be controlled
        # by setting the TMPDIR, TEMP or TMP environment variables.
        # The directory is readable and writable only by the creating user ID.
        path = Path(tempfile.mkdtemp(prefix=prefix))
    else:
        # Create a uniquely-named subdirectory
        utc_now = datetime.now(timezone.utc)
        # The colon character `:` is not advised for POSIX paths
        utc_now = utc_now.strftime("%Y%m%d%H%M%S")

        prefix_str = f"{'' if prefix is None else (prefix + '-')}{utc_now}-"

        path = Path(tempfile.mkdtemp(prefix=prefix_str, dir=parent_dir))

    try:
        yield path
    finally:
        log = nisarqa.get_logger()
        if delete:
            try:
                shutil.rmtree(path)
            except FileNotFoundError:
                msg = (
                    f"Created directory was '{path}', but it was"
                    " deleted external to (but within the context of)"
                    " this context manager."
                )
                log.error(msg)
                raise FileNotFoundError(msg)
            else:
                log.info(f"Directory deleted recursively: '{path}'")


def set_global_scratch_dir(scratch_dir: str | os.PathLike) -> None:
    """
    Set the persistent global scratch directory path.

    This function sets the persistent global scratch directory that is
    returned by `get_global_scratch_dir()`.
    Initially, the global scratch directory used by nisarqa is unset
    and calls to `get_global_scratch_dir()` will raise a `RuntimeError` until
    the first time `set_global_scratch_dir()` is called. Subsequent calls will
    update the stored path.

    Parameters
    ----------
    scratch_dir : path-like
        Path to the scratch directory. Must be an existing directory
        in the local file system. The user is responsible for deleting
        the scratch directory and its contents when done with it.

    See Also
    --------
    get_global_scratch_dir :
        After the global scratch directory has been set, use this function
        to get the Path to the current global scratch directory.
    """
    log = nisarqa.get_logger()

    path = Path(scratch_dir)

    if not path.is_dir():
        raise ValueError(f"{scratch_dir=}, must be an existing directory.")

    # Log if the global scratch directory already existed and is being updated.
    if hasattr(set_global_scratch_dir, "_scratch_dir"):
        old_dir = set_global_scratch_dir._scratch_dir
        log.info(
            f"Global scratch directory path was '{old_dir}'."
            f" Updating it to '{path}'."
        )

    # Set function attribute to the new global scratch path
    set_global_scratch_dir._scratch_dir = path

    log.info(
        f"Global scratch directory path set to "
        f" '{set_global_scratch_dir._scratch_dir}'."
    )


def get_global_scratch_dir() -> Path:
    """
    Get the persistent global scratch directory path.

    User must call `set_global_scratch_dir()` prior to calling this function.

    Returns
    -------
    path : pathlib.Path
        Path to global scratch directory.

    See Also
    --------
    set_global_scratch_dir :
        Set the global scratch directory. Must be called prior to calling
        `get_global_scratch_dir()`.
    """

    if not hasattr(set_global_scratch_dir, "_scratch_dir"):
        raise RuntimeError(
            "Scratch path not set. User must call `set_global_scratch_dir()`"
            " prior to calling this function."
        )

    return set_global_scratch_dir._scratch_dir


__all__ = nisarqa.get_all(__name__, objects_to_skip)
