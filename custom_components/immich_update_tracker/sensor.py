from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_CURRENT_VERSION, ATTR_LATEST_VERSION, ATTR_SOURCE, DOMAIN
from .entity import ImmichBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            ImmichVersionSensor(coordinator, entry, ATTR_CURRENT_VERSION, "Current Version", "mdi:package-up"),
            ImmichVersionSensor(coordinator, entry, ATTR_LATEST_VERSION, "Latest Version", "mdi:tag"),
        ]
    )


class ImmichVersionSensor(ImmichBaseEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry, key: str, name: str, icon: str) -> None:
        super().__init__(coordinator, entry)
        self._key = key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)

    @property
    def extra_state_attributes(self):
        return {ATTR_SOURCE: self.coordinator.data.get(ATTR_SOURCE)}
