from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


# Not marked as a dataclass because it needs to contain a mutable type
# (dict, in this case)
@dataclass
class DataAnnotation:
    """
    A set of attributes and description associated with a dataset or shape.
    """

    attributes: dict[str, Any]
    description: str

    @property
    def attribute_names(self) -> set[str]:
        return set(self.attributes.keys())


class XMLAnnotation(DataAnnotation):
    """
    A set of attributes and description associated with a dataset or shape, as
    described in an XML spec file.
    """

    @property
    def is_complex_marker(self) -> bool:
        """
        True if this annotation marks a dataset as complex; False otherwise.
        """
        if self.attributes["app"] != "io":
            return False
        if "kwd" in self.attributes:
            return self.attributes["kwd"] == "complex"
        return False

    @property
    def is_bool_marker(self) -> bool:
        """
        True if this annotation marks a Dataset as a boolean; False otherwise.

        Hacky method of figuring out if an annotation describes a
        boolean-valued dataset. Look for the terms "True" and "False" or
        "Flag to indicate" in the annotation description - there is no other
        unambiguous means of determining if a dataset is a boolean.
        """
        if self.attributes["app"] != "conformance":
            return False
        if '"True"' in self.description and '"False"' in self.description:
            return True
        if self.description.startswith("Flag to indicate"):
            return True
        return False


@dataclass
class DataShape:
    """
    A set of dimensions associated with one or more datasets in a NISAR product
    or other shapes.

    Also includes (at least) one annotation, which is a brief description of
    the dimensions, and can be used to check whether associated datasets are
    complex-valued.


    Parameters
    -------
    name : str
        The name of the shape.
    order : str
        The order attribute of the shape.
    annotations : list[XMLAnnotation]
        The set of annotations described within the shape.
    dimensions : list[Dimension]
        The set of dimensions described within the shape.
    """

    name: str
    order: str
    annotations: list[XMLAnnotation]
    dimensions: list[Dimension]

    @property
    def is_complex(self) -> bool:
        return any(dimension.is_complex_marker for dimension in self.dimensions)


@dataclass
class Dimension:
    """
    A data dimension.

    Parameters
    -------
    name : str
        The name of the dimension.
    extent : str
        The extent attribute of the dimension.
    """

    name: str
    extent: int

    @property
    def is_complex_marker(self) -> bool:
        return self.name == "complex"


__all__ = nisarqa.get_all(__name__, objects_to_skip)
