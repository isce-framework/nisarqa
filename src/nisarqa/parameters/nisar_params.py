from __future__ import annotations

import collections
import dataclasses
import io
import os
import sys
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, ClassVar, Optional, Type, Union

import h5py
from ruamel.yaml import YAML, CommentedMap, CommentedSeq

import nisarqa
from nisarqa.utils.typing import RootParamGroupT, RunConfigDict

objects_to_skip = nisarqa.get_all(name=__name__)

SerializableItem = Union[bool, int, float, str, None]
Serializable = Union[SerializableItem, list[SerializableItem]]


@dataclass
class YamlAttrs:
    """
    Dataclass to hold information about a parameter for the runconfig yaml.

    Parameters
    ----------
    name : str
        Name of the parameter parameter in a QA runconfig. Should be
        formatted in snakecase and no spaces.
    descr : str
        Detailed description of the yaml parameter, such as would appear
        in a runconfig. Should describe what the parameter is, its type,
        requirements, usage, examples, etc.
    """

    name: str
    descr: str


@dataclass
class HDF5Attrs:
    """
    Dataclass to hold information about a parameter for the stats.h5 file.

    Parameters
    ----------
    name : str
        Name of the HDF5 dataset as it should output to the stats.h5 file.
        It is suggested that this be formatted in camelCase with no spaces
        and the first letter lowercase. Acronyms like "RIFG" can be uppercase.
    units : str
        Units for this dataset; will be stored in a `units` attribute
        for the new Dataset.
        NISAR datasets use this convention:
            - If values have dimensions, use CF- and UDUNITS-compliant names.
              Units should be spelled out:
                  Correct: "meters"
                  Incorrect: "m"
              Units should favor math symbols:
                  Correct: "meters / second ^ 2"
                  Incorrect: "meters per second squared"
            - If values are numeric but dimensionless (e.g. ratios),
              set `ds_units` to "1" (the string "1").
            - If values are inherently descriptive and have no units
              (e.g. a file name, or a list of frequency names like: ['A', 'B']),
              then set `ds_units` to None so that no units attribute
              is created.
    descr : str
        Short one-line description of this parameter. Preferably,
        this should meet CF conventions; can be used for the stats.h5 file.
    group_path : str
        The HDF5 path to parent group for the `name` dataset
    """

    name: str
    units: str
    descr: str
    group_path: str


@dataclass(frozen=True)
class YamlParamGroup(ABC):
    """Abstract Base Class for creating *Params dataclasses."""

    @staticmethod
    @abstractmethod
    def get_path_to_group_in_runconfig():
        """
        Return the path to the group in the runconfig.

        For example, the dynamic ancillary file group in the NISAR runconfig
        is located via this nesting path:
              runconfig > groups > dynamic_ancillary_file_group
        So, get_path_to_group_in_runconfig() will return
              ['runconfig', 'groups', 'dynamic_ancillary_file_group']
        The first entry is a root group, and the final entry is
        the name of the group.

        Returns
        -------
        path_to_group : list of str
            The path in the runconfig file from root to group for this
            Params dataclass.
        """
        pass

    @classmethod
    def get_dict_of_yaml_names(cls):
        """
        For all attributes in this class that are also in the runconfig,
        return a dict mapping their class attribute name to their name
        as it appears in the runconfig.

        This will be parsed from each attribute's field metadata;
        specifically, it will be parsed from the 'yaml_attrs' key's
        YamlAttrs `name` attribute.

        Returns
        -------
        yaml_names : dict
            Dict mapping class attribute names to runconfig yaml names.
            Format: {<class_attribute_name> : <YamlAttrs object .name>}
            Types:  {<str> : <str>}
        """
        yaml_names = {}
        for field in fields(cls):
            if "yaml_attrs" in field.metadata:
                yaml_names[field.name] = field.metadata["yaml_attrs"].name

        if not yaml_names:
            # Sanity check - dict is still empty
            nisarqa.get_logger().warning(
                f"None of the attributes in {cls.__name__}"
                " contain info for an YamlAttrs object"
            )

        return yaml_names

    @classmethod
    def get_attribute_metadata(cls, attribute_name):
        """
        Get the attribute's field metadata.

        Returns
        -------
        metadata : dict
            Dict mapping class attribute names to runconfig yaml names.
            Format: {<class_attribute_name> : <YamlAttrs object .name>}
            Types:  {<str> : <str>}
        """
        for field in fields(cls):
            if attribute_name == field.name:
                return field.metadata
        else:
            raise ValueError(
                f"{attribute_name=} is not an attribute in {cls.__name__}"
            )

    def populate_user_runcfg(
        self, runconfig_cm: CommentedMap, indent: int = 4
    ) -> None:
        """
        Add this instance's final runconfig parameters to a commented map.

        Update the provided ruamel.yaml object with select attributes
        (parameters) of this dataclass instance for use in a NISAR product
        QA runconfig file

        Parameters
        ----------
        runconfig_cm : ruamel.yaml.comments.CommentedMap
            The base commented map; will be updated with the attributes
            from this class instance that are in the QA runconfig file.
        indent : int, optional
            Number of spaces per indent. Default: 4.

        Notes
        -----
        Reference: https://stackoverflow.com/questions/56471040/add-a-comment-in-list-element-in-ruamel-yaml

        See Also
        --------
        populate_default_runcfg :
            Class method to populate a commented map with only default
            runconfig parameters.
        """
        # build yaml params group
        params_cm = CommentedMap()

        # Add all attributes from this dataclass to the group
        for field in fields(self):
            if "yaml_attrs" in field.metadata:
                if field.default == dataclasses.MISSING:
                    msg = "REQUIRED"
                else:
                    msg = f"Default: {field.default}"

                yaml_attrs = field.metadata["yaml_attrs"]
                self.add_param_to_cm(
                    params_cm=params_cm,
                    name=yaml_attrs.name,
                    val=getattr(self, field.name),
                    comment=f"\n{yaml_attrs.descr}\n{msg}",
                    indent=indent,
                )

        if not params_cm:  # No attributes were added
            nisarqa.get_logger().warning(
                f"{type(self).__name__} is a subclass of YamlParamGroup"
                " but does not have any attributes whose"
                ' dataclasses.field metadata contains "yaml_attrs"'
            )
        else:
            # Add the new parameter group to the runconfig
            self.add_param_group_to_runconfig(runconfig_cm, params_cm)

    @classmethod
    def populate_default_runcfg(cls, runconfig_cm, indent=4):
        """
        Update the provided ruamel.yaml object with select attributes
        (parameters) of this dataclass object for use in a NISAR product
        QA runconfig file.

        Only default values will be used.

        Parameters
        ----------
        runconfig_cm : ruamel.yaml.comments.CommentedMap
            The base commented map; will be updated with the attributes
            from this dataclass that are in the QA runconfig file
        indent : int, optional
            Number of spaces per indent. Default: 4.

        Notes
        -----
        Reference: https://stackoverflow.com/questions/56471040/add-a-comment-in-list-element-in-ruamel-yaml

        See Also
        --------
        populate_user_runcfg :
            Instance method to populate a commented map with the final user
            runconfig parameters.
        """
        # build yaml params group
        params_cm = CommentedMap()

        # Add all attributes from this dataclass to the group
        for field in fields(cls):
            if "yaml_attrs" in field.metadata:
                if field.default == dataclasses.MISSING:
                    msg = "REQUIRED"

                    # in ruamel.yaml, providing None as a value causes
                    # the output .yaml to have an empty field argument.
                    # This indicates to a user that there is no default value.
                    val = None
                else:
                    msg = f"Default: {field.default}"
                    val = field.default

                yaml_attrs = field.metadata["yaml_attrs"]
                cls.add_param_to_cm(
                    params_cm=params_cm,
                    name=yaml_attrs.name,
                    val=val,
                    comment=f"\n{yaml_attrs.descr}\n{msg}",
                    indent=indent,
                )

        if not params_cm:  # No attributes were added
            nisarqa.get_logger().warning(
                f"{cls.__name__} is a subclass of YamlParamGroup"
                " but does not have any attributes whose"
                ' dataclasses.field metadata contains "yaml_attrs"'
            )
        else:
            # Add the new parameter group to the runconfig
            cls.add_param_group_to_runconfig(runconfig_cm, params_cm)

    @classmethod
    def add_param_to_cm(
        cls,
        params_cm: CommentedMap,
        name: str,
        val: Any,
        comment: str | None = None,
        indent: int = 4,
    ) -> None:
        """
        Add a new attribute to a Commented Map.

        This can be used to add a new parameter into a group for a runconfig.

        Parameters
        ----------
        params_cm : ruamel.yaml.comments.CommentedMap
            Commented Map for a parameter group in the runconfig.
            Will be updated to include `param_attr`.
        name : str
            Parameter name, as it should appear in `params_cm`.
        val : Any
            Parameter value, as it should appear in `params_cm`.
        comment : str or None, optional
            Parameter comment (description), as it should appear in `params_cm`.
            If None, then no comment will be added. Defaults to None.
        indent : int, optional
            Number of spaces of an indent. Defaults to 4.
        """
        # set indentation for displaying the comments correctly in the yaml
        comment_indent = len(cls.get_path_to_group_in_runconfig()) * indent

        # Prep the value to be type(s) that can be represented by ruamel.yaml
        def _yaml_encode(obj: Any) -> Serializable:
            if isinstance(obj, (bool, int, float, str)) or (obj is None):
                return obj
            elif isinstance(obj, os.PathLike):
                # ruamel.yaml cannot represent Path objects, and it poorly
                # displays bytes objects. Convert to string via `os.fsdecode()`.
                # (`os.fspath()` returns bytes objects as-is; not ok for yaml.)
                return os.fsdecode(obj)
            elif isinstance(obj, Iterable):
                return [_yaml_encode(item) for item in obj]
            raise NotImplementedError(
                f"{obj=} with type {type(obj)=}, which is not a supported type."
            )

        yaml_val = _yaml_encode(val)

        # To have ruamel.yaml display list values as a list in the runconfig,
        # use CommentedSeq
        # https://stackoverflow.com/questions/56937691/making-yaml-ruamel-yaml-always-dump-lists-inline
        if isinstance(yaml_val, list):
            seq = CommentedSeq()
            seq.fa.set_flow_style()
            for item in yaml_val:
                if isinstance(item, list):
                    raise NotImplementedError("Nested lists not supported.")
                seq.append(item)
            yaml_val = seq

        # Add parameter to the group
        params_cm[name] = yaml_val

        # If provided, add comment
        if comment is not None:
            for line in nisarqa.multi_line_string_iter(comment):
                params_cm.yaml_set_comment_before_after_key(
                    name, before=line, indent=comment_indent
                )

    @classmethod
    def add_param_group_to_runconfig(cls, yaml_cm, params_cm):
        """
        Add a new group of parameters to a yaml Commented Map
        along the nested directory structure specified by
        `get_path_to_group_in_runconfig()`.

        In the process, this function will check that the nested structure
        specified in get_path_to_group_in_runconfig() exists.
        If not, the missing commented maps are created.

        Parameters
        ----------
        yaml_cm : ruamel.yaml.comments.CommentedMap
            Commented Map object that holds the runconfig information.
            This will be updated to include `param_cm` added
            along the path specified by `get_path_to_group_in_runconfig()`.
        params_cm : ruamel.yaml.comments.CommentedMap
            A Commented Map populated with the parameters, etc. to be
            added to `yaml_cm` in the group specified by
            `get_path_to_group_in_runconfig()`.
        """
        path = cls.get_path_to_group_in_runconfig()

        # start at root Commented Map
        parent_cm = yaml_cm

        # Traverse to the direct parent CM group for this params_cm.
        # Ensure all parent groups for this params_cm exist
        for group in path[:-1]:
            # If group does not exist, create it
            if group not in parent_cm:
                parent_cm[group] = CommentedMap()

                # For readability, add a newline before this new group
                parent_cm.yaml_set_comment_before_after_key(group, before="\n")

            # Move into the next nested group
            parent_cm = parent_cm[group]

        # Attach new params_cm group into the runconfig yaml
        parent_cm[path[-1]] = params_cm

        # For readability, add a newline before the new params_cm group
        parent_cm.yaml_set_comment_before_after_key(path[-1], before="\n")

    @staticmethod
    def _validate_pair_of_numeric(
        param_value: Optional[Sequence[int | float]],
        param_name: str,
        min: Optional[int | float] = None,
        max: Optional[int | float] = None,
        none_is_valid_value: bool = False,
        strictly_increasing: bool = False,
    ) -> None:
        """
        Raise exception if `param_value` is not a valid input.

        Parameters
        ----------
        param_value : None or pair of int or float
            Sequence of two int or float value, or None.
        param_name : str
            Name of this parameter. Will be used for the error message.
        min, max : None or int or float, optional
            The minimum or maximum allowed values (respectively) for each value in
            `param_value`. `param_value` may not be outside this range.
        none_is_valid_value : bool, optional
            True if `param_value` should be considered valid if it is `None`.
            Note: This flag is for the entire value of the parameter; if the
            parameter is set to e.g. `[None, 1.0]`, this flag not relevant.
            Defaults to False.
        strictly_increasing : bool, optional
            True if `input_value[0]` must be less than `input_value[1]`.
            Defaults to False.
        """
        if param_value is None:
            if none_is_valid_value:
                return
            else:
                raise TypeError(
                    f"`{param_name}` is None, but must be a pair of numeric."
                )

        if not isinstance(param_value, Sequence):
            msg = f"`{param_name}` must be a sequence"
            if none_is_valid_value:
                msg += " or None."
            raise TypeError(msg)

        if len(param_value) != 2:
            raise ValueError(
                f"{param_name}={param_value}; must have a length of two."
            )

        if not all(isinstance(e, (float, int)) for e in param_value):
            raise TypeError(
                f"{param_name}={param_value}; must contain only float or int."
            )

        if (min is not None) and (any((e < min) for e in param_value)):
            raise ValueError(
                f"{param_name}={param_value}; must be in range [{min}, {max}]."
            )

        if (max is not None) and (any((e > max) for e in param_value)):
            raise ValueError(
                f"{param_name}={param_value}; must be in range [{min}, {max}]."
            )

        if strictly_increasing:
            if param_value[0] >= param_value[1]:
                raise ValueError(
                    f"{param_name}={param_value}; values must be"
                    " strictly increasing."
                )

    @classmethod
    def get_field_with_updated_default(
        cls, param_name: str, default: Any
    ) -> dataclasses.Field:
        """
        Return the Field object for a class parameter with an updated default.

        Parameters
        ----------
        param_name : str
            One of the class parameters of this class.
        default : object
            The desired default value for the parameter.

        Returns
        -------
        updated_field : dataclasses.Field
            A Field object with the updated default value. All other
            aspects of `ThresholdParamGroup` class' version of the Field
            object remain unchanged (for example, the `metadata` which contains
            the description is unchanged).

        Examples
        --------
        When subclassing, override the parent's parameter like this:
        ```
        nan_threshold: float = (
            nisarqa.YamlParamGroup.get_field_with_updated_default(
                param_name="nan_threshold", default=0
            )
        )
        ```
        """

        for f in fields(cls):
            if f.name == param_name:
                metadata = f.metadata
                return field(default=default, metadata=metadata)
        else:
            raise ValueError(
                f"`{param_name=}`, must be a parameter in `{cls.__name__}`"
            )


class HDF5ParamGroup:
    """Class for parameters that will be stored in the output HDF5 file."""

    def get_units_from_hdf5_metadata(self, attribute_name):
        """
        Return the value of the input attribute's HDF5Attrs `units` metadata.

        Parameters
        ----------
        attribute_name : str
            Name of the class attribute to parse the HDF5Attrs
            `units` value from

        Returns
        -------
        units : str
            The value of the `units` attribute of the HDF5Attrs metadata
            for this instance's attribute `attribute_name`.
        """
        for field in fields(self):
            if field.name == attribute_name:
                if "hdf5_attrs" in field.metadata:
                    return field.metadata["hdf5_attrs"].units
                elif "hdf5_attrs_func" in field.metadata:
                    return field.metadata["hdf5_attrs_func"](self).units
                else:
                    raise TypeError(
                        f"The field metadata for `{attribute_name}`"
                        " does not contain info for an HDF5Attrs"
                        " object"
                    )

        # If the request field was not found, raise an error
        raise KeyError(
            f"`{attribute_name}` is not an attribute of this dataclass."
        )

    def write_params_to_h5(self, h5_file, band):
        """
        Update `h5_file` with the attributes of this dataclass
        that are a subclass of HDF5Param.

        Parameters
        ----------
        h5_file : h5py.File
            Handle to an HDF5 file where the parameter metadata
            should be saved
        band : str
            The letter of the band. Ex: "L" or "S".
        """

        # Flag -- the intention is to help assist developers and ensure
        # child classes are set up correctly
        found_at_least_one_hdf5_attr = False

        # Add all attributes from this dataclass to the group
        for field in fields(self):
            if ("hdf5_attrs" in field.metadata) or (
                "hdf5_attrs_func" in field.metadata
            ):
                attr = getattr(self, field.name)

                # Create filler data to stand in for Python's Nonetype.
                # This is for cases such as gamma=None (not a float)
                val = "None" if attr is None else attr

                if "hdf5_attrs" in field.metadata:
                    hdf5_attrs = field.metadata["hdf5_attrs"]
                else:
                    hdf5_attrs = field.metadata["hdf5_attrs_func"](self)

                nisarqa.create_dataset_in_h5group(
                    h5_file=h5_file,
                    grp_path=hdf5_attrs.group_path % band,
                    ds_name=hdf5_attrs.name,
                    ds_data=val,
                    ds_units=hdf5_attrs.units,
                    ds_description=hdf5_attrs.descr,
                )

                found_at_least_one_hdf5_attr = True

        if not found_at_least_one_hdf5_attr:
            # No attributes in this class were added to stats.h5.
            # Since this class is specifically for HDF5 parameters, this
            # is probably cause for concern because something was not
            # set up (coded) properly elsewhere.
            nisarqa.get_logger().warning(
                f"{self.__name__} is a subclass of HDF5ParamGroup"
                " but does not have any attributes whose"
                " dataclasses.field metadata contains 'hdf5_attrs'"
                " or 'hdf5_attrs_func'"
            )


@dataclass(frozen=True)
class ThresholdParamGroup(YamlParamGroup):
    """
    Abstract Base Class for creating *Params dataclasses with thresholds.

    Parameters
    ----------
    nan_threshold, inf_threshold, fill_threshold, near_zero_threshold,
        total_invalid_threshold : float, optional
        Threshold value for alerting users to possible malformed datasets.
        If the percentage of NaN-, Inf-, fill-, near-zero-, or total
        invalid-valued pixels is above the respective threshold, it will be
        logged as an error and an exception raised.
        "Total invalid pixels" is the sum of NaN, Inf, & fill pixels.
        If `zero_is_invalid` is True, near-zero-valued pixels are also
        included in the total count of invalid pixels.
        Each threshold should be between 0 and 100.
        Setting a threshold to -1 causes that threshold to be effectively
        ignored (e.g. any percent of NaN values is fine; it will be noted as
        info, and will not trigger a QA failure).
        Setting a threshold to 0 triggers a QA failure if the dataset
        contains any pixels with that value.
        All default to `nisarqa.STATISTICS_THRESHOLD_PERCENTAGE`.
    epsilon : float, optional
        Absolute tolerance for determining if a raster pixel is 'almost zero'.
        Defaults to 1e-6.
    zero_is_invalid: bool, optional
        True if near-zero pixels should be counted towards the
        total number of invalid pixels. False to exclude them.
        If False, consider setting `near_zero_threshold` to -1.
        Note: fill values are always considered invalid, so if a raster's
        fill value is zero, then zeros will still be included in the total.
        Defaults to True.

    Notes
    -----
    When subclassing, to update the default for a particular threshold value,
    suggest using the class method `get_field_with_updated_default()`.
    """

    _threshold_descr_template: ClassVar[str] = (
        "Percent of %s pixels per total raster area allowed"
    )

    nan_threshold: float = field(
        default=nisarqa.STATISTICS_THRESHOLD_PERCENTAGE,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="nan_threshold",
                # This description will be printed first in the runconfig,
                # so have it describe all of the threshold parameters.
                # For subsequent parameters, use a short version.
                # (This helps keep the runconfig shorter and easier to read.)
                descr=f"""*** Threshold Percentage Parameters ***
        Check for malformed datasets using these threshold percentages.
        An exception is raised if the percent of pixels with the corresponding value
        per the total raster area exceeds the threshold percentage provided.
        Thresholds must be in the interval [0, 100], or -1 to be ignored.
        (-1 logs the percentages as INFO, but will not trigger a QA failure.)

        {_threshold_descr_template % 'NaN'}""",
            )
        },
    )

    inf_threshold: float = field(
        default=nisarqa.STATISTICS_THRESHOLD_PERCENTAGE,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="inf_threshold",
                descr=_threshold_descr_template % "+/- Inf",
            )
        },
    )

    fill_threshold: float = field(
        default=nisarqa.STATISTICS_THRESHOLD_PERCENTAGE,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="fill_threshold",
                descr=_threshold_descr_template % "Fill-valued",
            )
        },
    )

    near_zero_threshold: float = field(
        default=nisarqa.STATISTICS_THRESHOLD_PERCENTAGE,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="near_zero_threshold",
                descr=_threshold_descr_template % "Near-zero",
            )
        },
    )

    total_invalid_threshold: float = field(
        default=nisarqa.STATISTICS_THRESHOLD_PERCENTAGE,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="total_invalid_threshold",
                descr=(
                    f"{_threshold_descr_template % 'total invalid'}\n"
                    "'Total invalid pixels' is the sum of NaN, Inf, fill,"
                    " & (if `zero_is_invalid` is True) near-zero pixels."
                ),
            )
        },
    )

    epsilon: float = field(
        default=1e-6,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="epsilon",
                descr=(
                    "Absolute tolerance for determining if a raster pixel"
                    " is 'near zero'."
                ),
            ),
        },
    )

    zero_is_invalid: bool = field(
        default=True,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="zero_is_invalid",
                descr="""True if near-zero pixels should be counted towards the
                    total number of invalid pixels. False to exclude them.
                    If False, consider setting `near_zero_threshold` to -1.
                    Note: fill values are always considered invalid, so if a raster's
                    fill value is zero, then zeros will still be included in the total.""",
            ),
        },
    )

    def __post_init__(self):
        # VALIDATE INPUTS

        for name, thresh in zip(
            (
                "nan_threshold",
                "near_zero_threshold",
                "fill_threshold",
                "inf_threshold",
                "total_invalid_threshold",
            ),
            (
                self.nan_threshold,
                self.near_zero_threshold,
                self.fill_threshold,
                self.inf_threshold,
                self.total_invalid_threshold,
            ),
        ):
            if thresh != -1:
                try:
                    nisarqa.verify_valid_percent(thresh)
                except ValueError:
                    raise ValueError(
                        f"`{name}` is {thresh}, must be in range [0.0, 100.0]"
                        " or -1."
                    )

        if self.epsilon < 0:
            raise ValueError(f"`{self.epsilon=}`, must be >= 0.")


@dataclass(frozen=True)
class ZeroIsValidThresholdParamGroup(ThresholdParamGroup):
    """
    `ThresholdParamGroup` but with defaults of zeros as valid and all-zeros ok.

    Parameters
    ----------
    nan_threshold, inf_threshold, fill_threshold, near_zero_threshold,
        total_invalid_threshold : float, optional
        Threshold values for alerting users to possible malformed datasets.
        See `ThresholdParamGroup` docstring for complete description.
        Default for NaN, Inf, fill, and total thresholds:
            `nisarqa.STATISTICS_THRESHOLD_PERCENTAGE`.
        Default for near-zero threshold: -1.
    epsilon : float, optional
        Absolute tolerance for determining if a raster pixel is 'almost zero'.
        Defaults to 1e-6.
    zero_is_invalid: bool, optional
        True if near-zero pixels should be counted towards the
        total number of invalid pixels. False to exclude them.
        If False, consider setting `near_zero_threshold` to -1.
        Note: Fill values are always considered invalid. So, if a raster's
        fill value is zero, then zeros will still be included in the total.
        Defaults to False.
    """

    near_zero_threshold: float = (
        ThresholdParamGroup.get_field_with_updated_default(
            param_name="near_zero_threshold", default=-1
        )
    )

    zero_is_invalid: float = ThresholdParamGroup.get_field_with_updated_default(
        param_name="zero_is_invalid", default=False
    )


@dataclass(frozen=True)
class Threshold99ParamGroup(ThresholdParamGroup):
    """
    ABC for creating *Params dataclasses with default thresholds of 99%.

    Typically, geocoded L2 products should use defaults of 99% for thresholds

    Parameters
    ----------
    nan_threshold, inf_threshold, fill_threshold, near_zero_threshold,
        total_invalid_threshold : float, optional
        Threshold values for alerting users to possible malformed datasets.
        See `ThresholdParamGroup` docstring for complete description.
        All thresholds default to 99.0%.
    epsilon : float, optional
        Absolute tolerance for determining if a raster pixel is 'almost zero'.
        Defaults to 1e-6.
    zero_is_invalid: bool, optional
        True if near-zero pixels should be counted towards the
        total number of invalid pixels. False to exclude them.
        If False, consider setting `near_zero_threshold` to -1.
        Note: fill values are always considered invalid, so if a raster's
        fill value is zero, then zeros will still be included in the total.
        Defaults to True.

    Notes
    -----
    When subclassing, to update the default for a particular threshold value,
    suggest using the class method `get_field_with_updated_default()`.
    """

    nan_threshold: float = ThresholdParamGroup.get_field_with_updated_default(
        param_name="nan_threshold", default=99.0
    )
    inf_threshold: float = ThresholdParamGroup.get_field_with_updated_default(
        param_name="inf_threshold", default=99.0
    )
    fill_threshold: float = ThresholdParamGroup.get_field_with_updated_default(
        param_name="fill_threshold", default=99.0
    )
    near_zero_threshold: float = (
        ThresholdParamGroup.get_field_with_updated_default(
            param_name="near_zero_threshold", default=99.0
        )
    )
    total_invalid_threshold: float = (
        ThresholdParamGroup.get_field_with_updated_default(
            param_name="total_invalid_threshold", default=99.0
        )
    )


@dataclass(frozen=True)
class ZeroIsValidThreshold99ParamGroup(Threshold99ParamGroup):
    """
    `Threshold99ParamGroup` but w/ defaults of zeros as valid and all-zeros ok.

    Parameters
    ----------
    nan_threshold, inf_threshold, fill_threshold, near_zero_threshold,
        total_invalid_threshold : float, optional
        Threshold values for alerting users to possible malformed datasets.
        See `ThresholdParamGroup` docstring for complete description.
        Default for NaN, Inf, fill, and total thresholds: 99.0%
        Default for near-zero threshold: -1.
    epsilon : float, optional
        Absolute tolerance for determining if a raster pixel is 'almost zero'.
        Defaults to 1e-6.
    zero_is_invalid: bool, optional
        True if near-zero pixels should be counted towards the
        total number of invalid pixels. False to exclude them.
        If False, consider setting `near_zero_threshold` to -1.
        Note: Fill values are always considered invalid. So, if a raster's
        fill value is zero, then zeros will still be included in the total.
        Defaults to False.
    """

    near_zero_threshold: float = (
        ThresholdParamGroup.get_field_with_updated_default(
            param_name="near_zero_threshold", default=-1
        )
    )

    zero_is_invalid: float = ThresholdParamGroup.get_field_with_updated_default(
        param_name="zero_is_invalid", default=False
    )


@dataclass(frozen=True)
class WorkflowsParamGroup(YamlParamGroup):
    """
    The parameters specifying which QA workflows should be run.

    This corresponds to the `workflows` runconfig group.

    Attributes
    ----------
    validate : bool, optional
        True to run the validate workflow. Default: True
    qa_reports : bool, optional
        True to run the QA Reports workflow. Default: True
    """

    # default value for all workflows
    _default_val: ClassVar[bool] = True

    # Generic description for all workflows
    _descr: ClassVar[str] = f"Flag to run %s."

    validate: bool = field(
        default=_default_val,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="validate",
                descr=_descr % "`validate` workflow to validate the\n"
                " input file against its product spec",
            )
        },
    )

    qa_reports: bool = field(
        default=_default_val,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="qa_reports",
                descr=_descr % "`qa_reports` workflow to generate a\n"
                "PDF report, geolocated browse image, compute statistics\n"
                "on the input file, etc.",
            )
        },
    )

    def __post_init__(self):
        self._check_workflows_arg("validate", self.validate)
        self._check_workflows_arg("qa_reports", self.qa_reports)

    @staticmethod
    def get_path_to_group_in_runconfig():
        return ["runconfig", "groups", "qa", "workflows"]

    @staticmethod
    def _check_workflows_arg(attr_name, val):
        """
        Validate that `val` is of the correct type for the
        WorkflowsParamGroup's attribute `attr_name`.

        Parameters
        ----------
        attr_name : str
            The name of the attribute of WorkflowsParamGroup for `attr`
        val : bool
            Argument value for `attr_name`.
        """
        # Validate `val`
        if not isinstance(val, bool):
            raise TypeError(
                f"`{attr_name}` must be of type bool. It is {type(val)}"
            )

    def at_least_one_wkflw_requested(self):
        """
        Return True if at least one of this instance's workflow attributes
        (e.g. `validate` or `qa_reports`) is True.

        Returns
        -------
        at_least_one_true_wkflw : bool
            True if at least one of the workflow field attributes in this
            instance is True. False is all workflows are set to False.
        """
        return any(getattr(self, field.name) for field in fields(self))


@dataclass(frozen=True)
class InputFileGroupParamGroup(YamlParamGroup):
    """
    Parameters from the Input File Group runconfig group.

    This corresponds to the `groups: input_file_group` runconfig group.

    Parameters
    ----------
    qa_input_file : str
        The input NISAR product file name (with path).
    """

    # Required parameter - do not set a default
    qa_input_file: str = field(
        metadata={
            "yaml_attrs": YamlAttrs(
                name="qa_input_file",
                descr="""Filename of the input file for QA.
                REQUIRED for QA. NOT REQUIRED if only running Product SAS.
                If Product SAS and QA SAS are run back-to-back,
                this field should be identical to `sas_output_file`.
                Otherwise, this field should contain the filename of the single
                NISAR product for QA to process.""",
            )
        }
    )

    def __post_init__(self):
        # VALIDATE INPUTS
        nisarqa.validate_is_file(
            filepath=self.qa_input_file,
            parameter_name="qa_input_file",
            extension=".h5",
        )

    @staticmethod
    def get_path_to_group_in_runconfig():
        return ["runconfig", "groups", "input_file_group"]


@dataclass(frozen=True)
class ProductPathGroupParamGroup(YamlParamGroup):
    """
    Parameters from the Product Path Group runconfig group.

    This corresponds to the `groups: product_path_group` runconfig group.

    Parameters
    ----------
    qa_output_dir : path-like, optional
        Filepath to the output directory to store NISAR QA output files.
        If the directory does not exist, it will be created.
        Defaults to './qa'
    scratch_dir_parent : path-like, optional
        Directory where software may write temporary data.
        If the directory does not exist, it will be created.
        Because this scratch directory might be shared with e.g. ISCE3
        science product SASes, QA will create a uniquely-named
        directory inside `scratch_dir_parent` for any QA scratch files.
        Defaults to './scratch'
    """

    qa_output_dir: str | os.PathLike = field(
        default="./qa",
        metadata={
            "yaml_attrs": YamlAttrs(
                name="qa_output_dir",
                descr="""Output directory to store all QA output files.
                If the directory does not exist, it will be created.""",
            )
        },
    )

    scratch_dir_parent: str | os.PathLike = field(
        default="./scratch",
        metadata={
            "yaml_attrs": YamlAttrs(
                name="scratch_path",
                descr="""Directory where software may write temporary data.
                If the directory does not exist, it will be created.
                Because this scratch directory might be shared with e.g. ISCE3
                science product SASes, QA will create a uniquely-named
                directory inside `scratch_path` for any QA scratch files.""",
            )
        },
    )

    def __post_init__(self):
        # VALIDATE INPUTS

        for param_name in ("qa_output_dir", "scratch_dir_parent"):
            val = getattr(self, param_name)
            if not isinstance(val, (str, os.PathLike)):
                raise TypeError(f"`{param_name}` must be path-like")

            # If this directory does not exist, make it.
            if not os.path.isdir(val):
                log = nisarqa.get_logger()
                log.info(f"Creating {param_name} directory: '{val}'")
                os.makedirs(val, exist_ok=True)

    @staticmethod
    def get_path_to_group_in_runconfig():
        return ["runconfig", "groups", "product_path_group"]


@dataclass(frozen=True)
class SoftwareConfigParamGroup(YamlParamGroup):
    """
    Parameters from the Software Config Group runconfig group.

    Parameters
    ----------
    use_cache : bool, optional
        True to cache selected dataset(s) into intermediate
        memory-mapped flat file(s), which speeds up repeat access.
        False to always read data directly from the input file.
        Generally, enabling caching should reduce runtime.
        Defaults to True.
    delete_scratch_files : bool, optional
        True to delete the nested QA scratch directory and its contents
        from inside `scratch_dir_parent` when QA SAS is finished.
        Defaults to True.
    """

    use_cache: bool = field(
        default=True,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="use_cache",
                descr="""True to cache selected dataset(s) into intermediate
                memory-mapped flat file(s), which speeds up repeat access.
                False to always read data directly from the input file.
                Generally, enabling caching should reduce runtime.""",
            )
        },
    )

    # For NISAR mission operations, the scratch directory parameter will be
    # shared by QA with the L1/L2 ISCE3 Science Data product SASes.
    # Those SASes do not delete the scratch directory, and QA should not either.
    delete_scratch_files: bool = field(
        default=True,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="delete_qa_scratch_files",
                descr="""True to delete the nested QA scratch directory in
                `scratch_path` and its contents when QA SAS is finished.""",
            )
        },
    )

    def __post_init__(self):
        # VALIDATE INPUTS
        if not isinstance(self.use_cache, bool):
            raise TypeError(f"`{self.use_cache=}`, must be bool.")

        if not isinstance(self.delete_scratch_files, bool):
            raise TypeError(f"`{self.delete_scratch_files=}`, must be bool.")

    @staticmethod
    def get_path_to_group_in_runconfig():
        return ["runconfig", "groups", "qa", "software_config"]


@dataclass(frozen=True)
class ValidationGroupParamGroup(YamlParamGroup):
    """
    Parameters from the Validation Group runconfig group.

    Parameters
    ----------
    metadata_luts_fail_if_all_nan : str
        True to raise an exception if one or more metadata LUTs contain
        all non-finite (e.g. Nan, +/- Inf) values, or if one or more
        z-dimension height layers in a 3D LUT ("metadata cube") has
        all non-finite values.
        False to quiet the exception (although it will still be logged).
        Defaults to True.
    """

    metadata_luts_fail_if_all_nan: bool = field(
        default=True,
        metadata={
            "yaml_attrs": YamlAttrs(
                name="metadata_luts_fail_if_all_nan",
                descr="""True to raise an exception if one or more metadata LUTs
                contain all non-finite (e.g. Nan, +/- Inf) values, or if one or more
                z-dimension height layers in a 3D LUT ("metadata cube") has
                all non-finite values. False to quiet the exception (although
                it will still be logged).""",
            )
        },
    )

    def __post_init__(self):
        # VALIDATE INPUTS
        if not isinstance(self.metadata_luts_fail_if_all_nan, bool):
            raise TypeError(
                f"`{self.metadata_luts_fail_if_all_nan=}`, must be bool."
            )

    @staticmethod
    def get_path_to_group_in_runconfig():
        return ["runconfig", "groups", "qa", "validation"]


@dataclass
class RootParamGroup(ABC):
    """Abstract Base Class for all NISAR Products' *RootParamGroup"""

    workflows: WorkflowsParamGroup
    input_f: Optional[InputFileGroupParamGroup] = None
    prodpath: Optional[ProductPathGroupParamGroup] = None
    software_config: Optional[SoftwareConfigParamGroup] = None
    validation: Optional[ValidationGroupParamGroup] = None

    # Create a namedtuple which maps the workflows requested
    # in `workflows` to their corresponding *RootParamGroup attribute(s)
    # and runconfig groups.
    # Structure of each namedtuple:
    # (<bool of whether the requested workflows require this *ParamGroup>,
    #     <str name of the *RootParamGroup attribute to store the *ParamGroup>,
    #         <class object for the corresponding *ParamGroup>)
    ReqParamGrp: ClassVar[collections.namedtuple] = collections.namedtuple(
        typename="ReqParamGrp",
        field_names=[
            "flag_param_grp_req",
            "root_param_grp_attr_name",
            "param_grp_cls_obj",
        ],
    )

    def __post_init__(self):
        # Ensure that the minimum parameters were provided
        msg = (
            "`%s` parameter of type `%s` is required for the requested "
            "QA workflow(s)."
        )

        mapping_of_req_wkflws2params = (
            self.get_mapping_of_workflows2param_grps_from_self()
        )

        for param_grp in mapping_of_req_wkflws2params:
            if param_grp.flag_param_grp_req:
                attr = getattr(self, param_grp.root_param_grp_attr_name)
                if not isinstance(attr, param_grp.param_grp_cls_obj):
                    raise TypeError(
                        msg
                        % (
                            param_grp.root_param_grp_attr_name,
                            str(param_grp.param_grp_cls_obj),
                        )
                    )

    def get_mapping_of_workflows2param_grps_from_self(self):
        """Wrapper to call `get_mapping_of_workflows2param_grps` on
        the current instance of *RootParamGroup"""
        return self.get_mapping_of_workflows2param_grps(self.workflows)

    @staticmethod
    @abstractmethod
    def get_mapping_of_workflows2param_grps(workflows):
        """
        Return a tuple of tuples which map the workflows requested in this
        class' WorkflowsParamGroup attribute to their corresponding
        *RootParamGroup attribute(s) and runconfig groups.

        Parameters
        ----------
        workflows : WorkflowsParamGroup
            An instance of WorkflowsParamGroup with attributes that correspond
            to this product's *RootParams object.

        Returns
        -------
        grps_to_parse : Tuple of RootParamGroup.ReqParamGrp
            This tuple maps the workflows requested in the WorkflowsParamGroup
            attribute to their corresponding *RootParamGroup attribute(s)
            and runconfig groups.
            Structure of each inner named tuple:

            (<bool of whether the requested workflows require this *ParamGroup>,
                <str name of the *RootParamGroup attribute to store the *ParamGroup>,
                    <class object for the corresponding *ParamGroup>)
        """
        pass

    @staticmethod
    @abstractmethod
    def get_order_of_groups_in_yaml() -> dict[str, type[YamlParamGroup]]:
        """
        Return the order that parameter groups should appear in the output
        runconfig template file.

        Returns
        -------
        param_group_class_objects : tuple of *ParamGroup class objects
            Tuple containing the *ParamGroup class objects for the
            fields in this *RootParamGroup class. The order that these
            *ParamGroup objects appear in the tuple is the order that
            they will appear in the output runconfig yaml template file.

        Examples
        --------
        A call to `RSLCRootParamGroup.get_order_of_groups_in_yaml()`
        would return**:

            {
                "input_f": InputFileGroupParamGroup,
                "anc_files": DynamicAncillaryFileParamGroup,
                "prodpath": ProductPathGroupParamGroup,
                "workflows": RSLCWorkflowsParamGroup,
                "validation": ValidationGroupParamGroup,
                "backscatter_img": BackscatterImageParamGroup,
                "histogram": HistogramParamGroup,
                "range_spectra": RangeSpectraParamGroup,
                "az_spectra": AzimuthSpectraParamGroup,
                "abs_cal": AbsCalParamGroup,
                "pta": PointTargetAnalyzerParamGroup,
            }

        ** Exact RSLC groups are subject to change, based on code updates
           and new features added to RSLC QA-SAS.
        """
        pass

    def get_final_user_runconfig(self) -> str:
        """
        Get the final QA runconfig with complete processing parameters.

        Returns
        -------
        user_runconfig : str
            Copy of the runconfig with final parameters used for QA processing.
            Includes comments. Can be saved into a txt file and used
            to re-run the QA SAS.

        See Also
        --------
        dump_runconfig_template :
            Class method to dump the default runconfig template to stdout.
        """
        # Build a ruamel yaml object that contains the runconfig structure
        yaml = YAML()

        # Here, the `mapping` parameter sets the size of an indent for the
        # mapping keys (aka the variable names) in the output yaml file. But,
        # it does not set the indent for the in-line comments in the output
        # yaml file; the indent spacing for inline comments will need to be
        # set later while creating the commented maps.
        # Re: `sequence` and `offset` parameters -- At the time of writing,
        # the current QA implementation of `add_param_to_cm` specifies that
        # lists should always be dumped inline, which means that these
        # `sequence` and `offset` parameters are a moot point. However,
        # should that underlying implementation change, settings sequence=4,
        # offset=2 results in nicely-indented yaml files.
        # Ref: https://yaml.readthedocs.io/en/latest/detail.html#indentation-of-block-sequences
        indent = 4
        yaml.indent(mapping=indent, sequence=indent, offset=max(indent - 2, 0))

        usr_runconfig_cm = CommentedMap()

        # Populate the yaml object. This order determines the order
        # the groups will appear in the runconfig.
        param_group_attr_names = self.get_order_of_groups_in_yaml().keys()

        # We're trying to loop over all fields in `self` (each field corresponds
        # to a group in the runconfig) but in the particular order specified by
        # `self.get_order_of_groups_in_yaml()`.

        for next_attr_name in param_group_attr_names:
            # Fetch this instance's version of that class object
            instance_attr = getattr(self, next_attr_name)
            if instance_attr is None:
                # This instance's attribute was set to None, so do
                # not add it to the runconfig.
                continue

            # Append to the user runconfig commented map
            instance_attr.populate_user_runcfg(usr_runconfig_cm, indent=indent)

        # return as a string
        output = io.StringIO()
        yaml.dump(usr_runconfig_cm, output)
        return output.getvalue()

    @classmethod
    def dump_runconfig_template(cls, indent=4):
        """Output the runconfig template (with default values) to stdout.

        Parameters
        ----------
        indent : int, optional
            Number of spaces of an indent. Defaults to 4.

        See Also
        --------
        get_final_user_runconfig :
            Instance method to return the final user runconfig to str.
        """

        # Build a ruamel yaml object that contains the runconfig structure
        yaml = YAML()

        # Here, the `mapping` parameter sets the size of an indent for the
        # mapping keys (aka the variable names) in the output yaml file. But,
        # it does not set the indent for the in-line comments in the output
        # yaml file; the indent spacing for inline comments will need to be
        # set later while creating the commented maps.
        # Re: `sequence` and `offset` parameters -- At the time of writing,
        # the current QA implementation of `add_param_to_cm` specifies that
        # lists should always be dumped inline, which means that these
        # `sequence` and `offset` parameters are a moot point. However,
        # should that underlying implementation change, settings sequence=4,
        # offset=2 results in nicely-indented yaml files.
        # Ref: https://yaml.readthedocs.io/en/latest/detail.html#indentation-of-block-sequences
        yaml.indent(mapping=indent, sequence=indent, offset=max(indent - 2, 0))

        runconfig_cm = CommentedMap()

        # Populate the yaml object. This order determines the order
        # the groups will appear in the runconfig.
        param_group_class_objects = cls.get_order_of_groups_in_yaml().values()

        for param_grp in param_group_class_objects:
            param_grp.populate_default_runcfg(runconfig_cm, indent=indent)

        # output to console. Let user stream that into a file.
        yaml.dump(runconfig_cm, sys.stdout)

    def save_processing_params_to_stats_h5(
        self, h5_file: h5py.File, band: str
    ) -> None:
        """
        Populate the HDF5 file's processing group with QA processing parameters.

        This function updates the "processing" group in `h5_file` with each
        parameter in this instance of *RootParams that contains `hdf5_attrs`
        metadata. It also adds the QA software version.

        Parameters
        ----------
        h5_file : h5py.File
            Handle to an HDF5 file where processing metadata should be saved.
        band : str
            The letter of the band. Ex: "L" or "S".
        """
        for params_obj in fields(self):
            po = getattr(self, params_obj.name)
            # If a workflow was not requested, its RootParams attribute
            # will be None, so there will be no params to add to the HDF5 file
            if po is not None:
                if issubclass(type(po), HDF5ParamGroup):
                    po.write_params_to_h5(h5_file, band=band)

        # Add QA version to stats file
        nisarqa.create_dataset_in_h5group(
            h5_file=h5_file,
            grp_path=nisarqa.STATS_H5_QA_PROCESSING_GROUP % band,
            ds_name="QASoftwareVersion",
            ds_data=nisarqa.__version__,
            ds_description="QA software version used for processing",
            ds_units=None,
        )

        # Add QA processing datetime to stats file
        nisarqa.create_dataset_in_h5group(
            h5_file=h5_file,
            grp_path=nisarqa.STATS_H5_QA_PROCESSING_GROUP % band,
            ds_name="QAProcessingDateTime",
            ds_data=nisarqa.QA_PROCESSING_DATETIME,
            ds_description=(
                "QA processing date and time (in UTC) in the format"
                " YYYY-mm-ddTHH:MM:SS"
            ),
            ds_units=None,
        )

        # Save final runconfig parameters to HDF5
        nisarqa.create_dataset_in_h5group(
            h5_file=h5_file,
            grp_path=nisarqa.STATS_H5_QA_PROCESSING_GROUP % band,
            ds_name="runConfigurationContents",
            ds_data=self.get_final_user_runconfig(),
            ds_description=(
                "Contents of the run configuration file with parameters used"
                " for QA processing"
            ),
            ds_units=None,
        )

    def log_parameters(self):
        """Log the parameter values for this instance of *RootParamGroup."""
        log = nisarqa.get_logger()

        log.debug(
            "QA processing parameters, per runconfig and defaults (runconfig"
            " has precedence)"
        )

        # Iterate through each *ParamGroup attribute in the *RootParamGroup
        for root_group_attr in fields(self):
            param_group_obj = getattr(self, root_group_attr.name)

            # Iterate through each attribute in the *ParamGroup
            if param_group_obj is not None:
                # One of the `workflows` set to `True` required this group,
                # so this *ParamGroup was instantiated and its values logged.

                # Use the path in the runconfig to identify the group
                rncfg_grp_path = (
                    param_group_obj.get_path_to_group_in_runconfig()
                )
                rncfg_grp_path = "/".join(rncfg_grp_path)
                log.debug(
                    "  Final Input Parameters corresponding to Runconfig"
                    f" group: {rncfg_grp_path}"
                )

                # Show the final value assigned to the parameter
                for param in fields(param_group_obj):
                    po2 = getattr(param_group_obj, param.name)
                    log.debug(f"    {param.name}: {po2}")
            else:
                log.debug(
                    "  Per `workflows`, runconfig group for"
                    f" {root_group_attr.name} not required."
                )

    def get_output_dir(self) -> Path:
        """
        Returns the filepath to the output directory.

        Returns
        -------
        filepath : Path
            The filepath to the QA output directory.
        """
        if self.prodpath is None:
            raise ValueError("Output directory not provided via runconfig.")

        return Path(self.prodpath.qa_output_dir)

    def _get_input_file_basename_stripped(self) -> str:
        """
        Returns the input file's basename with the extension stripped.

        This can be used for creating the QA output filenames.

        Returns
        -------
        basename : str
            The input file's basename with the extension removed.
            For example, if the input filename is "/home/qa/my_goff.h5",
            then `basename` will be "my_goff".
        """
        if self.input_f is None:
            raise ValueError("Input filename not provided via runconfig.")

        return self.input_f.qa_input_file

    def get_browse_png_filename(self) -> Path:
        """Return the browse image filename as a Path object. Does not include
        the filepath.
        """
        # # For R3.3, QA should not use the input filename for the output files.
        # # However, if/when this change occurs, here is the new code to use:
        #
        # return Path(f{self._get_input_file_basename_stripped}.png")

        return Path("BROWSE.png")

    def get_kml_browse_filename(self) -> Path:
        """Return the browse kml filename as a Path object. Does not include
        the filepath.
        """
        # # For R3.3, QA should not use the input filename for the output files.
        # # However, if/when this change occurs, here is the new code to use:
        #
        # return Path(f{self._get_input_file_basename_stripped}.kml")

        return Path("BROWSE.kml")

    def get_summary_csv_filename(self) -> Path:
        """Return the Pass/Fail checks summary csv filename as a Path object.
        Does not include the filepath.
        """
        # # For R3.3, QA should not use the input filename for the output files.
        # # However, if/when this change occurs, here is the new code to use:
        #
        # return Path(f{self._get_input_file_basename_stripped}_QA_SUMMARY.csv")

        return Path("SUMMARY.csv")

    def get_report_pdf_filename(self) -> Path:
        """Return the reports PDF filename as a Path object. Does not include
        the filepath.
        """
        # # For R3.3, QA should not use the input filename for the output files.
        # # However, if/when this change occurs, here is the new code to use:
        #
        # return Path(f{self._get_input_file_basename_stripped}_QA_REPORT.pdf")

        return Path("REPORT.pdf")

    def get_stats_h5_filename(self) -> Path:
        """Return the stats HDF5 filename as a Path object. Does not include
        the filepath.
        """
        # # For R3.3, QA should not use the input filename for the output files.
        # # However, if/when this change occurs, here is the new code to use:
        #
        # return Path(f{self._get_input_file_basename_stripped}_QA_STATS.h5")

        return Path("STATS.h5")

    def get_log_filename(self) -> Path:
        """Return the log TXT filename as a Path object. Does not include
        the filepath.
        """
        # # For R3.3, QA should not use the input filename for the output files.
        # # However, if/when this change occurs, here is the new code to use:
        #
        # return Path(f{self._get_input_file_basename_stripped}_QA_LOG.txt")

        return Path("LOG.txt")

    @classmethod
    def from_runconfig_dict(
        cls: type[RootParamGroupT],
        user_rncfg: RunConfigDict,
        product_type: str,
    ) -> RootParamGroupT:
        """
        Build a *RootParamGroup for `product_type` from a QA runconfig dict.

        Parameters
        ----------
        user_rncfg : nisarqa.typing.RunConfigDict
            A dictionary whose structure matches `product_type`'s QA runconfig
            YAML file and that contains the parameters needed to run its QA SAS.
        product_type : str
            One of: 'rslc', 'gslc', 'gcov', 'rifg', 'runw', 'gunw', 'roff',
            or 'goff'.

        Returns
        -------
        root_params : nisarqa.typing.RootParamGroupT
            *RootParamGroup object for the specified product type. This will be
            populated with runconfig values where provided,
            and default values for missing runconfig parameters.

        Raises
        ------
        nisarqa.ExitEarly
            If all `workflows` were set to False in the runconfig.

        See Also
        --------
        RootParamGroup.from_runconfig_file
        """
        if product_type not in nisarqa.LIST_OF_NISAR_PRODUCTS:
            raise ValueError(
                f"{product_type=}, must be one of:"
                f" {nisarqa.LIST_OF_NISAR_PRODUCTS}"
            )

        if product_type == "rslc":
            workflows_param_cls_obj = nisarqa.RSLCWorkflowsParamGroup
            root_param_class_obj = nisarqa.RSLCRootParamGroup
        elif product_type == "gslc":
            workflows_param_cls_obj = nisarqa.SLCWorkflowsParamGroup
            root_param_class_obj = nisarqa.GSLCRootParamGroup
        elif product_type == "gcov":
            workflows_param_cls_obj = WorkflowsParamGroup
            root_param_class_obj = nisarqa.GCOVRootParamGroup
        elif product_type == "rifg":
            workflows_param_cls_obj = nisarqa.RIFGWorkflowsParamGroup
            root_param_class_obj = nisarqa.RIFGRootParamGroup
        elif product_type == "runw":
            workflows_param_cls_obj = nisarqa.RUNWWorkflowsParamGroup
            root_param_class_obj = nisarqa.RUNWRootParamGroup
        elif product_type == "gunw":
            workflows_param_cls_obj = nisarqa.GUNWWorkflowsParamGroup
            root_param_class_obj = nisarqa.GUNWRootParamGroup
        elif product_type == "roff":
            workflows_param_cls_obj = nisarqa.ROFFWorkflowsParamGroup
            root_param_class_obj = nisarqa.ROFFRootParamGroup
        elif product_type == "goff":
            workflows_param_cls_obj = nisarqa.GOFFWorkflowsParamGroup
            root_param_class_obj = nisarqa.GOFFRootParamGroup
        else:
            raise NotImplementedError(f"{product_type} code not implemented.")

        # Dictionary to hold the *ParamGroup objects. Will be used as
        # kwargs for the *RootParamGroup instance.
        root_inputs = {}

        # Construct *WorkflowsParamGroup dataclass (necessary for all workflows)
        try:
            root_inputs["workflows"] = (
                cls._get_param_group_instance_from_runcfg(
                    param_grp_cls_obj=workflows_param_cls_obj,
                    user_rncfg=user_rncfg,
                )
            )

        except KeyError as e:
            raise KeyError(
                "`workflows` group is a required runconfig group"
            ) from e
        # If all functionality is off (i.e. all workflows are set to false),
        # then exit early. We will not need any of the other runconfig groups.
        if not root_inputs["workflows"].at_least_one_wkflw_requested():
            raise nisarqa.ExitEarly("All `workflows` were set to False.")

        workflows = root_inputs["workflows"]

        wkflws2params_mapping = (
            root_param_class_obj.get_mapping_of_workflows2param_grps(
                workflows=workflows
            )
        )

        for param_grp in wkflws2params_mapping:
            if param_grp.flag_param_grp_req:
                populated_rncfg_group = (
                    cls._get_param_group_instance_from_runcfg(
                        param_grp_cls_obj=param_grp.param_grp_cls_obj,
                        user_rncfg=user_rncfg,
                    )
                )

                root_inputs[param_grp.root_param_grp_attr_name] = (
                    populated_rncfg_group
                )

        # Construct and return *RootParamGroup
        return root_param_class_obj(**root_inputs)

    @staticmethod
    def _get_param_group_instance_from_runcfg(
        param_grp_cls_obj: Type[YamlParamGroup],
        user_rncfg: Optional[dict] = None,
    ):
        """
        Generate an instance of a YamlParamGroup subclass) object
        where the values from a user runconfig take precedence.

        Parameters
        ----------
        param_grp_cls_obj : Type[YamlParamGroup]
            A class instance of a subclass of YamlParamGroup.
            For example, `HistogramParamGroup`.
        user_rncfg : nested dict, optional
            A dict containing the user's runconfig values that (at minimum)
            correspond to the `param_grp_cls_obj` parameters. (Other values
            will be ignored.) For example, a QA runconfig yaml loaded directly
            into a dict would be a perfect input for `user_rncfg`.
            The nested structure of `user_rncfg` must match the structure
            of the QA runconfig yaml file for this parameter group.
            To see the expected yaml structure for e.g. RSLC, run
            `nisarqa dumpconfig rslc` from the command line.
            If `user_rncfg` contains entries that do not correspond to
            attributes in `param_grp_cls_obj`, they will be ignored.
            If `user_rncfg` is either None, an empty dict, or does not contain
            values for `param_grp_cls_obj` in a nested structure that matches
            the QA runconfig group that corresponds to `param_grp_cls_obj`,
            then an instance with all default values will be returned.

        Returns
        -------
        param_grp_instance : `param_grp_cls_obj` instance
            An instance of `param_grp_cls_obj` that is fully instantiated
            using default values and the arguments provided in `user_rncfg`.
            The values in `user_rncfg` have precedence over the defaults.
        """

        if not user_rncfg:
            # If user_rncfg is None or is an empty dict, then return the default
            return param_grp_cls_obj()

        # Get the runconfig path for this *ParamGroup
        rncfg_path = param_grp_cls_obj.get_path_to_group_in_runconfig()

        try:
            runcfg_grp_dict = nisarqa.get_nested_element_in_dict(
                user_rncfg, rncfg_path
            )
        except KeyError:
            # Group was not found, so construct an instance using all defaults.
            # If a dataclass has a required parameter, this will (correctly)
            # throw another error.
            return param_grp_cls_obj()
        else:
            # Get the relevant yaml runconfig parameters for this ParamGroup
            yaml_names = param_grp_cls_obj.get_dict_of_yaml_names()

            # prune extraneous fields from the runconfig group
            # (aka keep only the runconfig fields that are relevant to QA)
            # The "if..." logic will allow us to skip missing runconfig fields.
            user_input_args = {
                cls_attr_name: runcfg_grp_dict[yaml_name]
                for cls_attr_name, yaml_name in yaml_names.items()
                if yaml_name in runcfg_grp_dict
            }

            return param_grp_cls_obj(**user_input_args)

    @classmethod
    def from_runconfig_file(
        cls: type[RootParamGroupT],
        runconfig_yaml: str | os.PathLike,
        product_type: str,
    ) -> RootParamGroupT:
        """
        Get a *RootParamGroup for `product_type` from a QA Runconfig YAML file.

        The input runconfig file must follow the standard QA runconfig
        format for `product_type`.
        For an example runconfig template with default parameters,
        run the command line command 'nisar_qa dumpconfig <product_type>'.
        (Ex: Use 'nisarqa dumpconfig rslc' for the RSLC runconfig template.)

        Parameters
        ----------
        runconfig_yaml : path-like
            Filename (with path) to a QA runconfig YAML file for `product_type`.
        product_type : str
            One of: 'rslc', 'gslc', 'gcov', 'rifg', 'runw', 'gunw', 'roff',
            or 'goff'.

        Returns
        -------
        root_params : nisarqa.typing.RootParamGroupT
            An instance of *RootParamGroup corresponding to `product_type`.
            For example, if `product_type` is 'gcov', the return type
            will be `nisarqa.GCOVRootParamGroup`. This will be
            populated with runconfig values where provided,
            and default values for missing runconfig parameters.

        Raises
        ------
        nisarqa.ExitEarly
            If all `workflows` were set to False in the runconfig.

        See Also
        --------
        RootParamGroup.from_runconfig_dict
        """
        # parse runconfig into a dict structure
        log = nisarqa.get_logger()
        log.info(f"Begin loading user runconfig yaml to dict: {runconfig_yaml}")
        user_rncfg = nisarqa.load_user_runconfig(runconfig_yaml)

        log.info("Begin parsing of runconfig for user-provided QA parameters.")

        # Build the *RootParamGroup parameters per the runconfig
        # (Raises an ExitEarly exception if all workflows in runconfig are
        # set to False)
        root_params = cls.from_runconfig_dict(
            user_rncfg=user_rncfg, product_type=product_type
        )
        log.info("Loading of user runconfig complete.")

        return root_params


__all__ = nisarqa.get_all(__name__, objects_to_skip)
