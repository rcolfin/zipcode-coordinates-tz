# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```sh
# Set up the Python environment (run first)
scripts/console.sh

# Install pre-commit hooks (first time only)
uvx pre-commit install

# Run all checks (lint, format, type check, tests)
scripts/check.sh

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/path/to/test.py::test_name

# Lint and format
uv run ruff check . --fix
uv run ruff format .

# Type check
uv run mypy .

# Lock dependencies (no version updates)
scripts/lock.sh

# Run as CLI
uv run python -m zipcode_coordinates_tz save NJ.json --state NJ --timezones --fill
```

## Architecture

The package converts US zip codes → coordinates → timezone via a three-stage pipeline:

1. **`postal.py`** — Queries the USPS postal API for zip code locale data. Returns a DataFrame with `[Street, City, State, ZipCode]`.

2. **`census.py`** — Queries the US Census geocoding API to resolve addresses to coordinates. Sends requests in batches (up to 9,500 rows per batch, 10,000 max, 5MB limit). Returns the input DataFrame with `[Latitude, Longitude]` columns appended.

3. **`timezone.py`** — Uses `timezonefinder` + `pytz` to map coordinates to timezone strings. Supports `fill_missing` to propagate timezones to rows without coordinates by grouping on `[ZipCode, City, State]`, then `[City, State]`, then `[State]`.

### Supporting modules

- **`models.py`** — Public types: `Coordinate` (NamedTuple), `Benchmark` (str enum for Census API benchmarks), `FillMissing` (IntEnum).
- **`constants.py`** — Column name constants (`Columns` class), env-var-based config (`TIMEZONE_FINDER_BIN_FILE_LOCATION`, `TIMEZONE_FINDER_IN_MEMORY`), and `get_date_in_ny()`.
- **`http.py`** — Async HTTP helpers (`get_json`, `get_and_download_file`, `post_and_download_file`) with tenacity retry logic (exponential backoff, max 3 retries or 60s).
- **`commands/`** — CLI built on `asyncclick`. Entry point: `__main__.py` → `commands.cli`.

### DataFrame column names

All column names are defined in `constants.Columns` to avoid magic strings:
`STREET`, `CITY`, `STATE`, `ZIPCODE`, `LATITUDE`, `LONGITUDE`, `TIMEZONE` (`"TZ"`).

## Testing

pytest is configured with `--doctest-modules --mypy --ruff --ruff-format`, so every run also type-checks and lints all modules. Doctests in module docstrings are executed as tests.

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `TIMEZONE_FINDER_BIN_FILE_LOCATION` | `None` | Custom binary file for `timezonefinder` |
| `TIMEZONE_FINDER_IN_MEMORY` | `false` | Load timezone data into memory for faster lookups |
