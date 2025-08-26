from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import backoff
import curl_cffi
from aiofiles import tempfile
from curl_cffi import requests

from zipcode_coordinates_tz import constants

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=constants.MAX_RETRIES, max_time=constants.MAX_RETRY_TIME)
@asynccontextmanager
async def get_json(session: requests.AsyncSession, url: str, params: dict[str, Any] | None = None) -> AsyncIterator[dict[str, Any]]:
    """
    Executes a get request returning a json payload

    Args:
        session (requests.AsyncSession): The Session.
        url (str): The url to the file to download.

    Returns:
        An Iterator that contains the json payload.
    """
    response = await session.get(url)
    response.raise_for_status()
    data: dict[str, Any] = await response.json()
    yield data


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=constants.MAX_RETRIES, max_time=constants.MAX_RETRY_TIME)
@asynccontextmanager
async def get_and_download_file(session: requests.AsyncSession, url: str) -> AsyncIterator[Path]:
    """
    Downloads a file from the specified url and returns the Path.

    Args:
        session (requests.AsyncSession): The Session.
        url (str): The url to the file to download.

    Returns:
        An Iterator that contains the Path to the downloaded file.
    """
    url_path = Path(url)
    logger.debug("Downloading %s", url)
    async with tempfile.NamedTemporaryFile(prefix=url_path.with_suffix("").name, suffix=url_path.suffix, delete=False) as f:
        response = await session.get(url, stream=True)
        response.raise_for_status()
        download_path = Path(cast("str", f.name))
        logger.debug("Saving %s to %s", url, download_path)
        async for chunk in response.aiter_content(chunk_size=constants.BUFFER_LENGTH):
            await f.write(chunk)

        await f.flush()
        await f.close()
        try:
            logger.debug("Downloaded %d bytes.", download_path.stat().st_size)
            yield download_path
        finally:
            if download_path.exists():
                download_path.unlink()


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=constants.MAX_RETRIES, max_time=constants.MAX_RETRY_TIME)
@asynccontextmanager
async def post_and_download_file(session: requests.AsyncSession, url: str, params: dict[str, Any], mp: curl_cffi.CurlMime) -> AsyncIterator[Path]:
    """
    Downloads a file from the specified url and returns the Path.

    Args:
        session (requests.AsyncSession): The Session.
        url (str): The url to the file to download.

    Returns:
        An Iterator that contains the Path to the downloaded file.
    """
    url_path = Path(url)
    logger.debug("Downloading %s", url)
    async with tempfile.NamedTemporaryFile(prefix=url_path.with_suffix("").name, suffix=url_path.suffix, delete=False) as f:
        response = await session.post(url, multipart=mp, params=params, stream=True)
        response.raise_for_status()
        download_path = Path(cast("str", f.name))
        logger.debug("Saving %s to %s", url, download_path)
        async for chunk in response.aiter_content(chunk_size=constants.BUFFER_LENGTH):
            await f.write(chunk)

        await f.flush()
        await f.close()
        try:
            logger.debug("Downloaded %d bytes.", download_path.stat().st_size)
            yield download_path
        finally:
            if download_path.exists():
                download_path.unlink()
