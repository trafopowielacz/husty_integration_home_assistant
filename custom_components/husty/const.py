"""Constants for the Husty integration."""

from datetime import timedelta

DOMAIN = "husty"

CONF_API_KEY = "api_key"

DEVICE_URL = "https://app.husty.pl/api/integrations/v1/device"

UPDATE_INTERVAL = timedelta(seconds=120)
REQUEST_TIMEOUT = 30

PLATFORMS: list[str] = [
    "sensor",
    "binary_sensor",
]
