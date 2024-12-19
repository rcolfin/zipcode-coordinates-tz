from __future__ import annotations

import datetime
import os
from typing import Final

import pytz

MAX_RETRIES: Final[int] = 3

MAX_RETRY_TIME: Final[int] = 60

BUFFER_LENGTH: Final[int] = 1024

DEFAULT_VINTAGE: Final[str] = "Current_Current"

DEFAULT_TIMEZONE: Final[datetime.tzinfo] = pytz.timezone("America/New_York")

TRUTHY: Final[frozenset[str]] = frozenset(["true", "1"])

TIMEZONE_FINDER_BIN_FILE_LOCATION: Final[str | None] = os.getenv("TIMEZONE_FINDER_BIN_FILE_LOCATION")
TIMEZONE_FINDER_IN_MEMORY: Final[bool] = os.getenv("TIMEZONE_FINDER_IN_MEMORY", "").casefold() in TRUTHY


class Columns:
    STREET: Final[str] = "Street"
    CITY: Final[str] = "City"
    STATE: Final[str] = "State"
    ZIPCODE: Final[str] = "ZipCode"
    LATITUDE: Final[str] = "Latitude"
    LONGITUDE: Final[str] = "Longitude"
    TIMEZONE: Final[str] = "TZ"


def get_date_in_ny() -> datetime.date:
    """Gets the current date for the America/New_York timezone."""
    return datetime.datetime.now(tz=DEFAULT_TIMEZONE).date()
