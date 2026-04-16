from __future__ import annotations

import re
from typing import Any

from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_IMMICH_API_KEY,
    CONF_IMMICH_URL,
    CONF_NAME,
    CONF_POLL_INTERVAL_MINUTES,
    CONF_UPDATE_WEBHOOK_URL,
    DEFAULT_NAME,
    DEFAULT_POLL_INTERVAL_MINUTES,
)


VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def get_entry_value(entry: ConfigEntry, key: str) -> Any:
    return entry.options.get(key, entry.data.get(key))


def get_entry_name(entry: ConfigEntry) -> str:
    return str(get_entry_value(entry, CONF_NAME) or entry.title or DEFAULT_NAME)


def merged_entry_data(entry: ConfigEntry) -> dict[str, Any]:
    return {
        CONF_NAME: get_entry_value(entry, CONF_NAME) or DEFAULT_NAME,
        CONF_IMMICH_URL: get_entry_value(entry, CONF_IMMICH_URL),
        CONF_IMMICH_API_KEY: get_entry_value(entry, CONF_IMMICH_API_KEY),
        CONF_UPDATE_WEBHOOK_URL: get_entry_value(entry, CONF_UPDATE_WEBHOOK_URL),
        CONF_POLL_INTERVAL_MINUTES: int(
            get_entry_value(entry, CONF_POLL_INTERVAL_MINUTES)
            or DEFAULT_POLL_INTERVAL_MINUTES
        ),
    }


def clean_version(value: str | None) -> str | None:
    if not value or not isinstance(value, str):
        return None
    value = value.strip().lstrip("v")
    match = VERSION_RE.search(value)
    return ".".join(match.groups()) if match else value


def version_tuple(value: str | None) -> tuple[int, int, int] | None:
    if not value:
        return None
    match = VERSION_RE.search(value)
    if not match:
        return None
    return tuple(int(x) for x in match.groups())


def is_newer_version(latest: str | None, current: str | None) -> bool | None:
    latest_t = version_tuple(latest)
    current_t = version_tuple(current)
    if not latest_t or not current_t:
        return None
    return latest_t > current_t
