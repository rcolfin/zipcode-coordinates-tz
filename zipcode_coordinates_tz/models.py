from enum import Enum, IntEnum
from typing import NamedTuple


class Coordinate(NamedTuple):
    latitude: float
    longitude: float


class Benchmark(str, Enum):
    Public_AR_CURRENT = "4"
    Public_AR_ACS2024 = "8"
    Public_AR_Census2020 = "2020"

    def __str__(self) -> str:
        return self.value


class FillMissing(IntEnum):
    DISABLED = 0
    ENABLED = 1

    def __str__(self) -> str:
        return str(self.name)
