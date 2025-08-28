
# Statistical Summary (QA HDF5)

This statistical HDF5 file contains a variety of data, including:

* Statistics and metrics about the layers and datasets in the input L1/L2 granule.
* The computed arrays used to generate the histograms and other plots in the QA report PDF
* The processing parameters used by QA to generate all of the QA outputs
    - This includes a copy of the final runconfig file settings
* A copy of the input L1/L2 product's `identification` group
    - [!Caution] The QA HDF5's `/science/LSAR/identification/` group 
      is a copy of the input L1/L2 product's group.
    - For the QA-specific software version, processing datetime, and 
      runconfiguration contents, please see the 
      `/science/LSAR/QA/processing/` group.

The contents of the QA HDF5 file for each product type is provided below.

While all possible options for frequencies, polarizations, covariance terms, 
etc. are noted in these tables, the actual QA HDF5 files will only include 
the subset of these which correspond to the available frequencies, 
polarizations, covariance terms, etc. found in the input L1/L2 science products.

