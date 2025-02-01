from __future__ import annotations

__all__ = [
    "RootParamGroupT",
    "RunConfigScalar",
    "RunConfigList",
    "RunConfigDict",
    "MetadataLUTT",
]

from collections.abc import Mapping, Sequence
from typing import TypeVar, Union

RunConfigScalar = Union[str, bool, int, float, None]
RunConfigList = Sequence[
    Union[RunConfigScalar, "RunConfigList", "RunConfigDict"]
]
RunConfigDict = Mapping[
    str, Union[RunConfigScalar, RunConfigList, "RunConfigDict"]
]

RootParamGroupT = TypeVar("RootParamGroupT", bound="RootParamGroup")

MetadataLUTT = TypeVar("MetadataLUTT", bound="MetadataLUT1D")
