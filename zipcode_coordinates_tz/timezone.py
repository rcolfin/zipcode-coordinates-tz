from __future__ import annotations

import contextlib
import logging
from functools import cache
from typing import TYPE_CHECKING

import pandas as pd
import pytz
from timezonefinder import TimezoneFinder

from zipcode_coordinates_tz import constants
from zipcode_coordinates_tz.models import FillMissing

if TYPE_CHECKING:
    import datetime


logger = logging.getLogger(__name__)


@cache
def _get_cached_timezone_finder() -> TimezoneFinder:
    return TimezoneFinder(bin_file_location=constants.TIMEZONE_FINDER_BIN_FILE_LOCATION, in_memory=constants.TIMEZONE_FINDER_IN_MEMORY)


def _get_timezone(latitude: float | None, longitude: float | None, timezone_finder: TimezoneFinder) -> datetime.tzinfo | None:
    if pd.isna(latitude) or pd.isna(longitude):
        return None

    assert latitude is not None  # noqa: S101
    assert longitude is not None  # noqa: S101
    with contextlib.suppress(ValueError):
        zone = timezone_finder.timezone_at(lat=latitude, lng=longitude)
        if zone is not None:
            return pytz.timezone(zone)

    return None


def fill_timezones(
    df: pd.DataFrame,
    fill_missing: FillMissing | bool = FillMissing.ENABLED,  # noqa: FBT001
    timezone_finder: TimezoneFinder | None = None,
) -> pd.DataFrame:
    """
    Fills in the timezones for each coordinate in the specifeid DataFrame.

    Args:
        df (pd.DataFrame):  A DataFrame with the shape of
            #   Column      Non-Null Count  Dtype
            ---  ------      --------------  -----
            0   Street      0 non-null      object
            1   City        0 non-null      object
            2   State       0 non-null      object
            3   ZipCode     0 non-null      object
            4   Latitude    0 non-null      float64
            5   Longitude  0 non-null      float64

        fill_missing (FillMissing): Flag indicating whether to fill in missing timezones by the closest match:
            ZipCode, City, State
            City, State
            State.
        timezone_finder (TimezoneFinder | None): The optional TimezoneFinder instance to use.

    Returns:
        A DataFrame with the shape of
            #   Column      Non-Null Count  Dtype
            ---  ------      --------------  -----
            0   Street      0 non-null      object
            1   City        0 non-null      object
            2   State       0 non-null      object
            3   ZipCode     0 non-null      object
            4   Latitude    0 non-null      float64
            5   Longitude   0 non-null      float64
            6   TZ          0 non-null      object
    """
    logger.debug("Filling in timezones into %d rows.", len(df))

    if timezone_finder is None:
        timezone_finder = _get_cached_timezone_finder()

    df[constants.Columns.TIMEZONE] = df.apply(
        lambda row: _get_timezone(
            float(row[constants.Columns.LATITUDE]) if not pd.isna(row[constants.Columns.LATITUDE]) else None,
            float(row[constants.Columns.LONGITUDE]) if not pd.isna(row[constants.Columns.LONGITUDE]) else None,
            timezone_finder,
        ),
        axis=1,
        result_type="expand",
    )

    if fill_missing is True or fill_missing == FillMissing.ENABLED:
        # This attempts to make a best effort at making sure that every row has a timezone.  It does this by filling based on the
        # closest match; ie: ZipCode, City, State, then by City, State and finally by State.

        df_before_no_tz = df[df.TZ.isna()]
        df[constants.Columns.TIMEZONE] = (
            df.groupby([constants.Columns.ZIPCODE, constants.Columns.CITY, constants.Columns.STATE])[constants.Columns.TIMEZONE]
            .transform(lambda x: x.ffill().bfill())  # Fill using ZipCode first
            .fillna(
                df.groupby([constants.Columns.CITY, constants.Columns.STATE])[constants.Columns.TIMEZONE].transform(lambda x: x.ffill().bfill())
            )  # Then City
            .fillna(df.groupby([constants.Columns.STATE])[constants.Columns.TIMEZONE].transform(lambda x: x.ffill().bfill()))  # Then State
        )

        df_after_no_tz = df[df.TZ.isna()]
        logger.debug("Filled in %d rows with their closest location.", len(df_before_no_tz) - len(df_after_no_tz))

    return df
