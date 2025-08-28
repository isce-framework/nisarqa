
# Graphical Summary (PDF)

The graphical summary PDF is provided to quickly visualize and assess the content and quality of an L1 or L2 input granule. It includes labeled plots, histograms, and other information for the layers and datasets in the input granule.

The processing parameters and computed arrays used to generate the histograms, spectra, and other plots in the QA Report PDF are stored in the QA HDF5 file. This allows users to do analysis algorithmically on the computed values seen in the PDFs. Please see Statistical Summary (QA HDF5) section in this documentation for details on the datasets stored in the QA HDF5 file.

The contents of each PDF are customized for each L1/L2 product type, although many features are reused for multiple products. This section of the documention is organized by product type and then by feature. The relevant product types noted in parentheses in the subsection titles.


## Cover Page (All L1/L2 products)

The PDF cover page contains the input's Granule ID, QA software version and processing date used to generate the PDF. It also displays the majority of the datasets from the input granule's `identification` group, with the following additions and distinctions:

* `softwareVersion`: The version of the software used to generate the L1/L2 granule. QA parses this from the input granule, but it is located outside of the `identification` group.
* `listOfPolarizations (frequency A)` and `listOfPolarizations (frequency B)`: The list of polarizations available in the input product per frequency. If a given frequency group is not present, this is assigned the value `n/a`. QA parses these from the input granule, but they is located outside of the `identification` group.
* (GCOV only) `listOfCovarianceTerms (frequency A)` and `listofCovarianceTerms (frequency B)`: The list of covariance terms available in the input product per frequency. If a given frequency group is not present, this is assigned the value `n/a`. QA parses these from the input granule, but they is located outside of the `identification` group.
* `boundingPolygon` (and other datasets whose string-representation length is greater than 30 characters) will not be displayed.

![Example Report PDF Cover Page](images/report_cover_page.jpg)





