import contextlib
import datetime
import logging
import os
from functools import cache

import pandas as pd
import pytz
from timezonefinder import TimezoneFinder

from geolocation import constants

logger = logging.getLogger(__name__)


@cache
def _get_cached_timezone_finder() -> TimezoneFinder:
    bin_file_location = os.getenv("TIMEZONE_FINDER_BIN_FILE_LOCATION")
    in_memory = os.getenv("TIMEZONE_FINDER_IN_MEMORY", "").casefold() in constants.TRUTHY
    return TimezoneFinder(bin_file_location=bin_file_location, in_memory=in_memory)


def _get_timezone(latitude: float | None, longitude: float | None, timezone_finder: TimezoneFinder) -> datetime.tzinfo | None:
    if latitude is None or longitude is None:
        logger.warning("NONE!!!!!!!!!!!!!!!!!!!")
        return None

    with contextlib.suppress(ValueError):
        zone = timezone_finder.timezone_at(lat=latitude, lng=longitude)
        if zone is not None:
            return pytz.timezone(zone)

    return None


def fill_timezones(df: pd.DataFrame, timezone_finder: TimezoneFinder | None = None) -> pd.DataFrame:
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
            5   Longtitude  0 non-null      float64

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
            5   Longtitude  0 non-null      float64
            6   TZ          0 non-null      object
    """
    logger.debug("Filling in timezones into %d rows.", len(df))

    if timezone_finder is None:
        timezone_finder = _get_cached_timezone_finder()

    df[constants.Columns.TIMEZONE] = df.apply(
        lambda row: _get_timezone(row[constants.Columns.LATITUDE], row[constants.Columns.LONGITUDE], timezone_finder), axis=1
    )
    return df
