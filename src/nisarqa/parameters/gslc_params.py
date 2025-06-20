from dataclasses import dataclass, field, fields, replace
from typing import Optional

import nisarqa

from .caltools_params import PointTargetAnalyzerParamGroup
from .nisar_params import (
    InputFileGroupParamGroup,
    ProductPathGroupParamGroup,
    RootParamGroup,
    SoftwareConfigParamGroup,
    ValidationGroupParamGroup,
    YamlAttrs,
)
from .rslc_caltools_params import (
    BackscatterImageParamGroup,
    DynamicAncillaryFileParamGroup,
    HistogramParamGroup,
    SLCWorkflowsParamGroup,
)

objects_to_skip = nisarqa.get_all(__name__)


@dataclass(frozen=True)
class GSLCDynamicAncillaryFileParamGroup(DynamicAncillaryFileParamGroup):
    """
    The parameters from the QA Dynamic Ancillary File runconfig group.

    This corresponds to the `groups: dynamic_ancillary_file_group`
    runconfig group.

    Parameters
    ----------
    corner_reflector_file : str or None, optional
        The input corner reflector file's file name (with path).
        A valid corner reflector file is required for the Point Target Analyzer
        workflow to generate results. Defaults to None.
    dem_file : str or None, optional
        Optional Digital Elevation Model (DEM) file in a GDAL-compatible raster
        format. Used for flattening phase removal of the GSLC data for point
        target analysis (PTA), if applicable (i.e. if the PTA tool is enabled
        and the GSLC is flattened). If None (no DEM is supplied), the PTA
        tool will attempt to un-flatten using the reference ellipsoid, which may
        produce less accurate results. Defaults to None.
    """

    # Override the base class's attribute in order to update the runconfig
    # description.
    corner_reflector_file: str = field(
        default=None,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="corner_reflector_file",
                descr="""File containing the locations of the corner reflectors
                in the input product.
                Required for `point_target_analyzer` QA-CalTools workflow to
                generate results. If a file is not provided, or if the corner
                file has no useful data for the given input product, then no
                results will be generated.""",
            )
        },
    )

    dem_file: str = field(
        default=None,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="dem_file",
                descr="""Optional Digital Elevation Model (DEM) file in a
                GDAL-compatible raster format. Used for flattening phase removal
                of the GSLC data for point target analysis (PTA), if applicable
                (i.e. if `point_target_analyzer` is enabled and the GSLC is
                flattened). If None (no DEM is supplied), the PTA tool will
                attempt to un-flatten using the reference ellipsoid, which may
                produce less accurate results.""",
            )
        },
    )

    def __post_init__(self):
        super().__post_init__()

        if self.dem_file is not None:
            nisarqa.validate_is_file(
                filepath=self.dem_file,
                parameter_name="dem_file",
            )


@dataclass
class GSLCRootParamGroup(RootParamGroup):
    """
    Dataclass of all *ParamGroup objects to process QA for NISAR GSLC products.

    `workflows` is the only required parameter; this *ParamGroup contains
    boolean attributes that indicate which QA workflows to run.

    All other parameters are optional, but they each correspond to (at least)
    one of the QA workflows. Based on the workflows set to True in
    `workflows`, certain others of these parameters will become required.

    Parameters
    ----------
    workflows : SLCWorkflowsParamGroup
        GSLC QA Workflows parameters
    input_f : InputFileGroupParamGroup or None, optional
        Input File Group parameters for QA
    prodpath : ProductPathGroupParamGroup or None, optional
        Product Path Group parameters for QA
    software_config : SoftwareConfigParamGroup or None, optional
        General QA Software Configuration Group parameters
    validation : ValidationGroupParamGroup or None, optional
        Validation Group parameters for QA
    backscatter_img : BackscatterImageParamGroup or None, optional
        Backscatter Image Group parameters for SLC QA
    histogram : HistogramParamGroup or None, optional
        Histogram Group parameters for RSLC or GSLC QA
    anc_files : GSLCDynamicAncillaryFileParamGroup or None, optional
        Dynamic Ancillary File Group parameters for GSLC QA-Caltools
    pta : PointTargetAnalyzerParamGroup or None, optional
        Point Target Analyzer group parameters for GSLC QA-Caltools
    """

    # Overwrite parent's attributes b/c new type
    workflows: SLCWorkflowsParamGroup

    # QA parameters
    backscatter_img: Optional[BackscatterImageParamGroup] = None
    histogram: Optional[HistogramParamGroup] = None

    # CalTools parameters
    anc_files: Optional[GSLCDynamicAncillaryFileParamGroup] = None
    pta: Optional[PointTargetAnalyzerParamGroup] = None

    def __post_init__(self):
        # If the PTA tool was enabled but no corner reflector file was provided,
        # log an error and disable the PTA workflow. This behavior mimics that
        # of `RSLCRootParamGroup.__post_init__()`. See the comments in that
        # method for details.
        if self.workflows.point_target and (
            self.anc_files.corner_reflector_file is None
        ):
            # Log as an error because QA cannot perform a requested feature
            nisarqa.get_logger().error(
                "`corner_reflector_file` not provided in runconfig. The Point"
                " Target Analyzer Caltool workflow requires this file. Setting"
                " that workflow to False. Its runconfig params will be ignored."
            )

            # Disable the PTA workflow.
            self.workflows = replace(self.workflows, point_target=False)
            self.pta = None

            # If no other dynamic ancillary files were provided, set the whole
            # group to None.
            # XXX: This has the undesirable effect of populating the contents of
            # `self.anc_files` in the `runConfigurationContents` dataset of the
            # ouptut STATS.h5 file if a DEM file was provided even if no corner
            # reflector CSV file was provided. But it's tricky to avoid this
            # without making assumptions about the contents of the dynamic
            # ancillary files group that may be violated in the future;
            # for example, if a new feature also needs to use the DEM,
            # it'd be bad to quietly set the DEM file to `None` here.
            for f in fields(self.anc_files):
                val = getattr(self.anc_files, f.name)
                if val is not None:
                    break
            else:
                self.anc_files = None

    @staticmethod
    def get_mapping_of_workflows2param_grps(workflows):
        Grp = RootParamGroup.ReqParamGrp  # class object for our named tuple

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
                param_grp_cls_obj=ProductPathGroupParamGroup,
            ),
            Grp(
                flag_param_grp_req=flag_any_workflows_true,
                root_param_grp_attr_name="software_config",
                param_grp_cls_obj=SoftwareConfigParamGroup,
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
                param_grp_cls_obj=nisarqa.HistogramParamGroup,
            ),
            Grp(
                flag_param_grp_req=workflows.point_target,
                root_param_grp_attr_name="anc_files",
                param_grp_cls_obj=GSLCDynamicAncillaryFileParamGroup,
            ),
            Grp(
                flag_param_grp_req=workflows.point_target,
                root_param_grp_attr_name="pta",
                param_grp_cls_obj=PointTargetAnalyzerParamGroup,
            ),
        )

        return grps_to_parse

    @staticmethod
    def get_order_of_groups_in_yaml():
        # This order determines the order
        # the groups will appear in the runconfig.
        return {
            "input_f": InputFileGroupParamGroup,
            "anc_files": GSLCDynamicAncillaryFileParamGroup,
            "prodpath": ProductPathGroupParamGroup,
            "workflows": SLCWorkflowsParamGroup,
            "software_config": SoftwareConfigParamGroup,
            "validation": ValidationGroupParamGroup,
            "backscatter_img": BackscatterImageParamGroup,
            "histogram": HistogramParamGroup,
            "pta": PointTargetAnalyzerParamGroup,
        }


__all__ = nisarqa.get_all(__name__, objects_to_skip)
