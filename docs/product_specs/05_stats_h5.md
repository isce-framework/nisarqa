
# Statistical Summary (QA HDF5)

The QA HDF5 file (See Appendix A [RD1]) contains a variety of metadata about the 
input L1/L2 granule, including:

* Statistics and metrics of the layers and datasets.
* The computed arrays used to generate the histograms and other 
plots in the QA report PDF.
* A copy of the final QA runconfig YAML, with all default values populated.
    - Additional processing parameters dynamically calculated and/or used
    by QA are provided as separate metadata.
* A copy of the input granule's `runConfigurationContents` dataset.
   - Note: QA copies this dataset's contents as-is, with no further processing. 
   The format (e.g. JSON, YAML) may differ depending on the L1/L2 product type.
* A copy of the input L1/L2 granule's `identification` group
    - Note: The QA HDF5's `/science/LSAR/identification/` group 
      is a copy of the input L1/L2 granule's group.
    - For the QA-specific software version, processing datetime, and 
      run configuration contents, please see the 
      `/science/LSAR/QA/processing/` group.

The contents of the QA HDF5 for each L1/L2 product type are documented in the 
subsequent subsections.

The top of each subsection notes all possible frequencies, polarizations, 
covariance terms, etc. which could appear in QA HDF5s for that particular 
product type. The tables in each subsection note all possible datasets 
that could appear; for brevity of the documentation, only one
combination of frequency/polarization/etc. for each dataset is included.

The final contents of each QA HDF5 reflect the contents of its 
input L1/L2 granule.

For example:
  * If the input granule contains data for Frequency A and Frequency B, 
  then the QA HDF5 will similarly contain data for Frequency A and Frequency B. 
  * If the input granule does not include VV polarization, then the QA HDF5
  will similarly not contain VV polarization.
  * If the input RSLC granule is not over a designated calibration site,
  then there will be no results from the PTA and AbsCal calibration tools.

