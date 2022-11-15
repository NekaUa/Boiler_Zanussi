from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .Boiler_Zanussi import boiler
from custom_components.Boiler_Zanussi.const import DOMAIN
import logging
_LOGGER = logging.getLogger(__name__)
#Перечисляем типы устройств, которое поддерживает интеграция
PLATFORMS: list[str] = ["sensor", "binary_sensor", "switch"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    #Создаем объект с подключением к сервису
    my_boiler = boiler.Boiler(hass, entry.data["username"], entry.data["password"])
    #Сохраняем объект в hass.data для доступа из других компонентов
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = my_boiler
#Вызываем метод получения данных в асинхронной джобе
    await hass.async_add_executor_job(
             my_boiler.get_state, my_boiler
         )

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok