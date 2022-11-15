from homeassistant.const import (TEMP_CELSIUS)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    my_boiler = hass.data[DOMAIN][config_entry.entry_id]


class BoilerEntity(Entity):
    @property
    def supported_features(self):
        return self._supported_features

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    _attr_unit_of_measurement = TEMP_CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self, boiler):
        self._boiler = boiler
        self._attributes = {}
        self._unique_id = None
        self._unit_of_measurement = None
        self._device_class = None
        self._state_class = SensorDeviceClass.TEMPERATUR
        self._available = True
        self.device_id = 10001

        self.name = "Boiler_Zanussi"
        self.domain = DOMAIN
        self.icon = "mdi:oil"
        self.class_ = "Boiler"
        self.dev_class = "heating"
        self.unit = "°C"
        self.state = 0
        self.min_temp = 0
        self.max_temp = 75
        self.target_temp = 50
        self.temperature = 0
        self.temp_step = 1
        self.antibacterial = 0
        self.mode = "off"
        self.modes = ["off", "power1", "power2", "power3", "timer", "nofrost"]
        self.supported_features = 3
        self.attributes = {
            "min_temp": self.min_temp,
            "max_temp": self.max_temp,
            "target_temp": self.target_temp,
            "temp_step": self.temp_step,
            "antibacterial": self.antibacterial,
            "temperature": self.temperature,
            "mode": self.mode,
            "modes": self.modes,
            "supported_features": self.supported_features,
        }
        self.payload = {
            "name": self.name,
            "domain": self.domain,
            "icon": self.icon,
            "class": self.class_,
            "dev_class": self.dev_class,
            "unit": self.unit,
            "state": self.state,
            "attributes": self.attributes,
        }

    @supported_features.setter
    def supported_features(self, value):
        self._supported_features = value

    @name.setter
    def name(self, value):
        self._name = value

    @icon.setter
    def icon(self, value):
        self._icon = value

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self.name,
            "sw_version": "none",
            "model": "Model name",
            "manufacturer": "manufacturer",
        }
