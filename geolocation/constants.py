import datetime
from typing import Final

import pytz

MAX_RETRIES: Final[int] = 3

MAX_RETRY_TIME: Final[int] = 60

BUFFER_LENGTH: Final[int] = 1024

DEFAULT_VINTAGE: Final[str] = "Current_Current"

DEFAULT_TIMEZONE: Final[datetime.tzinfo] = pytz.timezone("America/New_York")

TRUTHY: Final[frozenset[str]] = frozenset(["true", "1"])


class Columns:
    STREET: Final[str] = "Street"
    CITY: Final[str] = "City"
    STATE: Final[str] = "State"
    ZIPCODE: Final[str] = "ZipCode"
    LATITUDE: Final[str] = "Latitude"
    LONGITUDE: Final[str] = "Longtitude"
    TIMEZONE: Final[str] = "TZ"
