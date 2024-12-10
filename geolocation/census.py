import io
import logging
from typing import Final, cast

import aiohttp
import pandas as pd

from geolocation import constants, http, models

logger = logging.getLogger(__name__)


DEFAULT_BATCH_SIZE: Final[int] = 9500
MAX_BATCH_RECORDS: Final[int] = 10000
MAX_BATCH_BUFFER_SIZE: Final[int] = 5000000  # 5MB

_GEOLOCATION_URL: Final[str] = "https://geocoding.geo.census.gov/geocoder/locations/address"
_GEOLOCATION_BATCH_URL: Final[str] = "https://geocoding.geo.census.gov/geocoder/geographies/addressbatch"
_BENCHMARKS_URL: Final[str] = "https://geocoding.geo.census.gov/geocoder/benchmarks"
_VINTAGES_URL: Final[str] = "https://geocoding.geo.census.gov/geocoder/vintages"

_BENCHMARK_RENAME_COLUMNS: Final[dict[str, str]] = {"isDefault": "Default", "benchmarkName": "Name", "benchmarkDescription": "Description"}
_VINTAGE_RENAME_COLUMNS: Final[dict[str, str]] = {"isDefault": "Default", "vintageName": "Name", "vintageDescription": "Description"}
_COLUMNS: Final[list[str]] = ["Name", "Description", "Default"]
_GEOLOCATION_BATCH_COLUMNS = [
    "ID",  # Unique identifier from the input
    "Input Address",  # Original address string
    "Match",  # Match status (e.g., Match or No_Match)
    "Match Type",  # Level of certainty of the match
    "Matched Address",  # Standardized matched address
    "Coordinates",  # Latitude + Longitude of the matched location
    "unused1",  # Census block
    "unused2",  # Census block
    "unused3",  # Census block
    "unused4",  # Census block
    "unused5",  # Census block
    "unused6",  # Census block
]


async def get_benchmarks() -> pd.DataFrame:
    """
    Queries for the benchmarks.

    Returns:
        A DataFrame with the shape of
            #   Column       Non-Null Count  Dtype
            ---  ------       --------------  -----
            0   Name         0 non-null      object
            1   Description  0 non-null      object
            2   Default      0 non-null      bool
    """
    async with (
        aiohttp.ClientSession() as session,
        http.get_json(
            session,
            _BENCHMARKS_URL,
        ) as data,
    ):
        return pd.DataFrame(data.get("benchmarks", [])).rename(columns=_BENCHMARK_RENAME_COLUMNS)[_COLUMNS]


async def get_vintages(benchmark: models.Benchmark | str = models.Benchmark.Public_AR_CURRENT) -> pd.DataFrame:
    """
    Queries for the vintages for the specified benchmark.

    Args:
        benchmark (models.Benchmark | str): The benchmark value (see get_benchmarks for possible values).

    Returns:
        A DataFrame with the shape of
            #   Column       Non-Null Count  Dtype
            ---  ------       --------------  -----
            0   Name         0 non-null      object
            1   Description  0 non-null      object
            2   Default      0 non-null      bool
    """
    params = {"benchmark": str(benchmark)}
    async with (
        aiohttp.ClientSession() as session,
        http.get_json(
            session,
            _VINTAGES_URL,
            params,
        ) as data,
    ):
        return pd.DataFrame(data.get("vintages", [])).rename(columns=_VINTAGE_RENAME_COLUMNS)[_COLUMNS]


async def get_address_coordinates(
    street: str, city: str, state: str, zip_code: str, benchmark: models.Benchmark | str = models.Benchmark.Public_AR_CURRENT
) -> models.Coordinate | None:
    """
    Queries the coordinate for the specified address.

    Args:
        street (str): The street address.
        city (str): The city
        zip_code (str): The zip code.
        benchmark (models.Benchmark | str): The benchmark value (see get_benchmarks for possible values).

    Returns:
        models.Coordinate or None if not found.
    """
    params = {"format": "json", "benchmark": str(benchmark), "street": street, "city": city, "state": state, "zip": zip_code}
    async with (
        aiohttp.ClientSession() as session,
        http.get_json(
            session,
            _GEOLOCATION_URL,
            params,
        ) as data,
    ):
        address_matches = data.get("result", {}).get("addressMatches", [])
        coordinates = [
            models.Coordinate(float(am["coordinates"]["x"]), float(am["coordinates"]["y"])) for am in address_matches if "coordinates" in am
        ]
        return coordinates[0] if coordinates else None


async def get_coordinates(
    df_zip_locals: pd.DataFrame,
    benchmark: models.Benchmark | str = models.Benchmark.Public_AR_CURRENT,
    vintage: str = constants.DEFAULT_VINTAGE,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> pd.DataFrame:
    """
    Queries for the latitude and longitude coordinates for the addresses contained in the dataframe.

    Args:
        df_zip_locals (pd.DataFrame): A DataFrame in the shape of
            Data columns (total 4 columns):
            #   Column   Non-Null Count  Dtype
            ---  ------   --------------  -----
            0   Street   0 non-null      object
            1   City     0 non-null      object
            2   State    0 non-null      object
            3   ZipCode  0 non-null      object
        benchmark (models.Benchmark | str): The benchmark value (see get_benchmarks for possible values).
        vintage (str): The vintage value (see get_vintages for possible values).
        batch_size (int): The maximum number of rows to send in a single request (defaults to DEFAULT_BATCH_SIZE).

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
    """
    batch_size = min(MAX_BATCH_RECORDS, batch_size)
    params = {"benchmark": str(benchmark), "vintage": vintage}
    batch_cnt = max(1, len(df_zip_locals) // batch_size)
    logger.debug("Chunking %d rows into %d batch requests with %d rows each.", len(df_zip_locals), batch_cnt, batch_size)

    df_coordinates_lst: list[pd.DataFrame] = []
    async with aiohttp.ClientSession() as session:
        for idx in range(0, len(df_zip_locals), batch_size):
            chunk = df_zip_locals[idx : idx + batch_size]
            with io.BytesIO() as f:
                cast(pd.DataFrame, chunk).to_csv(f, header=False, encoding="utf-8")
                f.seek(0)

                assert len(chunk) < MAX_BATCH_RECORDS, f"{len(chunk)} >= {MAX_BATCH_RECORDS}"
                assert f.getbuffer().nbytes < MAX_BATCH_BUFFER_SIZE, f"{f.getbuffer().nbytes} < {MAX_BATCH_BUFFER_SIZE}"
                logger.debug("Sending request with csv file:\n%s", f.read().decode())

                f.seek(0)
                data = aiohttp.FormData()
                data.add_field("addressFile", f, filename=f"upload-{idx}.csv", content_type="text/csv")

                try:
                    async with http.post_and_download_file(session, _GEOLOCATION_BATCH_URL, params, data) as downloaded_file:
                        logger.debug("Response received:\n%s", downloaded_file.read_text())

                        # Parse the downloaded file as a CSV:
                        # Include only the Matches
                        # Extract the Longitude and Latitude from the Coordinates column
                        df_geo = pd.read_csv(
                            downloaded_file,
                            sep=",",
                            names=_GEOLOCATION_BATCH_COLUMNS,
                            index_col=False,
                        )
                        df_geo = df_geo.set_index("ID")
                        df_geo = df_geo.loc[df_geo["Match"] == "Match"]
                        df_geo["Longtitude"] = df_geo["Coordinates"].apply(lambda x: float(x.split(",")[0]))
                        df_geo["Latitude"] = df_geo["Coordinates"].apply(lambda x: float(x.split(",")[1]))
                        df_geo = df_geo[["Latitude", "Longtitude"]]

                        # Append the produced frame into the list
                        df_coordinates_lst.append(df_geo[["Latitude", "Longtitude"]])
                except aiohttp.client_exceptions.ClientResponseError:
                    logger.exception("Failed to download coordinates.")

    if not df_coordinates_lst:
        msg = "No coordinates were queried"
        raise ValueError(msg)

    # Concatenate all the dataframes then join by index with the original frame:
    df_coordinates = pd.concat(df_coordinates_lst)
    return df_zip_locals.join(df_coordinates)
