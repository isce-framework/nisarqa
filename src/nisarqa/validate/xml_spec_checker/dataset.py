from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum, EnumMeta
from typing import Any, TypeVar
from xml.etree.ElementTree import Element

import h5py
import isce3
import numpy as np

# List of objects from the import statements that
# should not be included when importing this module
import nisarqa
from nisarqa import DataShape, XMLAnnotation

objects_to_skip = nisarqa.get_all(name=__name__)


XMLDatasetT = TypeVar("XMLDatasetT", bound="XMLDataset")


class MetaEnum(EnumMeta):
    """
    A metaclass for enums that allows checking to see if it contains a value.
    """

    def __contains__(cls, item: Any) -> bool:
        """Returns True if `item` is a valid member value of the enum."""
        try:
            cls[item]
        except ValueError:
            return False
        return True


class XMLNodeType(Enum, metaclass=MetaEnum):
    """
    An enum of all accepted XML node tags.

    These can be used to infer the dtype of that dataset.
    """

    string = "string"
    # For XML nodes, "real" datasets include all float-valued data, including
    # complex datasets.
    real = "real"
    integer = "integer"

    # XMLs also have "shape" nodes (these do not correspond to HDF5 Datasets)
    shape = "shape"


@dataclass
class DatasetDesc(ABC):
    # TODO: Remove this along with HDF5Dataset
    name: str

    @property
    @abstractmethod
    def dtype(self) -> np.dtype | None:
        """
        The object's data type, or None if no valid data type could be
        found.
        """
        ...


@dataclass
class HDF5Dataset(DatasetDesc):
    """A dataset as expressed in the form of an h5py dataset."""

    # TODO: Remove this

    annotation: nisarqa.DataAnnotation
    dataset: h5py.Dataset

    @property
    def value(self) -> Any:
        return self.dataset[:]

    @property
    def dtype(self) -> np.dtype | None:
        if nisarqa.is_complex32(self.dataset):
            return nisarqa.complex32
        return self.dataset.dtype


@dataclass
class XMLDataset(DatasetDesc):
    """
    An XML spec dataset that is intended to describe an HDF5 dataset in a real
    product.

    Attributes
    --------
    annotations : list of XMLAnnotation
        The XMLAnnotations associated with this dataset, denoted by
        "annotation" sub-elements in the originating XML element.
    node_type : XMLNodeType or None
        The XMLNodeType of this dataset, be it REAL, INTEGER, or STRING.
        None if this dataset is malformed and does not have a valid node type
        name.
    shape : DataShape or None
        The DataShape associated with this dataset, denoted by a "shape"
        element referred to by name in the originating XML element.
        None if no valid DataShape object could be associated with this
        dataset.
    length : int or None
        The length of the dataset, if it is a string.
        None for reals or integers.
    width : int or None
        The width of the dataset in bits, if it is real or integer typed.
        None for strings.
    is_signed : bool or None
        For integers, whether the dataset is signed or not.
        None for strings or reals.
    """

    annotations: list[XMLAnnotation]
    node_type: XMLNodeType | None

    # All XMLDatasets should have a shape attribute -- however, in practice,
    # some are missing this attribute. So we need a workaround to ensure that
    # the code doesn't fail before we can usefully parse the XML/HDF5.
    shape: DataShape | None

    # The following are attributes which may or may not appear on a dataset
    # description.
    # Strings must have a length.
    length: int | None
    # Integers and reals must have a width.
    width: int | None
    # Integers may or may not have a sign.
    is_signed: bool | None

    # _dtype is an inferred type, and if an XMLDataset is malformed, that type
    # may not be inferrable. If it is not, this should be None, meaning that it
    # cannot be sensibly checked against.
    _dtype: np.dtype | None = None

    def __post_init__(self):
        if self.node_type == XMLNodeType.shape:
            raise ValueError(
                f"XML node provided with {self.node_type=}, but must be"
                " real, integer, string, or None for this class."
            )
        # If _dtype was not given, infer its type based on the given info.
        if self._dtype is None:
            self._dtype = self._determine_dtype()

    @classmethod
    def from_xml_element(
        cls: type[XMLDatasetT],
        xml_element: Element,
        shapes: Mapping[str, DataShape],
    ) -> XMLDatasetT:
        """
        Process an XML element into an XMLDataset object.

        Parameters
        ----------
        xml_element : Element
            The element to be processed.
        shapes : Mapping[str, DataShape]
            A mapping of DataShape objects indexable by their name.

        Returns
        -------
        nisarqa.XMLDataset
            The generated XMLDataset object.
        """
        log = nisarqa.get_logger()

        attributes = xml_element.attrib

        # Every XMLDataset should have a 'name' attribute.
        # If not, log the error.
        if "name" in attributes:
            name: str = attributes.pop("name")
        else:
            log.error(f"XML dataset element found with no 'name' attribute.")
            name = ""

        # Every XMLDataset should be associated with a DataShape object that
        # has already been found. If not, log the error.
        if "shape" in attributes:
            shape_name: str = attributes.pop("shape")
            if shape_name in shapes:
                shape = shapes[shape_name]
            else:
                log.error(
                    f"XML Dataset's shape is '{shape_name}', but there is no"
                    " corresponding shape Element in the XML spec. For QA,"
                    " this Dataset's shape will be treated as `None` - XML"
                    f" Dataset {name}"
                )
                shape = None
        else:
            log.error(f"XML dataset element has no shape: XML Dataset {name}")
            shape = None

        # Node Type. Should be one of {'integer', 'real', 'string', 'shape'}.
        node_tag = xml_element.tag
        if node_tag not in XMLNodeType:
            log.error(
                f"Bad node type: {node_tag}. Must be in"
                " (string, real, integer, shape):"
                f" XML dataset {name}"
            )
            node_type = None
        else:
            node_type = XMLNodeType[node_tag]

        # Create the XMLAnnotation objects associated with this XMLDataset.
        annotation_elements = xml_element.findall("annotation")
        annotations = nisarqa.parse_annotations(
            annotation_elements=annotation_elements,
            dataset_name=name,
            xml_node_type=node_type,
        )

        # Strings have a "length" attribute, other types don't. This will
        # be checked when the XMLDataset is initialized.
        length_int: int | None = None
        if "length" in attributes:
            length_str: str = attributes.pop("length")
            try:
                length_int = int(length_str)
            except ValueError:
                log.error(
                    f"Length given as non-integer value: {length_str} -"
                    f" XML dataset {name}"
                )

        # Numerical types have a "width" attribute, strings don't. This will
        # be checked when the XMLDataset is initialized.
        width_int: int | None = None
        if "width" in attributes:
            width_str: str = attributes.pop("width")
            try:
                width_int = int(width_str)
            except ValueError:
                log.error(
                    f"Width given as non-integer value: {width_str}:"
                    f" XML dataset {name}"
                )

        # Integers may have "signed" attribute, other types don't. This will
        # be checked when the XMLDataset is initialized. If an integer node
        # is missing a "signed" attribute, we assume it is signed.
        is_signed: bool | None = None
        if "signed" not in attributes.keys():
            if node_type == XMLNodeType.integer:
                is_signed = True
            else:
                is_signed = None
        else:
            signedness_str: str = attributes.pop("signed")
            if signedness_str.lower() == "true":
                is_signed = True
            elif signedness_str.lower() == "false":
                is_signed = False
            else:
                log.error(
                    f"Unrecognized signedness: {signedness_str}:"
                    f" XML dataset {name}"
                )

        # The attributes extracted above should be the only possible attributes
        # on an XML element describing an XMLDataset.
        # Warn of all others, if any are present.
        if len(attributes) > 0:
            log.warning(
                f"XML dataset contains unexpected attributes: {attributes} -"
                f" XML Dataset {name}"
            )

        # Return an XMLDataset object
        return cls(
            name=name,
            annotations=annotations,
            node_type=node_type,
            shape=shape,
            length=length_int,
            width=width_int,
            is_signed=is_signed,
        )

    @property
    def dtype(self) -> np.dtype | None:
        """
        The data type associated with this dataset, if any can be inferred.
        """
        return self._dtype

    def _determine_dtype(self) -> np.dtype | None:
        """
        Determine the data type associated with this dataset, if one can
        be inferred with the given information. Else, return None.
        """
        if self.node_type == XMLNodeType.string:
            return self._get_dtype_str()
        if self.node_type == XMLNodeType.integer:
            return self._get_dtype_int()
        if self.node_type == XMLNodeType.real:
            return self._get_dtype_real()
        return None

    def _get_dtype_str(self) -> np.dtype:
        log = nisarqa.get_logger()
        if self.width is not None:
            log.error(
                "String XML dataset listed with data width. Strings"
                f" do not have a data width. XML dataset {self.name}"
            )
        if self.is_signed is not None:
            log.error(
                "String XML dataset listed with positive/negative sign."
                f" Strings do not have a signs. XML dataset {self.name}"
            )
        if (self.shape is not None) and self.shape.is_complex:
            log.error(
                "String XML dataset listed with complex shape:"
                f" XML dataset {self.name}"
            )
        for annotation in self.annotations:
            if annotation.is_complex_marker:
                log.error(
                    "String XML dataset listed with complex annotation:"
                    f" XML dataset {self.name}"
                )
        return str

    def _get_dtype_int(self) -> np.dtype | None:
        log = nisarqa.get_logger()

        # Integer datasets should not have a length.
        # If one is found, log an error.
        if self.length is not None:
            log.error(
                "Integer XML dataset listed with length:"
                f" XML dataset {self.name}"
            )

        # Integer datasets should not have a complex shape or annotations.
        # If any are found, log an error.
        if (self.shape is not None) and self.shape.is_complex:
            log.error(
                "Integer XML dataset listed with complex shape:"
                f" XML dataset {self.name}"
            )

        for annotation in self.annotations:
            if annotation.is_complex_marker:
                log.error(
                    "Integer XML dataset listed with complex annotation:"
                    f" XML dataset {self.name}"
                )

        # Get the width and signedness of this dataset, and use that to infer
        # an appropriate data type.
        width = self.width
        if width is None:
            log.error(
                "XML integer dataset does not have a width property. No dtype"
                f" could be inferred. XML dataset {self.name}"
            )
            return None

        signed = self.is_signed
        if signed:
            if width == 8:
                return np.int8
            if width == 16:
                return np.int16
            if width == 32:
                return np.int32
            if width == 64:
                return np.int64
            if width == 128:
                return np.int128
            log.error(
                "Unrecognized int width and signedness for integer type:"
                f" width={width},"
                f" signed={signed} -"
                f" XML dataset {self.name}"
            )
            return None
        if width == 8:
            return np.uint8
        if width == 16:
            return np.uint16
        if width == 32:
            return np.uint32
        if width == 64:
            return np.uint64
        if width == 128:
            return np.uint128
        log.error(
            "Unrecognized int width and signedness for integer type:"
            f" width={width}, signed={signed} -"
            f" XML dataset {self.name}"
        )
        return None

    def _get_dtype_real(self) -> np.dtype | None:
        log = nisarqa.get_logger()

        # Float-valued datasets should not have a length.
        # If one is found, log an error.
        if self.length is not None:
            log.error(
                "Integer XML dataset listed with length:"
                f" XML dataset {self.name}"
            )

        if self.is_signed is not None:
            log.error(
                "Floating-point XML dataset listed with sign."
                " Unsigned floating-point types are not supported."
                f" XML dataset {self.name}"
            )
        width = self.width
        if width is None:
            log.error(
                "XML float dataset does not have a width property. No dtype"
                f" could be inferred. XML dataset {self.name}"
            )
            return None

        # Complex checking for real-valued XML dataset descriptions:
        # There are two features of a "real"-valued XML dataset that
        # signify that it is or is not complex-valued. These must both
        # signify the same thing in order to unambiguously confirm that
        # a dataset should or should not be considered complex.

        # Products list all complex-valued data objects using what this
        # code calls a "complex marker," or an annotation that contains
        # the following:
        #       <annotation app="io" kwd="complex" />
        # This is checked for in the annotation.is_complex_marker property.
        is_any_annotation_complex = any(
            annotation.is_complex_marker for annotation in self.annotations
        )

        # Products list all complex-valued data objects using a shape which
        # contains one complex dimension. This dimension contains the
        # following:
        #       <dimension name="complex" extent="2"/>
        # This is checked for in the shape.is_complex property.
        if self.shape is not None:
            is_shape_complex = self.shape.is_complex
            # If the dataset is marked as complex by one marker and not the
            # other, the dtype cannot be confirmed unambiguously.
            if is_shape_complex != is_any_annotation_complex:
                annotation_note = (
                    "is" if is_any_annotation_complex else "is not"
                )
                shape_note = "is" if is_shape_complex else "is not"
                log.error(
                    "Floating-point XML dataset annotations indicate that it"
                    f" {annotation_note} complex, while its shape indicates"
                    f" that it {shape_note}: XML dataset{self.name}"
                )
                return None
        else:
            log.debug(
                "Floating-point XML dataset does not have a valid shape."
                " Assuming annotations correctly indicate if it is complex."
                f" XML dataset {self.name}"
            )

        # At this time we have either confirmed that the complex markers
        # are identical or we have returned None.
        is_complex = is_any_annotation_complex

        # Acquire a dtype given the determined width and complexity values.
        if is_complex:
            if width == 16:
                return nisarqa.complex32
            if width == 32:
                return np.complex64
            if width == 64:
                return np.complex128
            log.error(
                f"Unrecognized width value for complex type: {width} -"
                f" XML dataset {self.name}"
            )
            return None
        if width == 16:
            return np.float16
        if width == 32:
            return np.float32
        if width == 64:
            return np.float64
        log.error(
            f"Unrecognized width value for float type: {width} -"
            f" XML dataset {self.name}"
        )
        return None


__all__ = nisarqa.get_all(__name__, objects_to_skip)
