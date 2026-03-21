from enum import Enum, IntEnum
from typing import NamedTuple


class Coordinate(NamedTuple):
    """Represents a geographic coordinate pair.

    Attributes:
        latitude: The latitude in decimal degrees (positive = north).
        longitude: The longitude in decimal degrees (positive = east).
    """

    latitude: float
    longitude: float


class Benchmark(str, Enum):
    """Census geocoding benchmark identifiers.

    Benchmarks define the version of address data used for geocoding.
    See https://geocoding.geo.census.gov/geocoder/benchmarks for available values.

    Members:
        Public_AR_CURRENT: The current production benchmark.
        Public_AR_ACS2024: The 2024 ACS benchmark.
        Public_AR_Census2020: The 2020 Decennial Census benchmark.
    """

    Public_AR_CURRENT = "4"
    Public_AR_ACS2024 = "8"
    Public_AR_Census2020 = "2020"

    def __str__(self) -> str:
        return self.value


class FillMissing(IntEnum):
    """Controls whether missing timezones are filled from neighboring records.

    Members:
        DISABLED: Do not fill missing timezones.
        ENABLED: Fill missing timezones using the closest geographic match
            (ZipCode, City+State, then State).
    """

    DISABLED = 0
    ENABLED = 1

    def __str__(self) -> str:
        return str(self.name)
