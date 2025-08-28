
## GSLC QA HDF5 Contents

Each QA HDF5 file includes a subset of the available options below, which will correspond to the available frequencies, polarizations, etc. in the input GSLC product.

* Possible Frequency Groups: `frequencyA`, `frequencyB`

* Possible Polarization Groups: `HH`, `VV`, `HV`, `VH`, `RH`, `RV`, `LH`, `LV`

* Possible CalTools groups: `pointTargetAnalyzer`


|     | GSLC QA HDF5 Dataset, Attributes, and additional metadata |
| :---: | --------------------------------------- |
| Path: | **`science/LSAR/QA/data/frequencyA/HH/backscatterHistogramDensity`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Normalized density of the backscatter image histogram |
|    | _units:_ 1/dB |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/HH/max_imag_value`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Maximum value of the imaginary component of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/HH/max_real_value`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Maximum value of the real component of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/HH/mean_imag_value`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Arithmetic average of the imaginary component of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/HH/mean_real_value`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Arithmetic average of the real component of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/HH/min_imag_value`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Minimum value of the imaginary component of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/HH/min_real_value`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Minimum value of the real component of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/HH/phaseHistogramDensity`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Normalized density of the phase histogram |
|    | _units:_ 1/radians |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/data/frequencyA/HH/sample_stddev_imag`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Standard deviation of the imaginary component of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/HH/sample_stddev_real`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Standard deviation of the real component of the numeric data points |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/data/frequencyA/listOfPolarizations`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Polarizations for Frequency A discovered in input NISAR product by QA code |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/processing/QASoftwareVersion`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ QA software version used for processing |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/processing/backscatterImageGammaCorrection`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Gamma correction parameter applied to backscatter and browse image(s). Dataset will be type float if gamma was applied, otherwise it is the string 'None' |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/processing/backscatterImageNlooksFreqA`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Number of looks along [\<Y direction\>,\<X direction\>] axes of Frequency A image arrays for multilooking the backscatter and browse images. |
|    | _units:_ 1 |
|    | _dtype:_ int64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/processing/backscatterImagePercentileClipped`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Percentile range that the image array was clipped to and that the colormap covers |
|    | _units:_ 1 |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/processing/backscatterImageUnits`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Units of the backscatter image. |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/QA/processing/histogramDecimationRatio`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Image decimation strides used to compute backscatter and phase histograms. Format: [\<azimuth\>, \<range\>] |
|    | _units:_ 1 |
|    | _dtype:_ int64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/processing/histogramEdgesBackscatter`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Bin edges (including endpoint) for backscatter histogram |
|    | _units:_ dB |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/processing/histogramEdgesPhase`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Bin edges (including endpoint) for phase histogram |
|    | _units:_ radians |
|    | _dtype:_ float64 |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/QA/processing/runConfigurationContents`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Contents of the run configuration file with parameters used for processing |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/absoluteOrbitNumber`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Absolute orbit number |
|    | _dtype:_ uint32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/boundingPolygon`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ OGR compatible WKT representing the bounding polygon of the image. Horizontal coordinates are WGS84 longitude followed by latitude (both in degrees), and the vertical coordinate is the height above the WGS84 ellipsoid in meters. The first point corresponds to the start-time, near-range radar coordinate, and the perimeter is traversed in counterclockwise order on the map. This means the traversal order in radar coordinates differs for left-looking and right-looking sensors. The polygon includes the four corners of the radar grid, with equal numbers of points distributed evenly in radar coordinates along each edge |
|    | _epsg:_ EPSG code |
|    | _ogr_geometry:_ polygon |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/compositeReleaseId`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Unique version identifier of the science data production system |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/diagnosticModeFlag`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Indicates if the radar operation mode is a diagnostic mode (1-2) or DBFed science (0): 0, 1, or 2 |
|    | _dtype:_ uint8 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/frameNumber`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Frame number |
|    | _dtype:_ uint16 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/granuleId`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Unique granule identification name |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/instrumentName`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Name of the instrument used to collect the remote sensing data provided in this product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isDithered`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ "True" if the pulse timing was varied (dithered) during acquisition, "False" otherwise. |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isFullFrame`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ "True" if the product fully covers a NISAR frame, "False" if partial coverage |
|    | _frameCoveragePercentage:_ Percentage of NISAR frame containing processed data |
|    | _thresholdPercentage:_ Threshold percentage used to determine if the product is full frame or partial frame |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isGeocoded`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Flag to indicate if the product data is in the radar geometry ("False") or in the map geometry ("True") |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isJointObservation`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ "True" if any portion of this product was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isMixedMode`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ "True" if this product is a composite of data collected in multiple radar modes, "False" otherwise. |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/isUrgentObservation`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Flag indicating if observation is nominal ("False") or urgent ("True") |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/listOfFrequencies`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ List of frequency layers available in the product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/identification/lookDirection`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Look direction, either "Left" or "Right" |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/missionId`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Mission identifier |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/orbitPassDirection`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Orbit direction, either "Ascending" or "Descending" |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/plannedDatatakeId`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ List of planned datatakes included in the product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/identification/plannedObservationId`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ List of planned observations included in the product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ 1-D array |
| Path: | **`science/LSAR/identification/platformName`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Name of the platform used to collect the remote sensing data provided in this product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/processingCenter`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Data processing center |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/processingDateTime`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/processingType`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Nominal (or) Urgent (or) Custom (or) Undefined |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productDoi`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Digital Object Identifier (DOI) for the product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productLevel`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Product level. L0A: Unprocessed instrument data; L0B: Reformatted, unprocessed instrument data; L1: Processed instrument data in radar coordinates system; and L2: Processed instrument data in geocoded coordinates system |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productSpecificationVersion`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Product specification version which represents the schema of this product |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productType`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Product type |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/productVersion`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Product version which represents the structure of the product and the science content governed by the algorithm, input data, and processing parameters |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/radarBand`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Acquired frequency band, either "L" or "S" |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/trackNumber`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Track number |
|    | _dtype:_ uint32 |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/zeroDopplerEndTime`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Azimuth stop time (in UTC) of the product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |
| Path: | **`science/LSAR/identification/zeroDopplerStartTime`** |
|    | _Product type:_ GSLC QA |
|    | _description:_ Azimuth start time (in UTC) of the product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
|    | _dtype:_ fixed-length byte string |
|    | _ndim:_ scalar |


