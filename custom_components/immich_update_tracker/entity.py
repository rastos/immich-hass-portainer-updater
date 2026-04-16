from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .helpers import get_entry_name, get_entry_value


class ImmichBaseEntity(CoordinatorEntity):
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=get_entry_name(self.entry),
            manufacturer="Immich",
            model="Update Tracker",
            configuration_url=get_entry_value(self.entry, "immich_url"),
        )
