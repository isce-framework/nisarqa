from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from typing import Any

import h5py
import numpy as np
from nisar.workflows import estimate_abscal_factor
from numpy.typing import DTypeLike

import nisarqa
from nisarqa import AbsCalParamGroup, DynamicAncillaryFileParamGroup

from ._utils import file_is_empty, get_copols

objects_to_skip = nisarqa.get_all(name=__name__)


def run_abscal_single_freq_pol(
    corner_reflector_csv: str | os.PathLike,
    rslc_hdf5: str | os.PathLike,
    freq: str,
    pol: str,
    abscal_params: AbsCalParamGroup,
) -> list[dict[str, Any]]:
    """
    Run the absolute radiometric calibration (AbsCal) tool.

    Run the `nisar.workflows.estimate_abscal_factor` workflow on a single
    freq/pol in the input RSLC file and parse the JSON output to a list of dicts
    containing one dict per valid corner reflector found in the scene.

    See the corresponding script in the `nisar` package for a detailed
    description of the output.

    Parameters
    ----------
    corner_reflector_csv : path-like
        A CSV file containing corner reflector data in the format defined by the
        NISAR Corner Reflector Software Interface Specification (SIS) document\
        [1]_.
    rslc_hdf5 : path-like
        A NISAR RSLC product file path.
    freq : {'A', 'B'}
        The frequency sub-band of the data.
    pol : str
        The transmit and receive polarization of the data.
    abscal_params : AbsCalParamGroup
        A dataclass containing the parameters for processing
        and outputting the Absolute Calibration Factor workflow.

    Returns
    -------
    results : list of dict
        A list of dicts containing one entry per valid corner reflector found
        within the area imaged by the RSLC product.

    Notes
    -----
    Since some corner reflectors may be outside the image bounds of a given
    radar observation, if the tool encounters an error while processing any
    particular target, it will emit a warning with the exception & traceback
    info and continue on to processing the next target.

    References
    ----------
    .. [1] B. Hawkins, "Corner Reflector Software Interface Specification," JPL
       D-107698 (2023).
    """
    # The parameter names in AbsCalParamGroup were designed to be identical to
    # the keyword arguments of `estimate_abscal_factor.main()` (with the
    # exception of `pthresh`, handled below). If/when this assumption no longer
    # holds, then a KeyError will be thrown below, and QA code will need to be
    # updated accordingly.
    kwds = asdict(abscal_params)

    # Rename 'power_threshold' to 'pthresh'.
    assert "pthresh" not in kwds
    kwds["pthresh"] = kwds.pop("power_threshold")

    # Create a scratch file to store the JSON output of the tool.
    tmpfile = nisarqa.get_global_scratch_dir() / f"abscal-{freq}-{pol}.json"

    # Run AbsCal tool.
    estimate_abscal_factor.main(
        corner_reflector_csv=corner_reflector_csv,
        csv_format="nisar",
        rslc_hdf5=rslc_hdf5,
        output_json=tmpfile,
        freq=freq,
        pol=pol,
        external_orbit_xml=None,  # Use the orbit in the RSLC product.
        **kwds,
    )

    # Parse the JSON output.
    # `json.load()` fails if the file is empty.
    if file_is_empty(tmpfile):
        return []
    else:
        with open(tmpfile, "r") as f:
            return json.load(f)


def populate_abscal_hdf5_output(
    stats_h5: h5py.File,
    grp_path: str,
    abscal_results: Sequence[Mapping[str, Any]],
) -> None:
    """
    Store the output of the AbsCal tool in the stats HDF5 file.

    Parameters
    ----------
    stats_h5 : h5py.File
        Handle to an HDF5 file where the absolute radiometric calibration
        (AbsCal) results should be saved.
    grp_path : str
        The path of the group within `stats_h5` to store the results in. The
        group will be created if it did not already exist.
    abscal_results : sequence of dict
        The output of the AbsCal tool. A list of dicts containing one entry per
        valid corner reflector found within the area imaged by the RSLC product.
    """

    # Helper function to create a new dataset within `grp_path` that stores info
    # about each corner reflector in the AbsCal output.
    #
    # The contents of the dataset are obtained by extracting the value of `key`
    # for each corner reflector in the input `abscal_results` and casting the
    # resulting array to `ds_dtype`.
    #
    # The dataset name, description, and (optional) units are supplied by the
    # `ds_name`, `ds_descr`, and `ds_units` arguments.
    def create_dataset_from_abscal_results(
        key: str,
        ds_name: str,
        ds_descr: str,
        ds_dtype: DTypeLike,
        ds_units: str | None = None,
    ):
        ds_data = np.asarray([d[key] for d in abscal_results], dtype=ds_dtype)
        nisarqa.create_dataset_in_h5group(
            h5_file=stats_h5,
            grp_path=grp_path,
            ds_name=ds_name,
            ds_data=ds_data,
            ds_description=ds_descr,
            ds_units=ds_units,
        )

    create_dataset_from_abscal_results(
        key="id",
        ds_name="cornerReflectorId",
        ds_descr="The unique identifier of the corner reflector",
        ds_dtype=np.bytes_,
    )

    create_dataset_from_abscal_results(
        key="survey_date",
        ds_name="cornerReflectorSurveyDate",
        ds_descr=(
            "The date (and time) when the corner reflector was surveyed most"
            " recently prior to the radar observation, as a string in ISO 8601"
            " format"
        ),
        ds_dtype=np.bytes_,
    )

    create_dataset_from_abscal_results(
        key="velocity",
        ds_name="cornerReflectorVelocity",
        ds_descr=(
            "The corner reflector velocity due to tectonic plate motion, as an"
            " East-North-Up (ENU) vector in meters per second (m/s). The"
            " velocity components are provided in local ENU coordinates with"
            " respect to the WGS 84 reference ellipsoid"
        ),
        ds_dtype=np.float64,
        ds_units="meters per second",
    )

    create_dataset_from_abscal_results(
        key="timestamp",
        ds_name="radarObservationDate",
        ds_descr=(
            "The radar observation date and time of the corner reflector in"
            " UTC, as a string in the format YYYY-mm-ddTHH:MM:SS.sssssssss"
        ),
        ds_dtype=np.bytes_,
    )

    create_dataset_from_abscal_results(
        key="elevation_angle",
        ds_name="elevationAngle",
        ds_descr=(
            "Antenna elevation angle, in radians, measured w.r.t. antenna"
            " boresight, increasing toward the far-range direction and"
            " decreasing (becoming negative) toward the near-range direction"
        ),
        ds_dtype=np.float64,
        ds_units="radians",
    )

    create_dataset_from_abscal_results(
        key="absolute_calibration_factor",
        ds_name="absoluteCalibrationFactor",
        ds_descr=(
            "The absolute radiometric calibration error for the corner"
            " reflector (the ratio of the measured RCS to the predicted RCS),"
            " in linear units"
        ),
        ds_dtype=np.float64,
        ds_units="1",
    )


@nisarqa.log_function_runtime
def run_abscal_tool(
    abscal_params: AbsCalParamGroup,
    dyn_anc_params: DynamicAncillaryFileParamGroup,
    rslc: nisarqa.RSLC,
    stats_filename: str | os.PathLike,
) -> None:
    """
    Run the Absolute Calibration Factor workflow.

    Parameters
    ----------
    abscal_params : AbsCalParamGroup
        A dataclass containing the parameters for processing
        and outputting the Absolute Calibration Factor workflow.
    dyn_anc_params : DynamicAncillaryFileParamGroup
        A dataclass containing the parameters for the dynamic
        ancillary files.
    rslc : nisarqa.RSLC
        The RSLC product.
    stats_filename : path-like
        Filename (with path) for output STATS.h5 file. This is where
        outputs from the CalTool should be stored.
    """
    for freq in rslc.freqs:
        # The scattering matrix of a canonical triangular trihedral corner
        # reflector is diagonal. We're only interested in measuring the co-pol
        # response since the cross-pol response should be negligible.
        pols = get_copols(rslc, freq)

        for pol in pols:
            with nisarqa.log_runtime(
                f"`run_abscal_single_freq_pol` for Frequency {freq},"
                f" Polarization {pol}"
            ):
                results = run_abscal_single_freq_pol(
                    corner_reflector_csv=dyn_anc_params.corner_reflector_file,
                    rslc_hdf5=rslc.filepath,
                    freq=freq,
                    pol=pol,
                    abscal_params=abscal_params,
                )
            nisarqa.get_logger().info(
                f"AbsCal Tool for Frequency {freq}, Polarization {pol}"
                f" found {len(results)} corner reflectors."
            )

            # Check if the results were empty (i.e. if there were no valid
            # corner reflectors in the scene). If so, don't create any HDF5
            # output for this freq/pol.
            if results:
                group_path = (
                    nisarqa.STATS_H5_ABSCAL_DATA_GROUP % rslc.band
                    + f"/frequency{freq}/{pol}"
                )

                with h5py.File(stats_filename, mode="a") as stats_h5:
                    populate_abscal_hdf5_output(
                        stats_h5=stats_h5,
                        grp_path=group_path,
                        abscal_results=results,
                    )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
