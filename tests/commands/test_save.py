from __future__ import annotations

import io
import json
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest
from asyncclick.testing import CliRunner

from zipcode_coordinates_tz.commands import save  # noqa: F401  (registers the "save" command on import)
from zipcode_coordinates_tz.commands.common import cli


def _make_postal_excel_bytes() -> bytes:
    """Build a minimal Excel file matching the USPS format, with two rows in the same city/state."""
    df = pd.DataFrame(
        {
            "PHYSICAL DELV ADDR": ["1 MAIN ST", "2 ELM ST"],
            "PHYSICAL CITY": ["NEW YORK", "NEW YORK"],
            "PHYSICAL STATE": ["NY", "NY"],
            "DELIVERY ZIPCODE": ["10001", "10002"],
        }
    )
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="ZIP_DETAIL", index=False)
    return buf.getvalue()


@pytest.mark.asyncio
class TestSaveCommand:
    async def test_pipeline_resolves_coordinates_and_fills_missing_timezones(self) -> None:
        """
        Exercises the full postal -> census -> timezone -> utils.save_frame pipeline through the
        "save" CLI command, mocking only the two external HTTP boundaries (USPS and Census). Row 0
        gets a Census match (and thus a directly-resolved timezone); row 1 shares the same City/State
        but gets no Census match, so its timezone should come from --fill propagating row 0's timezone
        across the City/State group.
        """
        postal_excel_bytes = _make_postal_excel_bytes()
        with tempfile.NamedTemporaryFile(suffix=".xls", delete=False, mode="wb") as f:
            f.write(postal_excel_bytes)
            postal_temp_path = Path(f.name)

        @asynccontextmanager
        async def fake_postal_download(*args, **kwargs):  # type: ignore[no-untyped-def]
            yield postal_temp_path

        # Only the first (matched) row is present in the Census response; the second is omitted,
        # mirroring how the Census batch geocoder drops addresses it can't match.
        census_csv = b'0,"1 MAIN ST, NEW YORK, NY, 10001",Match,Exact,"1 MAIN ST, NEW YORK, NY, 10001","-74.0060,40.7128",,,,,,\n'
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="wb") as f:
            f.write(census_csv)
            census_temp_path = Path(f.name)

        @asynccontextmanager
        async def fake_census_post(*args, **kwargs):  # type: ignore[no-untyped-def]
            yield census_temp_path

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "out.json"

            with (
                patch("zipcode_coordinates_tz.postal.http.get_and_download_file", side_effect=fake_postal_download),
                patch("zipcode_coordinates_tz.postal.requests.AsyncSession") as mock_postal_session_cls,
                patch("zipcode_coordinates_tz.census.http.post_and_download_file", side_effect=fake_census_post),
                patch("zipcode_coordinates_tz.census.requests.AsyncSession") as mock_census_session_cls,
            ):
                mock_postal_session = AsyncMock()
                mock_postal_session.__aenter__ = AsyncMock(return_value=mock_postal_session)
                mock_postal_session.__aexit__ = AsyncMock(return_value=False)
                mock_postal_session_cls.return_value = mock_postal_session

                mock_census_session = AsyncMock()
                mock_census_session.__aenter__ = AsyncMock(return_value=mock_census_session)
                mock_census_session.__aexit__ = AsyncMock(return_value=False)
                mock_census_session_cls.return_value = mock_census_session

                runner = CliRunner()
                result = await runner.invoke(
                    cli,
                    [
                        "save",
                        str(output_file),
                        "--date",
                        "2025-01-01",
                        "--timezones",
                        "--fill",
                    ],
                )

            assert result.exit_code == 0, result.output
            assert output_file.exists()

            rows = json.loads(output_file.read_text())
            assert len(rows) == 2

            by_zip = {row["ZipCode"]: row for row in rows}
            assert by_zip["10001"]["TZ"]["zone"] == "America/New_York"
            # Row 1 had no Census match (no coordinates), but --fill propagates the timezone
            # from row 0 since they share the same City/State.
            assert by_zip["10002"]["TZ"]["zone"] == "America/New_York"

            # --coordinates was not passed, so Latitude/Longitude should have been dropped.
            assert "Latitude" not in rows[0]
            assert "Longitude" not in rows[0]
