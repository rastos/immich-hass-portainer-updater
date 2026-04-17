from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiohttp import ClientError, ClientSession

from .helpers import clean_version

_LOGGER = logging.getLogger(__name__)


class ImmichApiError(Exception):
    """Base API error."""


class ImmichAuthError(ImmichApiError):
    """Authentication error."""


class ImmichWebhookError(ImmichApiError):
    """Webhook error."""


class ImmichUpdateClient:
    def __init__(
        self,
        immich_url: str,
        api_key: str,
        webhook_url: str,
        session: ClientSession,
    ) -> None:
        self.immich_url = self._normalize_base_url(immich_url)
        self.api_key = api_key.strip()
        self.webhook_url = webhook_url.strip()
        self.session = session

    @staticmethod
    def _normalize_base_url(url: str) -> str:
        url = url.rstrip("/").strip()
        if url.endswith("/api"):
            url = url[:-4]
        return url

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "x-api-key": self.api_key,
        }

    async def _get_json(self, path: str, *, use_auth: bool = True) -> dict[str, Any] | list[Any] | None:
        headers = self._headers if use_auth else {"Accept": "application/json"}
        url = f"{self.immich_url}{path}"

        try:
            async with asyncio.timeout(15):
                async with self.session.get(url, headers=headers) as response:
                    if response.status in (401, 403):
                        raise ImmichAuthError(f"Authentication failed for {path}")
                    if response.status != 200:
                        text = await response.text()
                        _LOGGER.debug("Request to %s failed with HTTP %s: %s", url, response.status, text)
                        return None
                    return await response.json()
        except ImmichAuthError:
            raise
        except (TimeoutError, ClientError, ValueError) as err:
            raise ImmichApiError(f"Request failed for {path}: {err}") from err

    async def validate(self) -> None:
        version = await self.get_current_version()
        if not version:
            raise ImmichApiError("Could not validate Immich version endpoint")

    async def get_current_version(self) -> str | None:
        data = await self._get_json("/api/server/version", use_auth=True)
        return self.extract_current_version(data)

    async def get_version_check(self) -> dict[str, Any] | None:
        data = await self._get_json("/api/server/version-check", use_auth=True)
        return data if isinstance(data, dict) else None

    async def get_latest_github_release(self) -> str | None:
        url = "https://api.github.com/repos/immich-app/immich/releases/latest"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "HomeAssistant-ImmichUpdateTracker",
        }

        try:
            async with asyncio.timeout(15):
                async with self.session.get(url, headers=headers) as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
        except (TimeoutError, ClientError, ValueError):
            return None

        tag_name = data.get("tag_name")
        return clean_version(tag_name) if isinstance(tag_name, str) else None

    async def trigger_update(self) -> None:
        payload = {
            "source": "home_assistant",
            "integration": "immich_update_tracker",
        }

        try:
            async with asyncio.timeout(20):
                async with self.session.post(self.webhook_url, json=payload) as response:
                    if 200 <= response.status < 300:
                        return
                    text = await response.text()
        except (TimeoutError, ClientError) as err:
            raise ImmichWebhookError(str(err)) from err

        raise ImmichWebhookError(f"Webhook failed with HTTP {response.status}: {text}")

    @staticmethod
    def extract_current_version(data: dict[str, Any] | list[Any] | None) -> str | None:
        if not isinstance(data, dict):
            return None

        if all(key in data for key in ("major", "minor", "patch")):
            return f"{data['major']}.{data['minor']}.{data['patch']}"

        for key in ("version", "currentVersion", "current_version"):
            value = data.get(key)
            if isinstance(value, str):
                return clean_version(value)

        return None

    @staticmethod
    def extract_latest_version(data: dict[str, Any] | None) -> str | None:
        if not isinstance(data, dict):
            return None

        for key in (
            "releaseVersion",
            "latestVersion",
            "latest_version",
            "newVersion",
            "release_version",
        ):
            value = data.get(key)
            if isinstance(value, str):
                return clean_version(value)

        return None

    @staticmethod
    def extract_update_available(data: dict[str, Any] | None) -> bool | None:
        if not isinstance(data, dict):
            return None

        for key in (
            "isUpdateAvailable",
            "updateAvailable",
            "update_available",
            "hasUpdate",
            "has_update",
        ):
            value = data.get(key)
            if isinstance(value, bool):
                return value

        return None
