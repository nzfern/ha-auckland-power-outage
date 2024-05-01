import logging
import requests
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from datetime import datetime, timedelta
from homeassistant.components.sensor import SensorEntity, PLATFORM_SCHEMA
from .const import CONF_ICP_NUMBER

_LOGGER = logging.getLogger(__name__)

# 常量定义
API_URL = "https://outagereporter.api.vector.co.nz/v2/planned-outages"
SCAN_INTERVAL = timedelta(minutes=60)
TIME_FORMAT = "%Y-%m-%d %H:%M"
API_KEY = "o2AGN2LXeYbNvyE5cytNGX9INtcPLfj7"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ICP_NUMBER): cv.string,
    }
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the power outage sensor platform."""
    icp_number = config[CONF_ICP_NUMBER]

    sensors = [
        PowerOutageStartTimeSensor(icp_number, hass),
        PowerOutageEndTimeSensor(icp_number, hass),
    ]
    async_add_entities(sensors)

class PowerOutageSensor(SensorEntity):
    def __init__(self, icp_number, hass, sensor_type):
        """Initialize the sensor."""
        super().__init__()
        self.hass = hass
        self._icp_number = icp_number
        self._outage = None
        self._name = f"Planned Power Outage {sensor_type}"
        self._icon = "mdi:power-plug-off-outline"
        self._unique_id = f"power_outage_sensor_{icp_number}_{sensor_type}"
        self._attr_unique_id = self._unique_id
        self._state = None
        self._outage_reason = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "reason": self._outage_reason
        }

    async def async_update(self):
        response = await self.hass.async_add_executor_job(self.call_api)

        if response is not None:
            data = response.json()
            future_outages = data.get("futurePlannedOutages", [])

            if future_outages:
                self._outage = future_outages[0]
                self._outage_reason = self._outage.get("reason")
                self._update_state()
            else:
                self._state = None
                self._outage_reason = None
                self._outage = None
        else:
            self._state = None
            self._outage_reason = None
            self._outage = None

        if self.hass is not None:
            self.async_write_ha_state()

    def _update_state(self):
        raise NotImplementedError()

    def call_api(self):
        params = {
            "groupByTimezone": "Pacific%2FAuckland",
            "icpNumber": self._icp_number
        }
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Apikey": API_KEY,
        }

        try:
            response = requests.get(API_URL, params=params, headers=headers)
            response.raise_for_status()
            return response
        except Exception as e:
            _LOGGER.error(f"Error occurred during API call: {e}")
            return None

class PowerOutageStartTimeSensor(PowerOutageSensor):
    def __init__(self, icp_number, hass):
        super().__init__(icp_number, hass, "Start Time")

    def _update_state(self):
        if self._outage is not None:
            advertised_start_date = self._outage.get("advertisedStartDate")
            advertised_times = self._outage.get("advertisedTimes", [])

            if advertised_start_date and advertised_times:
                start_time = advertised_start_date + " " + advertised_times[0].get("start")
                self._state = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").strftime(TIME_FORMAT)
            else:
                self._state = None

class PowerOutageEndTimeSensor(PowerOutageSensor):
    def __init__(self, icp_number, hass):
        super().__init__(icp_number, hass, "End Time")

    def _update_state(self):
        if self._outage is not None:
            advertised_end_date = self._outage.get("advertisedEndDate")
            advertised_times = self._outage.get("advertisedTimes", [])

            if advertised_end_date and advertised_times:
                end_time = advertised_end_date + " " + advertised_times[0].get("end")
                self._state = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").strftime(TIME_FORMAT)
            else:
                self._state = None