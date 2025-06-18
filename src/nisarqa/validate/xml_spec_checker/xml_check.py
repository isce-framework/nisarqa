from __future__ import annotations

import os
from collections.abc import Iterable, Mapping

# List of objects from the import statements that
# should not be included when importing this module
import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


def check_hdf5_against_xml(
    product_type: str,
    *,
    xml_file: os.PathLike | str,
    hdf5_file: os.PathLike | str,
    valid_freq_pols: Mapping[str, Iterable[str]],
    valid_layers: Iterable[str] | None = None,
    valid_subswaths: Iterable[str] | None = None,
):
    """
    Check an HDF5 product against an XML spec file and log the results.

    Parameters
    ----------
    product_type : str
        One of: 'rslc', 'gslc', 'gcov', 'rifg', 'runw', 'gunw', 'roff', 'goff'.
    xml_file : path-like
        The XML product specification file path.
    hdf5_file : path-like
        The HDF5 product file path.
    valid_freq_pols : Mapping[str, Iterable[str]]
        Dict of the expected frequency + polarization combinations that the
        input NISAR product says it contains.
            Example: { "A" : ["HH", "HV], "B" : ["VV", "VH"] }
    valid_layers : Iterable[str] or None, optional
        ROFF and GOFF products contain HDF5 datasets referred to as "layer number
        datasets" (e.g. `../layer1/..`, `../layer3/..`).
        This parameter should be a set of all valid layer groups for this product,
        e.g., {'layer1', 'layer2', 'layer3'}, or None.
        If None, layer datasets will not be checked. Defaults to None.
    valid_subswaths : Iterable[str] | None, optional
        Some products contain a number of subswaths - if the product has
        subswath information, this should be a set of subswaths expected
        in the product. If not, it should be None. The set of products with
        subswaths is not yet further defined because it has not yet been
        declared which products will have these groups. Defaults to None.
    """
    log = nisarqa.get_logger()

    # Get the set of dataset nodes and shapes from the XML file and process
    # them into a dictionary of XML dataset objects indexed by their path,
    # as well as a dictionary of XML shape objects indexed by their name.
    log.info(
        "HDF5 product XML checker: Retrieving dataset descriptions and"
        " shapes from XML."
    )
    xml_dataset_elmts, shapes = nisarqa.get_xml_datasets_and_shapes(
        xml_file=xml_file
    )
    shape_objs = nisarqa.elements_to_shapes(shapes)
    xml_datasets = nisarqa.elements_to_datasets(
        xml_elements=xml_dataset_elmts,
        shapes=shape_objs,
    )

    # Checked for unused shapes in the XML
    log.info("HDF5 product XML checker: Checking XML file shapes.")
    nisarqa.check_xml_for_unused_shape_elements(
        shape_names=shape_objs.keys(),
        shapes=shape_objs.values(),
        xml_datasets=xml_datasets.values(),
    )

    log.info("HDF5 product XML checker: Retrieving datasets from HDF5 product.")
    # Get the set of datasets from the HDF5 file and process them into a
    # dictionary of HDF5 dataset objects indexed by their path.
    # This is handled as a context manager to keep the HDF5 file open during
    # checks, but close it in the case of an unhandled exception.
    with nisarqa.get_datasets_from_hdf5_file(hdf5_file) as hdf5_datasets:
        # Get sets of datasets: Those shared by both the XML and HDF5, those
        # exclusive to the XML file, and those exclusive to the HDF5 file.
        log.info(
            "HDF5 product XML checker: Comparing HDF5 datasets existence"
            " vs. XML spec."
        )
        shared_datasets, _, _ = nisarqa.compare_dataset_lists(
            product_type=product_type,
            xml_datasets=xml_datasets,
            hdf5_datasets=hdf5_datasets,
            valid_freq_pols=valid_freq_pols,
            valid_layers=valid_layers,
            valid_subswaths=valid_subswaths,
        )

        # COMMON DATASET CHECKS:
        # These tests check the XML datasets and HDF5 datasets against each other.
        log.info(
            "HDF5 product XML checker: Comparing Dataset metadata (attributes,"
            " dtypes, descriptions, and units) of HDF5 product vs. XML spec."
        )
        attr_stats = nisarqa.MultipleAspectsMultipleInstancesSummary()
        for dataset_name in sorted(shared_datasets):
            xml_dataset = xml_datasets[dataset_name]
            hdf5_dataset = hdf5_datasets[dataset_name]
            attr_stats += nisarqa.compare_hdf5_dataset_to_xml(
                xml_dataset=xml_dataset, hdf5_dataset=hdf5_dataset
            )

        attr_stats.print_to_log()


__all__ = nisarqa.get_all(__name__, objects_to_skip)
