
## ROFF QA HDF5 Contents

Each QA HDF5 file includes a subset of the available options below, which will correspond to the available frequencies, polarizations, etc. in the input ROFF product.

* Possible Frequency Groups: `frequencyA`

* Possible Polarization Groups: `HH`, `VV`, `HV`, `VH`

* Possible layer Groups: `layer1`, `layer2`, `layer3`


|     | ROFF QA HDF5 Dataset, Attributes, and additional metadata |
| :---: | --------------------------------------- |
| Path: | **`science/LSAR/QA/data/frequencyA/listOfPolarizations`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Polarizations for Frequency A. |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffset/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters^2 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/alongTrackOffsetVariance/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/correlationSurfacePeak/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters^2 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/crossOffsetVariance/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffset/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters^2 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer1/slantRangeOffsetVariance/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffset/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffset/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffset/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffset/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffset/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffset/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffset/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffset/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffset/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffset/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffset/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffsetVariance/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffsetVariance/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters^2 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffsetVariance/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffsetVariance/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffsetVariance/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffsetVariance/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffsetVariance/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffsetVariance/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffsetVariance/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffsetVariance/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/alongTrackOffsetVariance/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/correlationSurfacePeak/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/correlationSurfacePeak/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/correlationSurfacePeak/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/correlationSurfacePeak/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/correlationSurfacePeak/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/correlationSurfacePeak/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/correlationSurfacePeak/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/correlationSurfacePeak/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/correlationSurfacePeak/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/correlationSurfacePeak/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/correlationSurfacePeak/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/crossOffsetVariance/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/crossOffsetVariance/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters^2 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/crossOffsetVariance/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/crossOffsetVariance/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/crossOffsetVariance/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/crossOffsetVariance/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/crossOffsetVariance/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/crossOffsetVariance/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/crossOffsetVariance/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/crossOffsetVariance/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/crossOffsetVariance/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffset/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffset/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffset/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffset/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffset/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffset/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffset/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffset/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffset/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffset/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffset/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffsetVariance/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffsetVariance/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters^2 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffsetVariance/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffsetVariance/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffsetVariance/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffsetVariance/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffsetVariance/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffsetVariance/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffsetVariance/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffsetVariance/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer2/slantRangeOffsetVariance/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffset/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffset/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffset/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffset/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffset/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffset/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffset/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffset/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffset/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffset/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffset/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffsetVariance/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffsetVariance/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters^2 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffsetVariance/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffsetVariance/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffsetVariance/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffsetVariance/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffsetVariance/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffsetVariance/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffsetVariance/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffsetVariance/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/alongTrackOffsetVariance/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/correlationSurfacePeak/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/correlationSurfacePeak/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/correlationSurfacePeak/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/correlationSurfacePeak/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/correlationSurfacePeak/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/correlationSurfacePeak/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/correlationSurfacePeak/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/correlationSurfacePeak/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/correlationSurfacePeak/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/correlationSurfacePeak/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/correlationSurfacePeak/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/crossOffsetVariance/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/crossOffsetVariance/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters^2 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/crossOffsetVariance/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/crossOffsetVariance/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/crossOffsetVariance/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/crossOffsetVariance/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/crossOffsetVariance/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/crossOffsetVariance/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/crossOffsetVariance/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/crossOffsetVariance/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/crossOffsetVariance/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffset/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffset/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffset/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffset/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffset/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffset/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffset/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffset/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffset/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffset/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffset/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffsetVariance/histogramBins`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffsetVariance/histogramDensity`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters^2 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffsetVariance/max_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffsetVariance/mean_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffsetVariance/min_value`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffsetVariance/percentFill`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffsetVariance/percentInf`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffsetVariance/percentNan`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffsetVariance/percentNearZero`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffsetVariance/percentTotalInvalid`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/layer3/slantRangeOffsetVariance/sample_stddev`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters^2 |
|    | _dtype:_ float32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/processing/QASoftwareVersion`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ QA software version used for processing |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/processing/azAndRngOffsetVarianceColorbarMinMax`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ The vmin and vmax values used to generate the plots for the az and slant range variance layers. The square root of these layers (i.e. the standard deviation of the offsets) was computed, clipped to this interval, and then plotted using this interval for the colorbar. If None, the interval was determined based on the units of the input layers: If `meters^2`, then [0.0, 10.0]. If `pixels^2`, then [0.0, 0.1]. Otherwise [0.0, max(sqrt(\<az var layer\>), sqrt(\<rg var layer\>))] |
|    | _units:_ meters |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/processing/browseDecimation`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Decimation strides for the browse image. Format: [\<y decimation\>, \<x decimation\>]. |
|    | _units:_ 1 |
|    | _dtype:_ int64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/processing/crossOffsetVarianceColorbarMinMax`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ The vmin and vmax values to generate the plots for the cross offset variance layer. If None, then the colorbar range was computed based on `crossOffsetVariancePercentileClipped` |
|    | _units:_ meters^2 |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/processing/crossOffsetVariancePercentileClipped`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Percentile range that the cross offset variance raster was clipped to, which determines the colormap interval. Can be superseded by `crossOffsetVarianceColorbarMinMax` |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/processing/quiverPlotColorbarIntervalFrequencyAPolarizationHHLayer1`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Colorbar interval for the slant range and along track offset layers' quiver plot(s). |
|    | _units:_ meters |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/processing/quiverPlotColorbarIntervalFrequencyAPolarizationHHLayer2`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Colorbar interval for the slant range and along track offset layers' quiver plot(s). |
|    | _units:_ meters |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/processing/quiverPlotColorbarIntervalFrequencyAPolarizationHHLayer3`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Colorbar interval for the slant range and along track offset layers' quiver plot(s). |
|    | _units:_ meters |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/processing/runConfigurationContents`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Contents of the run configuration file with parameters used for processing |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/boundingPolygon`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ OGR compatible WKT representing the bounding polygon of the image. Horizontal coordinates are WGS84 longitude followed by latitude (both in degrees), and the vertical coordinate is the height above the WGS84 ellipsoid in meters. The first point corresponds to the start-time, near-range radar coordinate, and the perimeter is traversed in counterclockwise order on the map. This means the traversal order in radar coordinates differs for left-looking and right-looking sensors. The polygon includes the four corners of the radar grid, with equal numbers of points distributed evenly in radar coordinates along each edge |
|    | _epsg:_ EPSG code |
|    | _ogr_geometry:_ polygon |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/compositeReleaseId`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Unique version identifier of the science data production system |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/diagnosticModeFlag`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Indicates if the radar operation mode is a diagnostic mode (1-2) or DBFed science (0): 0, 1, or 2 |
|    | _dtype:_ uint8 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/frameNumber`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Frame number |
|    | _dtype:_ uint16 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/granuleId`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Unique granule identification name |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/instrumentName`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Name of the instrument used to collect the remote sensing data provided in this product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isDithered`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ "True" if the pulse timing was varied (dithered) during acquisition, "False" otherwise |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isFullFrame`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ "True" if the product fully covers a NISAR frame, "False" if partial coverage |
|    | _frameCoveragePercentage:_ Percentage of NISAR frame containing processed data |
|    | _thresholdPercentage:_ Threshold percentage used to determine if the product is full frame or partial frame |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isGeocoded`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Flag to indicate if the product data is in the radar geometry ("False") or in the map geometry ("True") |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isMixedMode`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ "True" if this product is generated from reference and secondary RSLCs with different range bandwidths, "False" otherwise |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isUrgentObservation`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Flag indicating if observation is nominal ("False") or urgent ("True") |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/listOfFrequencies`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ List of frequency layers available in the product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/identification/lookDirection`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Look direction, either "Left" or "Right" |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/missionId`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Mission identifier |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/orbitPassDirection`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Orbit direction, either "Ascending" or "Descending" |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/plannedDatatakeId`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ List of planned datatakes included in the product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/identification/plannedObservationId`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ List of planned observations included in the product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/identification/platformName`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Name of the platform used to collect the remote sensing data provided in this product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/processingCenter`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Data processing center |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/processingDateTime`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/processingType`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Nominal (or) Urgent (or) Custom (or) Undefined |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productDoi`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Digital Object Identifier (DOI) for the product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productLevel`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Product level. L0A: Unprocessed instrument data; L0B: Reformatted, unprocessed instrument data; L1: Processed instrument data in radar coordinates system; and L2: Processed instrument data in geocoded coordinates system |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productSpecificationVersion`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Product specification version which represents the schema of this product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productType`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Product type |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productVersion`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Product version which represents the structure of the product and the science content governed by the algorithm, input data, and processing parameters |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/radarBand`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Acquired frequency band, either "L" or "S" |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/referenceAbsoluteOrbitNumber`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Absolute orbit number for the reference RSLC |
|    | _dtype:_ uint32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/referenceIsJointObservation`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ "True" if any portion of the reference RSLC was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/referenceZeroDopplerEndTime`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Azimuth stop time (in UTC) of reference RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/referenceZeroDopplerStartTime`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Azimuth start time (in UTC) of reference RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/secondaryAbsoluteOrbitNumber`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Absolute orbit number for the secondary RSLC |
|    | _dtype:_ uint32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/secondaryIsJointObservation`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ "True" if any portion of the secondary RSLC was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/secondaryZeroDopplerEndTime`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Azimuth stop time (in UTC) of secondary RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/secondaryZeroDopplerStartTime`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Azimuth start time (in UTC) of secondary RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/trackNumber`** |
|    | _Product type:_ ROFF QA |
|    | _description:_ Track number |
|    | _dtype:_ uint32 |
|    | _ndim:_ scalar |


