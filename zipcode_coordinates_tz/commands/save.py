from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Final

import asyncclick as click

from zipcode_coordinates_tz import census, constants, postal, timezone, utils
from zipcode_coordinates_tz.commands.common import cli

if TYPE_CHECKING:
    import datetime

logger = logging.getLogger(__name__)

DATE_TIME_FMT: Final[str] = "%Y-%m-%d"


@cli.command("save")
@click.argument("file", type=click.Path(dir_okay=False, writable=True))
@click.option("--date", type=click.DateTime([DATE_TIME_FMT]), default=constants.get_date_in_ny().strftime(DATE_TIME_FMT))
@click.option("--city", type=str.casefold, multiple=True, default=None, help="Filter on City or Town")
@click.option("--state", type=str.upper, multiple=True, default=None, help="Filter on State")
@click.option("--zipcode", type=str, multiple=True, default=None, help="Filter on Zipcode")
@click.option("--coordinates", type=bool, is_flag=True, help="Flag indicating whether to include coordinates")
@click.option("--timezones", type=bool, is_flag=True, help="Flag indicating whether to include timezones")
@click.option(
    "--fill",
    type=bool,
    is_flag=True,
    help="Flag indicating whether to fill in missing timezones with a value from their closest location.",
)
async def save(  # noqa: PLR0913
    file: str,
    date: datetime.date | None,
    city: tuple[str, ...],
    state: tuple[str, ...] | None,
    zipcode: tuple[str, ...],
    coordinates: bool,
    timezones: bool,
    fill: bool,
) -> None:
    df_postal_locales = await postal.get_locales(date)
    logger.info("Query for locales returned %d rows.", len(df_postal_locales))

    if city:
        df_postal_locales = df_postal_locales[df_postal_locales[constants.Columns.CITY].str.casefold().isin(city)]
        logger.info("City filter set applied reduced to %d rows", len(df_postal_locales))

    if state:
        df_postal_locales = df_postal_locales[df_postal_locales[constants.Columns.STATE].isin(state)]
        logger.info("State filter set applied reduced to %d rows", len(df_postal_locales))

    if zipcode:
        df_postal_locales = df_postal_locales[df_postal_locales[constants.Columns.ZIPCODE].isin(zipcode)]
        logger.info("ZipCode filter set applied reduced to %d rows", len(df_postal_locales))

    if coordinates or timezones:
        # In order to include timezones, we need the coordinates
        df_postal_locales = await census.get_coordinates(df_postal_locales)

    if timezones:
        df_postal_locales = timezone.fill_timezones(df_postal_locales, fill_missing=fill)

        df_postal_locales_missing_tz = df_postal_locales[df_postal_locales[constants.Columns.TIMEZONE].isna()]
        if not df_postal_locales_missing_tz.empty:
            logger.warning("There are %d rows with missing timezones.", len(df_postal_locales_missing_tz))

        if not coordinates:
            df_postal_locales = df_postal_locales.drop(columns=[constants.Columns.LATITUDE, constants.Columns.LONGITUDE])

    utils.save_frame(df_postal_locales, Path(file))
