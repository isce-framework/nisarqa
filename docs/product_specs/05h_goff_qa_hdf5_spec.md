
## GOFF QA HDF5 Contents

Each QA HDF5 file includes a subset of the available options below, which will correspond to the available frequencies, polarizations, etc. in the input GOFF granule.

* Possible Frequency groups: `frequencyA`

* Possible Polarization groups: `HH`, `VV`, `HV`, `VH`

* Possible layer groups: `layer1`, `layer2`, `layer3`


|     | GOFF QA HDF5 Datasets, Attributes, and Additional Metadata |
| :---: | --------------------------------------- |
| Path | **`/` _(Root Group - Global Attributes)_** |
|    | _contact:_ nisar-sds-ops@jpl.nasa.gov |
|    | _institution:_ NASA JPL |
|    | _mission_name:_ NISAR |
|    | _reference_document:_ D-107726 NASA SDS Product Specification for Level-1 and Level-2 Quality Assurance |
|    | _title:_ NISAR Quality Assurance Statistical Summary of GOFF HDF5 Product |
|     |     |    |
| Path | **`science/LSAR/QA/data/frequencyA/listOfPolarizations`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ Polarizations for Frequency A. |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/histogramBins`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/histogramDensity`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/max_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/mean_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/min_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/percentFill`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/percentInf`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/percentNan`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/percentNearZero`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/percentTotalInvalid`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/sample_stddev`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/histogramBins`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/histogramDensity`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/max_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/mean_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/min_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/percentFill`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/percentInf`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/percentNan`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/percentNearZero`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/percentTotalInvalid`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/sample_stddev`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/histogramBins`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/histogramDensity`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/max_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/mean_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/min_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/percentFill`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/percentInf`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/percentNan`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/percentNearZero`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/percentTotalInvalid`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/sample_stddev`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/histogramBins`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/histogramDensity`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/max_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/mean_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/min_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/percentFill`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/percentInf`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/percentNan`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/percentNearZero`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/percentTotalInvalid`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/sample_stddev`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/histogramBins`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/histogramDensity`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/max_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/mean_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/min_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/percentFill`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/percentInf`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/percentNan`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/percentNearZero`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/percentTotalInvalid`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/sample_stddev`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/histogramBins`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/histogramDensity`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/max_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/mean_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/min_value`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/percentFill`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/percentInf`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/percentNan`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/percentNearZero`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/percentTotalInvalid`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/sample_stddev`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/processing/QAProcessingDateTime`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ QA processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
| Path | **`science/LSAR/QA/processing/QASoftwareVersion`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ QA software version used for processing |
| Path | **`science/LSAR/QA/processing/azAndRngOffsetVarianceColorbarMinMax`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ The vmin and vmax values used to generate the plots for the az and slant range variance layers. The square root of these layers (i.e. the standard deviation of the offsets) was computed, clipped to this interval, and then plotted using this interval for the colorbar. If None, the interval was determined based on the units of the input layers: If `meters^2`, then [0.0, 10.0]. If `pixels^2`, then [0.0, 0.1]. Otherwise [0.0, max(sqrt(\<az var layer\>), sqrt(\<rg var layer\>))] |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/processing/browseDecimation`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** int64 |
|    | _description:_ Decimation strides for the browse image. Format: [\<y decimation\>, \<x decimation\>]. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/crossOffsetVarianceColorbarMinMax`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ The vmin and vmax values to generate the plots for the cross offset variance layer. If None, then the colorbar range was computed based on `crossOffsetVariancePercentileClipped` |
|    | _units:_ meters^2 |
| Path | **`science/LSAR/QA/processing/crossOffsetVariancePercentileClipped`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Percentile range that the cross offset variance raster was clipped to, which determines the colormap interval. Can be superseded by `crossOffsetVarianceColorbarMinMax` |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/quiverPlotColorbarIntervalFrequencyAPolarizationHHLayer1`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Colorbar interval for the slant range and along track offset layers' quiver plot(s). |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/processing/quiverPlotColorbarIntervalFrequencyAPolarizationHHLayer2`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Colorbar interval for the slant range and along track offset layers' quiver plot(s). |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/processing/quiverPlotColorbarIntervalFrequencyAPolarizationHHLayer3`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Colorbar interval for the slant range and along track offset layers' quiver plot(s). |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/processing/runConfigurationContents`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Contents of the run configuration file with parameters used for QA processing |
| Path | **`science/LSAR/identification/boundingPolygon`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ OGR compatible WKT representing the bounding polygon of the image. Horizontal coordinates are WGS84 longitude followed by latitude (both in degrees), and the vertical coordinate is the height above the WGS84 ellipsoid in meters. The first point corresponds to the start-time, near-range radar coordinate, and the perimeter is traversed in counterclockwise order on the map. This means the traversal order in radar coordinates differs for left-looking and right-looking sensors. The polygon includes the four corners of the radar grid, with equal numbers of points distributed evenly in radar coordinates along each edge |
|    | _epsg:_ EPSG code |
|    | _ogr_geometry:_ polygon |
| Path | **`science/LSAR/identification/compositeReleaseId`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Unique version identifier of the science data production system |
| Path | **`science/LSAR/identification/diagnosticModeFlag`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** uint8 |
|    | _description:_ Indicates if the radar operation mode is a diagnostic mode (1-2) or DBFed science (0): 0, 1, or 2 |
| Path | **`science/LSAR/identification/frameNumber`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** uint16 |
|    | _description:_ Frame number |
| Path | **`science/LSAR/identification/granuleId`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Unique granule identification name |
| Path | **`science/LSAR/identification/instrumentName`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Name of the instrument used to collect the remote sensing data provided in this product |
| Path | **`science/LSAR/identification/isDithered`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if the pulse timing was varied (dithered) during acquisition, "False" otherwise |
| Path | **`science/LSAR/identification/isFullFrame`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if the product fully covers a NISAR frame, "False" if partial coverage |
|    | _frameCoveragePercentage:_ Percentage of NISAR frame containing processed data |
|    | _thresholdPercentage:_ Threshold percentage used to determine if the product is full frame or partial frame |
| Path | **`science/LSAR/identification/isGeocoded`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Flag to indicate if the product data is in the radar geometry ("False") or in the map geometry ("True") |
| Path | **`science/LSAR/identification/isMixedMode`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if this product is generated from reference and secondary RSLCs with different range bandwidths, "False" otherwise |
| Path | **`science/LSAR/identification/isUrgentObservation`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Flag indicating if observation is nominal ("False") or urgent ("True") |
| Path | **`science/LSAR/identification/listOfFrequencies`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of frequency layers available in the product |
| Path | **`science/LSAR/identification/lookDirection`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Look direction, either "Left" or "Right" |
| Path | **`science/LSAR/identification/missionId`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Mission identifier |
| Path | **`science/LSAR/identification/orbitPassDirection`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Orbit direction, either "Ascending" or "Descending" |
| Path | **`science/LSAR/identification/plannedDatatakeId`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of planned datatakes included in the product |
| Path | **`science/LSAR/identification/plannedObservationId`** |
|    | GOFF QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of planned observations included in the product |
| Path | **`science/LSAR/identification/platformName`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Name of the platform used to collect the remote sensing data provided in this product |
| Path | **`science/LSAR/identification/processingCenter`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Data processing center |
| Path | **`science/LSAR/identification/processingDateTime`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
| Path | **`science/LSAR/identification/processingType`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Nominal (or) Urgent (or) Custom (or) Undefined |
| Path | **`science/LSAR/identification/productDoi`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Digital Object Identifier (DOI) for the product |
| Path | **`science/LSAR/identification/productLevel`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product level. L0A: Unprocessed instrument data; L0B: Reformatted, unprocessed instrument data; L1: Processed instrument data in radar coordinates system; and L2: Processed instrument data in geocoded coordinates system |
| Path | **`science/LSAR/identification/productSpecificationVersion`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product specification version which represents the schema of this product |
| Path | **`science/LSAR/identification/productType`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product type |
| Path | **`science/LSAR/identification/productVersion`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product version which represents the structure of the product and the science content governed by the algorithm, input data, and processing parameters |
| Path | **`science/LSAR/identification/radarBand`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Acquired frequency band, either "L" or "S" |
| Path | **`science/LSAR/identification/referenceAbsoluteOrbitNumber`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Absolute orbit number for the reference RSLC |
| Path | **`science/LSAR/identification/referenceIsJointObservation`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if any portion of the reference RSLC was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
| Path | **`science/LSAR/identification/referenceZeroDopplerEndTime`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth stop time (in UTC) of reference RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/referenceZeroDopplerStartTime`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth start time (in UTC) of reference RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/secondaryAbsoluteOrbitNumber`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Absolute orbit number for the secondary RSLC |
| Path | **`science/LSAR/identification/secondaryIsJointObservation`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if any portion of the secondary RSLC was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
| Path | **`science/LSAR/identification/secondaryZeroDopplerEndTime`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth stop time (in UTC) of secondary RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/secondaryZeroDopplerStartTime`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth start time (in UTC) of secondary RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/trackNumber`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Track number |
| Path | **`science/LSAR/sourceData/runConfigurationContents`** |
|    | GOFF QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Contents of the run configuration file associated with the processing of the source data |


