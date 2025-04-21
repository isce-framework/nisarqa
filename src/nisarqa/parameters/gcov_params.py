from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, fields
from typing import Optional

import nisarqa
from nisarqa.parameters.nisar_params import (
    InputFileGroupParamGroup,
    ScratchProductPathGroupParamGroup,
    SoftwareConfigGroupParamGroup,
    NonInsarRootParamGroup,
    ValidationGroupParamGroup,
    WorkflowsParamGroup,
)

# TODO Remove the rslc_caltools_params imports after re-org of code
from nisarqa.parameters.rslc_caltools_params import (
    BackscatterImageParamGroup,
    HistogramParamGroup,
)

objects_to_skip = nisarqa.get_all(__name__)


@dataclass(frozen=True)
class GCOVHistogramParamGroup(HistogramParamGroup):
    """
    Parameters to generate GCOV Backscatter and Phase Histograms.

    Parameters
    ----------
    decimation_ratio : pair of int, optional
        The step size to decimate the input array for computing
        the backscatter and phase histograms.
        For example, (2,3) means every 2nd azimuth line and
        every 3rd range sample will be used to compute the histograms.
        Defaults to (8, 8).
        Format: (<azimuth>, <range>)
    phase_histogram_y_axis_range : None or pair of float or None, optional
        The range for the phase histograms' y-axis.
            Format: [<min of range>, <max of range>]
            Example: None, [0.0, None], [None, 0.7], [-0.2, 1.2], [None, None]
        If the min or max is set to None, then that limit is set dynamically
        based on the range of phase histogram density values.
        If None, this is equivalent to [None, None].
        Defaults to None.
    backscatter_histogram_bin_edges_range : pair of float, optional
        The dB range for the backscatter histogram's bin edges. Endpoint will
        be included. Defaults to [-80.0, 20.0].
        Format: (<starting value>, <endpoint>)
    phs_in_radians : bool, optional
        True to compute phase in radians units, False for degrees units.
        Defaults to True.
        Note: If False, suggest adjusting `phase_histogram_y_axis_range`
        appropriately for degrees rather than radians.
    tile_shape : iterable of int, optional
        User-preferred tile shape for processing images by batches.
        Actual tile shape may be modified by QA to be an integer
        multiple of the number of looks for multilooking, of the
        decimation ratio, etc.
        Format: (num_rows, num_cols)
        -1 to indicate all rows / all columns (respectively).

    Attributes
    ----------
    backscatter_bin_edges : numpy.ndarray
        The bin edges (including endpoint) to use when computing
        the backscatter histograms. Will be set to 100 uniformly-spaced bins
        in range `backscatter_histogram_bin_edges_range`, including endpoint.
    phs_bin_edges : numpy.ndarray
        The bin edges (including endpoint) to use when computing
        the phase histograms.
        If `phs_in_radians` is True, this will be set to 100
        uniformly-spaced bins in range [-pi,pi], including endpoint.
        If `phs_in_radians` is False, this will be set to 100
        uniformly-spaced bins in range [-180,180], including endpoint.
    """

    phase_histogram_y_axis_range: None | Sequence[int | float | None] = (
        nisarqa.HistogramParamGroup.get_field_with_updated_default(
            param_name="phase_histogram_y_axis_range", default=None
        )
    )


@dataclass
class GCOVRootParamGroup(NonInsarRootParamGroup):
    """
    Dataclass of all *ParamGroup objects to process QA for NISAR GCOV products.

    `workflows` is the only required parameter; this *ParamGroup contains
    boolean attributes that indicate which QA workflows to run.

    All other parameters are optional, but they each correspond to (at least)
    one of the QA workflows. Based on the workflows set to True in
    `workflows`, certain others of these parameters will become required.

    Parameters
    ----------
    workflows : WorkflowsParamGroup
        QA Workflows parameters
    input_f : InputFileGroupParamGroup or None, optional
        Input File Group parameters for QA
    prodpath : ScratchProductPathGroupParamGroup or None, optional
        Product Path Group parameters for QA
    software_config : SoftwareConfigParamGroup or None, optional
        General QA Software Configuration Group parameters
    validation : ValidationGroupParamGroup or None, optional
        Validation Group parameters for QA
    backscatter_img : BackscatterImageParamGroup or None, optional
        Covariance Term Magnitude Image Group parameters for GCOV QA
    histogram : GCOVHistogramParamGroup or None, optional
        Histogram Group parameters for GCOV QA
    """

    # Overwrite parent's attributes b/c new type
    prodpath: Optional[ScratchProductPathGroupParamGroup] = None

    # QA parameters
    backscatter_img: Optional[BackscatterImageParamGroup] = None
    histogram: Optional[GCOVHistogramParamGroup] = None

    @staticmethod
    def get_mapping_of_workflows2param_grps(workflows):
        Grp = (
            NonInsarRootParamGroup.ReqParamGrp
        )  # class object for our named tuple

        flag_any_workflows_true = any(
            [getattr(workflows, field.name) for field in fields(workflows)]
        )

        grps_to_parse = (
            Grp(
                flag_param_grp_req=flag_any_workflows_true,
                root_param_grp_attr_name="input_f",
                param_grp_cls_obj=InputFileGroupParamGroup,
            ),
            Grp(
                flag_param_grp_req=flag_any_workflows_true,
                root_param_grp_attr_name="prodpath",
                param_grp_cls_obj=ScratchProductPathGroupParamGroup,
            ),
            Grp(
                flag_param_grp_req=flag_any_workflows_true,
                root_param_grp_attr_name="software_config",
                param_grp_cls_obj=SoftwareConfigGroupParamGroup,
            ),
            Grp(
                flag_param_grp_req=workflows.validate,
                root_param_grp_attr_name="validation",
                param_grp_cls_obj=ValidationGroupParamGroup,
            ),
            Grp(
                flag_param_grp_req=workflows.qa_reports,
                root_param_grp_attr_name="backscatter_img",
                param_grp_cls_obj=BackscatterImageParamGroup,
            ),
            Grp(
                flag_param_grp_req=workflows.qa_reports,
                root_param_grp_attr_name="histogram",
                param_grp_cls_obj=GCOVHistogramParamGroup,
            ),
        )

        return grps_to_parse

    @staticmethod
    def get_order_of_groups_in_yaml():
        # This order determines the order
        # the groups will appear in the runconfig.
        return {
            "input_f": InputFileGroupParamGroup,
            "prodpath": ScratchProductPathGroupParamGroup,
            "workflows": WorkflowsParamGroup,
            "software_config": SoftwareConfigGroupParamGroup,
            "validation": ValidationGroupParamGroup,
            "backscatter_img": BackscatterImageParamGroup,
            "histogram": GCOVHistogramParamGroup,
        }


__all__ = nisarqa.get_all(__name__, objects_to_skip)
