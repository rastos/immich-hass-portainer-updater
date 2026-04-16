from __future__ import annotations

from datetime import timedelta
from typing import Any
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ImmichAuthError, ImmichUpdateClient
from .const import (
    ATTR_CURRENT_VERSION,
    ATTR_LATEST_VERSION,
    ATTR_SOURCE,
    ATTR_UPDATE_AVAILABLE,
    ATTR_VERSION_CHECK_RAW,
    DOMAIN,
    SOURCE_GITHUB,
    SOURCE_IMMICH_API,
    SOURCE_UNKNOWN,
)
from .helpers import get_entry_name, is_newer_version, merged_entry_data

_LOGGER = logging.getLogger(__name__)


class ImmichUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: ImmichUpdateClient,
    ) -> None:
        self.entry = entry
        self.client = client
        merged = merged_entry_data(entry)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(minutes=merged["poll_interval_minutes"]),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            current_version = await self.client.get_current_version()
            if not current_version:
                raise UpdateFailed("Could not fetch current Immich version")

            version_check = await self.client.get_version_check()
            latest_version = self.client.extract_latest_version(version_check)
            update_available = self.client.extract_update_available(version_check)
            source = SOURCE_IMMICH_API if version_check is not None else SOURCE_UNKNOWN

            if not latest_version:
                latest_version = await self.client.get_latest_github_release()
                if latest_version:
                    source = SOURCE_GITHUB

            if update_available is None:
                update_available = is_newer_version(latest_version, current_version)

            return {
                ATTR_CURRENT_VERSION: current_version,
                ATTR_LATEST_VERSION: latest_version,
                ATTR_UPDATE_AVAILABLE: bool(update_available) if update_available is not None else False,
                ATTR_SOURCE: source,
                ATTR_VERSION_CHECK_RAW: version_check,
            }
        except ImmichAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(str(err)) from err

    @property
    def device_name(self) -> str:
        return get_entry_name(self.entry)
