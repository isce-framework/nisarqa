from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Generator

import h5py
import numpy as np

# List of objects from the import statements that
# should not be included when importing this module
import nisarqa
from nisarqa import HDF5Dataset

objects_to_skip = nisarqa.get_all(name=__name__)


def generate_h5_datasets(
    hdf5_object: h5py.Group | h5py.File | h5py.Dataset | h5py.Datatype,
    datasets: dict[str, HDF5Dataset],
    prefix="",
):
    """
    Given an HDF5 h5py object, generate HDF5 dataset objects for all datasets at or
    underneath it in the HDF5 file structure.

    Parameters
    ----------
    hdf5_object : h5py.Group | h5py.File | h5py.Dataset | h5py.Datatype
        The object to generate HDF5Datasets for.
    datasets : dict[str, nisarqa.HDF5Dataset]
        A dictionary of datasets to place the new datasets into, addressable by their path
        within the HDF5 file structure.
    prefix : str, optional
        The HDF5 file structure prefix of this object. Defaults to "".
    """
    # If this is a dataset, generate a dataset for it.
    if isinstance(hdf5_object, h5py.Dataset):
        # First, extract all the attributes of the object into a DataAnnotation object.
        attributes: dict[str, Any] = {}
        for key in hdf5_object.attrs.keys():
            attribute = hdf5_object.attrs[key]
            # Attributes are held in the
            if type(attribute) in [bytearray, bytes, np.bytes_]:
                attributes[key] = attribute.decode("utf-8")
            else:
                attributes[key] = attribute
        if "description" in attributes:
            description = attributes["description"]
            # Remove the "description" from the attributes dictionary.
            # Note: in `element_to_annotation()` in `xml_parser.py`, if the XML
            # has a designated "description" Attribute, that Attribute
            # is similarly deleted from the attributes dictionary and
            # stored in a separate parameter.
            del attributes["description"]
        else:
            description = ""
        annotation = nisarqa.DataAnnotation(
            attributes=attributes, description=description
        )
        # Now, create a Node object and place it in the dictionary at the
        # location of its' prefix.
        dataset = HDF5Dataset(
            name=prefix, dataset=hdf5_object, annotation=annotation
        )
        datasets[prefix] = dataset
    # For HDF5 datasets and files, check their children recursively.
    elif type(hdf5_object) in [h5py.Group, h5py.File]:
        for key in hdf5_object.keys():
            generate_h5_datasets(
                hdf5_object[key], datasets=datasets, prefix=f"{prefix}/{key}"
            )
    elif type(hdf5_object) == h5py.Datatype:
        log = nisarqa.get_logger()
        log.warning(
            f"HDF5 parsing: Found datatype HDF5 object {hdf5_object} at"
            f" prefix {prefix}"
        )
        return
    # This should not happen, but if an unrecognized type is passed in,
    # raise an error.
    else:
        raise ValueError(
            "HDF5 parsing: Unable to recognize"
            f" object {hdf5_object} with type {type(hdf5_object)} at"
            f" prefix {prefix}"
        )


@contextmanager
def get_datasets_from_hdf5_file(
    path: os.PathLike | str,
) -> Generator[dict[str, HDF5Dataset], None, None]:
    """
    Retrieve all datasets in an HDF5 file in the form of HDF5Dataset objects.

    Parameters
    ----------
    path : path-like
        The path to the file.

    Returns
    -------
    dict[str, nisarqa.HDF5Dataset]
        All generated dataset objects, addressable by their path in the HDF5 file.
    """
    datasets: dict[str, HDF5Dataset] = {}
    with h5py.File(os.fspath(path), "r") as file:
        generate_h5_datasets(hdf5_object=file["/"], datasets=datasets)

        yield datasets


__all__ = nisarqa.get_all(__name__, objects_to_skip)
