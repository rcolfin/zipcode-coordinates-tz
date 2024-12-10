from __future__ import annotations

import importlib.metadata

from geolocation import census, models, postal, timezone

# set the version number within the package using importlib
try:
    __version__: str | None = importlib.metadata.version("geolocation")
except importlib.metadata.PackageNotFoundError:
    # package is not installed
    __version__ = None


__all__ = ["__version__", "census", "models", "postal", "timezone"]
