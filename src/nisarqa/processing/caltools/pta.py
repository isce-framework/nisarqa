from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from typing import Any

import h5py
import numpy as np
from nisar.workflows import gslc_point_target_analysis, point_target_analysis
from numpy.typing import DTypeLike

import nisarqa
from nisarqa import (
    DynamicAncillaryFileParamGroup,
    GSLCDynamicAncillaryFileParamGroup,
    PointTargetAnalyzerParamGroup,
    RSLCPointTargetAnalyzerParamGroup,
)

from ._utils import file_is_empty, get_copols

objects_to_skip = nisarqa.get_all(name=__name__)


@nisarqa.log_function_runtime
def run_rslc_pta_tool(
    pta_params: RSLCPointTargetAnalyzerParamGroup,
    dyn_anc_params: DynamicAncillaryFileParamGroup,
    rslc: nisarqa.RSLC,
    stats_filename: str | os.PathLike,
) -> None:
    """
    Run the RSLC Point Target Analyzer (PTA) workflow.

    Parameters
    ----------
    pta_params : RSLCPointTargetAnalyzerParamGroup
        A dataclass containing the parameters for processing
        and outputting the Point Target Analyzer workflow.
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
                f"`run_rslc_pta_single_freq_pol` for Frequency {freq},"
                f" Polarization {pol}"
            ):
                results = run_rslc_pta_single_freq_pol(
                    corner_reflector_csv=dyn_anc_params.corner_reflector_file,
                    rslc_hdf5=rslc.filepath,
                    freq=freq,
                    pol=pol,
                    pta_params=pta_params,
                )
            nisarqa.get_logger().info(
                f"RSLC PTA Tool for Frequency {freq}, Polarization {pol}"
                f" found {len(results)} corner reflectors."
            )

            # Check if the results were empty (i.e. if there were no valid
            # corner reflectors in the scene). If so, don't create any HDF5
            # output for this freq/pol.
            if results:
                freq_group_path = (
                    nisarqa.STATS_H5_PTA_DATA_GROUP % rslc.band
                    + f"/frequency{freq}"
                )
                pol_group_path = freq_group_path + f"/{pol}"

                with h5py.File(stats_filename, mode="a") as stats_h5:
                    populate_pta_hdf5_output(
                        stats_h5=stats_h5,
                        grp_path=pol_group_path,
                        product_type="RSLC",
                        pta_results=results,
                    )

                    # Several of the PTA outputs are expressed in pixel
                    # coordinates rather than physical units. In order to assist
                    # with interpretability of these values, we also provide the
                    # pixel spacing of the radar grid (if not already provided
                    # for this frequency sub-band).
                    freq_group = stats_h5[freq_group_path]
                    if not "slantRangeSpacing" in freq_group:
                        nisarqa.create_dataset_in_h5group(
                            h5_file=stats_h5,
                            grp_path=freq_group_path,
                            ds_name="slantRangeSpacing",
                            ds_data=rslc.get_slant_range_spacing(freq),
                            ds_description="Slant range spacing of grid",
                            ds_units="meters",
                        )

                        assert "sceneCenterAlongTrackSpacing" not in freq_group
                        nisarqa.create_dataset_in_h5group(
                            h5_file=stats_h5,
                            grp_path=freq_group_path,
                            ds_name="sceneCenterAlongTrackSpacing",
                            ds_data=(
                                rslc.get_scene_center_along_track_spacing(freq)
                            ),
                            ds_description=(
                                "Nominal along track spacing in meters between"
                                " consecutive lines near mid swath of the RSLC"
                                " image"
                            ),
                            ds_units="meters",
                        )


@nisarqa.log_function_runtime
def run_gslc_pta_tool(
    pta_params: PointTargetAnalyzerParamGroup,
    dyn_anc_params: GSLCDynamicAncillaryFileParamGroup,
    gslc: nisarqa.GSLC,
    stats_filename: str | os.PathLike,
) -> None:
    """
    Run the GSLC Point Target Analyzer (PTA) workflow.

    Parameters
    ----------
    pta_params : PointTargetAnalyzerParamGroup
        A dataclass containing the parameters for processing
        and outputting the Point Target Analyzer workflow.
    dyn_anc_params : GSLCDynamicAncillaryFileParamGroup
        A dataclass containing the parameters for the dynamic
        ancillary files.
    gslc : nisarqa.GSLC
        The GSLC product.
    stats_filename : path-like
        Filename (with path) for output STATS.h5 file. This is where
        outputs from the CalTool should be stored.
    """

    for freq in gslc.freqs:
        # The scattering matrix of a canonical triangular trihedral corner
        # reflector is diagonal. We're only interested in measuring the co-pol
        # response since the cross-pol response should be negligible.
        pols = get_copols(gslc, freq)

        for pol in pols:
            with nisarqa.log_runtime(
                f"`run_gslc_pta_single_freq_pol` for Frequency {freq},"
                f" Polarization {pol}"
            ):
                results = run_gslc_pta_single_freq_pol(
                    corner_reflector_csv=dyn_anc_params.corner_reflector_file,
                    gslc_hdf5=gslc.filepath,
                    freq=freq,
                    pol=pol,
                    pta_params=pta_params,
                    dem_file=dyn_anc_params.dem_file,
                )
            nisarqa.get_logger().info(
                f"GSLC PTA Tool for Frequency {freq}, Polarization {pol}"
                f" found {len(results)} corner reflectors."
            )

            # Check if the results were empty (i.e. if there were no valid
            # corner reflectors in the scene). If so, don't create any HDF5
            # output for this freq/pol.
            if not results:
                continue

            freq_group_path = (
                nisarqa.STATS_H5_PTA_DATA_GROUP % gslc.band
                + f"/frequency{freq}"
            )
            pol_group_path = freq_group_path + f"/{pol}"

            with h5py.File(stats_filename, mode="a") as stats_h5:
                populate_pta_hdf5_output(
                    stats_h5=stats_h5,
                    grp_path=pol_group_path,
                    product_type="GSLC",
                    pta_results=results,
                )

                # Several of the PTA outputs are expressed in pixel coordinates
                # rather than physical units. In order to assist with
                # interpretability of these values, we also provide the pixel
                # spacing of the image grid (if not already provided for this
                # frequency sub-band).
                freq_group = stats_h5[freq_group_path]
                if not "xCoordinateSpacing" in freq_group:
                    with gslc.get_raster(freq, pol) as raster:
                        descr = (
                            "Nominal spacing in meters between consecutive"
                            " pixels"
                        )
                        nisarqa.create_dataset_in_h5group(
                            h5_file=stats_h5,
                            grp_path=freq_group_path,
                            ds_name="xCoordinateSpacing",
                            ds_data=raster.x_spacing,
                            ds_description=descr,
                            ds_units="meters",
                        )
                        assert "yCoordinateSpacing" not in freq_group
                        nisarqa.create_dataset_in_h5group(
                            h5_file=stats_h5,
                            grp_path=freq_group_path,
                            ds_name="yCoordinateSpacing",
                            ds_data=raster.y_spacing,
                            ds_description=descr,
                            ds_units="meters",
                        )


def run_rslc_pta_single_freq_pol(
    corner_reflector_csv: str | os.PathLike,
    rslc_hdf5: str | os.PathLike,
    *,
    freq: str,
    pol: str,
    pta_params: RSLCPointTargetAnalyzerParamGroup,
) -> list[dict[str, Any]]:
    """
    Run the RSLC point target analysis (PTA) tool.

    Run the `nisar.workflows.point_target_analysis` workflow on a single
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
    pta_params : RSLCPointTargetAnalyzerParamGroup
        A dataclass containing the parameters for processing
        and outputting the Point Target Analyzer workflow.

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
    # The parameter names in RSLCPointTargetAnalyzerParamGroup were designed to
    # be identical to the keyword arguments of
    # `point_target_analysis.process_corner_reflector_csv()`. If/when this
    # assumption no longer holds, then a KeyError will be thrown below, and QA
    # code will need to be updated accordingly.
    kwds = asdict(pta_params)

    # Create a scratch file to store the JSON output of the tool.
    tmpfile = nisarqa.get_global_scratch_dir() / f"abscal-{freq}-{pol}.json"

    # Run PTA tool.
    point_target_analysis.process_corner_reflector_csv(
        corner_reflector_csv=corner_reflector_csv,
        csv_format="nisar",
        rslc_hdf5=rslc_hdf5,
        output_json=tmpfile,
        freq=freq,
        pol=pol,
        cuts=True,
        **kwds,
    )

    # Parse the JSON output.
    # `json.load()` fails if the file is empty.
    if file_is_empty(tmpfile):
        return []
    else:
        with open(tmpfile, "r") as f:
            return json.load(f)


def run_gslc_pta_single_freq_pol(
    corner_reflector_csv: str | os.PathLike,
    gslc_hdf5: str | os.PathLike,
    *,
    freq: str,
    pol: str,
    pta_params: PointTargetAnalyzerParamGroup,
    dem_file: str | os.PathLike | None = None,
) -> list[dict[str, Any]]:
    """
    Run the GSLC point target analysis (PTA) tool.

    Run the `nisar.workflows.gslc_point_target_analysis` workflow on a single
    freq/pol in the input GSLC file and parse the JSON output to a list of dicts
    containing one dict per valid corner reflector found in the scene.

    See the corresponding script in the `nisar` package for a detailed
    description of the output.

    Parameters
    ----------
    corner_reflector_csv : path-like
        A CSV file containing corner reflector data in the format defined by the
        NISAR Corner Reflector Software Interface Specification (SIS) document\
        [1]_.
    gslc_hdf5 : path-like
        A NISAR GSLC product file path.
    freq : {'A', 'B'}
        The frequency sub-band of the data.
    pol : str
        The transmit and receive polarization of the data.
    pta_params : PointTargetAnalyzerParamGroup
        A dataclass containing the parameters for processing
        and outputting the Point Target Analyzer workflow.
    dem_file : path-like or None, optional
        Optional Digital Elevation Model (DEM) file in a GDAL-compatible raster
        format. Used for flattening phase removal of the GSLC data, if
        applicable (i.e. if the GSLC was flattened). If None (no DEM is
        supplied), the PTA tool will attempt to un-flatten using the reference
        ellipsoid, which may produce less accurate results. Defaults to None.

    Returns
    -------
    results : list of dict
        A list of dicts containing one entry per valid corner reflector found
        within the area imaged by the GSLC product.

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
    # The parameter names in PointTargetAnalyzerParamGroup were designed to be
    # identical to the keyword arguments of
    # `gslc_point_target_analysis.analyze_gslc_point_targets_csv()`. If/when
    # this assumption no longer holds, then a KeyError will be thrown below, and
    # QA code will need to be updated accordingly.
    kwds = asdict(pta_params)

    # Create a scratch file to store the JSON output of the tool.
    tmpfile = nisarqa.get_global_scratch_dir() / f"abscal-{freq}-{pol}.json"

    # Run PTA tool.
    gslc_point_target_analysis.analyze_gslc_point_targets_csv(
        gslc_filename=gslc_hdf5,
        output_file=tmpfile,
        corner_reflector_csv=corner_reflector_csv,
        freq=freq,
        pol=pol,
        dem_path=dem_file,
        cuts=True,
        cr_format="nisar",
        **kwds,
    )

    # Parse the JSON output.
    # `json.load()` fails if the file is empty.
    if file_is_empty(tmpfile):
        return []
    else:
        with open(tmpfile, "r") as f:
            return json.load(f)


def populate_pta_hdf5_output(
    stats_h5: h5py.File,
    grp_path: str,
    product_type: str,
    pta_results: Sequence[Mapping[str, Any]],
) -> None:
    """
    Store the output of the RSLC/GSLC PTA tool in the stats HDF5 file.

    Parameters
    ----------
    stats_h5 : h5py.File
        Handle to an HDF5 file where the point target analysis (PTA) results
        should be saved.
    grp_path : str
        The path of the group within `stats_h5` to store the results in. The
        group will be created if it did not already exist.
    product_type : {'RSLC', 'GSLC'}
        The type of NISAR product that the PTA tool was run on. Either 'RSLC' or
        'GSLC'.
    pta_results : sequence of dict
        The output of the PTA tool. A list of dicts containing one entry per
        valid corner reflector found within the area imaged by the RSLC/GSLC
        product.
    """

    valid_product_types = {"RSLC", "GSLC"}
    if product_type not in valid_product_types:
        raise ValueError(
            f"`product_type` must be in {valid_product_types}, instead got"
            f" {product_type!r}"
        )

    # Helper function to create a new dataset within `grp_path` that stores info
    # about each corner reflector in the PTA output. This function is a bit more
    # complicated than in the AbsCal case due to the presence of nested dicts in
    # the `pta_results` that are used to populate nested groups in the HDF5 file.
    #
    # The `key` and (optionally) `subkey` arguments are used to extract data for
    # each corner reflector from the input list of (possibly nested) dicts. The
    # resulting array is then cast to `ds_dtype` to form the contents of the
    # HDF5 dataset.
    #
    # The dataset name, description, and (optional) units are supplied by the
    # `ds_name`, `ds_descr`, and `ds_units` arguments.
    def create_dataset_from_pta_results(
        key: str,
        grp_path: str,
        ds_name: str,
        ds_descr: str,
        ds_dtype: DTypeLike,
        ds_units: str | None = None,
        subkey: str | None = None,
    ):
        if subkey is None:
            data = [d[key] for d in pta_results]
        else:
            data = [d[key][subkey] for d in pta_results]

        ds_data = np.asarray(data, dtype=ds_dtype)

        nisarqa.create_dataset_in_h5group(
            h5_file=stats_h5,
            grp_path=grp_path,
            ds_name=ds_name,
            ds_data=ds_data,
            ds_description=ds_descr,
            ds_units=ds_units,
        )

    create_dataset_from_pta_results(
        key="id",
        grp_path=grp_path,
        ds_name="cornerReflectorId",
        ds_descr="The unique identifier of the corner reflector",
        ds_dtype=np.bytes_,
    )

    create_dataset_from_pta_results(
        key="survey_date",
        grp_path=grp_path,
        ds_name="cornerReflectorSurveyDate",
        ds_descr=(
            "The date (and time) when the corner reflector was surveyed most"
            " recently prior to the radar observation, as a string in ISO 8601"
            " format"
        ),
        ds_dtype=np.bytes_,
    )

    create_dataset_from_pta_results(
        key="validity",
        grp_path=grp_path,
        ds_name="cornerReflectorValidity",
        ds_descr=(
            "The integer validity code of the corner reflector. Refer to the"
            " NISAR Corner Reflector Software Interface Specification (SIS)"
            " document for details"
        ),
        ds_dtype=np.int_,
    )

    create_dataset_from_pta_results(
        key="velocity",
        grp_path=grp_path,
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

    create_dataset_from_pta_results(
        key="magnitude",
        grp_path=grp_path,
        ds_name="peakMagnitude",
        ds_descr="The peak magnitude of the impulse response",
        ds_dtype=np.float64,
        ds_units="1",
    )

    create_dataset_from_pta_results(
        key="phase",
        grp_path=grp_path,
        ds_name="peakPhase",
        ds_descr="The phase at the peak location, in radians",
        ds_dtype=np.float64,
        ds_units="radians",
    )

    create_dataset_from_pta_results(
        key="timestamp",
        grp_path=grp_path,
        ds_name="radarObservationDate",
        ds_descr=(
            "The radar observation date and time of the corner reflector in"
            " UTC, as a string in the format YYYY-mm-ddTHH:MM:SS.sssssssss"
        ),
        ds_dtype=np.bytes_,
    )

    create_dataset_from_pta_results(
        key="elevation_angle",
        grp_path=grp_path,
        ds_name="elevationAngle",
        ds_descr=(
            "Antenna elevation angle, in radians, measured w.r.t. antenna"
            " boresight, increasing toward the far-range direction and"
            " decreasing (becoming negative) toward the near-range direction"
        ),
        ds_dtype=np.float64,
        ds_units="radians",
    )

    if product_type == "RSLC":
        image_axes = ["azimuth", "range"]
    elif product_type == "GSLC":
        image_axes = ["X", "Y"]
    else:
        # Should be unreachable.
        assert False, f"unexpected product type {product_type}"

    for axis in image_axes:
        axis_grp_path = f"{grp_path}/{axis.lower()}Position"

        create_dataset_from_pta_results(
            key=axis.lower(),
            subkey="index",
            grp_path=axis_grp_path,
            ds_name="peakIndex",
            ds_descr=(
                f"The real-valued {axis} index, in samples, of the estimated"
                " peak location of the impulse response function (IRF) within"
                f" the {product_type} image grid"
            ),
            ds_dtype=np.float64,
            ds_units="samples",
        )

        create_dataset_from_pta_results(
            key=axis.lower(),
            subkey="offset",
            grp_path=axis_grp_path,
            ds_name="peakOffset",
            ds_descr=(
                f"The error in the predicted target location in the {axis}"
                " direction, in samples. Equal to the signed difference between"
                " the measured location of the impulse response peak in the"
                f" {product_type} data and the predicted location of the peak"
                " based on the surveyed corner reflector location"
            ),
            ds_dtype=np.float64,
            ds_units="samples",
        )

        create_dataset_from_pta_results(
            key=axis.lower(),
            subkey="phase ramp",
            grp_path=axis_grp_path,
            ds_name="phaseSlope",
            ds_descr=(
                f"The estimated local {axis} phase slope at the target"
                " location, in radians per sample"
            ),
            ds_dtype=np.float64,
            ds_units="radians per sample",
        )

    for direction in ["azimuth", "range"]:
        direction_grp_path = f"{grp_path}/{direction}IRF"

        islr_descr = (
            f"The integrated sidelobe ratio (ISLR) of the {direction} impulse"
            " response function (IRF), in decibels (dB). A measure of the"
            " ratio of energy in the sidelobes to the energy in the main"
            " lobe"
        )

        # The RSLC PTA exposes the `predict_null` option, which is not supported
        # by the GSLC PTA tool.
        if product_type == "RSLC":
            islr_descr += (
                ". If `predict_null` was true, the first sidelobe will be"
                " considered part of the main lobe and the ISLR will instead"
                " measure the ratio of energy in the remaining sidelobes to the"
                " energy in the main lobe + first sidelobe"
            )

        create_dataset_from_pta_results(
            key=direction,
            subkey="ISLR",
            grp_path=direction_grp_path,
            ds_name="ISLR",
            ds_descr=islr_descr,
            ds_dtype=np.float64,
            ds_units="1",
        )

        create_dataset_from_pta_results(
            key=direction,
            subkey="PSLR",
            grp_path=direction_grp_path,
            ds_name="PSLR",
            ds_descr=(
                f"The peak-to-sidelobe ratio (PSLR) of the {direction} impulse"
                " response function (IRF), in decibels (dB). A measure of the"
                " ratio of peak sidelobe power to the peak main lobe power"
            ),
            ds_dtype=np.float64,
            ds_units="1",
        )

        create_dataset_from_pta_results(
            key=direction,
            subkey="resolution",
            grp_path=direction_grp_path,
            ds_name="resolution",
            ds_descr=(
                f"The measured 3dB width of the {direction} impulse response"
                " function (IRF), in samples"
            ),
            ds_dtype=np.float64,
            ds_units="samples",
        )

        cut_grp_path = direction_grp_path + "/cut"

        create_dataset_from_pta_results(
            key=direction,
            subkey="cut",
            grp_path=cut_grp_path,
            ds_name="index",
            ds_descr=(
                f"The {direction} sample indices of the magnitude and phase cut"
                " values"
            ),
            ds_dtype=np.float64,
            ds_units="samples",
        )

        create_dataset_from_pta_results(
            key=direction,
            subkey="magnitude cut",
            grp_path=cut_grp_path,
            ds_name="magnitude",
            ds_descr=(
                "The magnitude of the (upsampled) impulse response function"
                f" (IRF) in {direction}"
            ),
            ds_dtype=np.float64,
            ds_units="1",
        )

        create_dataset_from_pta_results(
            key=direction,
            subkey="phase cut",
            grp_path=cut_grp_path,
            ds_name="phase",
            ds_descr=(
                "The phase of the (upsampled) impulse response function (IRF)"
                f" in {direction}"
            ),
            ds_dtype=np.float64,
            ds_units="radians",
        )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
