from __future__ import annotations

import pytest

from zipcode_coordinates_tz.models import Benchmark, Coordinate, FillMissing


class TestCoordinate:
    def test_construction(self) -> None:
        coord = Coordinate(latitude=40.7128, longitude=-74.0060)
        assert coord.latitude == 40.7128
        assert coord.longitude == -74.0060

    def test_positional_construction(self) -> None:
        coord = Coordinate(1.0, 2.0)
        assert coord.latitude == 1.0
        assert coord.longitude == 2.0

    def test_unpacking(self) -> None:
        lat, lng = Coordinate(10.0, 20.0)
        assert lat == 10.0
        assert lng == 20.0

    def test_indexing(self) -> None:
        coord = Coordinate(3.0, 4.0)
        assert coord[0] == 3.0
        assert coord[1] == 4.0

    def test_equality(self) -> None:
        assert Coordinate(1.0, 2.0) == Coordinate(1.0, 2.0)
        assert Coordinate(1.0, 2.0) != Coordinate(1.0, 3.0)


class TestBenchmark:
    def test_values(self) -> None:
        assert Benchmark.Public_AR_CURRENT.value == "4"
        assert Benchmark.Public_AR_ACS2024.value == "8"
        assert Benchmark.Public_AR_Census2020.value == "2020"

    def test_str_returns_value(self) -> None:
        assert str(Benchmark.Public_AR_CURRENT) == "4"
        assert str(Benchmark.Public_AR_ACS2024) == "8"
        assert str(Benchmark.Public_AR_Census2020) == "2020"

    def test_is_str_subclass(self) -> None:
        assert isinstance(Benchmark.Public_AR_CURRENT, str)

    def test_all_members_present(self) -> None:
        names = {m.name for m in Benchmark}
        assert names == {"Public_AR_CURRENT", "Public_AR_ACS2024", "Public_AR_Census2020"}


class TestFillMissing:
    def test_values(self) -> None:
        assert FillMissing.DISABLED == 0
        assert FillMissing.ENABLED == 1

    def test_str_returns_name(self) -> None:
        assert str(FillMissing.DISABLED) == "DISABLED"
        assert str(FillMissing.ENABLED) == "ENABLED"

    def test_bool_comparison_enabled(self) -> None:
        assert FillMissing.ENABLED == True  # noqa: E712

    def test_bool_comparison_disabled(self) -> None:
        assert FillMissing.DISABLED == False  # noqa: E712

    def test_is_int_subclass(self) -> None:
        assert isinstance(FillMissing.ENABLED, int)

    @pytest.mark.parametrize("value", list(FillMissing))
    def test_roundtrip(self, value: FillMissing) -> None:
        assert FillMissing(int(value)) == value
