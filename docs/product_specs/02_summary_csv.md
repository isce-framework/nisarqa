
# High-Level Summary PASS/FAIL/WARN Checks (CSV)

## Overview

The summary CSV is high-level, human- and machine-readable file which summarizes detailed QA metrics into a CSV table.

Example PASS/FAIL/WARN checks included in the CSV:
* PASS: All checks complete
* FAIL: All pixels in one layer are NaN
* WARN: Geolocation error over corner reflectors exceeds a specified threshold

The specific checks included in the CSV will vary for each product type, with some checks depending on the content of individual granules. Select examples are presented below.

Observe that some of the checks in the examples below indicate a `"FAIL"`. This is because the QA software includes both fatal checks and soft checks. Fatal checks indicate a fatal error in the input L1/L2 granule which requires analysis and potential reprocessing by the NISAR mission team. If there is a fatal error, then the final row in the CSV (the `"QA completed with no exceptions?"` check) will be a `"FAIL"`.

The soft checks notify users of the existance of minor concerns in the input product; these concerns should not halt the release of a L1/L2 dataset publically. For example, the NISAR sample products used to generate the example CSVs below were derived from ALOS-1 datasets; the conversion from ALOS-1 to NISAR-format did not include metadata corresponding to NISAR's `plannedObservationId` field in the `identification` group, and so that field was populated with a placeholder value. However, that placeholder value is not valid for the launched NISAR mission data, so that soft check is noted as a "FAIL".


## Example RSLC QA Summary CSV

Here are the contents of an example RSLC QA Summary CSV:

```
Tool,Check,Result,Threshold,Actual,Notes
QA,Able to open input NISAR file?,PASS,,,
QA,Metadata cubes are valid?,FAIL,,,
QA,Passes all `identification` group checks?,FAIL,,,
QA,% Cumulative NaN and Inf and fill and near-zero pixels under threshold?,PASS,,,RSLC_L_A_HH backscatter: If a 'FAIL' then all histogram bin counts are zero. This likely indicates that the raster contained no valid data. Note: check performed on decimated raster not full raster.
QA,% Cumulative NaN and Inf and fill and near-zero pixels under threshold?,PASS,,,RSLC_L_A_HH phase: If a 'FAIL' then all histogram bin counts are zero. This likely indicates that the raster contained no valid data. Note: check performed on decimated raster not full raster.
QA,QA completed with no exceptions?,PASS,,,
```

Here are the same example RSLC QA Summary CSV contents, visualized in a table:


| Tool | Check | Result | Threshold | Actual | Notes |
| :---: | ------- | :---: | :----: | :---: | --------- |
| QA | Able to open input NISAR file? | PASS |  |  | 
| QA | Metadata cubes are valid? | FAIL |  |  | 
| QA | Passes all `identification` group checks? | FAIL |  |  | 
| QA | % Cumulative NaN and Inf and fill and near-zero pixels under threshold? | PASS |  |  | RSLC_L_A_HH backscatter: If a 'FAIL' then all histogram bin counts are zero. This likely indicates that the raster contained no valid data. Note: check performed on decimated raster not full raster.
| QA | % Cumulative NaN and Inf and fill and near-zero pixels under threshold? | PASS |  |  | RSLC_L_A_HH phase: If a 'FAIL' then all histogram bin counts are zero. This likely indicates that the raster contained no valid data. Note: check performed on decimated raster not full raster.
| QA | QA completed with no exceptions? | PASS |  |  | 

Here is an example RIFG QA Summary CSV contents, visualized in a table:

| Tool | Check | Result | Threshold | Actual | Notes |
| :---: | ------- | :---: | :----: | :---: | --------- |
| QA | Able to open input NISAR file? | PASS |  |  |  |
| QA | Metadata cubes are valid? | PASS |  |  |  |
| QA | Passes all `identification` group checks? | FAIL |  |  |  |
| QA | % NaN pixels under threshold? | PASS | 95.0 | 0.00 | RIFG_L_A_interferogram_HH_wrappedInterferogram |
| QA | % Cumulative NaN and Inf and fill and near-zero pixels under threshold? | PASS | 95.0 | 0.00 | RIFG_L_A_interferogram_HH_wrappedInterferogram |
| QA | % NaN pixels under threshold? | PASS | 95.0 | 0.03 | RIFG_L_A_interferogram_HH_coherenceMagnitude |
| QA | % Cumulative NaN and Inf and fill and near-zero pixels under threshold? | PASS | 95.0 | 0.03 | RIFG_L_A_interferogram_HH_coherenceMagnitude |
| QA | % NaN pixels under threshold? | PASS | 95.0 | 0.14 | RIFG_L_A_pixelOffsets_HH_alongTrackOffset |
| QA | % Cumulative NaN and Inf and fill and near-zero pixels under threshold? | PASS | 95.0 | 0.14 | RIFG_L_A_pixelOffsets_HH_alongTrackOffset |
| QA | % NaN pixels under threshold? | PASS | 95.0 | 0.00 | RIFG_L_A_pixelOffsets_HH_slantRangeOffset |
| QA | % Cumulative NaN and Inf and fill and near-zero pixels under threshold? | PASS | 95.0 | 0.00 | RIFG_L_A_pixelOffsets_HH_slantRangeOffset |
| QA | % NaN pixels under threshold? | PASS | 95.0 | 0.00 | RIFG_L_A_pixelOffsets_HH_correlationSurfacePeak |
| QA | % Cumulative NaN and Inf and fill and near-zero pixels under threshold? | PASS | 95.0 | 0.00 | RIFG_L_A_pixelOffsets_HH_correlationSurfacePeak |
| QA | QA completed with no exceptions? | PASS |  |  | 


## Example QA Summary CSV with Fatal Error

Here are the contents of an example QA Summary CSV for an input file with a fatal error, visualized in a table:

| Tool | Check | Result | Threshold | Actual | Notes
| :---: | ------- | :---: | :----: | :---: | --------- |
| QA | Able to open input NISAR file? | PASS |  |  | 
| QA | Coordinate grid metadata cubes are valid? | PASS |  |  | 
| QA | Calibration information LUTs are valid? | PASS |  |  | `crosstalk` LUTs skipped.
| QA | Passes all `identification` group checks? | FAIL |  |  | 
| QA | QA completed with no exceptions? | FAIL |  |  | 
