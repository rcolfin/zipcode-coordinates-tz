import asyncio
import logging

from geolocation import census, postal, timezone

logger = logging.getLogger(__name__)


async def main() -> None:
    df_postal_locales = await postal.get_locales()
    logger.info("Queried %d postal locales", len(df_postal_locales))

    df_postal_locales = df_postal_locales.loc[df_postal_locales.State == "NJ"]
    logger.info("Filtered to %d NJ postal locales", len(df_postal_locales))

    df_postal_locales = await census.get_coordinates(df_postal_locales)
    logger.info("Added coordinates.")

    df_postal_locales = timezone.fill_timezones(df_postal_locales)
    logger.info(df_postal_locales)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)-12s: %(levelname)-8s\t%(message)s",
    )

    asyncio.run(main())
