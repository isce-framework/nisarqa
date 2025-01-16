from __future__ import annotations

import numbers
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field, fields, replace
from typing import ClassVar, Optional, Type, Union

import numpy as np
from matplotlib.colors import to_rgba
from numpy.typing import ArrayLike

import nisarqa
from nisarqa import (
    AbsCalParamGroup,
    HDF5Attrs,
    HDF5ParamGroup,
    InputFileGroupParamGroup,
    ProductPathGroupParamGroup,
    RootParamGroup,
    RSLCPointTargetAnalyzerParamGroup,
    ValidationGroupParamGroup,
    WorkflowsParamGroup,
    YamlAttrs,
    YamlParamGroup,
)

objects_to_skip = nisarqa.get_all(__name__)


@dataclass(frozen=True)
class SLCWorkflowsParamGroup(WorkflowsParamGroup):
    """
    The parameters specifying which SLC-Caltools QA workflows should be run.

    This corresponds to the `qa: workflows` runconfig group.

    Parameters
    ----------
    validate : bool, optional
        True to run the validate workflow. Default: True
        (inherited from WorkflowsParamGroup class)
    qa_reports : bool, optional
        True to run the QA Reports workflow. Default: True
        (inherited from WorkflowsParamGroup class)
    point_target : bool, optional
        True to run the Point Target Analyzer (PTA) workflow. Default: True
    """

    point_target: bool = field(
        default=WorkflowsParamGroup._default_val,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="point_target_analyzer",
                descr=WorkflowsParamGroup._descr
                % "Point Target Analyzer calibration tool",
            )
        },
    )

    def __post_init__(self):
        super().__post_init__()
        self._check_workflows_arg("point_target", self.point_target)


@dataclass(frozen=True)
class RSLCWorkflowsParamGroup(SLCWorkflowsParamGroup):
    """
    The parameters specifying which RSLC-Caltools QA workflows should be run.

    This corresponds to the `qa: workflows` runconfig group.

    Parameters
    ----------
    validate : bool, optional
        True to run the validate workflow. Default: True
        (inherited from WorkflowsParamGroup class)
    qa_reports : bool, optional
        True to run the QA Reports workflow. Default: True
        (inherited from WorkflowsParamGroup class)
    point_target : bool, optional
        True to run the Point Target Analyzer (PTA) workflow. Default: True
    abs_cal : bool, optional
        True to run the Absolute Radiometric Calibration Factor CalTool workflow
        Default: True
    neb : bool, optional
        True to run the Noise Equivalent Backscatter Tool (NEB) workflow.
        Default: True.
    """

    abs_cal: bool = field(
        default=WorkflowsParamGroup._default_val,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="absolute_radiometric_calibration",
                descr=WorkflowsParamGroup._descr
                % "Absolute Radiometric Calibration calibration tool",
            )
        },
    )

    neb: bool = field(
        default=WorkflowsParamGroup._default_val,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="noise_equivalent_backscatter",
                descr=WorkflowsParamGroup._descr
                % "Noise Equivalent Backscatter calibration tool",
            )
        },
    )

    def __post_init__(self):
        # VALIDATE INPUTS
        super().__post_init__()
        self._check_workflows_arg("abs_cal", self.abs_cal)
        self._check_workflows_arg("neb", self.neb)


@dataclass(frozen=True)
class DynamicAncillaryFileParamGroup(YamlParamGroup):
    """
    The parameters from the QA Dynamic Ancillary File runconfig group.

    This corresponds to the `groups: dynamic_ancillary_file_group`
    runconfig group.

    Parameters
    ----------
    corner_reflector_file : str or None, optional
        The input corner reflector file's file name (with path).
        A valid corner reflector file is required for the Absolute Calibration
        Factor and Point Target Analyzer workflows to generate results.
        Defaults to None.
    """

    # WARNING: Before adding an additional parameter to this dataclass,
    # please review the comments in `RSLCRootParamGroup.__post_init__()`
    # and update the code accordingly.

    corner_reflector_file: str = field(
        default=None,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="corner_reflector_file",
                descr="""File containing the locations of the corner reflectors
            in the input product.
            Required for `absolute_radiometric_calibration` and/or
            `point_target_analyzer` QA-CalTools workflows to generate results.
            If a file is not provided, or if the corner file has no useful data
            for the given input product, then no results will be generated. """,
            )
        },
    )

    def __post_init__(self):
        if self.corner_reflector_file is not None:
            nisarqa.validate_is_file(
                filepath=self.corner_reflector_file,
                parameter_name="corner_reflector_file",
                extension=".csv",
            )

    @staticmethod
    def get_path_to_group_in_runconfig():
        return ["runconfig", "groups", "dynamic_ancillary_file_group"]


# TODO - move to generic SLC module
@dataclass(frozen=True)
class BackscatterImageParamGroup(YamlParamGroup, HDF5ParamGroup):
    """
    Parameters to generate RSLC or GSLC Backscatter Images and Browse Image.

    This corresponds to the `qa_reports: backscatter_img` runconfig group.

    Parameters
    ----------
    linear_units : bool, optional
        True to compute backscatter image in linear units; False for decibel units.
        Defaults to True.
    nlooks_freqa, nlooks_freqb : iterable of int, None, optional
        Number of looks along each axis of the input array
        for the specified frequency. If None, then nlooks will be computed
        internally based on `longest_side_max`.
    longest_side_max : int, optional
        The maximum number of pixels allowed for the longest side of the final
        2D multilooked browse image.
        Superseded by nlooks_freq* parameters. Defaults to 2048 pixels.
    percentile_for_clipping : pair of float, optional
        Defines the percentile range that the image array will be clipped to
        and that the colormap covers. Must be in the range [0.0, 100.0].
        Defaults to [5.0, 95.0].
    gamma : float, None, optional
        The gamma correction parameter.
        Gamma will be applied as follows:
            array_out = normalized_array ^ gamma
        where normalized_array is a copy of the image with values
        scaled to the range [0,1].
        The image colorbar will be defined with respect to the input
        image values prior to normalization and gamma correction.
        If None, then no normalization, no gamma correction will be applied.
        Default: 0.5
    nan_color : str or Sequence of float or None, optional
        Color to plot NaN pixels for the PDF report.
        For transparent, set to None.
        The color should given in a format recognized by matplotlib:
        https://matplotlib.org/stable/users/explain/colors/colors.html
        (Note: Browse image PNG will always plot NaN as transparent.)
        Defaults to "blue".
    tile_shape : iterable of int, optional
        User-preferred tile shape for processing images by batches.
        Actual tile shape may be modified by QA to be an integer
        multiple of the number of looks for multilooking, of the
        decimation ratio, etc.
        Format: (num_rows, num_cols)
        -1 to indicate all rows / all columns (respectively).
        Defaults to (1024, 1024).

    Attributes
    ----------
    backscatter_units : Param
        Units of the backscatter image.
        If `linear_units` is True, this will be set to 'linear'.
        If `linear_units` is False, this will be set to 'dB'.
    """

    linear_units: bool = field(
        default=True,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="linear_units",
                descr="""True to compute backscatter in linear units when generating
                the backscatter image for the browse images and graphical
                summary PDF. False for decibel units.""",
            )
        },
    )

    _nlooks_descr_template: ClassVar[
        str
    ] = """Number of looks along each axis of the Frequency %s
        image arrays for multilooking the backscatter image.
        Format: [<num_rows>, <num_cols>]
        Example: [6,7]
        If not provided, the QA code to compute the nlooks values
        based on `longest_side_max`."""

    nlooks_freqa: Optional[Iterable[int]] = field(
        default=None,
        metadata={
            "yaml_attrs": YamlAttrs(
                name=f"nlooks_freqa", descr=_nlooks_descr_template % "A"
            )
        },
    )

    nlooks_freqb: Optional[Iterable[int]] = field(
        default=None,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="nlooks_freqb", descr=_nlooks_descr_template % "B"
            )
        },
    )

    longest_side_max: int = field(
        default=2048,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="longest_side_max",
                descr="""The maximum number of pixels allowed for the longest side
                of the final 2D multilooked browse image. Defaults to 2048.
                If `nlooks_freq*` parameter(s) is not None, nlooks
                values will take precedence.""",
            )
        },
    )

    percentile_for_clipping: tuple[float, float] = field(
        default=(5.0, 95.0),
        metadata={
            "yaml_attrs": YamlAttrs(
                name="percentile_for_clipping",
                descr="""Percentile range that the image array will be clipped to
                    and that the colormap covers. Must be in range [0.0, 100.0].""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="backscatterImagePercentileClipped",
                units="1",
                descr=(
                    "Percentile range that the image array was clipped to"
                    " and that the colormap covers"
                ),
                group_path=nisarqa.STATS_H5_QA_PROCESSING_GROUP,
            ),
        },
    )

    gamma: Optional[float] = field(
        default=0.5,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="gamma",
                descr="""Gamma correction parameter applied to backscatter and browse image(s).
            Gamma will be applied as follows:
                array_out = normalized_array ^ gamma
            where normalized_array is a copy of the image with values
            scaled to the range [0,1].
            The image colorbar will be defined with respect to the input
            image values prior to normalization and gamma correction.
            If None, then no normalization and no gamma correction will be applied.""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="backscatterImageGammaCorrection",
                units="1",
                descr=(
                    "Gamma correction parameter applied to backscatter and"
                    " browse image(s). Dataset will be type float if gamma was"
                    " applied, otherwise it is the string 'None'"
                ),
                group_path=nisarqa.STATS_H5_QA_PROCESSING_GROUP,
            ),
        },
    )

    nan_color: str | Sequence[float] | None = field(
        default="blue",
        metadata={
            "yaml_attrs": YamlAttrs(
                name="nan_color_in_pdf",
                descr="""Color to plot NaN pixels for the PDF report.
                For transparent, set to None.
                The color should given in a format recognized by matplotlib:
                https://matplotlib.org/stable/users/explain/colors/colors.html
                (Note: Browse image PNG will always plot NaN as transparent.)""",
            )
        },
    )

    tile_shape: Iterable[int] = field(
        default=(1024, 1024),
        metadata={
            "yaml_attrs": YamlAttrs(
                name="tile_shape",
                descr="""User-preferred tile shape for processing images by batches.
                Actual tile shape may be modified by QA to be an integer
                multiple of the number of looks for multilooking, of the
                decimation ratio, etc.
                Format: [<num_rows>, <num_cols>]
                -1 to indicate all rows / all columns (respectively).""",
            )
        },
    )

    # Auto-generated attributes, so set init=False and have no default.
    # `backscatter_units` is determined by the `linear_units` attribute.
    backscatter_units: str = field(
        init=False,
        metadata={
            "hdf5_attrs": HDF5Attrs(
                name="backscatterImageUnits",
                units=None,
                descr="""Units of the backscatter image.""",
                group_path=nisarqa.STATS_H5_QA_PROCESSING_GROUP,
            )
        },
    )

    def __post_init__(self):
        # VALIDATE INPUTS

        # validate linear_units
        if not isinstance(self.linear_units, bool):
            raise TypeError(f"`linear_units` must be bool: {self.linear_units}")

        # validate nlooks_freq*
        self._validate_nlooks(self.nlooks_freqa, "A")
        self._validate_nlooks(self.nlooks_freqa, "B")

        # validate longest_side_max
        if not isinstance(self.longest_side_max, int):
            raise TypeError(
                f"longest_side_max must be a int: {self.longest_side_max}"
            )
        if self.longest_side_max <= 0:
            raise ValueError(
                f"`longest_side_max` must be positive: {self.longest_side_max}"
            )

        # validate percentile_for_clipping
        val = self.percentile_for_clipping
        if not isinstance(val, (list, tuple)):
            raise TypeError(
                f"{self.percentile_for_clipping=}, must be a list or tuple."
            )
        if not len(val) == 2:
            raise ValueError(
                f"{self.percentile_for_clipping=} must have a length of two."
            )
        if not all(isinstance(e, float) for e in val):
            raise TypeError(
                f"{self.percentile_for_clipping=} must contain only float."
            )
        if any((e < 0.0 or e > 100.0) for e in val):
            raise ValueError(
                f"{self.percentile_for_clipping=}, must be in range [0.0,"
                " 100.0]"
            )
        if self.percentile_for_clipping[0] >= self.percentile_for_clipping[1]:
            raise ValueError(
                f"{self.percentile_for_clipping=}; values must appear in"
                " increasing order."
            )

        # validate gamma
        if isinstance(self.gamma, float):
            if self.gamma < 0.0:
                raise ValueError(
                    "If `gamma` is a float, it must be non-negative:"
                    f" {self.gamma}"
                )
        elif self.gamma is not None:
            raise TypeError(
                "`gamma` must be a float or None. "
                f"Value: {self.gamma}, Type: {type(self.gamma)}"
            )

        # validate nan_color
        if self.nan_color is not None:
            try:
                to_rgba(c=self.nan_color)
            except ValueError as e:
                raise ValueError(
                    f"`nan_color_in_pdf` is `{self.nan_color}`, which is not"
                    " recognizable by Matplotlib. For acceptable options, see:"
                    " https://matplotlib.org/stable/users/explain/colors/colors.html"
                ) from e

        # validate tile_shape
        val = self.tile_shape
        if not isinstance(val, (list, tuple)):
            raise TypeError(f"`tile_shape` must be a list or tuple: {val}")
        if not len(val) == 2:
            raise TypeError(f"`tile_shape` must have a length of two: {val}")
        if not all(isinstance(e, int) for e in val):
            raise TypeError(f"`tile_shape` must contain only integers: {val}")
        if any(e < -1 for e in val):
            raise TypeError(f"Values in `tile_shape` must be >= -1: {val}")

        # SET ATTRIBUTES DEPENDENT UPON INPUT PARAMETERS
        # This dataclass is frozen to ensure that all inputs are validated,
        # so we need to use object.__setattr__()

        # use linear_units to set backscatter_units
        object.__setattr__(
            self, "backscatter_units", "linear" if self.linear_units else "dB"
        )

    @staticmethod
    def get_path_to_group_in_runconfig():
        return ["runconfig", "groups", "qa", "qa_reports", "backscatter_img"]

    @staticmethod
    def _validate_nlooks(nlooks, freq):
        """
        Raise exception if `nlooks` is not a valid input.

        Parameters
        ----------
        nlooks : iterable of int or None
            Number of looks along each axis of the input array
            for the specified frequency.
        freq : str
            The frequency to assign this number of looks to.
            Options: 'A' or 'B'
        """
        if isinstance(nlooks, (list, tuple)):
            if all(isinstance(e, int) for e in nlooks):
                if any((e < 1) for e in nlooks) or not len(nlooks) == 2:
                    raise TypeError(
                        f"nlooks_freq{freq.lower()} must be an int or a "
                        f"sequence of two ints, which are >= 1: {nlooks}"
                    )
        elif nlooks is None:
            # the code will use `longest_side_max` to compute `nlooks` instead.
            pass
        else:
            raise TypeError(
                f"`nlooks` must be of type iterable of int, or None: {nlooks}"
            )


@dataclass(frozen=True)
class HistogramParamGroup(YamlParamGroup, HDF5ParamGroup):
    """
    Parameters to generate RSLC, GSLC, GCOV Backscatter and Phase Histograms.

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
        Defaults to [0.0, 0.5].
    backscatter_histogram_bin_edges_range : pair of float, optional
        The dB range for the backscatter histogram's bin edges. Endpoint will
        be included. Defaults to [-80.0, 20.0].
        Format: (<starting value>, <endpoint>)
    phs_in_radians : bool, optional
        True to compute phase in radians units; False for degrees units.
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

    decimation_ratio: Iterable[int] = field(
        default=(8, 8),
        metadata={
            "yaml_attrs": YamlAttrs(
                name="decimation_ratio",
                descr="""Step size to decimate the input array for computing
                the backscatter and phase histograms.
                For example, [2,3] means every 2nd azimuth line and
                every 3rd range sample will be used to compute the histograms.
                Format: [<azimuth>, <range>]""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="histogramDecimationRatio",
                units="1",
                descr=(
                    "Image decimation strides used to compute backscatter"
                    " and phase histograms. Format: [<azimuth>, <range>]"
                ),
                group_path=nisarqa.STATS_H5_QA_PROCESSING_GROUP,
            ),
        },
    )

    backscatter_histogram_bin_edges_range: Iterable[Union[int, float]] = field(
        default=(-80.0, 20.0),
        metadata={
            "yaml_attrs": YamlAttrs(
                name="backscatter_histogram_bin_edges_range",
                descr="""Range in dB for the backscatter histogram's bin edges. Endpoint will
                be included. Format: [<starting value>, <endpoint>]""",
            )
        },
    )

    phase_histogram_y_axis_range: None | Sequence[int | float | None] = field(
        default=(0.0, 0.5),
        metadata={
            "yaml_attrs": YamlAttrs(
                name="phase_histogram_y_axis_range",
                descr="""The range for the phase histograms' y-axis.
            Format: [<min of range>, <max of range>]
            Examples: None, [0.0, None], [None, 0.7], [-0.2, 1.2], [None, None]
        If the min or max is set to None, then that limit is set dynamically
        based on the range of phase histogram density values.
        If None, this is equivalent to [None, None].""",
            ),
        },
    )

    phs_in_radians: bool = field(
        default=True,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="phs_in_radians",
                descr="""True to compute phase histogram in radians units,
                False for degrees units.
                Note: If False, suggest adjusting `phase_histogram_y_axis_range`
                appropriately for degrees rather than radians.""",
            )
        },
    )

    tile_shape: Iterable[int] = field(
        default=(1024, -1),
        metadata={
            "yaml_attrs": YamlAttrs(
                name="tile_shape",
                descr="""User-preferred tile shape for processing images by batches.
                Actual tile shape may be modified by QA to be an integer
                multiple of the number of looks for multilooking, of the
                decimation ratio, etc.
                Format: [<num_rows>, <num_cols>]
                -1 to indicate all rows / all columns (respectively).""",
            )
        },
    )

    # Auto-generated attributes
    # Backscatter Bin Edges (generated from `backscatter_histogram_bin_edges_range`)
    backscatter_bin_edges: ArrayLike = field(
        init=False,
        metadata={
            "hdf5_attrs": HDF5Attrs(
                name="histogramEdgesBackscatter",
                units="dB",
                descr=(
                    "Bin edges (including endpoint) for backscatter histogram"
                ),
                group_path=nisarqa.STATS_H5_QA_PROCESSING_GROUP,
            )
        },
    )

    # Phase bin edges (generated from `phs_in_radians`)
    # Note: `phs_bin_edges` is dependent upon `phs_in_radians` being set
    # first. The value of `phs_bin_edges` can be set in __post_init__,
    # but the contents of the field metadata cannot be modified
    # after initialization. It raises this error:
    #     TypeError: 'mappingproxy' object does not support item assignment
    # So, use a lambda function; this can be called to generate the correct
    # HDF5Attrs when needed, and it does not clutter the dataclass much.
    # Usage: `obj` is an instance of HistogramParamGroup()
    phs_bin_edges: ArrayLike = field(
        init=False,
        metadata={
            "hdf5_attrs_func": lambda obj: (
                HDF5Attrs(
                    name="histogramEdgesPhase",
                    units="radians" if obj.phs_in_radians else "degrees",
                    descr="Bin edges (including endpoint) for phase histogram",
                    group_path=nisarqa.STATS_H5_QA_PROCESSING_GROUP,
                )
                if (isinstance(obj, HistogramParamGroup))
                else nisarqa.raise_(
                    TypeError(
                        f"`obj` is {type(obj)}, but must be type"
                        " HistogramParamGroup"
                    )
                )
            )
        },
    )

    def __post_init__(self):
        # VALIDATE INPUTS

        # validate decimation_ratio
        val = self.decimation_ratio
        if not isinstance(val, (list, tuple)):
            raise TypeError(f"`decimation_ratio` must be list or tuple: {val}")
        if not len(val) == 2:
            raise ValueError(f"`decimation_ratio` must have length of 2: {val}")
        if not all(isinstance(e, int) for e in val):
            raise TypeError(f"`decimation_ratio` must contain integers: {val}")
        if any(e <= 0 for e in val):
            raise ValueError(
                f"`decimation_ratio` must contain positive values: {val}"
            )

        # Validate backscatter_histogram_bin_edges_range
        self._validate_pair_of_numeric(
            param_value=self.backscatter_histogram_bin_edges_range,
            param_name="backscatter_histogram_bin_edges_range",
            min=None,
            max=None,
            none_is_valid_value=False,
            strictly_increasing=True,
        )

        # Validate phase_histogram_y_axis_range
        val = self.phase_histogram_y_axis_range
        if val is None:
            pass
        elif all(x is not None for x in val):
            # phase histogram y axis range is a pair of numeric
            self._validate_pair_of_numeric(
                param_value=val,
                param_name="phase_histogram_y_axis_range",
                min=None,
                max=None,
                none_is_valid_value=False,
                strictly_increasing=True,
            )
        else:
            # Check that format is like: [None, <number>], [<number>, None],
            # or [None, None]
            if len(val) != 2:
                raise ValueError(
                    f"`phase_histogram_y_axis_range` must be length two: {val}"
                )
            for x in val:
                if (x is not None) and (not isinstance(x, numbers.Real)):
                    raise TypeError(
                        f"`phase_histogram_y_axis_range` must contain"
                        f" only numbers or None: {val}"
                    )

        # validate phs_in_radians
        if not isinstance(self.phs_in_radians, bool):
            raise TypeError(f"phs_in_radians` must be bool: {val}")

        # validate tile_shape
        val = self.tile_shape
        if not isinstance(val, (list, tuple)):
            raise TypeError(f"`tile_shape` must be a list or tuple: {val}")
        if not len(val) == 2:
            raise TypeError(f"`tile_shape` must have a length of two: {val}")
        if not all(isinstance(e, int) for e in val):
            raise TypeError(f"`tile_shape` must contain only integers: {val}")
        if any(e < -1 for e in val):
            raise TypeError(f"Values in `tile_shape` must be >= -1: {val}")

        # SET ATTRIBUTES DEPENDENT UPON INPUT PARAMETERS
        # This dataclass is frozen to ensure that all inputs are validated,
        # so we need to use object.__setattr__()

        # Set attributes dependent upon backscatter_histogram_bin_edges_range
        # Backscatter Bin Edges - hardcode to be in decibels
        # 201 bin edges => 200 bins
        object.__setattr__(
            self,
            "backscatter_bin_edges",
            np.linspace(
                self.backscatter_histogram_bin_edges_range[0],
                self.backscatter_histogram_bin_edges_range[1],
                num=201,
                endpoint=True,
            ),
        )

        # Set attributes dependent upon phs_in_radians
        start, stop = (-np.pi, np.pi) if self.phs_in_radians else (-180, 180)
        object.__setattr__(
            self,
            "phs_bin_edges",
            np.linspace(start=start, stop=stop, num=201, endpoint=True),
        )

    @staticmethod
    def get_path_to_group_in_runconfig():
        return ["runconfig", "groups", "qa", "qa_reports", "histogram"]


@dataclass(frozen=True)
class RangeSpectraParamGroup(YamlParamGroup, HDF5ParamGroup):
    """
    Parameters to generate the RSLC Range Spectra plots;
    this corresponds to the `qa_reports: range_spectra` runconfig group.

    Parameters
    ----------
    az_decimation : int, optional
        The stride to decimate the input array along the azimuth axis.
        For example, `4` means every 4th range line will
        be used to compute the range spectra.
        If `1`, no decimation will occur (but is slow to compute).
        Must be greater than zero. Defaults to 8.
    hz_to_mhz : bool, optional
        True if the input frequencies are in Hz, but user wants outputs in MHz.
        Defaults to True.
    tile_height : int, optional
        User-preferred tile height (number of range lines) for processing
        images by batches. Actual tile shape may be modified by QA to be
        an integer multiple of `az_decimation` . -1 to use all rows.
        Note: full rows must be read in, so the number of columns for each tile
        will be fixed to the number of columns in the input raster.
        Defaults to 512.
    """

    az_decimation: int = field(
        default=8,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="az_decimation",
                descr="""The stride to decimate the input array along the azimuth axis.
                    For example, `4` means every 4th range line will
                    be used to compute the range spectra. Must be greater than zero.
                    If `1`, no decimation will occur (but is slower to compute).""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="rangeSpectraDecimationAlongAzimuth",
                units="1",
                descr=(
                    "Decimation stride along the azimuth axis used to"
                    " compute the range spectra."
                ),
                group_path=nisarqa.STATS_H5_QA_PROCESSING_GROUP,
            ),
        },
    )

    hz_to_mhz: bool = field(
        default=True,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="hz_to_mhz",
                descr="""True if the input frequencies are in Hz,
                but output should be converted to MHz.""",
            )
        },
    )

    tile_height: int = field(
        default=512,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="tile_height",
                descr="""User-preferred tile height (number of range lines) for processing
        images by batches. Actual tile shape may be modified by QA to be
        an integer multiple of `az_decimation`. -1 to use all rows.
        Note: full rows must be read in, so the number of columns for each tile
        will be fixed to the number of columns in the input raster.""",
            )
        },
    )

    def __post_init__(self):
        # VALIDATE INPUTS

        # validate az_decimation
        if not isinstance(self.az_decimation, int):
            raise TypeError(
                f"`{self.az_decimation=}` and has type"
                f" {type(self.az_decimation)}, but must be an int."
            )
        if self.az_decimation <= 0:
            raise ValueError(
                f"`{self.az_decimation=}`, must be a positive value."
            )

        # validate hz_to_mhz
        if not isinstance(self.hz_to_mhz, bool):
            raise TypeError(f"hz_to_mhz` must be bool: {type(self.hz_to_mhz)}")

        # validate tile_height
        if not isinstance(self.tile_height, int):
            raise TypeError(
                f"`{self.tile_height=}` and has type"
                f" {type(self.tile_height)}, but must be an int."
            )
        if (self.tile_height < -1) or (self.tile_height == 0):
            raise ValueError(
                f"`{self.tile_height=}`, must be a positive value or -1."
            )

    @staticmethod
    def get_path_to_group_in_runconfig():
        return ["runconfig", "groups", "qa", "qa_reports", "range_spectra"]


@dataclass(frozen=True)
class AzimuthSpectraParamGroup(YamlParamGroup, HDF5ParamGroup):
    """
    Parameters to generate the RSLC Azimuth Spectra plots.

    Parameters
    ----------
    num_columns : int, optional
        Azimuth spectra will be computed by averaging `num_columns` contiguous
        range samples for each of near-, mid-, and far-range subswaths.
        If `num_columns` is -1 or greater than the total number of range
        samples, it will be set to the number of range samples.
        Must be equal to -1 or greater than zero. Defaults to 1024.
    hz_to_mhz : bool, optional
        True if the input frequencies are in Hz, but user wants outputs in MHz.
        Defaults to False.
    tile_width : int, optional
        Tile width (number of range samples) for processing
        each subswath by batches. -1 to set this to `num_columns`.
        Note: full columns must be read in, so the number of rows for each tile
        will be fixed to the height of the input raster.
        Defaults to 256.
    """

    num_columns: int = field(
        default=1024,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="num_columns",
                descr="""Azimuth spectra will be computed by averaging `num_columns` contiguous
        range samples for each of near-, mid-, and far-range subswaths.
        If `num_columns` is -1 or greater than the number of range samples,
        it will be set to the number of range samples.""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="azimuthSpectraColumnsPerSubswath",
                units="1",
                descr=(
                    "Number of columns (i.e. range samples) used to"
                    " compute the azimuth spectra for each subswath"
                    " (near-range, mid-range, and far-range)."
                ),
                group_path=nisarqa.STATS_H5_QA_PROCESSING_GROUP,
            ),
        },
    )

    hz_to_mhz: bool = field(
        default=False,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="hz_to_mhz",
                descr="""True if the input frequencies are in Hz,
                but output should be converted to MHz.""",
            )
        },
    )

    tile_width: int = field(
        default=256,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="tile_width",
                descr="""Tile width (number of columns) for processing
        each subswath by batches. -1 to set this to `num_columns`.
        Note: full columns must be read in, so the number of rows for each tile
        will be fixed to the height of the input raster.""",
            )
        },
    )

    def __post_init__(self):
        # VALIDATE INPUTS

        # validate num_columns
        if not isinstance(self.num_columns, int):
            raise TypeError(
                f"`{self.num_columns=}` and has type"
                f" {type(self.num_columns)}, but must be an int."
            )
        if (self.num_columns != -1) and (self.num_columns <= 0):
            raise ValueError(
                f"`{self.num_columns=}`, must be a positive value or -1."
            )

        # validate hz_to_mhz
        if not isinstance(self.hz_to_mhz, bool):
            raise TypeError(f"hz_to_mhz` must be bool: {type(self.hz_to_mhz)}")

        # validate tile_width
        if not isinstance(self.tile_width, int):
            raise TypeError(
                f"`{self.tile_width=}` and has type"
                f" {type(self.tile_width)}, but must be an int."
            )
        if (self.tile_width < -1) or (self.tile_width == 0):
            raise ValueError(
                f"`{self.tile_width=}`, must be a positive value or -1."
            )

    @staticmethod
    def get_path_to_group_in_runconfig():
        return ["runconfig", "groups", "qa", "qa_reports", "azimuth_spectra"]


@dataclass
class RSLCRootParamGroup(RootParamGroup):
    """
    Dataclass of all *ParamGroup objects to process QA for NISAR RSLC products.

    `workflows` is the only required parameter; this *ParamGroup contains
    boolean attributes that indicate which QA workflows to run.

    All other parameters are optional, but they each correspond to (at least)
    one of the QA workflows. Based on the workflows set to True in
    `workflows`, certain others of these parameters will become required.

    Parameters
    ----------
    workflows : RSLCWorkflowsParamGroup
        RSLC QA Workflows parameters
    input_f : InputFileGroupParamGroup or None, optional
        Input File Group parameters for RSLC QA
    prodpath : ProductPathGroupParamGroup or None, optional
        Product Path Group parameters for RSLC QA
    validation : ValidationGroupParamGroup or None, optional
        Validation Group parameters for QA
    backscatter_img : BackscatterImageParamGroup or None, optional
        Backscatter Image Group parameters for RSLC QA
    histogram : HistogramParamGroup or None, optional
        Histogram Group parameters for RSLC or GSLC QA
    range_spectra : RangeSpectraParamGroup or None, optional
        Range Spectra Group parameters for RSLC QA
    az_spectra : AzimuthSpectraParamGroup or None, optional
        Azimuth Spectra Group parameters for RSLC QA
    anc_files : DynamicAncillaryFileParamGroup or None, optional
        Dynamic Ancillary File Group parameters for RSLC QA-Caltools
    abs_cal : AbsCalParamGroup or None, optional
        Absolute Radiometric Calibration group parameters for RSLC QA-Caltools
    pta : RSLCPointTargetAnalyzerParamGroup or None, optional
        Point Target Analyzer group parameters for RSLC QA-Caltools
    """

    # Shared parameters
    workflows: (
        RSLCWorkflowsParamGroup  # overwrite parent's `workflows` b/c new type
    )

    # QA parameters
    backscatter_img: Optional[BackscatterImageParamGroup] = None
    histogram: Optional[HistogramParamGroup] = None
    range_spectra: Optional[RangeSpectraParamGroup] = None
    az_spectra: Optional[AzimuthSpectraParamGroup] = None

    # CalTools parameters
    anc_files: Optional[DynamicAncillaryFileParamGroup] = None
    abs_cal: Optional[AbsCalParamGroup] = None
    pta: Optional[RSLCPointTargetAnalyzerParamGroup] = None

    def __post_init__(self):
        # Per request from project, the desired behavior for QA is to have
        # all workflows default to True, and to have the default
        # runconfig successfully complete QA (meaning: not raise an error)
        # with only the input file be provided.

        # However, without the corner reflector file, neither the Abs Cal
        # tool nor the point target analyzer are able to run. So, the corner
        # reflector file should be optional.
        # In the scenario where AbsCal or PTA are requested via their
        # `workflows` flag, but the corner file is not provided, then we need
        # to warn the user about this issue and have QA handle accordingly.

        # To help QA behave "as the User expects", let's update the `workflows`
        # so that these two workflows are `False`. Doing this step during
        # __post_init__ means that the corresponding runconfig groups will
        # never be parsed during the call to `from_runconfig_dict()`,
        # and (more importantly) that QA-generated stats.h5 file will never
        # have groups (directories) created and populated for these two tools
        # during the call to `root_params.save_processing_params_to_stats_h5()`
        # and `root_params.log_parameters()`. Otherwise, we
        # would need to do cleanup later and remove these two groups from
        # STATS.h5.

        log = nisarqa.get_logger()

        if self.workflows.abs_cal or self.workflows.point_target:
            if self.anc_files.corner_reflector_file is None:
                # Log as an error because QA cannot perform a requested feature
                log.error(
                    "`corner_reflector_file` not provided in runconfig."
                    " Absolute Calibration Factor and Point Target Analyzer"
                    " Caltools workflows require this file. Setting those"
                    " two workflows to False. Their runconfig params will"
                    " be ignored."
                )

                # Set these `workflows` to False
                self.workflows = replace(
                    self.workflows, abs_cal=False, point_target=False
                )

                # Per the convention noted in
                # RootParamGroup.save_processing_params_to_stats_h5():
                #       If a workflow was not requested, its RootParams
                #       attribute will be None, so there will be no params to
                #       add to the h5 file."
                # In nominal cases, these groups are set to None during
                # `from_runconfig_dict()`. But, that step occurs prior to
                # checking whether a corner reflector file was provided,
                # so we need to manually update the
                # corresponding param groups to False.
                self.abs_cal = None
                self.pta = None

                # Similarly, if we leave the `anc_file` group instantiated
                # and with its only attribute set to None, this leads to code
                # hygiene issues due to not following QA convention.
                # For example, during `save_processing_params_to_stats_h5()`,
                # when 'runConfigurationContents' is saved to the STATS file,
                # it would include the `anc_file` group but have a null
                # corner reflector file.

                # To solve this, we could simply set `self.anc_files = None`.
                # However, if another file (such as a DEM) is later added
                # to `anc_files`, then we want a more forward-looking behavior.

                # For now, assume that any parameter added to
                # DynamicAncillaryFileParamGroup will either be required
                # (and likely contain a string filepath), or will default to
                # None.
                # Note: if/when that assumption becomes invalid, please update
                # this check.
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
                param_grp_cls_obj=HistogramParamGroup,
            ),
            Grp(
                flag_param_grp_req=workflows.qa_reports,
                root_param_grp_attr_name="range_spectra",
                param_grp_cls_obj=RangeSpectraParamGroup,
            ),
            Grp(
                flag_param_grp_req=workflows.qa_reports,
                root_param_grp_attr_name="az_spectra",
                param_grp_cls_obj=AzimuthSpectraParamGroup,
            ),
            Grp(
                flag_param_grp_req=workflows.abs_cal,
                root_param_grp_attr_name="abs_cal",
                param_grp_cls_obj=AbsCalParamGroup,
            ),
            Grp(
                flag_param_grp_req=workflows.abs_cal or workflows.point_target,
                root_param_grp_attr_name="anc_files",
                param_grp_cls_obj=DynamicAncillaryFileParamGroup,
            ),
            Grp(
                flag_param_grp_req=workflows.point_target,
                root_param_grp_attr_name="pta",
                param_grp_cls_obj=RSLCPointTargetAnalyzerParamGroup,
            ),
        )

        return grps_to_parse

    @staticmethod
    def get_order_of_groups_in_yaml():
        # This order determines the order
        # the groups will appear in the runconfig.
        return {
            "input_f": InputFileGroupParamGroup,
            "anc_files": DynamicAncillaryFileParamGroup,
            "prodpath": ProductPathGroupParamGroup,
            "workflows": RSLCWorkflowsParamGroup,
            "validation": ValidationGroupParamGroup,
            "backscatter_img": BackscatterImageParamGroup,
            "histogram": HistogramParamGroup,
            "range_spectra": RangeSpectraParamGroup,
            "az_spectra": AzimuthSpectraParamGroup,
            "pta": RSLCPointTargetAnalyzerParamGroup,
            "abs_cal": AbsCalParamGroup,
        }


__all__ = nisarqa.get_all(__name__, objects_to_skip)
