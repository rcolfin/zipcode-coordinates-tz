from __future__ import annotations

import datetime

from zipcode_coordinates_tz import constants


class TestColumns:
    def test_street(self) -> None:
        assert constants.Columns.STREET == "Street"

    def test_city(self) -> None:
        assert constants.Columns.CITY == "City"

    def test_state(self) -> None:
        assert constants.Columns.STATE == "State"

    def test_zipcode(self) -> None:
        assert constants.Columns.ZIPCODE == "ZipCode"

    def test_latitude(self) -> None:
        assert constants.Columns.LATITUDE == "Latitude"

    def test_longitude(self) -> None:
        assert constants.Columns.LONGITUDE == "Longitude"

    def test_timezone(self) -> None:
        assert constants.Columns.TIMEZONE == "TZ"

    def test_all_are_strings(self) -> None:
        cols = [
            constants.Columns.STREET,
            constants.Columns.CITY,
            constants.Columns.STATE,
            constants.Columns.ZIPCODE,
            constants.Columns.LATITUDE,
            constants.Columns.LONGITUDE,
            constants.Columns.TIMEZONE,
        ]
        assert all(isinstance(c, str) for c in cols)

    def test_all_unique(self) -> None:
        cols = [
            constants.Columns.STREET,
            constants.Columns.CITY,
            constants.Columns.STATE,
            constants.Columns.ZIPCODE,
            constants.Columns.LATITUDE,
            constants.Columns.LONGITUDE,
            constants.Columns.TIMEZONE,
        ]
        assert len(cols) == len(set(cols))


class TestGetDateInNY:
    def test_returns_date(self) -> None:
        result = constants.get_date_in_ny()
        assert isinstance(result, datetime.date)

    def test_not_datetime(self) -> None:
        result = constants.get_date_in_ny()
        assert type(result) is datetime.date

    def test_is_recent(self) -> None:
        result = constants.get_date_in_ny()
        today_utc = datetime.datetime.now(tz=datetime.timezone.utc).date()
        delta = abs((result - today_utc).days)
        # Should be within 1 day of UTC (accounting for timezone offset)
        assert delta <= 1
