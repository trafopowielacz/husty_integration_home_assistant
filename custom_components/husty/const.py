"""Constants for the Husty integration."""

from datetime import timedelta

DOMAIN = "husty"

CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_DEVICE_ID = "device_id"

PLATFORMS = [
    "sensor",
    "binary_sensor",
]

API_URL = "https://aplikacja.husty.pl"

LOGIN_URL = f"{API_URL}/api/auth/sign-in/email"
SESSION_URL = f"{API_URL}/api/auth/get-session"

DEVICE_URL = (
    f"{API_URL}/api/trpc/"
    "device.getSensorsForSoftener,device.getDevice"
)

UPDATE_INTERVAL = timedelta(seconds=60)

REQUEST_TIMEOUT = 30
