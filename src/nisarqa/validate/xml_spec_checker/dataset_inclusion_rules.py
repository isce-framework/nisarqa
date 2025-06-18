from __future__ import annotations

import itertools
import re
from collections.abc import Iterable, Mapping
from string import Template
from typing import Tuple

# List of objects from the import statements that
# should not be included when importing this module
import nisarqa
from nisarqa import pol_options, subswaths_options

objects_to_skip = nisarqa.get_all(name=__name__)


def path_contains_substrings(
    path: str, all_options: Iterable[str], valid_options: Iterable[str]
) -> bool:
    """
    Compare a path to a rule and return its accepted/rejected status.

    Parameters
    ----------
    path : str
        The path to check.
    all_options : Iterable[str]
        A list of all substrings to check for. If none are found, the string will be
        accepted by default.
    valid_options : Iterable[str]
        The subset of all_options which will be accepted if found.

    Returns
    -------
    contains_substring: bool
        True if accepted; False if rejected.
    """
    if not set(valid_options).issubset(all_options):
        raise ValueError(
            f"{valid_options=} must be a subset of {all_options=}."
        )
    return (
        find_substrings_in_path(
            path=path, all_options=all_options, valid_options=valid_options
        )
        is not None
    )


def find_substrings_in_path(
    path: str, all_options: Iterable[str], valid_options: Iterable[str]
) -> str | None:
    """
    Find substrings in a path and return a valid substring if it is found.

    This function assumes that only one instance of any valid substring is
    possible within the parent string, and will raise an error if this is
    not the case.

    Parameters
    ----------
    path : str
        The path to check.
    all_options : Iterable[str]
        A list of all substrings to check for. If none are found, the string will be
        accepted by default.
    valid_options : Iterable[str]
        The subset of all_options which will be accepted if found.

    Returns
    -------
    valid_substring : str | None:
        Will return a string with the accepted substring if a valid substring is found.
        Will return None if a substring is found that is not valid.
        Will return an empty string if no substring was found.

    Raises
    ------
    ValueError
        If `valid_options` is not a subset of `all_options`.
    ValueError
        If multiple instances of `all_options` are found as a substring of `path`.
    """

    if not set(valid_options).issubset(all_options):
        raise ValueError(
            f"{valid_options=} must be a subset of {all_options=}."
        )

    found_valid_substr = set()
    found_invalid_substr = set()

    for option in all_options:
        # If a valid option (e.g. 'HH') is a substring of an invalid one
        # (e.g. 'HHHV') or vice versa, avoid false positives/negatives
        # by surrounding the Group or Dataset with slash characters or
        # end of string (e.g. '/HH/' or '/HH'). (This assumes that the
        # substring represents the full name of a Group or Dataset.)
        option_re = re.compile(f"(.*/{option}/.*|.*/{option}$)")
        if option_re.match(path):
            # path contains the substring
            if option in valid_options:
                # path contains a valid substring
                found_valid_substr.add(option)
            else:
                # path contains a substring, but it is not a valid substring.
                found_invalid_substr.add(option)

    # Currently, this function can only handle returning a single substring.
    # If multiple are found, raise an error to decide later how best to refactor.
    if len(found_valid_substr) + len(found_invalid_substr) > 1:
        raise ValueError(
            f"{path=} contains multiple valid substrings ({found_valid_substr})"
            f" and/or invalid substrings ({found_invalid_substr})."
        )

    if len(found_valid_substr) > 0:
        return found_valid_substr.pop()
    elif len(found_invalid_substr) > 0:
        return None
    else:
        # Path does not contain any of the substrings, so trivially accept it.
        return ""


def check_path_by_freq_pol(
    path: str,
    all_freqs: Iterable[str],
    all_pols: Iterable[str],
    valid_freq_pols: Mapping[str, Iterable[str]],
) -> bool:
    """
    Check if a path conforms to a set of valid freqs and pols.

    Parameters
    ----------
    path : str
        The path to check.
    all_freqs : Iterable[str]
        A list of all possible frequencies for this product type.
    all_pols : Iterable[str]
        A list of all possible polarizations for this product type.
    valid_freq_pols : Mapping[str, Iterable[str]]
        A mapping of available frequencies to their available
        polarizations for the input product. It is suggested that
        this is constructed from the input product's `listOfFrequencies`
        and `listOfPolarizations` Datasets.

    Returns
    -------
    result : bool
        True if the path contains only valid freq and pols (as noted in
        `valid_freq_pols`). False if it contains an unexpected freq or pol.
    """
    if not set(valid_freq_pols.keys()).issubset(all_freqs):
        raise ValueError(
            f"Frequency set {valid_freq_pols.keys()=} must be a subset of"
            f" {all_freqs=}."
        )
    for freq in valid_freq_pols:
        if not set(valid_freq_pols[freq]).issubset(all_pols):
            raise ValueError(
                f"Polarization set {valid_freq_pols[freq]=} for"
                f" frequency{freq} must be a subset of {all_pols=}."
            )

    valid_freqs = _prepend_frequency_to_items(valid_freq_pols.keys())
    all_freqs = _prepend_frequency_to_items(all_freqs)
    check_result = find_substrings_in_path(
        path=path, all_options=all_freqs, valid_options=valid_freqs
    )

    if check_result is None:
        return False
    if check_result == "":
        return True

    # If a frequency was found, then the result of the check will be the name
    # of the frequency dataset.
    frequency = check_result
    # Get the part of the path that comes after the frequency.
    remaining_string = path.split(frequency, maxsplit=1)[1]
    # Get all polarizations associated with the identified frequency dataset.
    # The final letter of the frequency name (e.g. "frequencyA") can be used
    # to access the desired polarizations.
    valid_pols = valid_freq_pols[frequency[-1]]

    if not set(valid_pols).issubset(all_pols):
        raise ValueError(
            f"Polarization set {valid_freq_pols.keys()=} for {frequency=}"
            f" must be a subset of {all_pols=}."
        )

    # Return the results of a substring check for the polarizations over
    # the part of the path that follows the frequency.
    return path_contains_substrings(
        path=remaining_string, all_options=all_pols, valid_options=valid_pols
    )


def check_path(
    path: str,
    all_freqs: Iterable[str],
    all_pols: Iterable[str],
    all_layers: Iterable[str],
    all_subswaths: Iterable[str],
    valid_freq_pols: Mapping[str, Iterable[str]],
    valid_layers: Iterable[str] | None = None,
    valid_subswaths: Iterable[str] | None = None,
    rule_exceptions: Iterable[str] = None,
) -> bool:
    """
    Accept or reject a path by frequency, polarity, layer, and subswath rules.

    Parameters
    ----------
    paths : Iterable[str]
        The set of paths to check.
    all_freqs : Iterable[str]
        A set containing all possible frequencies for this product.
    all_pols : Iterable[str]
        A set containing all possible polarizations for this product.
    all_layers : Iterable[str]
        A set of all possible layer datasets for this product.
    all_subswaths : Iterable[str]
        A set of all possible subswath datasets for this product.
    valid_freq_pols : Mapping[str, Iterable[str]]
        Dict of the expected frequency + polarization combinations that the input
        NISAR product says it contains.
        e.g., { "A" : ["HH", "HV], "B" : ["VV", "VH"] }
    valid_layers : Iterable[str] | None, optional
        A set of all valid layer groups for this product,
        e.g., {'layer1', 'layer2', 'layer3'}, or None.
        If None, layer datasets will not be checked. Defaults to None.
    valid_subswaths : Iterable[str] | None, optional
        A set of all valid subswath datasets for this product, or None. If None,
        subswath datasets will not be checked. Defaults to None.
    rule_exceptions : Iterable[str] | None, optional
        A set of regex patterns to consider valid regardless of other rules.
        May not contain placeholder datasets. If None, no exceptions will be
        checked. Defaults to None.

    Returns
    -------
    accepted : bool
        True if the path is accepted within the rules; False if not.
    """
    if rule_exceptions is None:
        rule_exceptions = []

    for exception_path in rule_exceptions:
        if re.match(exception_path, path):
            return True

    if not check_path_by_freq_pol(
        path=path,
        all_freqs=all_freqs,
        all_pols=all_pols,
        valid_freq_pols=valid_freq_pols,
    ):
        return False

    if valid_subswaths is not None:
        if not path_contains_substrings(
            path=path,
            all_options=all_subswaths,
            valid_options=valid_subswaths,
        ):
            return False

    if valid_layers is not None:
        if not path_contains_substrings(
            path=path,
            all_options=all_layers,
            valid_options=valid_layers,
        ):
            return False

    return True


def check_paths(
    paths: Iterable[str],
    valid_freq_pols: Mapping[str, Iterable[str]],
    all_freqs: Iterable[str] = nisarqa.NISAR_FREQS,
    all_pols: Iterable[str] = pol_options(),
    all_layers: Iterable[str] = nisarqa.NISAR_LAYERS,
    all_subswaths: Iterable[str] = subswaths_options(),
    valid_layers: Iterable[str] | None = None,
    valid_subswaths: Iterable[str] | None = None,
    rule_exceptions: Iterable[Template] = (),
) -> Tuple[set[str], set[str]]:
    """
    Check a set of HDF5 paths against frequency/polarization, layer, and subswath rules
    and return sets of accepted and rejected paths.

    Parameters
    ----------
    paths : Iterable[str]
        The set of paths to check.
    valid_freq_pols : Mapping[str, Iterable[str]]
        Dict of the expected frequency + polarization combinations that the input
        NISAR product says it contains.
        e.g., { "A" : ["HH", "HV], "B" : ["VV", "VH"] }
    all_freqs : Iterable[str]
        A set containing all possible frequencies for this product.
        Defaults to the global list of frequencies.
    all_pols : Iterable[str]
        A set containing all possible polarizations for this product.
        Defaults to the set of all polarizations, without covariance terms.
    all_layers : Iterable[str]
        A set of all possible layer datasets for this product.
        Defaults to the global list of layers.
    all_subswaths : Iterable[str]
        A set of all possible subswath datasets for this product.
        Defaults to the list of all possible subswaths.
    valid_layers : Iterable[str] | None, optional
        A set of all valid layer groups for this product,
        e.g., {'layer1', 'layer2', 'layer3'}, or None.
        If None, layer datasets will not be checked. Defaults to None.
    valid_subswaths : Iterable[str] | None, optional
        A set of all valid subswath datasets for this product, or None.
        If None, subswath datasets will not be checked. Defaults to None.
    rule_exceptions : Iterable[Template], optional
        A set of regex pattern templates to consider valid regardless of other
        rules. May contain placeholder datasets. Defaults to an empty tuple.

    Returns
    -------
    accepted : set[str]
        A sorted set of all paths accepted by the rulesets.
    rejected : set[str]
        A sorted set of all paths rejected by the rulesets.
    """
    if (valid_layers is not None) and not (
        set(valid_layers).issubset(all_layers)
    ):
        raise ValueError(
            f"Valid layer set {valid_layers=} must be a subset of"
            f" {all_layers=}."
        )

    if (valid_subswaths is not None) and not (
        set(valid_subswaths).issubset(all_subswaths)
    ):
        raise ValueError(
            f"Valid subswath set {valid_subswaths=} must be a subset of"
            f" {all_subswaths=}."
        )

    if not set(valid_freq_pols.keys()).issubset(all_freqs):
        raise ValueError(
            f"Frequency set {valid_freq_pols.keys()=} must be a subset of"
            f" {all_freqs=}."
        )
    for freq in valid_freq_pols:
        if not set(valid_freq_pols[freq]).issubset(all_pols):
            raise ValueError(
                f"Polarization set {valid_freq_pols[freq]=} for"
                f" frequency{freq} must be a subset of {all_pols=}."
            )

    rule_exceptions = process_excepted_paths(
        valid_freq_pols=valid_freq_pols,
        unprocessed_rule_exceptions=rule_exceptions,
    )

    accepted = set()
    rejected = set()

    for path in paths:
        if check_path(
            path=path,
            all_freqs=all_freqs,
            all_pols=all_pols,
            all_layers=all_layers,
            all_subswaths=all_subswaths,
            valid_freq_pols=valid_freq_pols,
            valid_layers=valid_layers,
            valid_subswaths=valid_subswaths,
            rule_exceptions=rule_exceptions,
        ):
            accepted.add(path)
        else:
            rejected.add(path)

    return accepted, rejected


def process_excepted_paths(
    valid_freq_pols: Mapping[str, Iterable[str]],
    unprocessed_rule_exceptions: Iterable[Template],
) -> set[str]:
    """
    Replace placeholders in the given list of excepted paths with appropriate
    replacements.

    For strings given in the `unprocessed_rule_exceptions` list:
        Any string with "$freq" will require that the string still match one
            of the frequencies given in `valid_freq_pols` at that position.
        Any string with "$pol" will require that the string still match
            one of the frequency/polarity associations given in `valid_freq_pols`.
        Any string with "$lin_pol" will match all linear polarizations.
        Any string with "$circ_pol" will match all circular polarizations.

    Parameters
    ----------
    valid_freq_pols : Mapping[str, Iterable[str]]
        Dict of the expected frequency + polarization combinations that the input
        NISAR product says it contains.
        e.g., { "A" : ["HH", "HV], "B" : ["VV", "VH"] }
    unprocessed_rule_exceptions : Iterable[Template]
        The set of unprocessed rule exception templates to format.

    Returns
    -------
    exception_strings : set[str]
        The formatted exception strings.
    """
    rule_exceptions: set[str] = set()

    # Check to determine if the exceptions contain various formatting
    # substrings. If these substrings are absent, do not process.
    # This is intended to decrease repetitive generation of exception
    # strings.
    process_freq_pols = False
    process_lin_pols = False
    process_circ_pols = False

    for exception in unprocessed_rule_exceptions:
        template_str = exception.template
        if "$freq" in template_str or "$pol" in template_str:
            process_freq_pols = True
        if "$lin_pol" in template_str:
            process_lin_pols = True
        if "$circ_pol" in template_str:
            process_circ_pols = True

    processing_values = []

    if process_freq_pols:
        # Permute all valid frequencies and polarizations into a list of valid
        # pairs.
        freq_pols: list[tuple[str, str]] = []
        for freq, pols in valid_freq_pols.items():
            for pol in pols:
                freq_pols.append((f"frequency{freq}", pol))
        processing_values.append(freq_pols)

    if process_lin_pols:
        # Add all linear polarizations.
        processing_values.append(nisarqa.linear_pols())

    if process_circ_pols:
        # Add all linear polarizations.
        processing_values.append(nisarqa.circular_pols())

    # Get all possible combinations of elements from the lists above.
    combinations = itertools.product(*processing_values)

    # For every item in each combination, process all exceptions in the
    # template list and add it to the exception set.
    for combination in combinations:
        # Create a dictionary of substitute values to place into the template.
        substitutes = dict()
        i = 0
        # Only place those substitutions that have been called for in the set
        # of templates.
        if process_freq_pols:
            (freq, pol) = combination[i]
            substitutes["freq"] = freq
            substitutes["pol"] = pol
            i += 1
        if process_lin_pols:
            substitutes["lin_pol"] = combination[i]
            i += 1
        if process_circ_pols:
            substitutes["circ_pol"] = combination[i]
        # Place the given substitutes into each exception template, and put
        # the newly-formatted string into the output list.
        for exception_template in unprocessed_rule_exceptions:
            reformatted_exception = exception_template.safe_substitute(
                **substitutes
            )
            rule_exceptions.add(reformatted_exception)
    return rule_exceptions


def _prepend_frequency_to_items(freqs: Iterable[str]) -> list[str]:
    """Append "frequency" to the start of each item in `freqs`."""
    if not all(isinstance(f, str) for f in freqs):
        raise TypeError(f"{freqs=}, must contain only strings.")
    return [f"frequency{f}" for f in freqs]


__all__ = nisarqa.get_all(__name__, objects_to_skip)
