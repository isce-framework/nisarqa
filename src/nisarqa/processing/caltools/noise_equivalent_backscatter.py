from __future__ import annotations

import os
from contextlib import ExitStack

import h5py

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


@nisarqa.log_function_runtime
def run_neb_tool(
    rslc: nisarqa.RSLC,
    stats_filename: str | os.PathLike,
) -> None:
    """
    Run the Noise Equivalent Backscatter (NEB) Tool workflow.

    Parameters
    ----------
    rslc : nisarqa.RSLC
        The RSLC product.
    stats_filename : path-like
        Filename (with path) for output STATS.h5 file. This is where
        outputs from the CalTool should be stored.
    """
    with ExitStack() as stack:
        stats_file = stack.enter_context(h5py.File(stats_filename, "a"))

        for freq in rslc.freqs:
            try:
                src_grp = stack.enter_context(
                    rslc.get_noise_eq_group(freq=freq)
                )
            except nisarqa.InvalidNISARProductError:
                nisarqa.get_logger().error(
                    "Input RSLC product is missing noise equivalent backscatter"
                    f" data for frequency {freq}. Skipping copying of data"
                    " to STATS HDF5 and skipping creating plots."
                )
                # Return early
                return

            # Step 1: Copy NEB data from input RSLC to outputs STATS.h5
            dest_grp_path = (
                f"{nisarqa.STATS_H5_NEB_DATA_GROUP % rslc.band}"
                f"/frequency{freq}"
            )
            src_grp.copy(src_grp, stats_file, dest_grp_path)

            # TODO: Step 2: create plots


__all__ = nisarqa.get_all(__name__, objects_to_skip)
