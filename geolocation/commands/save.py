from __future__ import annotations

import datetime
import logging
from pathlib import Path

import asyncclick as click

from geolocation import census, constants, postal, timezone, utils
from geolocation.commands.common import cli

logger = logging.getLogger(__name__)


@cli.command("save")
@click.argument("file", type=click.Path(dir_okay=False, writable=True))
@click.option("--date", type=click.DateTime("%Y-%m-%d"), default=None)
@click.option("--city", type=str.casefold, multiple=True, default=None, help="Filter on City or Town")
@click.option("--state", type=str.upper, multiple=True, default=None, help="Filter on State")
@click.option("--zipcode", type=str, multiple=True, default=None, help="Filter on Zipcode")
@click.option("--coordinates", type=bool, is_flag=True, help="Flag indicating whether to include coordinates")
@click.option("--timezones", type=bool, is_flag=True, help="Flag indicating whether to include timezones")
async def save(  # noqa: PLR0913
    file: str,
    date: datetime.date | None,
    city: tuple[str, ...],
    state: tuple[str, ...] | None,
    zipcode: tuple[str, ...],
    coordinates: bool,
    timezones: bool,
) -> None:
    df_postal_locales = await postal.get_locales(date)
    logger.info("Query for locales returned %d rows.", len(df_postal_locales))

    if city:
        df_postal_locales = df_postal_locales[df_postal_locales[constants.Columns.CITY].str.casefold().isin(city)]
        logger.info("City filter set produced %d rows", len(df_postal_locales))

    if state:
        df_postal_locales = df_postal_locales[df_postal_locales[constants.Columns.STATE].isin(state)]
        logger.info("State filter set produced %d rows", len(df_postal_locales))

    if zipcode:
        df_postal_locales = df_postal_locales[df_postal_locales[constants.Columns.ZIPCODE].isin(zipcode)]
        logger.info("ZipCode filter set produced %d rows", len(df_postal_locales))

    if coordinates or timezones:
        # In order to include timezones, we need the coordinates
        df_postal_locales = await census.get_coordinates(df_postal_locales)

    if timezones:
        df_postal_locales = timezone.fill_timezones(df_postal_locales)
        if not coordinates:
            df_postal_locales = df_postal_locales.drop(columns=[constants.Columns.LATITUDE, constants.Columns.LONGITUDE])

    utils.save_frame(df_postal_locales, Path(file))
