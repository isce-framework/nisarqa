
## RUNW QA HDF5 Contents

Each QA HDF5 file includes a subset of the available options below, which will correspond to the available frequencies, polarizations, etc. in the input RUNW product.

* Possible Frequency Groups: `frequencyA`

* Possible Polarization Groups: `HH`, `VV`, `HV`, `VH`


|     | RUNW QA HDF5 Dataset, Attributes, and additional metadata |
| :---: | --------------------------------------- |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/histogramBins`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/histogramDensity`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/max_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/mean_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/min_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentFill`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentInf`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentNan`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentNearZero`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentTotalInvalid`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/sample_stddev`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/connectedComponentLabels`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ List of all connected component labels, including 0 and the fill value `65535` |
|    | _dtype:_ uint16 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/connectedComponentPercentages`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percentages of total raster area with each connected component label. Indices correspond to `connectedComponentLabels` |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/numValidConnectedComponents`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Number of valid connected components, excluding 0 and the fill value `65535` |
|    | _units:_ 1 |
|    | _dtype:_ int64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentFill`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: 65535. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentInf`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentNan`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentNearZero`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentPixelsInLargestCC`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percentage of pixels in the largest valid connected component relative to the total image size. (0 and fill value (65535) are not valid connected components. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentPixelsWithNonZeroCC`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percentage of pixels with non-zero, non-fill connected components relative to the total image size. (0 and fill value (65535) are not valid connected components. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/connectedComponents/percentTotalInvalid`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/histogramBins`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/histogramDensity`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/radians |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/max_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/mean_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/min_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/percentFill`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/percentInf`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/percentNan`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/percentNearZero`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/percentTotalInvalid`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreen/sample_stddev`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/histogramBins`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/histogramDensity`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/radians |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/max_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/mean_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/min_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/percentFill`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/percentInf`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/percentNan`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/percentNearZero`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/percentTotalInvalid`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/ionospherePhaseScreenUncertainty/sample_stddev`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/histogramBins`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/histogramDensity`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/radians |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/max_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/mean_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/min_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/percentFill`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/percentInf`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/percentNan`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/percentNearZero`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/percentTotalInvalid`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/interferogram/HH/unwrappedPhase/sample_stddev`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ radians |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/listOfPolarizations`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Polarizations for Frequency A. |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/histogramBins`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/histogramDensity`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/max_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/mean_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/min_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentFill`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentInf`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentNan`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentNearZero`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentTotalInvalid`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/sample_stddev`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/histogramBins`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/histogramDensity`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/max_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/mean_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/min_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentFill`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentInf`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentNan`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentNearZero`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentTotalInvalid`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/sample_stddev`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/histogramBins`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/histogramDensity`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/max_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/mean_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/min_value`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentFill`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentInf`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentNan`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentNearZero`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentTotalInvalid`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/sample_stddev`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/processing/QASoftwareVersion`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ QA software version used for processing |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/processing/browseImage`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Basis image for the browse PNG. 'phase' if (optionally re-wrapped) unwrapped phase, 'hsi' if an HSI image with that phase information encoded as Hue and coherence encoded as Intensity. |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/processing/browseImageRewrap`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ The multiple of pi for rewrapping the unwrapped phase layer for the browse PNG. 'None' if no rewrapping occurred. Example: If `browseImageRewrap` is 3, the unwrapped phase was rewrapped to the interval [0, 3pi). |
|    | _units:_ 1 |
|    | _dtype:_ int64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/processing/equalizeBrowse`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ If True and if `browseImage` is 'hsi', histogram equalization was applied to the intensity channel (coherence magnitude layer) in the HSI browse image PNG. Otherwise, not used while processing the browse PNG. |
|    | _units:_ 1 |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/processing/phaseImageRewrap`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ The multiple of pi for rewrapping the unwrapped phase image in the report PDF; applied to both unwrapped phase image plot(s) and HSI plot(s). 'None' if no rewrapping occurred. Example: If `phaseImageRewrap`=3, the image was rewrapped to the interval [0, 3pi). |
|    | _units:_ 1 |
|    | _dtype:_ int64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/processing/runConfigurationContents`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Contents of the run configuration file with parameters used for processing |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/boundingPolygon`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ OGR compatible WKT representing the bounding polygon of the image. Horizontal coordinates are WGS84 longitude followed by latitude (both in degrees), and the vertical coordinate is the height above the WGS84 ellipsoid in meters. The first point corresponds to the start-time, near-range radar coordinate, and the perimeter is traversed in counterclockwise order on the map. This means the traversal order in radar coordinates differs for left-looking and right-looking sensors. The polygon includes the four corners of the radar grid, with equal numbers of points distributed evenly in radar coordinates along each edge |
|    | _epsg:_ EPSG code |
|    | _ogr_geometry:_ polygon |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/compositeReleaseId`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Unique version identifier of the science data production system |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/diagnosticModeFlag`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Indicates if the radar operation mode is a diagnostic mode (1-2) or DBFed science (0): 0, 1, or 2 |
|    | _dtype:_ uint8 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/frameNumber`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Frame number |
|    | _dtype:_ uint16 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/granuleId`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Unique granule identification name |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/instrumentName`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Name of the instrument used to collect the remote sensing data provided in this product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isDithered`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ "True" if the pulse timing was varied (dithered) during acquisition, "False" otherwise |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isFullFrame`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ "True" if the product fully covers a NISAR frame, "False" if partial coverage |
|    | _frameCoveragePercentage:_ Percentage of NISAR frame containing processed data |
|    | _thresholdPercentage:_ Threshold percentage used to determine if the product is full frame or partial frame |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isGeocoded`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Flag to indicate if the product data is in the radar geometry ("False") or in the map geometry ("True") |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isMixedMode`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ "True" if this product is generated from reference and secondary RSLCs with different range bandwidths, "False" otherwise |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isUrgentObservation`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Flag indicating if observation is nominal ("False") or urgent ("True") |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/listOfFrequencies`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ List of frequency layers available in the product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/identification/lookDirection`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Look direction, either "Left" or "Right" |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/missionId`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Mission identifier |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/orbitPassDirection`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Orbit direction, either "Ascending" or "Descending" |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/plannedDatatakeId`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ List of planned datatakes included in the product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/identification/plannedObservationId`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ List of planned observations included in the product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/identification/platformName`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Name of the platform used to collect the remote sensing data provided in this product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/processingCenter`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Data processing center |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/processingDateTime`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/processingType`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Nominal (or) Urgent (or) Custom (or) Undefined |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productDoi`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Digital Object Identifier (DOI) for the product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productLevel`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Product level. L0A: Unprocessed instrument data; L0B: Reformatted, unprocessed instrument data; L1: Processed instrument data in radar coordinates system; and L2: Processed instrument data in geocoded coordinates system |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productSpecificationVersion`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Product specification version which represents the schema of this product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productType`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Product type |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productVersion`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Product version which represents the structure of the product and the science content governed by the algorithm, input data, and processing parameters |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/radarBand`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Acquired frequency band, either "L" or "S" |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/referenceAbsoluteOrbitNumber`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Absolute orbit number for the reference RSLC |
|    | _dtype:_ uint32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/referenceIsJointObservation`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ "True" if any portion of the reference RSLC was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/referenceZeroDopplerEndTime`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Azimuth stop time (in UTC) of reference RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/referenceZeroDopplerStartTime`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Azimuth start time (in UTC) of reference RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/secondaryAbsoluteOrbitNumber`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Absolute orbit number for the secondary RSLC |
|    | _dtype:_ uint32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/secondaryIsJointObservation`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ "True" if any portion of the secondary RSLC was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/secondaryZeroDopplerEndTime`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Azimuth stop time (in UTC) of secondary RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/secondaryZeroDopplerStartTime`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Azimuth start time (in UTC) of secondary RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/trackNumber`** |
|    | _Product type:_ RUNW QA |
|    | _description:_ Track number |
|    | _dtype:_ uint32 |
|    | _ndim:_ scalar |


