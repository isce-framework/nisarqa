
## GCOV QA HDF5 Contents

Each QA HDF5 file includes a subset of the available options below, which will correspond to the available frequencies, polarizations, etc. in the input GCOV granule.

* Possible Frequency groups: `frequencyA`, `frequencyB`

* Possible On- and Off-diagonal Covariance Term groups: `HHHH`, `HVHV`, `VHVH`, `VVVV`, `RHRH`, `RVRV`, `LHLH`, `LVLV`, `HHHV`, `HHVH`, `HHVV`, `HVHH`, `HVVH`, `HVVV`, `VHHH`, `VHHV`, `VHVV`, `VVHH`, `VVHV`, `VVVH`, `RHRV`, `RVRH`, `LHLV`, `LVLH`

* Possible Polarization groups (for e.g. calibration information): `HH`, `HV`, `VH`, `VV`, `RH`, `RV`, `LH`, `LV`, `HH`, `HH`, `HH`, `HV`, `HV`, `HV`, `VH`, `VH`, `VH`, `VV`, `VV`, `VV`, `RH`, `RV`, `LH`, `LV`


|     | GCOV QA HDF5 Datasets, Attributes, and Additional Metadata |
| :---: | --------------------------------------- |
| Path | **`/` _(Root Group - Global Attributes)_** |
|    | _contact:_ nisar-sds-ops@jpl.nasa.gov |
|    | _institution:_ NASA JPL |
|    | _mission_name:_ NISAR |
|    | _reference_document:_ D-107726 NASA SDS Product Specification for Level-1 and Level-2 Quality Assurance |
|    | _title:_ NISAR Quality Assurance Statistical Summary of GCOV HDF5 Product |
|     |     |    |
| Path | **`science/LSAR/QA/data/frequencyA/HHHH/backscatterHistogramDensity`** |
|    | GCOV QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the backscatter image histogram |
|    | _units:_ 1/dB |
| Path | **`science/LSAR/QA/data/frequencyA/HHHH/max_value`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Maximum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/HHHH/mean_value`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Arithmetic average of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/HHHH/min_value`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Minimum value of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/HHHH/sample_stddev`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Standard deviation of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/listOfPolarizations`** |
|    | GCOV QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ Polarizations for Frequency A discovered in input NISAR product by QA code |
| Path | **`science/LSAR/QA/processing/QAProcessingDateTime`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ QA processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
| Path | **`science/LSAR/QA/processing/QASoftwareVersion`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ QA software version used for processing |
| Path | **`science/LSAR/QA/processing/backscatterImageGammaCorrection`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Gamma correction parameter applied to backscatter and browse image(s). Dataset will be type float if gamma was applied, otherwise it is the string 'None' |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/backscatterImageNlooksFreqA`** |
|    | GCOV QA dataset, **ndim:** 1-D array, **dtype:** int64 |
|    | _description:_ Number of looks along [\<Y direction\>,\<X direction\>] axes of Frequency A image arrays for multilooking the backscatter and browse images. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/backscatterImagePercentileClipped`** |
|    | GCOV QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Percentile range that the image array was clipped to and that the colormap covers |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/backscatterImageUnits`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Units of the backscatter image. |
| Path | **`science/LSAR/QA/processing/histogramDecimationRatio`** |
|    | GCOV QA dataset, **ndim:** 1-D array, **dtype:** int64 |
|    | _description:_ Image decimation strides used to compute backscatter and phase histograms. Format: [\<azimuth\>, \<range\>] |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/histogramEdgesBackscatter`** |
|    | GCOV QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Bin edges (including endpoint) for backscatter histogram |
|    | _units:_ dB |
| Path | **`science/LSAR/QA/processing/runConfigurationContents`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Contents of the run configuration file with parameters used for QA processing |
| Path | **`science/LSAR/identification/absoluteOrbitNumber`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Absolute orbit number |
| Path | **`science/LSAR/identification/boundingPolygon`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ OGR compatible WKT representing the bounding polygon of the image. Horizontal coordinates are WGS84 longitude followed by latitude (both in degrees), and the vertical coordinate is the height above the WGS84 ellipsoid in meters. The first point corresponds to the start-time, near-range radar coordinate, and the perimeter is traversed in counterclockwise order on the map. This means the traversal order in radar coordinates differs for left-looking and right-looking sensors. The polygon includes the four corners of the radar grid, with equal numbers of points distributed evenly in radar coordinates along each edge |
|    | _epsg:_ EPSG code |
|    | _ogr_geometry:_ polygon |
| Path | **`science/LSAR/identification/compositeReleaseId`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Unique version identifier of the science data production system |
| Path | **`science/LSAR/identification/diagnosticModeFlag`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** uint8 |
|    | _description:_ Indicates if the radar operation mode is a diagnostic mode (1-2) or DBFed science (0): 0, 1, or 2 |
| Path | **`science/LSAR/identification/frameNumber`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** uint16 |
|    | _description:_ Frame number |
| Path | **`science/LSAR/identification/granuleId`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Unique granule identification name |
| Path | **`science/LSAR/identification/instrumentName`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Name of the instrument used to collect the remote sensing data provided in this product |
| Path | **`science/LSAR/identification/isDithered`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if the pulse timing was varied (dithered) during acquisition, "False" otherwise. |
| Path | **`science/LSAR/identification/isFullFrame`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if the product fully covers a NISAR frame, "False" if partial coverage |
|    | _frameCoveragePercentage:_ Percentage of NISAR frame containing processed data |
|    | _thresholdPercentage:_ Threshold percentage used to determine if the product is full frame or partial frame |
| Path | **`science/LSAR/identification/isGeocoded`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Flag to indicate if the product data is in the radar geometry ("False") or in the map geometry ("True") |
| Path | **`science/LSAR/identification/isJointObservation`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if any portion of this product was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
| Path | **`science/LSAR/identification/isMixedMode`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if this product is a composite of data collected in multiple radar modes, "False" otherwise. |
| Path | **`science/LSAR/identification/isUrgentObservation`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Flag indicating if observation is nominal ("False") or urgent ("True") |
| Path | **`science/LSAR/identification/listOfFrequencies`** |
|    | GCOV QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of frequency layers available in the product |
| Path | **`science/LSAR/identification/lookDirection`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Look direction, either "Left" or "Right" |
| Path | **`science/LSAR/identification/missionId`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Mission identifier |
| Path | **`science/LSAR/identification/orbitPassDirection`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Orbit direction, either "Ascending" or "Descending" |
| Path | **`science/LSAR/identification/plannedDatatakeId`** |
|    | GCOV QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of planned datatakes included in the product |
| Path | **`science/LSAR/identification/plannedObservationId`** |
|    | GCOV QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of planned observations included in the product |
| Path | **`science/LSAR/identification/platformName`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Name of the platform used to collect the remote sensing data provided in this product |
| Path | **`science/LSAR/identification/processingCenter`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Data processing center |
| Path | **`science/LSAR/identification/processingDateTime`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
| Path | **`science/LSAR/identification/processingType`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Nominal (or) Urgent (or) Custom (or) Undefined |
| Path | **`science/LSAR/identification/productDoi`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Digital Object Identifier (DOI) for the product |
| Path | **`science/LSAR/identification/productLevel`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product level. L0A: Unprocessed instrument data; L0B: Reformatted, unprocessed instrument data; L1: Processed instrument data in radar coordinates system; and L2: Processed instrument data in geocoded coordinates system |
| Path | **`science/LSAR/identification/productSpecificationVersion`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product specification version which represents the schema of this product |
| Path | **`science/LSAR/identification/productType`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product type |
| Path | **`science/LSAR/identification/productVersion`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product version which represents the structure of the product and the science content governed by the algorithm, input data, and processing parameters |
| Path | **`science/LSAR/identification/radarBand`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Acquired frequency band, either "L" or "S" |
| Path | **`science/LSAR/identification/trackNumber`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Track number |
| Path | **`science/LSAR/identification/zeroDopplerEndTime`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth stop time (in UTC) of the product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/zeroDopplerStartTime`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth start time (in UTC) of the product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/sourceData/runConfigurationContents`** |
|    | GCOV QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Contents of the run configuration file associated with the processing of the source data |


