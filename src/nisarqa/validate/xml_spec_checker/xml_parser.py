from __future__ import annotations

import os
from collections.abc import Iterable, Mapping
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

import nisarqa

from .data_annotation import Dimension
from .dataset import DataShape, XMLAnnotation, XMLDataset

objects_to_skip = nisarqa.get_all(name=__name__)


def get_xml_datasets_and_shapes(
    xml_file: os.PathLike | str,
) -> tuple[list[Element], list[Element]]:
    """
    Get all of the dataset node and shape elements from a valid NISAR product
    spec file.

    Parameters
    ----------
    xml_file : path-like
        The path to the XML file.

    Returns
    -------
    datasets: list[Element]
        All of the datasets node elements held within the XML file.
    shapes: list[Element]
        All of the shape description elements held within the XML file.
    """
    xml_tree = ET.parse(xml_file)

    # This program assumes that the given XML file will contain a root group
    # which contains a hierarchy in which the root element contains "product",
    # "science", and "nodes" elements, one of each nested in that order.
    # The "nodes" element is expected to contain only a list of dataset
    # description elements (herein called "datasets") and the "product"
    # element should contain a list of "shape" elements.
    algorithm_element = xml_tree.getroot()
    product_element = algorithm_element.find("product")
    science_element = product_element.find("science")
    nodes_element = science_element.find("nodes")

    # In the XML, HDF5 dataset descriptions are called "nodes". For the rest of
    # this program, these will be called "datasets" for consistency.
    datasets = nodes_element[:]
    shapes = product_element.findall("shape")

    return datasets, shapes


def elements_to_shapes(
    xml_elements: Iterable[Element],
) -> dict[str, DataShape]:
    """
    Parse a set of "shape" XML elements into DataShape objects.

    Parameters
    ----------
    xml_elements : Iterable[Element]
        The XML elements to parse.

    Returns
    -------
    dict[str, nisarqa.DataShape]
        The DataShape objects generated, addressable by name.
    """
    shapes: dict[str, DataShape] = {}
    for element in xml_elements:
        shape: nisarqa.DataShape = element_to_shape(element)
        shapes[shape.name] = shape
    return shapes


def element_to_shape(xml_element: Element) -> nisarqa.DataShape:
    """
    Process a "shape" XML element into an DataShape object.

    Parameters
    ----------
    xml_element : Element
        The element to be processed.

    Returns
    -------
    nisarqa.DataShape
        The generated DataShape object.
    """
    if xml_element.tag != "shape":
        raise ValueError(f"{xml_element.tag=}, must have tag of 'shape'.")

    attributes = xml_element.attrib
    name = attributes["name"]
    order = attributes["order"]

    annotation_elements = xml_element.findall("annotation")
    annotations = parse_annotations(
        annotation_elements=annotation_elements,
        dataset_name=name,
        xml_node_type=nisarqa.XMLNodeType.shape,
    )

    dimension_elements = xml_element.findall("dimension")
    dimensions = parse_dims(dimension_elements)

    return nisarqa.DataShape(
        name=name,
        order=order,
        annotations=annotations,
        dimensions=dimensions,
    )


def parse_dims(
    dimension_elements: Iterable[Element],
) -> list[Dimension]:
    """
    Parse a set of "dimension" XML elements into Dimension objects.

    Parameters
    ----------
    dimension_elements : Iterable[Element]
        The XML elements to parse.

    Returns
    -------
    list[nisarqa.Dimension]
        The Dimension objects generated.
    """
    dimensions: list[Dimension] = []
    for dimension in dimension_elements:
        dimensions.append(element_to_dimension(dimension))
    return dimensions


def element_to_dimension(element: Element) -> Dimension:
    """
    Parse a "dimension" XML element into a Dimension object.

    Parameters
    ----------
    element : Element
        The XML element to parse.

    Returns
    -------
    nisarqa.Dimension
        The generated Dimension object.
    """
    dimension_attribs = element.attrib
    dim_name = dimension_attribs["name"]
    extent = dimension_attribs["extent"]
    return nisarqa.Dimension(name=dim_name, extent=extent)


def elements_to_datasets(
    xml_elements: Iterable[Element],
    shapes: Mapping[str, DataShape],
) -> dict[str, XMLDataset]:
    """
    Parse a set of XML elements into XMLDataset objects.

    Parameters
    ----------
    xml_elements : Iterable[Element]
        The XML elements to parse.
    shapes : Mapping[str, DataShape]
        A mapping of DataShape objects indexable by their name.

    Returns
    -------
    dict[str, nisarqa.XMLDataset]
        The XMLDataset objects generated, addressable by name.
        Each XMLDataset name should be its path in the HDF5 file.
    """

    datasets: dict[str, XMLDataset] = {}
    for element in xml_elements:
        dataset = XMLDataset.from_xml_element(
            xml_element=element,
            shapes=shapes,
        )

        # Check for duplicate occurrences of the same dataset in the XML
        if dataset.name in datasets:
            nisarqa.get_logger().error(
                "XML contains multiple occurrences of the same Dataset."
                f" Using the first occurrence. Dataset: {dataset.name}"
            )
            continue

        datasets[dataset.name] = dataset

    return datasets


def parse_annotations(
    annotation_elements: Iterable[Element],
    dataset_name: str,
    xml_node_type: nisarqa.XMLNodeType | None,
) -> list[XMLAnnotation]:
    """
    Parse a set of "annotation" XML elements into DataAnnotation objects.

    Parameters
    ----------
    annotation_elements : Iterable[Element]
        The XML elements to parse.
    dataset_name : str
        Name of the dataset that the annotations are attached to.
        Example: "/science/LSAR/RSLC/swaths/frequencyA/slantRange"
    xml_node_type : nisarqa.XMLNodeType | None
        dtype for the dataset that this annotation is attached to.

    Returns
    -------
    list[DataAnnotation]
        The DataAnnotation objects generated.
    """
    annotation_objs: list[XMLAnnotation] = []
    for annotation in annotation_elements:
        annotation_objs.append(
            element_to_annotation(
                element=annotation,
                dataset_name=dataset_name,
                xml_node_type=xml_node_type,
            )
        )
    return annotation_objs


def element_to_annotation(
    element: Element,
    dataset_name: str,
    xml_node_type: nisarqa.XMLNodeType | None,
) -> nisarqa.XMLAnnotation:
    """
    Parse a single "annotation" XML element into a DataAnnotation object.

    Parameters
    ----------
    element : Element
        The XML element to parse.
    dataset_name : str
        Name of the dataset that this annotation is attached to.
        Example: "/science/LSAR/RSLC/swaths/frequencyA/slantRange"
    xml_node_type : nisarqa.XMLNodeType | None
        XML type of the dataset that this annotation is attached to.

    Returns
    -------
    DataAnnotation
        The generated DataAnnotation object.

    Notes
    -----
    The XML Spec should be treated as the source of truth, however, there
    are likely "bugs" in the XML. If any of these "buggy" cases are found,
    this function will log the bugs but still include them in the
    DataAnnotation's attributes.
    This way, downstream processing can ensure that the HDF5 products
    generated faithfully match the current state of the XML (issues included).

    An error will be logged in these cases:
        * The annotation contains a "description" attribute.
        * `xml_node_type` is string and the annotation contains a "units" attribute.
        * `xml_node_type` is numeric and `dataset_name` ends with a name in
          `nisarqa.numeric_dtype_should_not_have_units()` and the annotation
          contains a "units" attribute.
    """
    log = nisarqa.get_logger()
    annotation_attribs = element.attrib
    description = element.text

    if element.tag != "annotation":
        raise ValueError(
            f"`{element.tag=}`, must be 'annotation'. XML Element:"
            f" {dataset_name}"
        )

    # Verification of the annotations:

    # For reference in maintaining this function, here is an example XML
    # dataset which contains two "annotations":
    #
    #        <real name="/science/LSAR/RSLC/swaths/frequencyA/HH"
    #            shape="complexDataFrequencyAShape"
    #            width="32">
    #        <annotation app="conformance"
    #                    lang="en"
    #                    units="1">Focused RSLC image (HH)</annotation>
    #        <annotation app="io" kwd="complex" />
    #        </real>

    # The "conformance" annotation holds the dataset's attributes and text
    # for the description.
    # The "io" annotation should only appear to designate a Dataset as
    # complex-valued.
    # There should not be any other annotations.

    # Verify "description" is not listed as an attribute. (The description
    # of a Dataset should instead be stored in the `element.text` XML field.)
    if "description" in annotation_attribs:
        log.error(
            f"{element.tag} annotation contains attribute 'description'."
            " This tag is deprecated; use the text field to describe"
            f" the element instead - XML Element: {dataset_name}"
        )
        # Delete the "description" attribute. (It should be in `element.text`.)
        # Note: in `generate_h5_datasets()` in `h5_parser.py``, if the HDF5
        # Dataset has a "description" Attribute, that Attribute is similarly
        # deleted from the attributes dictionary and stored in a separate
        # parameter.
        del annotation_attribs["description"]

    # Each XML annotation tag must contain an attribute named "app".
    if "app" not in annotation_attribs:
        log.error(
            f"{element.tag} annotation does not contain attribute 'app'."
            " This attribute is required for annotations -"
            f" XML Element {dataset_name}"
        )
    # The "app" attribute must set to be either "conformance" or "io".
    elif annotation_attribs["app"] == "conformance":
        # Annotations with "conformance" contain all information about HDF5
        # Attributes, the description, etc.
        # Verify that these are reasonably formed.
        if xml_node_type == nisarqa.XMLNodeType.string:
            # string datasets should never have a units attribute
            if "units" in annotation_attribs:
                log.error(
                    f"{element.tag} annotation contains attribute 'units' but is"
                    " attached to a node with type string. (String nodes should not"
                    f" have units). XML Element: {dataset_name}"
                )

        elif xml_node_type == nisarqa.XMLNodeType.shape:
            # shape elements do not have units
            pass
        elif dataset_name.endswith(
            tuple(nisarqa.numeric_dtype_should_not_have_units())
        ):
            # only certain numeric datasets should have a units attribute
            if "units" in annotation_attribs:
                log.error(
                    f"{element.tag} annotation contains attribute 'units' but"
                    " is attached to a node which should not have units."
                    f" XML Element: {dataset_name}"
                )
        else:
            if "units" not in annotation_attribs:
                log.error(
                    f"{element.tag} annotation does not contain attribute 'units'"
                    " but is attached to a node which should have units."
                    f" XML Element: {dataset_name}"
                )
            else:
                # "units" is an Attribute
                xml_units = str(annotation_attribs["units"])

                if xml_units == "":
                    log.error(
                        f'Empty "units" attribute in XML: Dataset {dataset_name}'
                    )

                # datetime template string check
                if nisarqa.contains_datetime_template_substring(
                    input_str=xml_units
                ):
                    xml_datetime_template = (
                        nisarqa.extract_datetime_template_substring(
                            input_str=xml_units, dataset_name=dataset_name
                        )
                    )
                    # (This function logs if there is a discrepancy)
                    nisarqa.verify_nisar_datetime_template_string(
                        datetime_template_string=xml_datetime_template,
                        dataset_name=dataset_name,
                    )

    # The "io" annotations are used to designate complex datasets.
    elif annotation_attribs["app"] != "io":
        log.error(
            f"{element.tag} annotation contains has 'app' attribute of"
            f" {annotation_attribs['app']=}, but only 'conformance' and"
            f" 'io' are supported. XML Element: {dataset_name}"
        )

    return nisarqa.XMLAnnotation(
        attributes=annotation_attribs, description=description
    )


__all__ = nisarqa.get_all(__name__, objects_to_skip)
