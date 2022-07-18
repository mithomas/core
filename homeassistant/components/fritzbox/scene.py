"""Support for Fritzbox templates."""

from __future__ import annotations

from typing import Any

from pyfritzhome.devicetypes import FritzhomeTemplate

from homeassistant.components.scene import Scene
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_COORDINATOR, DOMAIN as FRITZBOX_DOMAIN
from .coordinator import FritzboxDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the FRITZ!SmartHome template from ConfigEntry."""

    coordinator = hass.data[FRITZBOX_DOMAIN][entry.entry_id][CONF_COORDINATOR]

    async_add_entities(
        FritzboxScene(template, coordinator)
        for template in coordinator.data["templates"].values()
    )


class FritzboxScene(Scene, CoordinatorEntity):
    """Representation of a FritzBox scene."""

    coordinator: FritzboxDataUpdateCoordinator

    def __init__(
        self,
        template: FritzhomeTemplate,
        coordinator: FritzboxDataUpdateCoordinator,
    ) -> None:
        """Initialize the Fritzbox Smarthome scene."""

        super().__init__(coordinator)

        self.ain = template.ain
        self.coordinator = coordinator
        self.available_on_last_update = True
        self._attr_name = template.name
        self._attr_unique_id = f"{self.ain}"

    async def async_activate(self, **kwargs: Any) -> None:
        """Activate the scene."""
        await self.hass.async_add_executor_job(
            self.coordinator.fritz.apply_template, self.ain
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return super().available and self.available_on_last_update

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle rename & deletions."""

        self._attr_name = self.coordinator.data["templates"][self.ain].name
        self.available_on_last_update = self.ain in self.coordinator.data["templates"]
        self.async_write_ha_state()
