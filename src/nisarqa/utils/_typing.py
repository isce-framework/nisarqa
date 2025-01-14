from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Union

RunConfigScalar = Union[str, bool, int, float, None]
RunConfigList = Sequence[
    Union[RunConfigScalar, "RunConfigList", "RunConfigDict"]
]
RunConfigDict = Mapping[
    str, Union[RunConfigScalar, RunConfigList, "RunConfigDict"]
]


# The are global constants and not functions nor classes,
# so manually create the __all__ attribute.
__all__ = [
    "RunConfigScalar",
    "RunConfigList",
    "RunConfigDict",
]
