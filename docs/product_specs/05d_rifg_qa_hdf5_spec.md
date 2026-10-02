
## RIFG QA HDF5 Contents

Each QA HDF5 file includes a subset of the available options below, which will correspond to the available frequencies, polarizations, etc. in the input RIFG granule.

* Possible Frequency groups: `frequencyA`

* Possible Polarization groups: `HH`, `VV`, `HV`, `VH`


|     | RIFG QA HDF5 Datasets, Attributes, and Additional Metadata |
| :---: | --------------------------------------- |
| Path | **`/` _(Root Group - Global Attributes)_** |
|    | _contact:_ nisar-sds-ops@jpl.nasa.gov |
|    | _institution:_ NASA JPL |
|    | _mission_name:_ NISAR |
|    | _reference_document:_ D-107726 NASA SDS Product Specification for Level-1 and Level-2 Quality Assurance |
|    | _title:_ NISAR Quality Assurance Statistical Summary of RIFG HDF5 Product |
|     |     |    |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/histogramBins`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/histogramDensity`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/max_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/mean_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/min_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentFill`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentInf`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentNan`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentNearZero`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/percentTotalInvalid`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/coherenceMagnitude/sample_stddev`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/histogramBins`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/histogramDensity`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/max_imag_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the imaginary component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/max_real_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the real component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/mean_imag_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the imaginary component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/mean_real_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the real component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/min_imag_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the imaginary component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/min_real_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the real component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/percentFill`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: (nan+nanj). |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/percentInf`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/percentNan`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/percentNearZero`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/percentTotalInvalid`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/sample_stddev_imag`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the imaginary component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/interferogram/HH/wrappedInterferogram/sample_stddev_real`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the real component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/listOfPolarizations`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ Polarizations for Frequency A. |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/histogramBins`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/histogramDensity`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/max_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/mean_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/min_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentFill`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentInf`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentNan`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentNearZero`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/percentTotalInvalid`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/alongTrackOffset/sample_stddev`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/histogramBins`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/histogramDensity`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/max_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/mean_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/min_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentFill`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentInf`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentNan`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentNearZero`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/percentTotalInvalid`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, fill, or near-zero valued pixels. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/correlationSurfacePeak/sample_stddev`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/histogramBins`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** float32 |
|    | _description:_ Histogram bin edges |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/histogramDensity`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the histogram |
|    | _units:_ 1/meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/max_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/mean_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/min_value`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentFill`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements containing the fill value, which is: nan. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentInf`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a +/- inf value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentNan`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements with a NaN value. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentNearZero`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are within 1e-06 of zero. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/percentTotalInvalid`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Percent of dataset elements that are either NaN, Inf, or fill valued pixels. (Near-zero valued pixels are not included.) |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/pixelOffsets/HH/slantRangeOffset/sample_stddev`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** float32 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ meters |
| Path | **`science/LSAR/QA/processing/QAProcessingDateTime`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ QA processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
| Path | **`science/LSAR/QA/processing/QASoftwareVersion`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ QA software version used for processing |
| Path | **`science/LSAR/QA/processing/runConfigurationContents`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Contents of the run configuration file with parameters used for QA processing |
| Path | **`science/LSAR/identification/boundingPolygon`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ OGR compatible WKT representing the bounding polygon of the image. Horizontal coordinates are WGS84 longitude followed by latitude (both in degrees), and the vertical coordinate is the height above the WGS84 ellipsoid in meters. The first point corresponds to the start-time, near-range radar coordinate, and the perimeter is traversed in counterclockwise order on the map. This means the traversal order in radar coordinates differs for left-looking and right-looking sensors. The polygon includes the four corners of the radar grid, with equal numbers of points distributed evenly in radar coordinates along each edge |
|    | _epsg:_ EPSG code |
|    | _ogr_geometry:_ polygon |
| Path | **`science/LSAR/identification/compositeReleaseId`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Unique version identifier of the science data production system |
| Path | **`science/LSAR/identification/diagnosticModeFlag`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** uint8 |
|    | _description:_ Indicates if the radar operation mode is a diagnostic mode (1-2) or DBFed science (0): 0, 1, or 2 |
| Path | **`science/LSAR/identification/frameNumber`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** uint16 |
|    | _description:_ Frame number |
| Path | **`science/LSAR/identification/granuleId`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Unique granule identification name |
| Path | **`science/LSAR/identification/instrumentName`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Name of the instrument used to collect the remote sensing data provided in this product |
| Path | **`science/LSAR/identification/isDithered`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if the pulse timing was varied (dithered) during acquisition, "False" otherwise |
| Path | **`science/LSAR/identification/isFullFrame`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if the product fully covers a NISAR frame, "False" if partial coverage |
|    | _frameCoveragePercentage:_ Percentage of NISAR frame containing processed data |
|    | _thresholdPercentage:_ Threshold percentage used to determine if the product is full frame or partial frame |
| Path | **`science/LSAR/identification/isGeocoded`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Flag to indicate if the product data is in the radar geometry ("False") or in the map geometry ("True") |
| Path | **`science/LSAR/identification/isMixedMode`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if this product is generated from reference and secondary RSLCs with different range bandwidths, "False" otherwise |
| Path | **`science/LSAR/identification/isUrgentObservation`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Flag indicating if observation is nominal ("False") or urgent ("True") |
| Path | **`science/LSAR/identification/listOfFrequencies`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of frequency layers available in the product |
| Path | **`science/LSAR/identification/lookDirection`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Look direction, either "Left" or "Right" |
| Path | **`science/LSAR/identification/missionId`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Mission identifier |
| Path | **`science/LSAR/identification/orbitPassDirection`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Orbit direction, either "Ascending" or "Descending" |
| Path | **`science/LSAR/identification/plannedDatatakeId`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of planned datatakes included in the product |
| Path | **`science/LSAR/identification/plannedObservationId`** |
|    | RIFG QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of planned observations included in the product |
| Path | **`science/LSAR/identification/platformName`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Name of the platform used to collect the remote sensing data provided in this product |
| Path | **`science/LSAR/identification/processingCenter`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Data processing center |
| Path | **`science/LSAR/identification/processingDateTime`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
| Path | **`science/LSAR/identification/processingType`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Nominal (or) Urgent (or) Custom (or) Undefined |
| Path | **`science/LSAR/identification/productDoi`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Digital Object Identifier (DOI) for the product |
| Path | **`science/LSAR/identification/productLevel`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product level. L0A: Unprocessed instrument data; L0B: Reformatted, unprocessed instrument data; L1: Processed instrument data in radar coordinates system; and L2: Processed instrument data in geocoded coordinates system |
| Path | **`science/LSAR/identification/productSpecificationVersion`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product specification version which represents the schema of this product |
| Path | **`science/LSAR/identification/productType`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product type |
| Path | **`science/LSAR/identification/productVersion`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product version which represents the structure of the product and the science content governed by the algorithm, input data, and processing parameters |
| Path | **`science/LSAR/identification/radarBand`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Acquired frequency band, either "L" or "S" |
| Path | **`science/LSAR/identification/referenceAbsoluteOrbitNumber`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Absolute orbit number for the reference RSLC |
| Path | **`science/LSAR/identification/referenceIsJointObservation`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if any portion of the reference RSLC was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
| Path | **`science/LSAR/identification/referenceZeroDopplerEndTime`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth stop time (in UTC) of reference RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/referenceZeroDopplerStartTime`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth start time (in UTC) of reference RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/secondaryAbsoluteOrbitNumber`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Absolute orbit number for the secondary RSLC |
| Path | **`science/LSAR/identification/secondaryIsJointObservation`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if any portion of the secondary RSLC was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
| Path | **`science/LSAR/identification/secondaryZeroDopplerEndTime`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth stop time (in UTC) of secondary RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/secondaryZeroDopplerStartTime`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth start time (in UTC) of secondary RSLC product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/trackNumber`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Track number |
| Path | **`science/LSAR/sourceData/runConfigurationContents`** |
|    | RIFG QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Contents of the run configuration file associated with the processing of the source data |


