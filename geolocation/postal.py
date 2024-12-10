import datetime
import logging
from typing import Final

import aiohttp
import pandas as pd

from geolocation import constants, http

logger = logging.getLogger(__name__)


_RENAME_COLUMNS: Final[dict[str, str]] = {
    "PHYSICAL DELV ADDR": "Street",
    "PHYSICAL CITY": "City",
    "PHYSICAL STATE": "State",
    "DELIVERY ZIPCODE": "ZipCode",
}
_DTYPES: Final[dict[str, type]] = {
    "PHYSICAL DELV ADDR": str,
    "PHYSICAL CITY": str,
    "PHYSICAL STATE": str,
    "DELIVERY ZIPCODE": str,
}
_TAKE_COLUMNS: Final[list[str]] = ["Street", "City", "State", "ZipCode"]
_SHEET_NAME: Final[str] = "ZIP_DETAIL"
_URL_FMT: Final[str] = "https://postalpro.usps.com/mnt/glusterfs/{YEAR}-{MONTH}/ZIP_Locale_Detail.xls"


async def get_locales(date: datetime.date | None = None) -> pd.DataFrame:
    """
    Queries US Postoffice for a DataFrame containing zip code to address, city and state.

    Args:
        date (datetime.date | None): The date (defaults to today)

    Returns:
        A DataFrame with the shape of
            #   Column   Non-Null Count  Dtype
            ---  ------   --------------  -----
            0   Street   0 non-null      object
            1   City     0 non-null      object
            2   State    0 non-null      object
            3   ZipCode  0 non-null      object
    """
    if date is None:
        date = datetime.datetime.now(tz=constants.DEFAULT_TIMEZONE).date()
    url = _URL_FMT.format(YEAR=date.year, MONTH=date.month)
    async with aiohttp.ClientSession() as session, http.get_and_download_file(session, url) as f:
        df_zip_locale = pd.read_excel(f, sheet_name=_SHEET_NAME, dtype=_DTYPES)
        return df_zip_locale.rename(
            columns=_RENAME_COLUMNS,
        )[_TAKE_COLUMNS]
