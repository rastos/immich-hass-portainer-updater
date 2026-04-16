from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import ImmichWebhookError
from .const import DOMAIN
from .entity import ImmichBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ImmichUpdateButton(coordinator, entry)])


class ImmichUpdateButton(ImmichBaseEntity, ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Run Update"
    _attr_icon = "mdi:cloud-download-outline"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_run_update"

    async def async_press(self) -> None:
        try:
            await self.coordinator.client.trigger_update()
        except ImmichWebhookError as err:
            raise HomeAssistantError(f"Failed to trigger update webhook: {err}") from err
        await self.coordinator.async_request_refresh()
