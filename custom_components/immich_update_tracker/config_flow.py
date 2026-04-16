from __future__ import annotations

from urllib.parse import urlparse

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ImmichApiError, ImmichAuthError, ImmichUpdateClient
from .const import (
    CONF_IMMICH_API_KEY,
    CONF_IMMICH_URL,
    CONF_NAME,
    CONF_POLL_INTERVAL_MINUTES,
    CONF_UPDATE_WEBHOOK_URL,
    DEFAULT_NAME,
    DEFAULT_POLL_INTERVAL_MINUTES,
    DOMAIN,
)
from .helpers import merged_entry_data


def _normalize_url(value: str) -> str:
    return value.rstrip("/").strip()


def _valid_url(value: str) -> str:
    value = _normalize_url(value)
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise vol.Invalid("invalid_url")
    return value


class ImmichUpdateTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                normalized_url = _valid_url(user_input[CONF_IMMICH_URL])
                normalized_webhook_url = _valid_url(user_input[CONF_UPDATE_WEBHOOK_URL])
            except vol.Invalid:
                errors["base"] = "invalid_url"
            else:
                await self.async_set_unique_id(normalized_url)
                self._abort_if_unique_id_configured()

                session = async_get_clientsession(self.hass)
                client = ImmichUpdateClient(
                    immich_url=normalized_url,
                    api_key=user_input[CONF_IMMICH_API_KEY],
                    webhook_url=normalized_webhook_url,
                    session=session,
                )

                try:
                    await client.validate()
                except ImmichAuthError:
                    errors["base"] = "auth"
                except ImmichApiError:
                    errors["base"] = "cannot_connect"
                except Exception:
                    errors["base"] = "unknown"
                else:
                    user_input[CONF_IMMICH_URL] = normalized_url
                    user_input[CONF_UPDATE_WEBHOOK_URL] = normalized_webhook_url
                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data=user_input,
                    )

        return self.async_show_form(step_id="user", data_schema=_build_schema(), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        return ImmichUpdateTrackerOptionsFlow()


class ImmichUpdateTrackerOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        errors = {}
        current = merged_entry_data(self.config_entry)

        if user_input is not None:
            try:
                normalized_url = _valid_url(user_input[CONF_IMMICH_URL])
                normalized_webhook_url = _valid_url(user_input[CONF_UPDATE_WEBHOOK_URL])
            except vol.Invalid:
                errors["base"] = "invalid_url"
            else:
                session = async_get_clientsession(self.hass)
                client = ImmichUpdateClient(
                    immich_url=normalized_url,
                    api_key=user_input[CONF_IMMICH_API_KEY],
                    webhook_url=normalized_webhook_url,
                    session=session,
                )
                try:
                    await client.validate()
                except ImmichAuthError:
                    errors["base"] = "auth"
                except ImmichApiError:
                    errors["base"] = "cannot_connect"
                except Exception:
                    errors["base"] = "unknown"
                else:
                    user_input[CONF_IMMICH_URL] = normalized_url
                    user_input[CONF_UPDATE_WEBHOOK_URL] = normalized_webhook_url
                    return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(current),
            errors=errors,
        )


def _build_schema(defaults: dict | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_NAME)): str,
            vol.Required(CONF_IMMICH_URL, default=defaults.get(CONF_IMMICH_URL, "")): str,
            vol.Required(CONF_IMMICH_API_KEY, default=defaults.get(CONF_IMMICH_API_KEY, "")): str,
            vol.Required(
                CONF_UPDATE_WEBHOOK_URL,
                default=defaults.get(CONF_UPDATE_WEBHOOK_URL, ""),
            ): str,
            vol.Required(
                CONF_POLL_INTERVAL_MINUTES,
                default=defaults.get(CONF_POLL_INTERVAL_MINUTES, DEFAULT_POLL_INTERVAL_MINUTES),
            ): vol.All(vol.Coerce(int), vol.Range(min=5, max=1440)),
        }
    )
