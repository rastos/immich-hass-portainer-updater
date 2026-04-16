from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_CURRENT_VERSION,
    ATTR_LATEST_VERSION,
    ATTR_SOURCE,
    ATTR_UPDATE_AVAILABLE,
    DOMAIN,
)
from .entity import ImmichBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ImmichUpdateAvailableBinarySensor(coordinator, entry)])


class ImmichUpdateAvailableBinarySensor(ImmichBaseEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Update Available"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_{ATTR_UPDATE_AVAILABLE}"

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get(ATTR_UPDATE_AVAILABLE, False))

    @property
    def icon(self) -> str:
        return "mdi:update" if self.is_on else "mdi:check-circle"

    @property
    def extra_state_attributes(self):
        return {
            ATTR_CURRENT_VERSION: self.coordinator.data.get(ATTR_CURRENT_VERSION),
            ATTR_LATEST_VERSION: self.coordinator.data.get(ATTR_LATEST_VERSION),
            ATTR_SOURCE: self.coordinator.data.get(ATTR_SOURCE),
        }
