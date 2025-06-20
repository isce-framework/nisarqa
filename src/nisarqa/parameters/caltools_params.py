from dataclasses import dataclass, field

import nisarqa

from .nisar_params import HDF5Attrs, HDF5ParamGroup, YamlAttrs, YamlParamGroup

objects_to_skip = nisarqa.get_all(__name__)


@dataclass(frozen=True)
class AbsCalParamGroup(YamlParamGroup, HDF5ParamGroup):
    """
    Parameters from the QA-CalTools Absolute Radiometric Calibration
    runconfig group.

    Parameters
    ----------
    nchip : int, optional
        The width, in samples, of the square block of image data to extract
        centered around the target position for oversampling and peak finding.
        Must be >= 1. Defaults to 64.
    upsample_factor : int, optional
        The upsampling ratio. Must be >= 1. Defaults to 32.
    peak_find_domain : {'time', 'freq'}, optional
        Option controlling how the target peak position is estimated.

        'time':
          The default mode. The peak location is found in the time domain by
          detecting the maximum value within a square block of image data around
          the expected target location. The signal data is upsampled to improve
          precision.

        'freq':
          The peak location is found by estimating the phase ramp in the
          frequency domain. This mode is useful when target is well-focused, has
          high SNR, and is the only target in the neighborhood (often the case
          in point target simulations).
    nfit : int, optional
        The width, in *oversampled* samples, of the square sub-block of image
        data to extract centered around the target position for fitting a
        quadratic polynomial to the peak. Note that this is the size in samples
        *after upsampling*. Must be >= 3. Defaults to 5.
    power_method : {'box', 'integrated'}, optional
        The method for estimating the target signal power.

        'box':
          The default mode. Measures power using the rectangular box method,
          which assumes that the target response can be approximated by a 2-D
          rectangular function. The total power is estimated by multiplying the
          peak power by the 3dB response widths in along-track and cross-track
          directions.

        'integrated':
          Measures power using the integrated power method. The total power is
          measured by summing the power of bins whose power exceeds a predefined
          minimum power threshold.
    power_threshold : float, optional
        The minimum power threshold, measured in dB below the peak power, for
        estimating the target signal power using the integrated power method.
        This parameter is ignored if `power_method` is not 'integrated'.
        Defaults to 3.

    Notes
    -----
    Parameter descriptions are adapted from the
    `nisar.workflows.estimate_abscal_factor` module. The original docstring
    descriptions can be found here:
    https://github-fn.jpl.nasa.gov/isce-3/isce/blob/34963f77d2d008c8cfc9e7a9f44d9d0f1548c522/python/packages/nisar/workflows/estimate_abscal_factor.py#L85-L125
    """

    nchip: int = field(
        default=64,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="nchip",
                descr="""The width, in samples, of the square block of image data
                centered around the target position to extract for oversampling
                and peak finding. Must be >= 1.""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="numSamplesChip",
                units="samples",
                descr=(
                    "The width, in samples, of the square block of image data"
                    " centered around the target position used for oversampling"
                    " and peak finding."
                ),
                group_path=nisarqa.STATS_H5_ABSCAL_PROCESSING_GROUP,
            ),
        },
    )

    upsample_factor: int = field(
        default=32,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="upsample_factor",
                descr="The upsampling ratio. Must be >= 1.",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="upsampleFactor",
                units="1",
                descr="The upsampling ratio.",
                group_path=nisarqa.STATS_H5_ABSCAL_PROCESSING_GROUP,
            ),
        },
    )

    peak_find_domain: str = field(
        default="time",
        metadata={
            "yaml_attrs": YamlAttrs(
                name="peak_find_domain",
                descr="""Option controlling how the target peak position is
                estimated. Valid options are 'time' or 'freq'.

                'time':
                  The peak location is found in the time domain by detecting the
                  maximum value within a square block of image data around the
                  expected target location. The signal data is upsampled to
                  improve precision.

                'freq':
                  The peak location is found by estimating the phase ramp in the
                  frequency domain. This mode is useful when the target is
                  well-focused, has high SNR, and is the only target in the
                  neighborhood (often the case in point target simulations).""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="peakFindDomain",
                units=None,
                descr=(
                    "Option controlling how the target peak position was"
                    " estimated."
                ),
                group_path=nisarqa.STATS_H5_ABSCAL_PROCESSING_GROUP,
            ),
        },
    )

    nfit: int = field(
        default=5,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="nfit",
                descr="""The width, in *oversampled* samples, of the square
                sub-block of image data centered around the target position to
                extract for fitting a quadratic polynomial to the peak. Note
                that this is the size in samples *after upsampling*.
                Must be >= 3.""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="numSamplesFit",
                units="samples",
                descr=(
                    "The width, in *oversampled* samples, of the square"
                    " sub-block of image data centered around the target"
                    " position used for fitting a quadratic polynomial to the"
                    " peak."
                ),
                group_path=nisarqa.STATS_H5_ABSCAL_PROCESSING_GROUP,
            ),
        },
    )

    power_method: str = field(
        default="box",
        metadata={
            "yaml_attrs": YamlAttrs(
                name="power_method",
                descr="""Method to use for estimating the target signal power.
                Valid options are 'box' or 'integrated'.

                'box':
                  Measures power using the rectangular box method, which assumes
                  that the target response can be approximated by a 2-D
                  rectangular function. The total power is estimated by
                  multiplying the peak power by the 3dB response widths in
                  along-track and cross-track directions.

                'integrated':
                  Measures power using the integrated power method. The total
                  power is measured by summing the power of bins whose power
                  exceeds a predefined minimum power threshold.""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="powerMethod",
                units=None,
                descr="Method used to estimate the target signal power.",
                group_path=nisarqa.STATS_H5_ABSCAL_PROCESSING_GROUP,
            ),
        },
    )

    power_threshold: float = field(
        default=3.0,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="power_threshold",
                descr="""The minimum power threshold, measured in dB below the
                peak power, for estimating the target signal power using the
                integrated power method. This parameter is ignored if
                `power_method` is not 'integrated'.""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="powerThreshold",
                units="dB",
                descr=(
                    "The minimum power threshold, measured in dB below the peak"
                    " power, used to estimate the target signal power if the"
                    " integrated power method was used."
                ),
                group_path=nisarqa.STATS_H5_ABSCAL_PROCESSING_GROUP,
            ),
        },
    )

    def __post_init__(self):
        # Validate nchip.
        if not isinstance(self.nchip, int):
            raise TypeError(f"`nchip` must be an int, got {type(self.nchip)}")
        if self.nchip < 1:
            raise ValueError(f"`nchip` must be >= 1, got {self.nchip}")

        # Validate upsample_factor.
        if not isinstance(self.upsample_factor, int):
            raise TypeError(
                "`upsample_factor` must be an int, got"
                f" {type(self.upsample_factor)}"
            )
        if self.upsample_factor < 1:
            raise ValueError(
                f"`upsample_factor` must be >= 1, got {self.upsample_factor}"
            )

        # Validate peak_find_domain.
        if not isinstance(self.peak_find_domain, str):
            raise TypeError(
                "`peak_find_domain` must be a str, got"
                f" {type(self.peak_find_domain)}"
            )
        peak_find_domain_choices = {"time", "freq"}
        if self.peak_find_domain not in peak_find_domain_choices:
            raise ValueError(
                f"`peak_find_domain` must be one of {peak_find_domain_choices},"
                f" got {self.peak_find_domain!r}"
            )

        # Validate nfit.
        if not isinstance(self.nfit, int):
            raise TypeError(f"`nfit` must be an int, got {type(self.nfit)}")
        if self.nfit < 3:
            raise ValueError(f"`nfit` must be >= 3, got {self.nfit}")

        # Validate power_method.
        if not isinstance(self.power_method, str):
            raise TypeError(
                f"`power_method` must be a str, got {type(self.power_method)}"
            )
        power_method_choices = {"box", "integrated"}
        if self.power_method not in power_method_choices:
            raise ValueError(
                f"`power_method` must be one of {power_method_choices}, got"
                f" {self.power_method!r}"
            )

        # Validate power_threshold.
        if not isinstance(self.power_threshold, (int, float)):
            raise TypeError(
                "`power_threshold` must be a float, got"
                f" {type(self.power_threshold)}"
            )

    @staticmethod
    def get_path_to_group_in_runconfig():
        return [
            "runconfig",
            "groups",
            "qa",
            "absolute_radiometric_calibration",
        ]


@dataclass(frozen=True)
class PointTargetAnalyzerParamGroup(YamlParamGroup, HDF5ParamGroup):
    """
    Parameters from the QA-CalTools Point Target Analyzer runconfig group.

    Parameters
    ----------
    nchip : int, optional
        The width, in samples, of the square block of image data centered around
        the target position to extract for oversampling and peak finding. Must
        be >= 1. Defaults to 64.
    upsample_factor : int, optional
        The upsampling ratio. Must be >= 1. Defaults to 32.
    peak_find_domain : {'time', 'frequency'}, optional
        Option controlling how the target peak position is estimated.

        'time':
          The default mode. The peak location is found in the time domain by
          detecting the maximum value within a square block of image data around
          the expected target location. The signal data is upsampled to improve
          precision.

        'frequency':
          The peak location is found by estimating the phase ramp in the
          frequency domain. This mode is useful when the target is well-focused,
          has high SNR, and is the only target in the neighborhood (often the
          case in point target simulations).
    num_sidelobes : int, optional
        The number of sidelobes, including the main lobe, to use for computing
        the integrated sidelobe ratio (ISLR). Must be > 1. Defaults to 10.

    Notes
    -----
    Parameter descriptions are adapted from the
    `nisar.workflows.gslc_point_target_analysis` module. The original docstring
    descriptions can be found here:
    https://github-fn.jpl.nasa.gov/isce-3/isce/blob/089d2af9147e424444beec39b115eba569557808/python/packages/nisar/workflows/gslc_point_target_analysis.py#L503-L525
    """

    nchip: int = field(
        default=64,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="nchip",
                descr="""The width, in samples, of the square block of image data
                centered around the target position to extract for oversampling
                and peak finding. Must be >= 1.""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="numSamplesChip",
                units="samples",
                descr=(
                    "The width, in samples, of the square block of image data"
                    " centered around the target position used for oversampling"
                    " and peak finding."
                ),
                group_path=nisarqa.STATS_H5_PTA_PROCESSING_GROUP,
            ),
        },
    )

    upsample_factor: int = field(
        default=32,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="upsample_factor",
                descr="The upsampling ratio. Must be >= 1.",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="upsampleFactor",
                units="1",
                descr="The upsampling ratio.",
                group_path=nisarqa.STATS_H5_PTA_PROCESSING_GROUP,
            ),
        },
    )

    peak_find_domain: str = field(
        default="time",
        metadata={
            "yaml_attrs": YamlAttrs(
                name="peak_find_domain",
                descr="""Option controlling how the target peak position is
                estimated. Valid options are 'time' or 'frequency'.

                'time':
                  The peak location is found in the time domain by detecting the
                  maximum value within a square block of image data around the
                  expected target location. The signal data is upsampled to
                  improve precision.

                'frequency':
                  The peak location is found by estimating the phase ramp in the
                  frequency domain. This mode is useful when the target is
                  well-focused, has high SNR, and is the only target in the
                  neighborhood (often the case in point target simulations).""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="peakFindDomain",
                units=None,
                descr=(
                    "Option controlling how the target peak position was"
                    " estimated."
                ),
                group_path=nisarqa.STATS_H5_PTA_PROCESSING_GROUP,
            ),
        },
    )

    num_sidelobes: int = field(
        default=10,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="num_sidelobes",
                descr="""The number of sidelobes, including the main lobe, to
                use for computing the integrated sidelobe ratio (ISLR).
                Must be > 1.""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="numSidelobesISLR",
                units=None,
                descr=(
                    "The number of sidelobes, including the main lobe, used to"
                    " compute the integrated sidelobe ratio (ISLR)."
                ),
                group_path=nisarqa.STATS_H5_PTA_PROCESSING_GROUP,
            ),
        },
    )

    def __post_init__(self):
        # Validate nchip.
        if not isinstance(self.nchip, int):
            raise TypeError(f"`nchip` must be an int, got {type(self.nchip)}")
        if self.nchip < 1:
            raise ValueError(f"`nchip` must be >= 1, got {self.nchip}")

        # Validate upsample_factor.
        if not isinstance(self.upsample_factor, int):
            raise TypeError(
                "`upsample_factor` must be an int, got"
                f" {type(self.upsample_factor)}"
            )
        if self.upsample_factor < 1:
            raise ValueError(
                f"`upsample_factor` must be >= 1, got {self.upsample_factor}"
            )

        # Validate peak_find_domain.
        if not isinstance(self.peak_find_domain, str):
            raise TypeError(
                "`peak_find_domain` must be a str, got"
                f" {type(self.peak_find_domain)}"
            )
        # XXX this differs from the `peak_find_domain` parameter of the AbsCal
        # tool, which expects 'time' or 'freq'!
        peak_find_domain_choices = {"time", "frequency"}
        if self.peak_find_domain not in peak_find_domain_choices:
            raise ValueError(
                f"`peak_find_domain` must be one of {peak_find_domain_choices},"
                f" got {self.peak_find_domain!r}"
            )

        # Validate num_sidelobes.
        if not isinstance(self.num_sidelobes, int):
            raise TypeError(
                "`num_sidelobes` must be an int, got"
                f" {type(self.num_sidelobes)}"
            )
        if self.num_sidelobes <= 1:
            raise ValueError(
                f"`num_sidelobes` must be > 1, got {self.num_sidelobes}"
            )

    @staticmethod
    def get_path_to_group_in_runconfig():
        return ["runconfig", "groups", "qa", "point_target_analyzer"]


@dataclass(frozen=True)
class RSLCPointTargetAnalyzerParamGroup(PointTargetAnalyzerParamGroup):
    """
    Parameters from the QA-CalTools RSLC Point Target Analyzer runconfig group.

    Parameters
    ----------
    nchip : int, optional
        The width, in samples, of the square block of image data centered around
        the target position to extract for oversampling and peak finding. Must
        be >= 1. Defaults to 64.
    upsample_factor : int, optional
        The upsampling ratio. Must be >= 1. Defaults to 32.
    peak_find_domain : {'time', 'frequency'}, optional
        Option controlling how the target peak position is estimated.

        'time':
          The default mode. The peak location is found in the time domain by
          detecting the maximum value within a square block of image data around
          the expected target location. The signal data is upsampled to improve
          precision.

        'frequency':
          The peak location is found by estimating the phase ramp in the
          frequency domain. This mode is useful when the target is well-focused,
          has high SNR, and is the only target in the neighborhood (often the
          case in point target simulations).
    num_sidelobes : int, optional
        The number of sidelobes, including the main lobe, to use for computing
        the integrated sidelobe ratio (ISLR). Must be > 1. Defaults to 10.
    predict_null : bool, optional
        Controls how the main lobe null locations are determined for ISLR
        computation. If `predict_null` is true, the null locations are
        determined analytically by assuming that the corner reflector has the
        impulse response of a point target with known sampling-rate-to-bandwidth
        ratio (given by `fs_bw_ratio`) and range & azimuth spectral windows
        (given by `window_type` & `window_parameter`). In this case, the first
        sidelobe will be considered to be part of the main lobe. Alternatively,
        if `predict_null` is false, the apparent null locations will be
        estimated from the RSLC image data by searching for nulls in range &
        azimuth cuts centered on the target location. In this case, the main
        lobe does *not* include the first sidelobe. `predict_null` has no effect
        on peak-to-sidelobe ratio (PSLR) computation -- for PSLR analysis, the
        null locations are always determined by searching for nulls in the RSLC
        data. Defaults to False.
    fs_bw_ratio : float, optional
        The ratio of sampling rate to bandwidth in the RSLC image data. Must be
        the same for both range & azimuth. It is ignored if `predict_null` was
        false. Defaults to 1.2 (the nominal oversampling ratio of NISAR RSLC
        data).
    window_type : {'rect', 'cosine', 'kaiser'}, optional
        The window type used in RSLC formation. Used to predict the locations of
        main lobe nulls during ISLR processing if `predict_null` was true. It is
        ignored if `predict_null` was false. The same window type is assumed to
        have been used for both range & azimuth focusing.

        'rect':
            The default. Assumes that the RSLC image was formed using a
            rectangular-shaped window (i.e. no spectral weighting was applied).

        'cosine':
            Assumes that the RSLC image was formed using a raised-cosine window
            with pedestal height defined by `window_parameter`.

        'kaiser':
            Assumes that the RSLC image was formed using a Kaiser window with
            beta parameter defined by `window_parameter`.
    window_parameter : float, optional
        The window shape parameter used in RSLC formation. The meaning of this
        parameter depends on the `window_type`. For a raised-cosine window, it
        is the pedestal height of the window. For a Kaiser window, it is the
        beta parameter. It is ignored if `window_type` was 'rect' or if
        `predict_null` was false. The same shape parameter is assumed to have
        been used for both range & azimuth focusing. Defaults to 0.

    Notes
    -----
    Parameter descriptions are adapted from the
    `nisar.workflows.point_target_analysis` module. The original docstring
    descriptions can be found here:
    https://github-fn.jpl.nasa.gov/isce-3/isce/blob/34963f77d2d008c8cfc9e7a9f44d9d0f1548c522/python/packages/nisar/workflows/point_target_analysis.py#L444-L504
    """

    predict_null: bool = field(
        default=False,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="predict_null",
                descr="""Controls how the main lobe null locations are
                determined for ISLR computation. If `predict_null` is true, the
                null locations are determined analytically by assuming that the
                corner reflector has the impulse response of a point target with
                known sampling-rate-to-bandwidth ratio (given by `fs_bw_ratio`)
                and range & azimuth spectral windows (given by `window_type` &
                `window_parameter`). In this case, the first sidelobe will be
                considered to be part of the main lobe. Alternatively, if
                `predict_null` is false, the apparent null locations will be
                estimated from the RSLC image data by searching for nulls in
                range & azimuth cuts centered on the target location. In this
                case, the main lobe does *not* include the first sidelobe.
                `predict_null` has no effect on peak-to-sidelobe ratio (PSLR)
                computation -- for PSLR analysis, the null locations are always
                determined by searching for nulls in the RSLC data.""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="predictNullISLR",
                units=None,
                descr=(
                    "How the main lobe null locations were determined for ISLR"
                    " computation. If True, the main lobe was considered to"
                    " include the first sidelobe and the null locations were"
                    " predicted analytically. Otherwise, the main lobe null"
                    " locations were estimated from the RSLC data."
                ),
                group_path=nisarqa.STATS_H5_PTA_PROCESSING_GROUP,
            ),
        },
    )

    fs_bw_ratio: float = field(
        default=1.2,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="fs_bw_ratio",
                descr="""The ratio of sampling rate to bandwidth in the RSLC
                image data. Must be the same for both range & azimuth. It is
                ignored if `predict_null` was false. Must be > 0.""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="samplingRateBandwidthRatio",
                units="1",
                descr=(
                    "Assumed ratio of sampling rate to bandwidth in the RSLC"
                    " image data."
                ),
                group_path=nisarqa.STATS_H5_PTA_PROCESSING_GROUP,
            ),
        },
    )

    window_type: str = field(
        default="rect",
        metadata={
            "yaml_attrs": YamlAttrs(
                name="window_type",
                descr="""The window type used in RSLC formation. Used to predict
                the locations of main lobe nulls during ISLR processing if
                `predict_null` was true. It is ignored if `predict_null` was
                false. The same window type is assumed to have been used for
                both range & azimuth focusing. Valid options are 'rect',
                'cosine', or 'kaiser'.

                'rect':
                  Assumes that the RSLC image was formed using a
                  rectangular-shaped window (i.e. no spectral weighting was
                  applied).

                'cosine':
                  Assumes that the RSLC image was formed using a raised-cosine
                  window with pedestal height defined by `window_parameter`.

                'kaiser':
                  Assumes that the RSLC image was formed using a Kaiser window
                  with beta parameter defined by `window_parameter`.""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="windowType",
                units=None,
                descr="Assumed window type used in RSLC formation.",
                group_path=nisarqa.STATS_H5_PTA_PROCESSING_GROUP,
            ),
        },
    )

    window_parameter: float = field(
        default=0.0,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="window_parameter",
                descr="""The window shape parameter used in RSLC formation. The
                meaning of this parameter depends on the `window_type`. For a
                raised-cosine window, it is the pedestal height of the window
                and must be in the interval [0, 1]. For a Kaiser window, it is
                the beta parameter and must be >= 0. It is ignored if
                `window_type` was 'rect' or if `predict_null` was false. The
                same shape parameter is assumed to have been used for both range
                & azimuth focusing.""",
            ),
            "hdf5_attrs": HDF5Attrs(
                name="windowShape",
                units="1",
                descr="Assumed window shape parameter used in RSLC formation.",
                group_path=nisarqa.STATS_H5_PTA_PROCESSING_GROUP,
            ),
        },
    )

    def __post_init__(self):
        super().__post_init__()

        # Validate predict_null.
        if not isinstance(self.predict_null, bool):
            raise TypeError(
                f"`predict_null` must be a bool, got {type(self.predict_null)}"
            )

        # Validate fs_bw_ratio.
        if not isinstance(self.fs_bw_ratio, (int, float)):
            raise TypeError(
                f"`fs_bw_ratio` must be a float, got {type(self.fs_bw_ratio)}"
            )
        if self.fs_bw_ratio <= 0.0:
            raise ValueError(
                f"`fs_bw_ratio` must be > 0, got {self.fs_bw_ratio}"
            )

        # Validate window_type.
        if not isinstance(self.window_type, str):
            raise TypeError(
                f"`window_type` must be a str, got {type(self.window_type)}"
            )
        window_type_choices = {"rect", "cosine", "kaiser"}
        if self.window_type not in window_type_choices:
            raise ValueError(
                f"`window_type` must be one of {window_type_choices}, got"
                f" {self.window_type!r}"
            )

        # Validate window_parameter.
        if not isinstance(self.window_parameter, (int, float)):
            raise TypeError(
                "`window_parameter` must be a float, got"
                f" {type(self.window_parameter)}"
            )
        if self.window_type == "cosine":
            if not (0.0 <= self.window_parameter <= 1.0):
                raise ValueError(
                    "`window_parameter` must be in the interval [0, 1] when"
                    f" `window_type` is 'cosine', got {self.window_parameter}"
                )
        elif self.window_type == "kaiser":
            if self.window_parameter < 0.0:
                raise ValueError(
                    "`window_parameter` must be >= 0 when `window_type` is"
                    f" 'kaiser', got {self.window_parameter}"
                )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
