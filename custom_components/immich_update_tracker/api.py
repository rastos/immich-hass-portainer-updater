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
        self.immich_url = immich_url.rstrip("/")
        self.api_key = api_key.strip()
        self.webhook_url = webhook_url.strip()
        self.session = session

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "x-api-key": self.api_key,
            "x-immich-api-key": self.api_key,
        }

    async def _get_json_candidates(
        self,
        paths: list[str],
        *,
        use_auth: bool = True,
    ) -> dict[str, Any] | list[Any] | None:
        headers = self._headers if use_auth else {"Accept": "application/json"}

        for path in paths:
            url = f"{self.immich_url}{path}"
            try:
                async with asyncio.timeout(15):
                    async with self.session.get(url, headers=headers) as response:
                        if response.status in (401, 403):
                            raise ImmichAuthError("Authentication failed")
                        if response.status != 200:
                            _LOGGER.debug("Skipping %s due to HTTP %s", url, response.status)
                            continue
                        return await response.json()
            except ImmichAuthError:
                raise
            except (TimeoutError, ClientError, ValueError) as err:
                _LOGGER.debug("Request to %s failed: %s", url, err)
                continue

        return None

    async def validate(self) -> None:
        version = await self.get_current_version()
        if not version:
            raise ImmichApiError("Could not validate Immich version endpoint")

    async def get_current_version(self) -> str | None:
        data = await self._get_json_candidates(
            [
                "/api/server/version",
                "/api/server-info/version",
                "/server/version",
            ],
            use_auth=True,
        )
        return self.extract_current_version(data)

    async def get_version_check(self) -> dict[str, Any] | None:
        data = await self._get_json_candidates(
            [
                "/api/server/version-check",
                "/api/server/versionCheck",
                "/api/server-info/version-check",
                "/api/server-info/versionCheck",
                "/server/version-check",
                "/server/versionCheck",
            ],
            use_auth=True,
        )
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
        raw = ImmichUpdateClient._find_first(
            data,
            {
                "latestVersion",
                "latest_version",
                "newVersion",
                "releaseVersion",
                "release_version",
            },
        )
        if isinstance(raw, str):
            return clean_version(raw)
        if isinstance(raw, dict):
            return ImmichUpdateClient.extract_current_version(raw)
        return None

    @staticmethod
    def extract_update_available(data: dict[str, Any] | None) -> bool | None:
        raw = ImmichUpdateClient._find_first(
            data,
            {
                "isUpdateAvailable",
                "updateAvailable",
                "update_available",
                "hasUpdate",
                "has_update",
            },
        )
        return raw if isinstance(raw, bool) else None

    @staticmethod
    def _find_first(obj: Any, keys: set[str]) -> Any:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in keys:
                    return value
                found = ImmichUpdateClient._find_first(value, keys)
                if found is not None:
                    return found

        if isinstance(obj, list):
            for item in obj:
                found = ImmichUpdateClient._find_first(item, keys)
                if found is not None:
                    return found

        return None
