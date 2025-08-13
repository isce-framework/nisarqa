from __future__ import annotations

import warnings

import numpy as np
from numpy.typing import ArrayLike, DTypeLike

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


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


__all__ = nisarqa.get_all(__name__, objects_to_skip)
