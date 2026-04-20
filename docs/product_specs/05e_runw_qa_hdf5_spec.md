
## RUNW QA HDF5 Contents

Each QA HDF5 file includes a subset of the available options below, which will correspond to the available frequencies, polarizations, etc. in the input RUNW granule.

* Possible Frequency groups: `frequencyA`

* Possible Polarization groups: `HH`, `VV`, `HV`, `VH`


|     | RUNW QA HDF5 Datasets, Attributes, and Additional Metadata |
| :---: | --------------------------------------- |
| Path | **`/` _(Root Group - Global Attributes)_** |
|    | _contact:_ nisar-sds-ops@jpl.nasa.gov |
|    | _institution:_ NASA JPL |
|    | _mission_name:_ NISAR |
|    | _reference_document:_ D-107726 NASA SDS Product Specification for Level-1 and Level-2 Quality Assurance |
|    | _title:_ NISAR Quality Assurance Statistical Summary of RUNW HDF5 Product |
|     |     |    |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/histogramBins`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/histogramDensity`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/max_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/mean_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/min_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentFill`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentInf`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentNan`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentNearZero`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentTotalInvalid`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/sample_stddev`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/connectedComponentLabels`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** uint16 |
|    | _description:_ List of all connected component labels, including 0 and the fill value `65535` |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/connectedComponentPercentages`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Percentages of total raster area with each connected component label. Indices correspond to `connectedComponentLabels` |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/numValidConnectedComponents`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ Number of valid connected components, excluding 0 and the fill value `65535` |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentFill`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: 65535. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentInf`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentNan`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentNearZero`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentPixelsInLargestCC`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percentage of pixels in the largest valid connected component relative to the total image size. (0 and fill value (65535) are not valid connected components. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentPixelsWithNonZeroCC`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percentage of pixels with non-zero, non-fill connected components relative to the total image size. (0 and fill value (65535) are not valid connected components. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentTotalInvalid`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/histogramBins`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/histogramDensity`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/max_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/mean_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/min_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/percentFill`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/percentInf`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/percentNan`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/percentNearZero`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/percentTotalInvalid`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/sample_stddev`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/histogramBins`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/histogramDensity`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/max_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/mean_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/min_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/percentFill`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/percentInf`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/percentNan`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/percentNearZero`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/percentTotalInvalid`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/sample_stddev`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/histogramBins`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/histogramDensity`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/max_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/mean_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/min_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/percentFill`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/percentInf`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/percentNan`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/percentNearZero`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/percentTotalInvalid`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/sample_stddev`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/data/frequencyA/listOfPolarizations`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ Polarizations for Frequency A. |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/histogramBins`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/histogramDensity`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/max_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/mean_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/min_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentFill`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentInf`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentNan`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentNearZero`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentTotalInvalid`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/sample_stddev`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/histogramBins`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/histogramDensity`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/max_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/mean_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/min_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentFill`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentInf`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentNan`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentNearZero`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentTotalInvalid`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/sample_stddev`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/histogramBins`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/histogramDensity`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/max_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/mean_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/min_value`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentFill`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentInf`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentNan`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentNearZero`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentTotalInvalid`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/sample_stddev`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/processing/QAProcessingDateTime`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ QA processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
| Path | **`science/LSAR/QA/processing/QASoftwareVersion`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ QA software version used for processing |
| Path | **`science/LSAR/QA/processing/browseImageRewrap`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ The multiple of pi for rewrapping the unwrapped phase layer for the browse PNG. 'None' if no rewrapping occurred. Example: If `browseImageRewrap` is 3, the unwrapped phase was rewrapped to the interval [0, 3pi). |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/phaseImageRewrap`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ The multiple of pi for rewrapping the unwrapped phase image in the report PDF. 'None' if no rewrapping occurred. Example: If `phaseImageRewrap`=3, the image was rewrapped to the interval [0, 3pi). |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/runConfigurationContents`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Contents of the run configuration file with parameters used for QA processing |
| Path | **`science/LSAR/identification/boundingPolygon`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ OGR compatible WKT representing the bounding polygon of the image. Horizontal coordinates are WGS84 longitude followed by latitude (both in degrees), and the vertical coordinate is the height above the WGS84 ellipsoid in meters. The first point corresponds to the start-time, near-range radar coordinate, and the perimeter is traversed in counterclockwise order on the map. This means the traversal order in radar coordinates differs for left-looking and right-looking sensors. The polygon includes the four corners of the radar grid, with equal numbers of points distributed evenly in radar coordinates along each edge |
|    | _epsg:_ EPSG code |
|    | _ogr_geometry:_ polygon |
| Path | **`science/LSAR/identification/compositeReleaseId`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Unique version identifier of the science data production system |
| Path | **`science/LSAR/identification/diagnosticModeFlag`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** uint8 |
|    | _description:_ Indicates if the radar operation mode is a diagnostic mode (1-2) or DBFed science (0): 0, 1, or 2 |
| Path | **`science/LSAR/identification/frameNumber`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** uint16 |
|    | _description:_ Frame number |
| Path | **`science/LSAR/identification/granuleId`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Unique granule identification name |
| Path | **`science/LSAR/identification/instrumentName`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Name of the instrument used to collect the remote sensing data provided in this product |
| Path | **`science/LSAR/identification/isDithered`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if the pulse timing was varied (dithered) during acquisition, "False" otherwise |
| Path | **`science/LSAR/identification/isFullFrame`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if the product fully covers a NISAR frame, "False" if partial coverage |
|    | _frameCoveragePercentage:_ Percentage of NISAR frame containing processed data |
|    | _thresholdPercentage:_ Threshold percentage used to determine if the product is full frame or partial frame |
| Path | **`science/LSAR/identification/isGeocoded`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Flag to indicate if the product data is in the radar geometry ("False") or in the map geometry ("True") |
| Path | **`science/LSAR/identification/isMixedMode`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if this product is generated from reference and secondary RSLCs with different range bandwidths, "False" otherwise |
| Path | **`science/LSAR/identification/isUrgentObservation`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Flag indicating if observation is nominal ("False") or urgent ("True") |
| Path | **`science/LSAR/identification/listOfFrequencies`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of frequency layers available in the product |
| Path | **`science/LSAR/identification/lookDirection`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Look direction, either "Left" or "Right" |
| Path | **`science/LSAR/identification/missionId`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Mission identifier |
| Path | **`science/LSAR/identification/orbitPassDirection`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Orbit direction, either "Ascending" or "Descending" |
| Path | **`science/LSAR/identification/plannedDatatakeId`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of planned datatakes included in the product |
| Path | **`science/LSAR/identification/plannedObservationId`** |
|    | RUNW QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of planned observations included in the product |
| Path | **`science/LSAR/identification/platformName`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Name of the platform used to collect the remote sensing data provided in this product |
| Path | **`science/LSAR/identification/processingCenter`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Data processing center |
| Path | **`science/LSAR/identification/processingDateTime`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
| Path | **`science/LSAR/identification/processingType`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Nominal (or) Urgent (or) Custom (or) Undefined |
| Path | **`science/LSAR/identification/productDoi`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Digital Object Identifier (DOI) for the product |
| Path | **`science/LSAR/identification/productLevel`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product level. L0A: Unprocessed instrument data; L0B: Reformatted, unprocessed instrument data; L1: Processed instrument data in radar coordinates system; and L2: Processed instrument data in geocoded coordinates system |
| Path | **`science/LSAR/identification/productSpecificationVersion`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product specification version which represents the schema of this product |
| Path | **`science/LSAR/identification/productType`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product type |
| Path | **`science/LSAR/identification/productVersion`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product version which represents the structure of the product and the science content governed by the algorithm, input data, and processing parameters |
| Path | **`science/LSAR/identification/radarBand`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Acquired frequency band, either "L" or "S" |
| Path | **`science/LSAR/identification/referenceAbsoluteOrbitNumber`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Absolute orbit number for the reference RSLC |
| Path | **`science/LSAR/identification/referenceIsJointObservation`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if any portion of the reference RSLC was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
| Path | **`science/LSAR/identification/referenceZeroDopplerEndTime`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth stop time (in UTC) of reference RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/referenceZeroDopplerStartTime`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth start time (in UTC) of reference RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/secondaryAbsoluteOrbitNumber`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Absolute orbit number for the secondary RSLC |
| Path | **`science/LSAR/identification/secondaryIsJointObservation`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if any portion of the secondary RSLC was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
| Path | **`science/LSAR/identification/secondaryZeroDopplerEndTime`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth stop time (in UTC) of secondary RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/secondaryZeroDopplerStartTime`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth start time (in UTC) of secondary RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/trackNumber`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Track number |
| Path | **`science/LSAR/sourceData/runConfigurationContents`** |
|    | RUNW QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Contents of the run configuration file associated with the processing of the source data |


