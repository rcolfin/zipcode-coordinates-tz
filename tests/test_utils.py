from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import pytest

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
