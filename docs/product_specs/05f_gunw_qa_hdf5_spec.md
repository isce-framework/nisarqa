
## GUNW QA HDF5 Contents

Each QA HDF5 file includes a subset of the available options below, which will correspond to the available frequencies, polarizations, etc. in the input GUNW granule.

* Possible Frequency groups: `frequencyA`

* Possible Polarization groups: `HH`, `VV`, `HV`, `VH`


|     | GUNW QA HDF5 Datasets, Attributes, and Additional Metadata |
| :---: | --------------------------------------- |
| Path | **`/` _(Root Group - Global Attributes)_** |
|    | _contact:_ nisar-sds-ops@jpl.nasa.gov |
|    | _institution:_ NASA JPL |
|    | _mission_name:_ NISAR |
|    | _reference_document:_ D-107726 NASA SDS Product Specification for Level-1 and Level-2 Quality Assurance |
|    | _title:_ NISAR Quality Assurance Statistical Summary of GUNW HDF5 Product |
|     |     |    |
| Path | **`science/LSAR/QA/data/frequencyA/listOfPolarizations`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ Polarizations for Frequency A. |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/histogramBins`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/histogramDensity`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/max_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/mean_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/min_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentFill`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentInf`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentNan`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentNearZero`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentTotalInvalid`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/sample_stddev`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/histogramBins`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/histogramDensity`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/max_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/mean_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/min_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentFill`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentInf`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentNan`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentNearZero`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentTotalInvalid`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/sample_stddev`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/histogramBins`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/histogramDensity`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/max_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/mean_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/min_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentFill`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentInf`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentNan`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentNearZero`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentTotalInvalid`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/sample_stddev`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/coherenceMagnitude/histogramBins`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/coherenceMagnitude/histogramDensity`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/coherenceMagnitude/max_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/coherenceMagnitude/mean_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/coherenceMagnitude/min_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/coherenceMagnitude/percentFill`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/coherenceMagnitude/percentInf`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/coherenceMagnitude/percentNan`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/coherenceMagnitude/percentNearZero`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/coherenceMagnitude/percentTotalInvalid`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/coherenceMagnitude/sample_stddev`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/connectedComponents/connectedComponentLabels`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** uint16 |
|    | _description:_ List of all connected component labels, including 0 and the fill value `65535` |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/connectedComponents/connectedComponentPercentages`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Percentages of total raster area with each connected component label. Indices correspond to `connectedComponentLabels` |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/connectedComponents/numValidConnectedComponents`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ Number of valid connected components, excluding 0 and the fill value `65535` |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/connectedComponents/percentFill`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: 65535. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/connectedComponents/percentInf`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/connectedComponents/percentNan`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/connectedComponents/percentNearZero`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/connectedComponents/percentPixelsInLargestCC`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percentage of pixels in the largest valid connected component relative to the total image size. (0 and fill value (65535) are not valid connected components. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/connectedComponents/percentPixelsWithNonZeroCC`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percentage of pixels with non-zero, non-fill connected components relative to the total image size. (0 and fill value (65535) are not valid connected components. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/connectedComponents/percentTotalInvalid`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreen/histogramBins`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreen/histogramDensity`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreen/max_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreen/mean_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreen/min_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreen/percentFill`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreen/percentInf`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreen/percentNan`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreen/percentNearZero`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreen/percentTotalInvalid`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreen/sample_stddev`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreenUncertainty/histogramBins`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreenUncertainty/histogramDensity`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreenUncertainty/max_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreenUncertainty/mean_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreenUncertainty/min_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreenUncertainty/percentFill`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreenUncertainty/percentInf`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreenUncertainty/percentNan`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreenUncertainty/percentNearZero`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreenUncertainty/percentTotalInvalid`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/ionospherePhaseScreenUncertainty/sample_stddev`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/unwrappedPhase/histogramBins`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/unwrappedPhase/histogramDensity`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/unwrappedPhase/max_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/unwrappedPhase/mean_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/unwrappedPhase/min_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/unwrappedPhase/percentFill`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/unwrappedPhase/percentInf`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/unwrappedPhase/percentNan`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/unwrappedPhase/percentNearZero`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/unwrappedPhase/percentTotalInvalid`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/unwrappedInterferogram/HH/unwrappedPhase/sample_stddev`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/coherenceMagnitude/histogramBins`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/coherenceMagnitude/histogramDensity`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/coherenceMagnitude/max_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/coherenceMagnitude/mean_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/coherenceMagnitude/min_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/coherenceMagnitude/percentFill`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/coherenceMagnitude/percentInf`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/coherenceMagnitude/percentNan`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/coherenceMagnitude/percentNearZero`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/coherenceMagnitude/percentTotalInvalid`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/coherenceMagnitude/sample_stddev`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/histogramBins`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/histogramDensity`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/max_imag_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the imaginary component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/max_real_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the real component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/mean_imag_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the imaginary component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/mean_real_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the real component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/min_imag_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the imaginary component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/min_real_value`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the real component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/percentFill`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: (nan+nanj). |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/percentInf`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/percentNan`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/percentNearZero`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/percentTotalInvalid`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/sample_stddev_imag`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the imaginary component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/wrappedInterferogram/HH/wrappedInterferogram/sample_stddev_real`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the real component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/QAProcessingDateTime`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ QA processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
| Path | **`science/LSAR/QA/processing/QASoftwareVersion`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ QA software version used for processing |
| Path | **`science/LSAR/QA/processing/browseImageRewrap`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ The multiple of pi for rewrapping the unwrapped phase layer for the browse PNG. 'None' if no rewrapping occurred. Example: If `browseImageRewrap` is 3, the unwrapped phase was rewrapped to the interval [0, 3pi). |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/phaseImageRewrap`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ The multiple of pi for rewrapping the unwrapped phase image in the report PDF. 'None' if no rewrapping occurred. Example: If `phaseImageRewrap`=3, the image was rewrapped to the interval [0, 3pi). |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/runConfigurationContents`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Contents of the run configuration file with parameters used for QA processing |
| Path | **`science/LSAR/identification/boundingPolygon`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ OGR compatible WKT representing the bounding polygon of the image. Horizontal coordinates are WGS84 longitude followed by latitude (both in degrees), and the vertical coordinate is the height above the WGS84 ellipsoid in meters. The first point corresponds to the start-time, near-range radar coordinate, and the perimeter is traversed in counterclockwise order on the map. This means the traversal order in radar coordinates differs for left-looking and right-looking sensors. The polygon includes the four corners of the radar grid, with equal numbers of points distributed evenly in radar coordinates along each edge |
|    | _epsg:_ EPSG code |
|    | _ogr_geometry:_ polygon |
| Path | **`science/LSAR/identification/compositeReleaseId`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Unique version identifier of the science data production system |
| Path | **`science/LSAR/identification/diagnosticModeFlag`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** uint8 |
|    | _description:_ Indicates if the radar operation mode is a diagnostic mode (1-2) or DBFed science (0): 0, 1, or 2 |
| Path | **`science/LSAR/identification/frameNumber`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** uint16 |
|    | _description:_ Frame number |
| Path | **`science/LSAR/identification/granuleId`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Unique granule identification name |
| Path | **`science/LSAR/identification/instrumentName`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Name of the instrument used to collect the remote sensing data provided in this product |
| Path | **`science/LSAR/identification/isDithered`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if the pulse timing was varied (dithered) during acquisition, "False" otherwise |
| Path | **`science/LSAR/identification/isFullFrame`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if the product fully covers a NISAR frame, "False" if partial coverage |
|    | _frameCoveragePercentage:_ Percentage of NISAR frame containing processed data |
|    | _thresholdPercentage:_ Threshold percentage used to determine if the product is full frame or partial frame |
| Path | **`science/LSAR/identification/isGeocoded`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Flag to indicate if the product data is in the radar geometry ("False") or in the map geometry ("True") |
| Path | **`science/LSAR/identification/isMixedMode`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if this product is generated from reference and secondary RSLCs with different range bandwidths, "False" otherwise |
| Path | **`science/LSAR/identification/isUrgentObservation`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Flag indicating if observation is nominal ("False") or urgent ("True") |
| Path | **`science/LSAR/identification/listOfFrequencies`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of frequency layers available in the product |
| Path | **`science/LSAR/identification/lookDirection`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Look direction, either "Left" or "Right" |
| Path | **`science/LSAR/identification/missionId`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Mission identifier |
| Path | **`science/LSAR/identification/orbitPassDirection`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Orbit direction, either "Ascending" or "Descending" |
| Path | **`science/LSAR/identification/plannedDatatakeId`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of planned datatakes included in the product |
| Path | **`science/LSAR/identification/plannedObservationId`** |
|    | GUNW QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of planned observations included in the product |
| Path | **`science/LSAR/identification/platformName`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Name of the platform used to collect the remote sensing data provided in this product |
| Path | **`science/LSAR/identification/processingCenter`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Data processing center |
| Path | **`science/LSAR/identification/processingDateTime`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
| Path | **`science/LSAR/identification/processingType`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Nominal (or) Urgent (or) Custom (or) Undefined |
| Path | **`science/LSAR/identification/productDoi`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Digital Object Identifier (DOI) for the product |
| Path | **`science/LSAR/identification/productLevel`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product level. L0A: Unprocessed instrument data; L0B: Reformatted, unprocessed instrument data; L1: Processed instrument data in radar coordinates system; and L2: Processed instrument data in geocoded coordinates system |
| Path | **`science/LSAR/identification/productSpecificationVersion`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product specification version which represents the schema of this product |
| Path | **`science/LSAR/identification/productType`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product type |
| Path | **`science/LSAR/identification/productVersion`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product version which represents the structure of the product and the science content governed by the algorithm, input data, and processing parameters |
| Path | **`science/LSAR/identification/radarBand`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Acquired frequency band, either "L" or "S" |
| Path | **`science/LSAR/identification/referenceAbsoluteOrbitNumber`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Absolute orbit number for the reference RSLC |
| Path | **`science/LSAR/identification/referenceIsJointObservation`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if any portion of the reference RSLC was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
| Path | **`science/LSAR/identification/referenceZeroDopplerEndTime`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth stop time (in UTC) of reference RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/referenceZeroDopplerStartTime`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth start time (in UTC) of reference RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/secondaryAbsoluteOrbitNumber`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Absolute orbit number for the secondary RSLC |
| Path | **`science/LSAR/identification/secondaryIsJointObservation`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if any portion of the secondary RSLC was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
| Path | **`science/LSAR/identification/secondaryZeroDopplerEndTime`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth stop time (in UTC) of secondary RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/secondaryZeroDopplerStartTime`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth start time (in UTC) of secondary RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/trackNumber`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Track number |
| Path | **`science/LSAR/sourceData/runConfigurationContents`** |
|    | GUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Contents of the run configuration file associated with the processing of the source data |


