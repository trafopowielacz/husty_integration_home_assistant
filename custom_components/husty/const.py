"""Constants for the Husty integration."""

DOMAIN = "husty"

CONF_API_KEY = "api_key"
CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_UPDATE_INTERVAL = 120
UPDATE_INTERVAL_OPTIONS = (5, 10, 30, 60, 120, 300)

DEVICE_URL = "https://app.husty.pl/api/integrations/v1/device"

REQUEST_TIMEOUT = 30

PLATFORMS: list[str] = [
    "sensor",
    "binary_sensor",
]
