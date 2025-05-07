from __future__ import annotations

import warnings
from collections.abc import Callable
from typing import Optional

import numpy as np
from numpy.typing import ArrayLike, DTypeLike

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)

###############################################
######      Main Tiling Functions       #######
###############################################


class TileIterator:
    def __init__(
        self,
        arr_shape: tuple[int, int],
        axis_0_tile_dim: int = -1,
        axis_1_tile_dim: int = -1,
        axis_0_stride: int = 1,
        axis_1_stride: int = 1,
    ):
        """
        Simple iterator class to iterate over a 2D array by tiles.

        The iterator's first slice yielded will always start at row 0, column 0.
        To start in the middle of the 2D array (e.g. for iterating over
        a subswath of an array), please use the `SubBlock2D` class.

        Parameters
        ----------
        arr_shape : tuple of int
            The shape of the 2D array that this TileIterator is for.
        axis_0_tile_dim : int, optional
            Length of tile (i.e. number of elements) along axis 0.
            Defaults to -1, meaning all elements along axis 0 will be processed.
        axis_1_tile_dim : int, optional
            Width of tile (i.e. number of elements) along axis 1.
            Defaults to -1, meaning all elements along axis 1 will be processed.
        axis_0_stride : int, optional
            Amount to decimate the input array along axis 0.
            Ex: If `axis_0_stride` is 5, then the slices yielded during the
            iteration process will have an axes 0 step value of 5,
            i.e. rows 0, 5, 10,... will be yielded.
            Defaults to 1 (no decimation).
        axis_1_stride : int, optional
            Amount to decimate the input array along axis 1.
            Ex: If `axis_1_stride` is 5, then the slices yielded during the
            iteration process will have an axis 1 step value of 5,
            i.e. columns 0, 5, 10,... will be yielded.
            Defaults to 1 (no decimation).
        """

        # Step 1: Determine the axis 0 and axis 1 indice intervals
        if len(arr_shape) != 2:
            raise ValueError(
                f"{arr_shape=} has {self.num_dim} dimensions"
                " but only 2D arrays are currently supported."
            )
        self._arr_shape = arr_shape

        if axis_0_tile_dim == -1:
            self._axis_0_tile_dim = arr_shape[0]
        else:
            self._axis_0_tile_dim = axis_0_tile_dim

        if axis_1_tile_dim == -1:
            self._axis_1_tile_dim = arr_shape[1]
        else:
            self._axis_1_tile_dim = axis_1_tile_dim

        self._axis_0_stride = axis_0_stride
        self._axis_1_stride = axis_1_stride

        # Warn if the tile dimensions are not integer multiples of the strides
        msg = (
            "The axes %s length is %d, which is not an integer"
            + "multiple of the axes %s stride value of %s."
            + "This will lead to incorrect decimation of the source array."
        )

        if self._axis_1_tile_dim % self._axis_1_stride != 0:
            warnings.warn(
                msg % ("1", self._axis_1_tile_dim, "1", self._axis_1_stride),
                RuntimeWarning,
            )

        if self._axis_0_tile_dim % self._axis_0_stride != 0:
            warnings.warn(
                msg % ("0", self._axis_0_tile_dim, "0", self._axis_0_stride),
                RuntimeWarning,
            )

    def __iter__(self):
        """
        Iterator for TileIterator class.

        The iterator's first slice yielded will always start at row 0, column 0.
        To start in the middle of the 2D array (e.g. for iterating over
        a subswath of an array), please use the `SubBlock2D` class.

        Yields
        ------
        np_slice : tuple of slice objects
            A tuple of slice objects that can be used for
            indexing into the next tile of an array_like object.
        """
        for row_start in range(0, self._arr_shape[0], self._axis_0_tile_dim):
            for col_start in range(
                0, self._arr_shape[1], self._axis_1_tile_dim
            ):
                yield np.s_[
                    row_start : row_start
                    + self._axis_0_tile_dim : self._axis_0_stride,
                    col_start : col_start
                    + self._axis_1_tile_dim : self._axis_1_stride,
                ]


def process_arr_by_tiles(
    in_arr, out_arr, func, input_batches, output_batches, in_arr_2=None
):
    """
    Map a function to tiles of an array.

    Apply `func` to the input array sequentially by tiles
    and store the result in `out_arr`.

    TODO - at end of development, see if there is a reason to
    keep in_arr_2 parameter.

    Parameters
    ----------
    in_arr : array_like
        Input 1D or 2D array
    out_arr : array_like
        Output 1D or 2D array. Will be populated by this function.
    func : function or partial function
        Function to apply to every tile in the input array(s).
        The function should take an array as a single positional argument
        (or two arrays as positional arguments if `in_arr_2` is not None)
        and return an output array. For a given input tile shape,
        `func` must return an array with the same shape as an output tile shape.
    input_batches : TileIterator
        Iterator for the input array
    output_batches : TileIterator
        Iterator for the output array
    in_arr_2 : array_like, optional
        Optional 2nd input argument of same shape as `in_arr`.
    """

    for out_slice, in_slice in zip(output_batches, input_batches):
        # Process this batch
        if in_arr_2 is None:
            tmp_out = func(in_arr[in_slice])
        else:
            tmp_out = func(in_arr[in_slice], in_arr_2[in_slice])

        # Write the batch output to the output array
        out_arr[out_slice] = tmp_out


class SubBlock2D:
    """
    An array-like class for representing a 2D subblock of a 2D array.

    Internally, this class does not create a copy in memory of the source
    array; instead, it uses views of the source array.

    Parameters
    ----------
    arr : array_like
        Full input array.
    slices : pair of slices
        Pair of slices which define a 2D sub-block of `arr`.
            Format: ( <axes 0 rows slice>, <axes 1 columns slice> )
    """

    def __init__(self, arr: ArrayLike, slices: tuple[slice, slice]):
        self._arr = arr
        self._slices = slices

    def __array__(self) -> np.ndarray:
        """Return the subblock as a NumPy array."""
        return np.asanyarray(self._arr[self._slices])

    @property
    def dtype(self) -> DTypeLike:
        return self._arr.dtype

    @property
    def shape(self) -> tuple[int, int]:
        """Return the shape of the subblock."""
        nrow, ncol = np.shape(self._arr)

        rowslice, colslice = self._slices

        rowstart, rowstop, rowstride = rowslice.indices(nrow)
        new_nrow = (rowstop - rowstart) // rowstride

        colstart, colstop, colstride = colslice.indices(ncol)
        new_ncol = (colstop - colstart) // colstride

        return new_nrow, new_ncol

    def __getitem__(self, /, key: tuple[slice, slice]) -> np.ndarray:
        """
        Return a tile of the 2D subblock.

        Parameters
        ----------
        key : pair of slices
            Pair of slices which define a tile in the primary 2D subblock
            defined by this instance.
            The indice values in the slices should correspond to the indices
            of the primary 2D subblock; they should not correspond to the indices
            of the orginal, full source array.
            Format: ( <axes 0 rows slice>, <axes 1 columns slice> )
        """

        # Notes on variable names:
        # Use arr_ to denote variables pertaining to the source array
        # Use sub_ to denote variables pertaining to the 2D subblock
        # Use tile_ to denote variables pertaining to the tile in the subblock

        # Use 0 for index values in source array's "index coordinate system"
        # Use 1 for index values in the sublock's "index coordinate system"

        # Step 1: Get the subblock indices
        arr_nrow, arr_ncol = np.shape(self._arr)
        sub_rowslice0, sub_colslice0 = self._slices
        sub_rowstart0, _, sub_rowstride0 = sub_rowslice0.indices(arr_nrow)
        sub_colstart0, _, sub_colstride0 = sub_colslice0.indices(arr_ncol)

        # Step 2: Get the tile indices+strides requested by the caller.
        # These indices will be in the index coordinate system of the SUB-BLOCK.
        sub_nrow, sub_ncol = self.shape
        tile_rowslice1, tile_colslice1 = key
        tile_rowstart1, tile_rowstop1, tile_rowstride1 = tile_rowslice1.indices(
            sub_nrow
        )
        tile_colstart1, tile_colstop1, tile_colstride1 = tile_colslice1.indices(
            sub_ncol
        )

        # Step 3: Compute the final indices in source-array coordinates to use
        # to extract the requested tile
        tile_rowstart0 = sub_rowstart0 + tile_rowstart1
        tile_rowstop0 = sub_rowstart0 + tile_rowstop1
        tile_rowstride0 = sub_rowstride0 * tile_rowstride1

        tile_colstart0 = sub_colstart0 + tile_colstart1
        tile_colstop0 = sub_colstart0 + tile_colstop1
        tile_colstride0 = sub_colstride0 * tile_colstride1

        tile_rowslice0 = slice(tile_rowstart0, tile_rowstop0, tile_rowstride0)
        tile_colslice0 = slice(tile_colstart0, tile_colstop0, tile_colstride0)

        return self._arr[tile_rowslice0, tile_colslice0]


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
    input_iter = TileIterator(
        arr_shape=in_arr_valid_shape,
        axis_0_tile_dim=in_tiling_shape[0],
        axis_1_tile_dim=in_tiling_shape[1],
    )
    out_iter = TileIterator(
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
    process_arr_by_tiles(
        arr,
        multilook_img,
        calc_backscatter_and_multilook,
        input_batches=input_iter,
        output_batches=out_iter,
    )

    return multilook_img


def compute_histogram_by_tiling(
    arr: ArrayLike,
    bin_edges: np.ndarray,
    arr_name: str = "",
    data_prep_func: Callable | None = None,
    density: bool = False,
    decimation_ratio: tuple[int, int] = (1, 1),
    tile_shape: tuple[int, int] = (512, -1),
) -> np.ndarray:
    """
    Compute decimated histograms by tiling.

    Parameters
    ----------
    arr : array_like
        The input array
    bin_edges : numpy.ndarray
        The bin edges to use for the histogram
    arr_name : str
        Name for the array. (Will be used for log messages.)
    data_prep_func : Callable or None, optional
        Function to process each tile of data through before computing
        the histogram counts. For example, this function can be used
        to convert the values in each tile of raw data to backscatter,
        dB scale, etc. before taking the histogram.
        If `None`, then histogram will be computed on `arr` as-is,
        and no pre-processing of the data will occur.
        Defaults to None.
    density : bool, optional
        If True, return probability densities for histograms:
        Each bin will display the bin's raw count divided by the
        total number of counts and the bin width
        (density = counts / (sum(counts) * np.diff(bins))),
        so that the area under the histogram integrates to 1
        (np.sum(density * np.diff(bins)) == 1).
        Defaults to False.
    decimation_ratio : pair of int, optional
        The step size to decimate the input array for computations.
        For example, (2,3) means every 2nd azimuth line and
        every 3rd range line will be used to compute the histograms.
        Defaults to (1,1), i.e. no decimation will occur.
        Format: (<azimuth>, <range>)
    tile_shape : tuple of ints, optional
        Shape of each tile to be processed. If `tile_shape` is
        larger than the shape of `arr`, or if the dimensions of `arr`
        are not integer multiples of the dimensions of `tile_shape`,
        then smaller tiles may be used.
        -1 to use all rows / all columns (respectively).
        Format: (num_rows, num_cols)
        Defaults to (512,-1) to use all columns (i.e. full rows of data)
        and leverage Python's row-major ordering.

    Returns
    -------
    hist_counts : numpy.ndarray
        The histogram counts.
        If `density` is True, then the backscatter and phase histogram
        densities (respectively) will be returned instead.

    Notes
    -----
    If a cell in the input array is non-finite (invalid),
    then it will not be included in the counts for either
    backscatter nor phase.

    If a cell in the input array is almost zero, then it will not
    be included in the counts for phase.
    """
    arr_shape = np.shape(arr)

    if (arr_shape[0] < decimation_ratio[0]) or (
        arr_shape[1] < decimation_ratio[1]
    ):
        raise ValueError(
            f"{decimation_ratio=} but the array has has dimensions {arr_shape}."
            " For axis 0 and axis 1, `decimation_ratio` must be <= the length"
            " of that dimension."
        )

    if tile_shape[0] == -1:
        tile_shape = (arr_shape[0], tile_shape[1])
    if tile_shape[1] == -1:
        tile_shape = (tile_shape[0], arr_shape[1])

    # Shrink the tile shape to be an even multiple of the decimation ratio.
    # Otherwise, the decimation will get messy to book-keep.
    in_tiling_shape = tuple(
        [m - (m % n) for m, n in zip(tile_shape, decimation_ratio)]
    )

    # Create the Iterator over the input array
    input_iter = TileIterator(
        arr_shape=arr_shape,
        axis_0_tile_dim=in_tiling_shape[0],
        axis_1_tile_dim=in_tiling_shape[1],
        axis_0_stride=decimation_ratio[0],
        axis_1_stride=decimation_ratio[1],
    )

    # Initialize accumulator arrays
    # Use dtype of int to avoid floating point errors
    # (The '- 1' is because the final entry in the *_bin_edges array
    # is the endpoint, which is not considered a bin itself.)
    hist_counts = np.zeros((len(bin_edges) - 1,), dtype=int)

    # Do calculation and accumulate the counts
    for tile_slice in input_iter:
        arr_slice = arr[tile_slice]

        # Remove invalid entries
        # Note: for generating histograms, we do not need to retain the
        # original shape of the array.
        arr_slice = arr_slice[np.isfinite(arr_slice)]

        # Prep the data
        if data_prep_func is not None:
            arr_slice = data_prep_func(arr_slice)

        # Clip the array so that it falls within the bounds of the histogram
        arr_slice = np.clip(arr_slice, a_min=bin_edges[0], a_max=bin_edges[-1])

        # Accumulate the counts
        counts, _ = np.histogram(arr_slice, bins=bin_edges)
        hist_counts += counts

    # If the histogram counts are all zero, then the raster likely did not
    # contain any valid imagery pixels. (Typically, this occurs when
    # there was an issue with ISCE3 processing, and the raster is all NaNs.)
    if np.any(hist_counts):
        sum_check = "PASS"
    else:
        sum_check = "FAIL"
        errmsg = (
            f"{arr_name} histogram contains all zero values. This often occurs"
            " if the source raster contains all NaN values."
        )
        nisarqa.get_logger().error(errmsg)

    # Note result of the check in the summary file before raising an Exception.
    nisarqa.get_summary().check_invalid_pixels_within_threshold(
        result=sum_check,
        threshold="",
        actual="",
        notes=(
            f"{arr_name}: If a 'FAIL' then all histogram bin counts are zero."
            " This likely indicates that the raster contained no valid data."
            " Note: check performed on decimated raster not full raster."
        ),
    )

    if sum_check == "FAIL":
        raise nisarqa.InvalidRasterError(errmsg)

    if density:
        # Change dtype to float
        hist_counts = hist_counts.astype(float)

        # Compute density
        hist_counts = nisarqa.counts2density(hist_counts, bin_edges)

    return hist_counts


def compute_range_spectra_by_tiling(
    arr: ArrayLike,
    sampling_rate: float,
    az_decimation: int = 1,
    tile_height: int = 512,
    fft_shift: bool = True,
) -> np.ndarray:
    """
    Compute the normalized range power spectral density in dB re 1/Hz by tiling.

    Parameters
    ----------
    arr : array_like
        The input array, representing a two-dimensional discrete-time signal.
    sampling_rate : numeric
        Range sample rate (inverse of the sample spacing) in Hz.
    az_decimation : int, optional
        The stride to decimate the input array along the azimuth axis.
        For example, `4` means every 4th range line will
        be used to compute the range spectra.
        If `1`, no decimation will occur (but is slower to compute).
        Must be greater than zero. Defaults to 1.
    tile_height : int, optional
        User-preferred tile height (number of range lines) for processing
        images by batches. Actual tile shape may be modified by QA to be
        an integer multiple of `az_decimation`. -1 to use all rows.
        Note: full rows must be read in, so the number of columns for each tile
        will be fixed to the number of columns in the input raster.
        Defaults to 512.
    fft_shift : bool, optional
        True to shift `S_out` to correspond to frequency bins that are
        continuous from negative (min) -> positive (max) values.

        False to leave `S_out` unshifted, such that the values correspond to
        `numpy.fft.fftfreq()`, where this discrete FFT operation orders values
        from 0 -> max positive -> min negative -> 0- . (This creates
        a discontinuity in the interval's values.)

        Defaults to True.

    Returns
    -------
    S_out : numpy.ndarray
        Normalized range power spectral density in dB re 1/Hz of `arr`.
    """
    shape = np.shape(arr)
    if len(shape) != 2:
        raise ValueError(
            f"Input array has {len(shape)} dimensions, but must be 2D."
        )

    nrows, ncols = shape

    if az_decimation > nrows:
        raise ValueError(
            f"{az_decimation=}, must be <= the height of the input array"
            f" ({nrows} pixels)."
        )

    if tile_height == -1:
        tile_height = nrows

    # Adjust the tile height to be an integer multiple of `az_decimation`.
    # Otherwise, the decimation will get messy to book-keep.
    if tile_height < az_decimation:
        # Grow tile height
        tile_height = az_decimation
    else:
        # Shrink tile height (less risk of memory issues)
        tile_height = tile_height - (tile_height % az_decimation)

    # Compute total number of range lines that will be used to generate
    # the range power spectra. This will be used for averaging.
    # The TileIterator will truncate the array azimuth direction to be
    # an integer multiple of the stride, so use integer division here.
    num_range_lines = nrows // az_decimation

    # Create the Iterator over the input array
    input_iter = TileIterator(
        arr_shape=np.shape(arr),
        axis_0_tile_dim=tile_height,
        axis_0_stride=az_decimation,
    )

    # Initialize the accumulator array
    S_avg = np.zeros(ncols)

    for tile_slice in input_iter:
        S_avg += _get_s_avg_for_tile(
            arr_slice=arr[tile_slice],
            fft_axis=1,  # Compute fft over range axis (axis 1)
            num_fft_bins=ncols,
            averaging_denominator=num_range_lines,
        )

    return _post_process_s_avg(
        S_avg=S_avg, sampling_rate=sampling_rate, fft_shift=fft_shift
    )


def compute_az_spectra_by_tiling(
    arr: ArrayLike,
    sampling_rate: float,
    subswath_slice: Optional[slice] = None,
    tile_width: int = 256,
    fft_shift: bool = True,
) -> np.ndarray:
    """
    Compute normalized azimuth power spectral density in dB re 1/Hz by tiling.

    Parameters
    ----------
    arr : array_like
        Input array, representing a two-dimensional discrete-time signal.
    sampling_rate : numeric
        Azimuth sample rate (inverse of the sample spacing) in Hz.
    subswath_slice : slice or None, optional
        The slice for axes 1 that specifies the columns which define a subswath
        of `arr`; the azimuth spectra will be computed by averaging the
        range samples in this subswath.
            Format: slice(start, stop)
            Example: slice(2, 5)
        If None, or if the number of columns in the subswath is greater than
        the width of the input array, then the full input array will be used.
        Note that all rows will be used to compute the azimuth spectra, so
        there is no need to provide a slice for axes 0.
        Defaults to None.
    tile_width : int, optional
        Tile width (number of columns) for processing each subswath by batches.
        -1 to use the full width of the subswath.
        Defaults to 256.
    fft_shift : bool, optional
        True to shift `S_out` to correspond to frequency bins that are
        continuous from negative (min) -> positive (max) values.

        False to leave `S_out` unshifted, such that the values correspond to
        `numpy.fft.fftfreq()`, where this discrete FFT operation orders values
        from 0 -> max positive -> min negative -> 0- . (This creates
        a discontinuity in the interval's values.)

        Defaults to True.

    Returns
    -------
    S_out : numpy.ndarray
        Normalized azimuth power spectral density in dB re 1/Hz of the
        subswath of `arr` specified by `col_indices`. Azimuth spectra will
        be computed by averaging across columns within the subswath.

    Notes
    -----
    When computing the azimuth spectra, full columns must be read in to
    perform the FFT; this means that the number of rows is always fixed to
    the height of `arr`.

    To reduce processing time, users can decrease the interval of `col_indices`.
    """
    arr_shape = np.shape(arr)
    if len(arr_shape) != 2:
        raise ValueError(
            f"Input array has {len(arr_shape)} dimensions, but must be 2D."
        )

    arr_nrows, arr_ncols = arr_shape

    # Validate column indices
    if subswath_slice is None:
        subswath_slice = np.s_[:]  # equivalent to slice(None, None, None)

    if (subswath_slice.step != 1) and (subswath_slice.step is not None):
        # In theory, having a step size >1 could be supported, but it seems
        # unnecessary and overly complicated to bookkeep for current QA needs.
        msg = (
            "Subswath slice along axes 1 has step value of:"
            f" `{subswath_slice.step}`, which is not supported. Please set"
            " the step value to 1."
        )
        raise NotImplementedError(msg)

    subswath_start, subswath_stop, _ = subswath_slice.indices(arr_ncols)
    subswath_width = subswath_stop - subswath_start

    if (tile_width == -1) or (tile_width > subswath_width):
        tile_width = subswath_width

    # Setup a 2D subblock view of the source array.
    subswath = SubBlock2D(arr=arr, slices=(np.s_[:], subswath_slice))
    assert arr_nrows == subswath.shape[0]
    assert subswath_width == subswath.shape[1]

    # From here on out, we'll treat the `subswath` as if it is our full array.
    # That means are index values will be in `subswath`'s "index
    # coordinate system". (They will no longer be in the "index coordinate
    # system" of the input `arr`.)

    # The TileIterator can only pull full tiles. In other functions, we simply
    # truncate the full array to have each edge be an integer multiple of the
    # tile shape. Here, the user specified an exact number of columns, so we
    # should not truncate.
    # To handle this, let's first iterate over the "truncated" array,
    # and then add in the "leftover" columns.

    # Truncate the column indices to be an integer multiple of `tile_width`.
    leftover_width = subswath_width % tile_width
    trunc_width = subswath_width - leftover_width

    # Create the Iterator over the truncated subswath array
    input_iter = TileIterator(
        arr_shape=(arr_nrows, trunc_width),
        axis_0_tile_dim=-1,  # use all rows
        axis_1_tile_dim=tile_width,
    )

    # Initialize the accumulator array
    S_avg = np.zeros(arr_nrows)

    # Compute FFT over the truncated portion of the subswath
    for tile_slice in input_iter:
        S_avg += _get_s_avg_for_tile(
            arr_slice=subswath[tile_slice],
            fft_axis=0,  # Compute fft over along-track axis (axis 0)
            num_fft_bins=arr_nrows,
            averaging_denominator=subswath_width,  # full subswath (not truncated)
        )

    # Repeat process for the "leftover" portion of the subswath
    if leftover_width > 0:
        leftover_2D_slice = (
            np.s_[:],
            slice(subswath_width - leftover_width, subswath_width),
        )

        leftover_subswath = subswath[leftover_2D_slice]
        S_avg += _get_s_avg_for_tile(
            arr_slice=leftover_subswath,
            fft_axis=0,  # Compute fft over along-track axis (axis 0)
            num_fft_bins=arr_nrows,
            averaging_denominator=subswath_width,
        )

    return _post_process_s_avg(
        S_avg=S_avg, sampling_rate=sampling_rate, fft_shift=fft_shift
    )


def _get_s_avg_for_tile(
    arr_slice: ArrayLike,
    fft_axis: int,
    num_fft_bins: int,
    averaging_denominator: int,
) -> np.ndarray:
    """
    Helper function for the power spectra; computes the S_avg array for a tile.

    This function is designed to be called by a function that is handling the
    iteration process over all tiles in an array.

    Parameters
    ----------
    arr_slice : array_like
        Slice of a 2D Array to compute the FFT of. We're in the "tiling.py"
        module; `arr_slice` should be a full tile.
    fft_axis : int
        0 to compute the FFT along the azimuth axis,
        1 to compute along the range axis.
    num_fft_bins : int
        Number of FFT bins.
    averaging_denominator : int
        Total number of elements in the source array that will be averaged
        together to form the `S_avg` array.
        For Range Spectra, this is the number of range lines.
        For Azimuth Spectra, this is the subswath width.
        (We are processing the array by tiles, but the total summation of
        power might cause float overflow.
        So, during the accumulation process, if we divide each tile's
        power density by the total number of samples used, then the
        final accumulated array will be mathematically equivalent to
        the average.)

    Returns
    -------
    S_avg_partial : numpy.ndarray
        Normalized FFT that has been "averaged" with `averaging_denominator`.
    """

    # Compute FFT
    # Ensure no normalization occurs here; do that manually below.
    # Units of `fft` are the same as the units of `arr_slice`: unitless
    fft = nisarqa.compute_fft(arr_slice, axis=fft_axis)

    # Compute the power
    S = np.abs(fft) ** 2

    # Normalize the transform
    S /= num_fft_bins

    # Average over the opposite axis
    #   `1 - fft_axis` will flip a 1 to a 0, or a 0 to a 1.
    return np.sum(S, axis=1 - fft_axis) / averaging_denominator


def _post_process_s_avg(
    S_avg: ArrayLike, sampling_rate: float, fft_shift: bool
) -> np.ndarray:
    """
    Helper function for the power spectra; post-processes average spectra.

    Parameters
    ----------
    S_avg : array_like
        The averaged spectra
    sampling_rate : numeric
        Range sample rate (inverse of the sample spacing) in Hz. Used to
        normalize `S_avg`.
    fft_shift : bool, optional
        True to shift `S_out` to correspond to frequency bins that are
        continuous from negative (min) -> positive (max) values.

        False to leave `S_out` unshifted, such that the values correspond to
        `numpy.fft.fftfreq()`, where this discrete FFT operation orders values
        from 0 -> max positive -> min negative -> 0- . (This creates
        a discontinuity in the interval's values.)

        Defaults to True.

    Returns
    -------
    S_out : numpy.ndarray
        Normalized power spectral density in dB re 1/Hz.
    """
    # Normalize by the sampling rate
    # This makes the units unitless/Hz
    S_out = S_avg / sampling_rate

    # Convert to dB
    with nisarqa.ignore_runtime_warnings():
        # This line throws these warnings:
        #   "RuntimeWarning: divide by zero encountered in log10"
        # when there are zero values. Ignore those warnings.
        S_out = nisarqa.pow2db(S_out)

    if fft_shift:
        # Shift S_out to be aligned with the shifted FFT frequencies.
        S_out = np.fft.fftshift(S_out)

    return S_out


__all__ = nisarqa.get_all(__name__, objects_to_skip)
