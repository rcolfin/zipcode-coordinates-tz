from __future__ import annotations

import pandas as pd
import pytest
from timezonefinder import TimezoneFinder

from zipcode_coordinates_tz import constants
from zipcode_coordinates_tz.models import FillMissing
from zipcode_coordinates_tz.timezone import fill_timezones


def _make_df(rows: list[dict]) -> pd.DataFrame:  # type: ignore[type-arg]
    """Build a minimal DataFrame with required columns."""
    return pd.DataFrame(
        rows,
        columns=[
            constants.Columns.STREET,
            constants.Columns.CITY,
            constants.Columns.STATE,
            constants.Columns.ZIPCODE,
            constants.Columns.LATITUDE,
            constants.Columns.LONGITUDE,
        ],
    )


# Known coordinates for deterministic tests
_NYC_LAT = 40.7128
_NYC_LNG = -74.0060
_NYC_TZ = "America/New_York"

_LA_LAT = 34.0522
_LA_LNG = -118.2437
_LA_TZ = "America/Los_Angeles"


class TestFillTimezones:
    def test_returns_tz_column(self) -> None:
        df = _make_df([{"Street": "1 Main St", "City": "New York", "State": "NY", "ZipCode": "10001", "Latitude": _NYC_LAT, "Longitude": _NYC_LNG}])
        result = fill_timezones(df)
        assert constants.Columns.TIMEZONE in result.columns

    def test_known_nyc_coordinates(self) -> None:
        df = _make_df([{"Street": "1 Main St", "City": "New York", "State": "NY", "ZipCode": "10001", "Latitude": _NYC_LAT, "Longitude": _NYC_LNG}])
        result = fill_timezones(df)
        tz = result[constants.Columns.TIMEZONE].iloc[0]
        assert str(tz) == _NYC_TZ

    def test_known_la_coordinates(self) -> None:
        df = _make_df(
            [{"Street": "1 Sunset Blvd", "City": "Los Angeles", "State": "CA", "ZipCode": "90001", "Latitude": _LA_LAT, "Longitude": _LA_LNG}]
        )
        result = fill_timezones(df)
        tz = result[constants.Columns.TIMEZONE].iloc[0]
        assert str(tz) == _LA_TZ

    def test_multiple_rows(self) -> None:
        df = _make_df(
            [
                {"Street": "1 Main St", "City": "New York", "State": "NY", "ZipCode": "10001", "Latitude": _NYC_LAT, "Longitude": _NYC_LNG},
                {"Street": "1 Sunset Blvd", "City": "Los Angeles", "State": "CA", "ZipCode": "90001", "Latitude": _LA_LAT, "Longitude": _LA_LNG},
            ]
        )
        result = fill_timezones(df)
        assert str(result[constants.Columns.TIMEZONE].iloc[0]) == _NYC_TZ
        assert str(result[constants.Columns.TIMEZONE].iloc[1]) == _LA_TZ

    def test_fill_missing_disabled_leaves_none(self) -> None:
        df = _make_df(
            [
                {"Street": "1 Main St", "City": "New York", "State": "NY", "ZipCode": "10001", "Latitude": _NYC_LAT, "Longitude": _NYC_LNG},
                {"Street": "2 Main St", "City": "New York", "State": "NY", "ZipCode": "10001", "Latitude": None, "Longitude": None},
            ]
        )
        result = fill_timezones(df, fill_missing=FillMissing.DISABLED)
        assert pd.isna(result[constants.Columns.TIMEZONE].iloc[1])

    def test_fill_missing_enabled_propagates_from_zipcode(self) -> None:
        df = _make_df(
            [
                {"Street": "1 Main St", "City": "New York", "State": "NY", "ZipCode": "10001", "Latitude": _NYC_LAT, "Longitude": _NYC_LNG},
                {"Street": "2 Main St", "City": "New York", "State": "NY", "ZipCode": "10001", "Latitude": None, "Longitude": None},
            ]
        )
        result = fill_timezones(df, fill_missing=FillMissing.ENABLED)
        assert str(result[constants.Columns.TIMEZONE].iloc[1]) == _NYC_TZ

    def test_fill_missing_bool_true_propagates(self) -> None:
        df = _make_df(
            [
                {"Street": "1 Main St", "City": "New York", "State": "NY", "ZipCode": "10001", "Latitude": _NYC_LAT, "Longitude": _NYC_LNG},
                {"Street": "2 Main St", "City": "New York", "State": "NY", "ZipCode": "10001", "Latitude": None, "Longitude": None},
            ]
        )
        result = fill_timezones(df, fill_missing=True)
        assert str(result[constants.Columns.TIMEZONE].iloc[1]) == _NYC_TZ

    def test_fill_missing_bool_false_leaves_none(self) -> None:
        df = _make_df(
            [
                {"Street": "1 Main St", "City": "New York", "State": "NY", "ZipCode": "10001", "Latitude": _NYC_LAT, "Longitude": _NYC_LNG},
                {"Street": "2 Main St", "City": "New York", "State": "NY", "ZipCode": "10001", "Latitude": None, "Longitude": None},
            ]
        )
        result = fill_timezones(df, fill_missing=False)
        assert pd.isna(result[constants.Columns.TIMEZONE].iloc[1])

    def test_fill_missing_propagates_by_state(self) -> None:
        # Different ZipCode and City, same State — should still fill by State
        df = _make_df(
            [
                {"Street": "1 Main St", "City": "New York", "State": "NY", "ZipCode": "10001", "Latitude": _NYC_LAT, "Longitude": _NYC_LNG},
                {"Street": "1 Albany St", "City": "Albany", "State": "NY", "ZipCode": "12201", "Latitude": None, "Longitude": None},
            ]
        )
        result = fill_timezones(df, fill_missing=FillMissing.ENABLED)
        assert str(result[constants.Columns.TIMEZONE].iloc[1]) == _NYC_TZ

    def test_accepts_custom_timezone_finder(self) -> None:
        tf = TimezoneFinder()
        df = _make_df([{"Street": "1 Main St", "City": "New York", "State": "NY", "ZipCode": "10001", "Latitude": _NYC_LAT, "Longitude": _NYC_LNG}])
        result = fill_timezones(df, timezone_finder=tf)
        assert str(result[constants.Columns.TIMEZONE].iloc[0]) == _NYC_TZ

    @pytest.mark.parametrize("fill_missing", [FillMissing.DISABLED, FillMissing.ENABLED, True, False])
    def test_empty_df_does_not_raise(self, fill_missing: FillMissing | bool) -> None:
        df = _make_df([])
        result = fill_timezones(df, fill_missing=fill_missing)
        assert constants.Columns.TIMEZONE in result.columns
        assert len(result) == 0
