from __future__ import annotations

import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from zipcode_coordinates_tz import census, constants
from zipcode_coordinates_tz.models import Benchmark, Coordinate


def _make_json_response(payload: dict[str, Any]) -> AsyncMock:
    response = AsyncMock()
    response.raise_for_status = MagicMock()
    response.json = AsyncMock(return_value=payload)
    return response


def _make_empty_df() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            constants.Columns.STREET,
            constants.Columns.CITY,
            constants.Columns.STATE,
            constants.Columns.ZIPCODE,
        ]
    )


def _make_locales_df(rows: list[dict]) -> pd.DataFrame:  # type: ignore[type-arg]
    return pd.DataFrame(
        rows,
        columns=[
            constants.Columns.STREET,
            constants.Columns.CITY,
            constants.Columns.STATE,
            constants.Columns.ZIPCODE,
        ],
    )


@pytest.mark.asyncio
class TestGetBenchmarks:
    async def test_returns_dataframe_with_correct_columns(self) -> None:
        payload = {
            "benchmarks": [
                {"benchmarkName": "Public_AR_Current", "benchmarkDescription": "Current", "isDefault": True},
            ]
        }
        mock_response = _make_json_response(payload)

        with patch("zipcode_coordinates_tz.census.requests.AsyncSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session_cls.return_value = mock_session

            result = await census.get_benchmarks()

        assert list(result.columns) == ["Name", "Description", "Default"]
        assert len(result) == 1
        assert result["Name"].iloc[0] == "Public_AR_Current"

    async def test_returns_empty_dataframe_when_no_benchmarks(self) -> None:
        payload: dict[str, Any] = {"benchmarks": []}
        mock_response = _make_json_response(payload)

        with patch("zipcode_coordinates_tz.census.requests.AsyncSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session_cls.return_value = mock_session

            result = await census.get_benchmarks()

        assert len(result) == 0


@pytest.mark.asyncio
class TestGetVintages:
    async def test_returns_dataframe_with_correct_columns(self) -> None:
        payload = {
            "vintages": [
                {"vintageName": "Current_Current", "vintageDescription": "Current Vintage", "isDefault": True},
            ]
        }
        mock_response = _make_json_response(payload)

        with patch("zipcode_coordinates_tz.census.requests.AsyncSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session_cls.return_value = mock_session

            result = await census.get_vintages()

        assert list(result.columns) == ["Name", "Description", "Default"]
        assert len(result) == 1

    async def test_accepts_benchmark_enum(self) -> None:
        payload: dict[str, Any] = {"vintages": []}
        mock_response = _make_json_response(payload)

        with patch("zipcode_coordinates_tz.census.requests.AsyncSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session_cls.return_value = mock_session

            result = await census.get_vintages(Benchmark.Public_AR_ACS2024)

        assert isinstance(result, pd.DataFrame)


@pytest.mark.asyncio
class TestGetAddressCoordinates:
    async def test_returns_coordinate_when_match_found(self) -> None:
        payload = {
            "result": {
                "addressMatches": [
                    {"coordinates": {"x": -74.0060, "y": 40.7128}},
                ]
            }
        }
        mock_response = _make_json_response(payload)

        with patch("zipcode_coordinates_tz.census.requests.AsyncSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session_cls.return_value = mock_session

            result = await census.get_address_coordinates("1 Main St", "New York", "NY", "10001")

        assert isinstance(result, Coordinate)
        assert result.latitude == pytest.approx(40.7128)
        assert result.longitude == pytest.approx(-74.0060)

    async def test_returns_none_when_no_match(self) -> None:
        payload: dict[str, Any] = {"result": {"addressMatches": []}}
        mock_response = _make_json_response(payload)

        with patch("zipcode_coordinates_tz.census.requests.AsyncSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session_cls.return_value = mock_session

            result = await census.get_address_coordinates("1 Nowhere St", "NoCity", "XX", "00000")

        assert result is None

    async def test_returns_first_match_when_multiple(self) -> None:
        payload = {
            "result": {
                "addressMatches": [
                    {"coordinates": {"x": -74.0060, "y": 40.7128}},
                    {"coordinates": {"x": -118.2437, "y": 34.0522}},
                ]
            }
        }
        mock_response = _make_json_response(payload)

        with patch("zipcode_coordinates_tz.census.requests.AsyncSession") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session.get = AsyncMock(return_value=mock_response)
            mock_session_cls.return_value = mock_session

            result = await census.get_address_coordinates("1 Main St", "New York", "NY", "10001")

        assert result is not None
        assert result.latitude == pytest.approx(40.7128)


@pytest.mark.asyncio
class TestGetCoordinates:
    async def test_empty_dataframe_returns_with_lat_lng_columns(self) -> None:
        df = _make_empty_df()
        result = await census.get_coordinates(df)
        assert constants.Columns.LATITUDE in result.columns
        assert constants.Columns.LONGITUDE in result.columns
        assert len(result) == 0

    async def test_joins_coordinates_to_input(self) -> None:
        df = _make_locales_df(
            [
                {"Street": "1 Main St", "City": "New York", "State": "NY", "ZipCode": "10001"},
            ]
        )

        # CSV that mimics the Census batch response format (index 0 = first row)
        csv_content = b'0,"1 Main St, New York, NY, 10001",Match,Exact,"1 MAIN ST, NEW YORK, NY, 10001","-74.006,40.7128",,,,,,\n'

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="wb") as f:
            f.write(csv_content)
            temp_path = Path(f.name)

        @asynccontextmanager
        async def fake_post(*args, **kwargs):  # type: ignore[no-untyped-def]
            yield temp_path

        with (
            patch("zipcode_coordinates_tz.census.requests.AsyncSession") as mock_session_cls,
            patch("zipcode_coordinates_tz.census.http.post_and_download_file", return_value=fake_post()),
        ):
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session_cls.return_value = mock_session

            result = await census.get_coordinates(df)

        assert constants.Columns.LATITUDE in result.columns
        assert constants.Columns.LONGITUDE in result.columns
