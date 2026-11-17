import logging
from collections.abc import Callable
from pathlib import Path
from typing import Final

import pandas as pd

from zipcode_coordinates_tz import constants

logger = logging.getLogger(__name__)


def _save_csv(df: pd.DataFrame, file: Path) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file, index=False)


def _save_json(df: pd.DataFrame, file: Path) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    if constants.Columns.TIMEZONE in df.columns:
        # zoneinfo.ZoneInfo serializes as {"key": ...}; keep the long-standing {"zone": ...} shape
        # that pytz.timezone(...) produced so the saved file format doesn't change.
        df = df.assign(**{constants.Columns.TIMEZONE: df[constants.Columns.TIMEZONE].map(lambda tz: {"zone": str(tz)} if pd.notna(tz) else None)})
    df.to_json(file, orient="records", index=False)


def _save_excel(df: pd.DataFrame, file: Path) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(file, index=False)


_SAVE_FORMATS: Final[dict[str, Callable[[pd.DataFrame, Path], None]]] = {
    ".csv": _save_csv,
    ".json": _save_json,
    ".xls": _save_excel,
    ".xlsx": _save_excel,
}


def save_frame(df: pd.DataFrame, file: Path) -> None:
    """
    Saves the DataFrame to the file.

    Args:
        df (pd.DataFrame): The Pandas DataFrame.
        file (Path): The Path to save the file to.
    """
    save = _SAVE_FORMATS.get(file.suffix.casefold())
    if save is not None:
        logger.info("Saving %d rows to %s.", len(df), file)
        save(df, file)
        return

    msg = f"{file.suffix} is not a supported format, please select ({','.join(_SAVE_FORMATS.keys())})"
    raise ValueError(msg)
