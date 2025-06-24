# Directory Structure and Paths in QA STATS.h5 file
STATS_H5_BASE_GROUP = "/science/%sSAR"
STATS_H5_IDENTIFICATION_GROUP = STATS_H5_BASE_GROUP + "/identification"
processing_group = "/processing"
data_group = "/data"

# QA Directory Structure and Paths in STATS.h5 file
STATS_H5_QA_STATS_H5_BASE_GROUP = STATS_H5_BASE_GROUP + "/QA"
STATS_H5_QA_PROCESSING_GROUP = (
    STATS_H5_QA_STATS_H5_BASE_GROUP + processing_group
)
STATS_H5_QA_DATA_GROUP = STATS_H5_QA_STATS_H5_BASE_GROUP + data_group
# Frequency group. Note: There are two '%s' here. The first is for the band,
# the second for the frequency.
# Example end result: '/science/%s/QA/data/frequency%s'
STATS_H5_QA_FREQ_GROUP = (
    STATS_H5_QA_DATA_GROUP + "/frequency%s"
)  # Two '%s' here!

# Input Granule Source Data group (for copying Datasets verbatim)
STATS_H5_SOURCE_DATA = STATS_H5_BASE_GROUP + "/sourceData"

# RFI Group
STATS_H5_RFI_BASE_GROUP = STATS_H5_SOURCE_DATA + "/RFI"
STATS_H5_RFI_DATA_GROUP = STATS_H5_RFI_BASE_GROUP + data_group

# CalTools
STATS_H5_ABSCAL_STATS_H5_BASE_GROUP = (
    STATS_H5_BASE_GROUP + "/absoluteRadiometricCalibration"
)
STATS_H5_ABSCAL_PROCESSING_GROUP = (
    STATS_H5_ABSCAL_STATS_H5_BASE_GROUP + processing_group
)
STATS_H5_ABSCAL_DATA_GROUP = STATS_H5_ABSCAL_STATS_H5_BASE_GROUP + data_group

STATS_H5_PTA_STATS_H5_BASE_GROUP = STATS_H5_BASE_GROUP + "/pointTargetAnalyzer"
STATS_H5_PTA_PROCESSING_GROUP = (
    STATS_H5_PTA_STATS_H5_BASE_GROUP + processing_group
)
STATS_H5_PTA_DATA_GROUP = STATS_H5_PTA_STATS_H5_BASE_GROUP + data_group

STATS_H5_NEB_STATS_H5_BASE_GROUP = (
    STATS_H5_BASE_GROUP + "/noiseEquivalentBackscatter"
)
STATS_H5_NEB_PROCESSING_GROUP = (
    STATS_H5_NEB_STATS_H5_BASE_GROUP + processing_group
)
STATS_H5_NEB_DATA_GROUP = STATS_H5_NEB_STATS_H5_BASE_GROUP + data_group

# The are global constants and not functions nor classes,
# so manually create the __all__ attribute.
__all__ = [
    "STATS_H5_BASE_GROUP",
    "STATS_H5_IDENTIFICATION_GROUP",
    "STATS_H5_QA_STATS_H5_BASE_GROUP",
    "STATS_H5_QA_PROCESSING_GROUP",
    "STATS_H5_QA_DATA_GROUP",
    "STATS_H5_QA_FREQ_GROUP",
    "STATS_H5_SOURCE_DATA",
    "STATS_H5_RFI_BASE_GROUP",
    "STATS_H5_RFI_DATA_GROUP",
    "STATS_H5_ABSCAL_STATS_H5_BASE_GROUP",
    "STATS_H5_ABSCAL_PROCESSING_GROUP",
    "STATS_H5_ABSCAL_DATA_GROUP",
    "STATS_H5_PTA_STATS_H5_BASE_GROUP",
    "STATS_H5_PTA_PROCESSING_GROUP",
    "STATS_H5_PTA_DATA_GROUP",
    "STATS_H5_NEB_STATS_H5_BASE_GROUP",
    "STATS_H5_NEB_PROCESSING_GROUP",
    "STATS_H5_NEB_DATA_GROUP",
]
