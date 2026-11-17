from __future__ import annotations

import json
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from zipcode_coordinates_tz import constants
from zipcode_coordinates_tz.utils import save_frame

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})


class TestSaveFrame:
    def test_save_csv(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        file = tmp_path / "output.csv"
        save_frame(sample_df, file)
        result = pd.read_csv(file)
        pd.testing.assert_frame_equal(result, sample_df)

    def test_save_json(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        file = tmp_path / "output.json"
        save_frame(sample_df, file)
        result = pd.read_json(file)
        pd.testing.assert_frame_equal(result, sample_df)

    def test_save_xlsx(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        file = tmp_path / "output.xlsx"
        save_frame(sample_df, file)
        result = pd.read_excel(file)
        pd.testing.assert_frame_equal(result, sample_df)

    def test_save_xls(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        # .xls is dispatched to the same Excel handler as .xlsx
        file = tmp_path / "output.xls"
        save_frame(sample_df, file)
        result = pd.read_excel(file)
        pd.testing.assert_frame_equal(result, sample_df)

    def test_unsupported_extension_raises(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        file = tmp_path / "output.txt"
        with pytest.raises(ValueError, match=r"\.txt"):
            save_frame(sample_df, file)

    def test_creates_parent_directories(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        file = tmp_path / "nested" / "deep" / "output.csv"
        assert not file.parent.exists()
        save_frame(sample_df, file)
        assert file.exists()

    def test_csv_case_insensitive_extension(self, sample_df: pd.DataFrame, tmp_path: Path) -> None:
        file = tmp_path / "output.CSV"
        save_frame(sample_df, file)
        result = pd.read_csv(file)
        pd.testing.assert_frame_equal(result, sample_df)

    def test_save_json_timezone_column_serialized_as_zone_dict(self, tmp_path: Path) -> None:
        # Regression test for the TZ-column special-case in utils._save_json: a `zoneinfo.ZoneInfo`
        # value must serialize to the long-standing {"zone": "<iana key>"} shape (what pytz.timezone(...)
        # produced before the pytz -> zoneinfo migration), not zoneinfo's own {"key": "<iana key>"} shape.
        df = pd.DataFrame(
            {
                constants.Columns.ZIPCODE: ["10001", "99999"],
                constants.Columns.TIMEZONE: [ZoneInfo("America/New_York"), None],
            }
        )
        file = tmp_path / "output.json"
        save_frame(df, file)

        rows = json.loads(file.read_text())
        assert rows[0][constants.Columns.TIMEZONE] == {"zone": "America/New_York"}
        assert rows[1][constants.Columns.TIMEZONE] is None
