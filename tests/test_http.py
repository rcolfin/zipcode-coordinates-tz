from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from zipcode_coordinates_tz import http


def _make_streaming_response(content: bytes) -> MagicMock:
    """Build a mock streaming response that yields content in one chunk."""
    response = MagicMock()
    response.raise_for_status = MagicMock()

    async def aiter_content(chunk_size: int = 1024):
        yield content

    response.aiter_content = aiter_content
    return response


@pytest.mark.asyncio
class TestGetJson:
    async def test_returns_payload(self) -> None:
        payload: dict[str, Any] = {"key": "value"}
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=payload)

        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)

        async with http.get_json(mock_session, "https://example.com") as data:
            assert data == payload

    async def test_passes_params(self) -> None:
        payload: dict[str, Any] = {}
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=payload)

        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)

        params = {"format": "json"}
        async with http.get_json(mock_session, "https://example.com", params):
            mock_session.get.assert_called_once_with("https://example.com")

    async def test_no_params_by_default(self) -> None:
        payload: dict[str, Any] = {}
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=payload)

        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)

        async with http.get_json(mock_session, "https://example.com"):
            pass

        mock_session.get.assert_called_once()


@pytest.mark.asyncio
class TestGetAndDownloadFile:
    async def test_downloads_content(self) -> None:
        content = b"file content here"
        mock_response = _make_streaming_response(content)
        mock_response.raise_for_status = MagicMock()

        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)

        async with http.get_and_download_file(mock_session, "https://example.com/file.csv") as path:
            assert isinstance(path, Path)
            assert path.read_bytes() == content

    async def test_file_is_deleted_after_context(self) -> None:
        content = b"data"
        mock_response = _make_streaming_response(content)
        mock_response.raise_for_status = MagicMock()

        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)

        async with http.get_and_download_file(mock_session, "https://example.com/file.csv") as path:
            saved_path = path

        assert not saved_path.exists()


@pytest.mark.asyncio
class TestPostAndDownloadFile:
    async def test_downloads_response_content(self) -> None:
        content = b"response data"
        mock_response = _make_streaming_response(content)
        mock_response.raise_for_status = MagicMock()

        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)

        mock_mp = MagicMock()

        async with http.post_and_download_file(mock_session, "https://example.com/upload", {}, mock_mp) as path:
            assert isinstance(path, Path)
            assert path.read_bytes() == content

    async def test_file_is_deleted_after_context(self) -> None:
        content = b"data"
        mock_response = _make_streaming_response(content)
        mock_response.raise_for_status = MagicMock()

        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)

        mock_mp = MagicMock()

        async with http.post_and_download_file(mock_session, "https://example.com/upload", {}, mock_mp) as path:
            saved_path = path

        assert not saved_path.exists()

    async def test_passes_params_to_post(self) -> None:
        content = b""
        mock_response = _make_streaming_response(content)
        mock_response.raise_for_status = MagicMock()

        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)

        mock_mp = MagicMock()
        params = {"benchmark": "4"}

        async with http.post_and_download_file(mock_session, "https://example.com/upload", params, mock_mp):
            pass

        mock_session.post.assert_called_once_with(
            "https://example.com/upload",
            multipart=mock_mp,
            params=params,
            stream=True,
        )
