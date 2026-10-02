
## RSLC QA HDF5 Contents

Each QA HDF5 file includes a subset of the available options below, which will correspond to the available frequencies, polarizations, etc. in the input RSLC granule.

* Possible Frequency groups: `frequencyA`, `frequencyB`

* Possible Polarization groups: `HH`, `VV`, `HV`, `VH`, `RH`, `RV`, `LH`, `LV`

* Possible CalTools groups: `pointTargetAnalyzer`, `absoluteRadiometricCalibration`, `noiseEquivalentBackscatter`
   - Note: PTA and AbsCal results only possible for granules over designated calibration sites.


|     | RSLC QA HDF5 Datasets, Attributes, and Additional Metadata |
| :---: | --------------------------------------- |
| Path | **`/` _(Root Group - Global Attributes)_** |
|    | _contact:_ nisar-sds-ops@jpl.nasa.gov |
|    | _institution:_ NASA JPL |
|    | _mission_name:_ NISAR |
|    | _reference_document:_ D-107726 NASA SDS Product Specification for Level-1 and Level-2 Quality Assurance |
|    | _title:_ NISAR Quality Assurance Statistical Summary of RSLC HDF5 Product |
|     |     |    |
| Path | **`science/LSAR/QA/data/azimuthSpectraFrequencies`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Frequency coordinates for azimuth power spectra. |
|    | _units:_ hertz |
| Path | **`science/LSAR/QA/data/frequencyA/HH/azimuthPowerSpectralDensityFarRange`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized azimuth power spectral density for Frequency A, Polarization HH Far-Range. |
|    | _subswathStartIndex:_ Starting index for the subswath used to generate this plot |
|    | _subswathStopIndex:_ Stopping index for the subswath used to generate this plot |
|    | _units:_ decibel re 1/hertz |
| Path | **`science/LSAR/QA/data/frequencyA/HH/azimuthPowerSpectralDensityMidRange`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized azimuth power spectral density for Frequency A, Polarization HH Mid-Range. |
|    | _subswathStartIndex:_ Starting index for the subswath used to generate this plot |
|    | _subswathStopIndex:_ Stopping index for the subswath used to generate this plot |
|    | _units:_ decibel re 1/hertz |
| Path | **`science/LSAR/QA/data/frequencyA/HH/azimuthPowerSpectralDensityNearRange`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized azimuth power spectral density for Frequency A, Polarization HH Near-Range. |
|    | _subswathStartIndex:_ Starting index for the subswath used to generate this plot |
|    | _subswathStopIndex:_ Stopping index for the subswath used to generate this plot |
|    | _units:_ decibel re 1/hertz |
| Path | **`science/LSAR/QA/data/frequencyA/HH/backscatterHistogramDensity`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the backscatter image histogram |
|    | _units:_ 1/dB |
| Path | **`science/LSAR/QA/data/frequencyA/HH/max_imag_value`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Maximum value of the imaginary component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/HH/max_real_value`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Maximum value of the real component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/HH/mean_imag_value`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Arithmetic average of the imaginary component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/HH/mean_real_value`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Arithmetic average of the real component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/HH/min_imag_value`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Minimum value of the imaginary component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/HH/min_real_value`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Minimum value of the real component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/HH/phaseHistogramDensity`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized density of the phase histogram |
|    | _units:_ 1/radians |
| Path | **`science/LSAR/QA/data/frequencyA/HH/rangePowerSpectralDensity`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Normalized range power spectral density for Frequency A, Polarization HH. |
|    | _units:_ decibel re 1/hertz |
| Path | **`science/LSAR/QA/data/frequencyA/HH/sample_stddev_imag`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Standard deviation of the imaginary component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/HH/sample_stddev_real`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Standard deviation of the real component of the numeric data points |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/data/frequencyA/listOfPolarizations`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ Polarizations for Frequency A discovered in input NISAR product by QA code |
| Path | **`science/LSAR/QA/data/frequencyA/rangeSpectraFrequencies`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Frequency coordinates for Frequency A range power spectra. |
|    | _units:_ megahertz |
| Path | **`science/LSAR/QA/processing/QAProcessingDateTime`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ QA processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
| Path | **`science/LSAR/QA/processing/QASoftwareVersion`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ QA software version used for processing |
| Path | **`science/LSAR/QA/processing/azimuthSpectraColumnsPerSubswath`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ Number of columns (i.e. range samples) used to compute the azimuth spectra for each subswath (near-range, mid-range, and far-range). |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/backscatterImageGammaCorrection`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Gamma correction parameter applied to backscatter and browse image(s). Dataset will be type float if gamma was applied, otherwise it is the string 'None' |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/backscatterImageNlooksFreqA`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** int64 |
|    | _description:_ Number of looks along [\<azimuth\>,\<range\>] axes of Frequency A image arrays for multilooking the backscatter and browse images. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/backscatterImagePercentileClipped`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Percentile range that the image array was clipped to and that the colormap covers |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/backscatterImageUnits`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Units of the backscatter image. |
| Path | **`science/LSAR/QA/processing/histogramDecimationRatio`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** int64 |
|    | _description:_ Image decimation strides used to compute backscatter and phase histograms. Format: [\<azimuth\>, \<range\>] |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/histogramEdgesBackscatter`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Bin edges (including endpoint) for backscatter histogram |
|    | _units:_ dB |
| Path | **`science/LSAR/QA/processing/histogramEdgesPhase`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Bin edges (including endpoint) for phase histogram |
|    | _units:_ radians |
| Path | **`science/LSAR/QA/processing/rangeSpectraDecimationAlongAzimuth`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ Decimation stride along the azimuth axis used to compute the range spectra. |
|    | _units:_ 1 |
| Path | **`science/LSAR/QA/processing/runConfigurationContents`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Contents of the run configuration file with parameters used for QA processing |
| Path | **`science/LSAR/RFI/data/frequencyA/HH/rfiLikelihood`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Severity of radio frequency interference (RFI) contamination in the data. Value is in the interval [0,1], where 0: lowest severity, and 1: highest severity (or NaN if RFI detection was skipped) |
|    | _units:_ 1 |
| Path | **`science/LSAR/absoluteRadiometricCalibration/data/frequencyA/HH/absoluteCalibrationFactor`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The absolute radiometric calibration error for the corner reflector (the ratio of the measured RCS to the predicted RCS), in linear units |
|    | _units:_ 1 |
| Path | **`science/LSAR/absoluteRadiometricCalibration/data/frequencyA/HH/cornerReflectorId`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ The unique identifier of the corner reflector |
| Path | **`science/LSAR/absoluteRadiometricCalibration/data/frequencyA/HH/cornerReflectorSurveyDate`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ The date (and time) when the corner reflector was surveyed most recently prior to the radar observation, as a string in ISO 8601 format |
| Path | **`science/LSAR/absoluteRadiometricCalibration/data/frequencyA/HH/cornerReflectorVelocity`** |
|    | RSLC QA dataset, **ndim:** 2-D array, **dtype:** float64 |
|    | _description:_ The corner reflector velocity due to tectonic plate motion, as an East-North-Up (ENU) vector in meters per second (m/s). The velocity components are provided in local ENU coordinates with respect to the WGS 84 reference ellipsoid |
|    | _units:_ meters per second |
| Path | **`science/LSAR/absoluteRadiometricCalibration/data/frequencyA/HH/elevationAngle`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Antenna elevation angle, in radians, measured w.r.t. antenna boresight, increasing toward the far-range direction and decreasing (becoming negative) toward the near-range direction |
|    | _units:_ radians |
| Path | **`science/LSAR/absoluteRadiometricCalibration/data/frequencyA/HH/radarObservationDate`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ The radar observation date and time of the corner reflector in UTC, as a string in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/absoluteRadiometricCalibration/processing/numSamplesChip`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ The width, in samples, of the square block of image data centered around the target position used for oversampling and peak finding. |
|    | _units:_ samples |
| Path | **`science/LSAR/absoluteRadiometricCalibration/processing/numSamplesFit`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ The width, in *oversampled* samples, of the square sub-block of image data centered around the target position used for fitting a quadratic polynomial to the peak. |
|    | _units:_ samples |
| Path | **`science/LSAR/absoluteRadiometricCalibration/processing/peakFindDomain`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Option controlling how the target peak position was estimated. |
| Path | **`science/LSAR/absoluteRadiometricCalibration/processing/powerMethod`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Method used to estimate the target signal power. |
| Path | **`science/LSAR/absoluteRadiometricCalibration/processing/powerThreshold`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ The minimum power threshold, measured in dB below the peak power, used to estimate the target signal power if the integrated power method was used. |
|    | _units:_ dB |
| Path | **`science/LSAR/absoluteRadiometricCalibration/processing/upsampleFactor`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ The upsampling ratio. |
|    | _units:_ 1 |
| Path | **`science/LSAR/identification/absoluteOrbitNumber`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Absolute orbit number |
| Path | **`science/LSAR/identification/boundingPolygon`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ OGR compatible WKT representing the bounding polygon of the image. Horizontal coordinates are WGS84 longitude followed by latitude (both in degrees), and the vertical coordinate is the height above the WGS84 ellipsoid in meters. The first point corresponds to the start-time, near-range radar coordinate, and the perimeter is traversed in counterclockwise order on the map. This means the traversal order in radar coordinates differs for left-looking and right-looking sensors. The polygon includes the four corners of the radar grid, with equal numbers of points distributed evenly in radar coordinates along each edge |
|    | _epsg:_ EPSG code |
|    | _ogr_geometry:_ polygon |
| Path | **`science/LSAR/identification/compositeReleaseId`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Unique version identifier of the science data production system |
| Path | **`science/LSAR/identification/diagnosticModeFlag`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** uint8 |
|    | _description:_ Indicates if the radar operation mode is a diagnostic mode (1-2) or DBFed science (0): 0, 1, or 2 |
| Path | **`science/LSAR/identification/frameNumber`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** uint16 |
|    | _description:_ Frame number |
| Path | **`science/LSAR/identification/granuleId`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Unique granule identification name |
| Path | **`science/LSAR/identification/instrumentName`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Name of the instrument used to collect the remote sensing data provided in this product |
| Path | **`science/LSAR/identification/isDithered`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if the pulse timing was varied (dithered) during acquisition, "False" otherwise. |
| Path | **`science/LSAR/identification/isFullFrame`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if the product fully covers a NISAR frame, "False" if partial coverage |
|    | _frameCoveragePercentage:_ Percentage of NISAR frame containing processed data |
|    | _thresholdPercentage:_ Threshold percentage used to determine if the product is full frame or partial frame |
| Path | **`science/LSAR/identification/isGeocoded`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Flag to indicate if the product data is in the radar geometry ("False") or in the map geometry ("True") |
| Path | **`science/LSAR/identification/isJointObservation`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if any portion of this product was acquired in a joint observation mode (e.g., L-band and S-band simultaneously), "False" otherwise |
| Path | **`science/LSAR/identification/isMixedMode`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ "True" if this product is a composite of data collected in multiple radar modes, "False" otherwise. |
| Path | **`science/LSAR/identification/isUrgentObservation`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Flag indicating if observation is nominal ("False") or urgent ("True") |
| Path | **`science/LSAR/identification/listOfFrequencies`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of frequency layers available in the product |
| Path | **`science/LSAR/identification/lookDirection`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Look direction, either "Left" or "Right" |
| Path | **`science/LSAR/identification/missionId`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Mission identifier |
| Path | **`science/LSAR/identification/orbitPassDirection`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Orbit direction, either "Ascending" or "Descending" |
| Path | **`science/LSAR/identification/plannedDatatakeId`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of planned datatakes included in the product |
| Path | **`science/LSAR/identification/plannedObservationId`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ List of planned observations included in the product |
| Path | **`science/LSAR/identification/processingCenter`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Data processing center |
| Path | **`science/LSAR/identification/processingDateTime`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Processing date and time (in UTC) in the format YYYY-mm-ddTHH:MM:SS |
| Path | **`science/LSAR/identification/processingType`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Nominal (or) Urgent (or) Custom (or) Undefined |
| Path | **`science/LSAR/identification/productDoi`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Digital Object Identifier (DOI) for the product |
| Path | **`science/LSAR/identification/productLevel`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product level. L0A: Unprocessed instrument data; L0B: Reformatted, unprocessed instrument data; L1: Processed instrument data in radar coordinates system; and L2: Processed instrument data in geocoded coordinates system |
| Path | **`science/LSAR/identification/productSpecificationVersion`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product specification version which represents the schema of this product |
| Path | **`science/LSAR/identification/productType`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product type |
| Path | **`science/LSAR/identification/productVersion`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Product version which represents the structure of the product and the science content governed by the algorithm, input data, and processing parameters |
| Path | **`science/LSAR/identification/radarBand`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Acquired frequency band, either "L" or "S" |
| Path | **`science/LSAR/identification/trackNumber`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** uint32 |
|    | _description:_ Track number |
| Path | **`science/LSAR/identification/zeroDopplerEndTime`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth stop time (in UTC) of the product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/identification/zeroDopplerStartTime`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Azimuth start time (in UTC) of the product in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/noiseEquivalentBackscatter/data/frequencyA/HH`** |
|    | RSLC QA dataset, **ndim:** 2-D array, **dtype:** float32 |
|    | _description:_ Noise equivalent backscatter in linear scale (units of DN^2) |
|    | _units:_ 1 |
| Path | **`science/LSAR/noiseEquivalentBackscatter/data/frequencyA/slantRange`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Slant range dimension corresponding to calibration noiseEquivalentBackscatter records |
|    | _units:_ meters |
| Path | **`science/LSAR/noiseEquivalentBackscatter/data/frequencyA/zeroDopplerTime`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Zero Doppler time since UTC epoch dimension corresponding to calibration noiseEquivalentBackscatter records |
|    | _units:_ seconds since YYYY-mm-ddTHH:MM:SS |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/azimuthIRF/ISLR`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The integrated sidelobe ratio (ISLR) of the azimuth impulse response function (IRF), in decibels (dB). A measure of the ratio of energy in the sidelobes to the energy in the main lobe. If `predict_null` was true, the first sidelobe will be considered part of the main lobe and the ISLR will instead measure the ratio of energy in the remaining sidelobes to the energy in the main lobe + first sidelobe |
|    | _units:_ 1 |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/azimuthIRF/PSLR`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The peak-to-sidelobe ratio (PSLR) of the azimuth impulse response function (IRF), in decibels (dB). A measure of the ratio of peak sidelobe power to the peak main lobe power |
|    | _units:_ 1 |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/azimuthIRF/cut/index`** |
|    | RSLC QA dataset, **ndim:** 2-D array, **dtype:** float64 |
|    | _description:_ The azimuth sample indices of the magnitude and phase cut values |
|    | _units:_ samples |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/azimuthIRF/cut/magnitude`** |
|    | RSLC QA dataset, **ndim:** 2-D array, **dtype:** float64 |
|    | _description:_ The magnitude of the (upsampled) impulse response function (IRF) in azimuth |
|    | _units:_ 1 |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/azimuthIRF/cut/phase`** |
|    | RSLC QA dataset, **ndim:** 2-D array, **dtype:** float64 |
|    | _description:_ The phase of the (upsampled) impulse response function (IRF) in azimuth |
|    | _units:_ radians |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/azimuthIRF/resolution`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The measured 3dB width of the azimuth impulse response function (IRF), in samples |
|    | _units:_ samples |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/azimuthPosition/peakIndex`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The real-valued azimuth index, in samples, of the estimated peak location of the impulse response function (IRF) within the RSLC image grid |
|    | _units:_ samples |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/azimuthPosition/peakOffset`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The error in the predicted target location in the azimuth direction, in samples. Equal to the signed difference between the measured location of the impulse response peak in the RSLC data and the predicted location of the peak based on the surveyed corner reflector location |
|    | _units:_ samples |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/azimuthPosition/phaseSlope`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The estimated local azimuth phase slope at the target location, in radians per sample |
|    | _units:_ radians per sample |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/cornerReflectorId`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ The unique identifier of the corner reflector |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/cornerReflectorSurveyDate`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ The date (and time) when the corner reflector was surveyed most recently prior to the radar observation, as a string in ISO 8601 format |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/cornerReflectorValidity`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** int64 |
|    | _description:_ The integer validity code of the corner reflector. Refer to the NISAR Corner Reflector Software Interface Specification (SIS) document for details |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/cornerReflectorVelocity`** |
|    | RSLC QA dataset, **ndim:** 2-D array, **dtype:** float64 |
|    | _description:_ The corner reflector velocity due to tectonic plate motion, as an East-North-Up (ENU) vector in meters per second (m/s). The velocity components are provided in local ENU coordinates with respect to the WGS 84 reference ellipsoid |
|    | _units:_ meters per second |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/elevationAngle`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ Antenna elevation angle, in radians, measured w.r.t. antenna boresight, increasing toward the far-range direction and decreasing (becoming negative) toward the near-range direction |
|    | _units:_ radians |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/peakMagnitude`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The peak magnitude of the impulse response |
|    | _units:_ 1 |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/peakPhase`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The phase at the peak location, in radians |
|    | _units:_ radians |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/radarObservationDate`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** fixed-length byte string |
|    | _description:_ The radar observation date and time of the corner reflector in UTC, as a string in the format YYYY-mm-ddTHH:MM:SS.sssssssss |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/rangeIRF/ISLR`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The integrated sidelobe ratio (ISLR) of the range impulse response function (IRF), in decibels (dB). A measure of the ratio of energy in the sidelobes to the energy in the main lobe. If `predict_null` was true, the first sidelobe will be considered part of the main lobe and the ISLR will instead measure the ratio of energy in the remaining sidelobes to the energy in the main lobe + first sidelobe |
|    | _units:_ 1 |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/rangeIRF/PSLR`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The peak-to-sidelobe ratio (PSLR) of the range impulse response function (IRF), in decibels (dB). A measure of the ratio of peak sidelobe power to the peak main lobe power |
|    | _units:_ 1 |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/rangeIRF/cut/index`** |
|    | RSLC QA dataset, **ndim:** 2-D array, **dtype:** float64 |
|    | _description:_ The range sample indices of the magnitude and phase cut values |
|    | _units:_ samples |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/rangeIRF/cut/magnitude`** |
|    | RSLC QA dataset, **ndim:** 2-D array, **dtype:** float64 |
|    | _description:_ The magnitude of the (upsampled) impulse response function (IRF) in range |
|    | _units:_ 1 |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/rangeIRF/cut/phase`** |
|    | RSLC QA dataset, **ndim:** 2-D array, **dtype:** float64 |
|    | _description:_ The phase of the (upsampled) impulse response function (IRF) in range |
|    | _units:_ radians |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/rangeIRF/resolution`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The measured 3dB width of the range impulse response function (IRF), in samples |
|    | _units:_ samples |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/rangePosition/peakIndex`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The real-valued range index, in samples, of the estimated peak location of the impulse response function (IRF) within the RSLC image grid |
|    | _units:_ samples |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/rangePosition/peakOffset`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The error in the predicted target location in the range direction, in samples. Equal to the signed difference between the measured location of the impulse response peak in the RSLC data and the predicted location of the peak based on the surveyed corner reflector location |
|    | _units:_ samples |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/HH/rangePosition/phaseSlope`** |
|    | RSLC QA dataset, **ndim:** 1-D array, **dtype:** float64 |
|    | _description:_ The estimated local range phase slope at the target location, in radians per sample |
|    | _units:_ radians per sample |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/sceneCenterAlongTrackSpacing`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Nominal along track spacing in meters between consecutive lines near mid swath of the RSLC image |
|    | _units:_ meters |
| Path | **`science/LSAR/pointTargetAnalyzer/data/frequencyA/slantRangeSpacing`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Slant range spacing of grid |
|    | _units:_ meters |
| Path | **`science/LSAR/pointTargetAnalyzer/processing/numSamplesChip`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ The width, in samples, of the square block of image data centered around the target position used for oversampling and peak finding. |
|    | _units:_ samples |
| Path | **`science/LSAR/pointTargetAnalyzer/processing/numSidelobesISLR`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ The number of sidelobes, including the main lobe, used to compute the integrated sidelobe ratio (ISLR). |
| Path | **`science/LSAR/pointTargetAnalyzer/processing/peakFindDomain`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Option controlling how the target peak position was estimated. |
| Path | **`science/LSAR/pointTargetAnalyzer/processing/predictNullISLR`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ How the main lobe null locations were determined for ISLR computation. If True, the main lobe was considered to include the first sidelobe and the null locations were predicted analytically. Otherwise, the main lobe null locations were estimated from the RSLC data. |
| Path | **`science/LSAR/pointTargetAnalyzer/processing/samplingRateBandwidthRatio`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Assumed ratio of sampling rate to bandwidth in the RSLC image data. |
|    | _units:_ 1 |
| Path | **`science/LSAR/pointTargetAnalyzer/processing/upsampleFactor`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** int64 |
|    | _description:_ The upsampling ratio. |
|    | _units:_ 1 |
| Path | **`science/LSAR/pointTargetAnalyzer/processing/windowShape`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** float64 |
|    | _description:_ Assumed window shape parameter used in RSLC formation. |
|    | _units:_ 1 |
| Path | **`science/LSAR/pointTargetAnalyzer/processing/windowType`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Assumed window type used in RSLC formation. |
| Path | **`science/LSAR/sourceData/runConfigurationContents`** |
|    | RSLC QA dataset, **ndim:** scalar, **dtype:** fixed-length byte string |
|    | _description:_ Contents of the run configuration file associated with the processing of the source data |


