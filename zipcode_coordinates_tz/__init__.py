from __future__ import annotations

import importlib.metadata

from zipcode_coordinates_tz import census, constants, models, postal, timezone

# set the version number within the package using importlib
try:
    __version__: str | None = importlib.metadata.version("zipcode-coordinates-tz")
except importlib.metadata.PackageNotFoundError:
    # package is not installed
    __version__ = None


__all__ = ["__version__", "census", "constants", "models", "postal", "timezone"]
