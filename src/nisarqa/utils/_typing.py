from __future__ import annotations

from collections.abc import Mapping, Sequence

RunConfigScalar = str | bool | int | float | None
RunConfigList = Sequence[RunConfigScalar | "RunConfigList" | "RunConfigDict"]
RunConfigDict = Mapping[str, RunConfigScalar | RunConfigList | "RunConfigDict"]


# The are global constants and not functions nor classes,
# so manually create the __all__ attribute.
__all__ = [
    "RunConfigScalar",
    "RunConfigList",
    "RunConfigDict",
]