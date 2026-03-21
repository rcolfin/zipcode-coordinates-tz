from __future__ import annotations

import datetime
import io
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest

from zipcode_coordinates_tz import constants, postal


def _make_excel_bytes() -> bytes:
    """Build a minimal Excel file matching the USPS format."""
    df = pd.DataFrame(
        {
            "PHYSICAL DELV ADDR": ["1 MAIN ST"],
            "PHYSICAL CITY": ["NEW YORK"],
            "PHYSICAL STATE": ["NY"],
            "DELIVERY ZIPCODE": ["10001"],
        }
    )
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="ZIP_DETAIL", index=False)
    return buf.getvalue()


@pytest.mark.asyncio
class TestGetLocales:
    async def test_returns_dataframe_with_correct_columns(self) -> None:
        excel_bytes = _make_excel_bytes()

        with tempfile.NamedTemporaryFile(suffix=".xls", delete=False, mode="wb") as f:
            f.write(excel_bytes)
            temp_path = Path(f.name)

        @asynccontextmanager
        async def fake_download(*args, **kwargs):
            yield temp_path

        with (
            patch("zipcode_coordinates_tz.postal.http.get_and_download_file", side_effect=fake_download),
            patch("zipcode_coordinates_tz.postal.requests.AsyncSession") as mock_session_cls,
        ):
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session_cls.return_value = mock_session

            result = await postal.get_locales(datetime.date(2025, 1, 1))

        expected_columns = [
            constants.Columns.STREET,
            constants.Columns.CITY,
            constants.Columns.STATE,
            constants.Columns.ZIPCODE,
        ]
        assert list(result.columns) == expected_columns

    async def test_returns_correct_data(self) -> None:
        excel_bytes = _make_excel_bytes()

        with tempfile.NamedTemporaryFile(suffix=".xls", delete=False, mode="wb") as f:
            f.write(excel_bytes)
            temp_path = Path(f.name)

        @asynccontextmanager
        async def fake_download(*args, **kwargs):
            yield temp_path

        with (
            patch("zipcode_coordinates_tz.postal.http.get_and_download_file", side_effect=fake_download),
            patch("zipcode_coordinates_tz.postal.requests.AsyncSession") as mock_session_cls,
        ):
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session_cls.return_value = mock_session

            result = await postal.get_locales(datetime.date(2025, 1, 1))

        assert len(result) == 1
        assert result[constants.Columns.STREET].iloc[0] == "1 MAIN ST"
        assert result[constants.Columns.CITY].iloc[0] == "NEW YORK"
        assert result[constants.Columns.STATE].iloc[0] == "NY"
        assert result[constants.Columns.ZIPCODE].iloc[0] == "10001"

    async def test_uses_ny_date_by_default(self) -> None:
        """Verifies that get_locales defaults to today's NY date when no date is provided."""
        excel_bytes = _make_excel_bytes()

        with tempfile.NamedTemporaryFile(suffix=".xls", delete=False, mode="wb") as f:
            f.write(excel_bytes)
            temp_path = Path(f.name)

        captured_url: list[str] = []

        @asynccontextmanager
        async def fake_download(session: object, url: str):
            captured_url.append(url)
            yield temp_path

        with (
            patch("zipcode_coordinates_tz.postal.http.get_and_download_file", side_effect=fake_download),
            patch("zipcode_coordinates_tz.postal.requests.AsyncSession") as mock_session_cls,
        ):
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session_cls.return_value = mock_session

            await postal.get_locales()

        assert len(captured_url) == 1
        ny_date = constants.get_date_in_ny()
        expected_fragment = f"{ny_date.year:04}-{ny_date.month:02}"
        assert expected_fragment in captured_url[0]
