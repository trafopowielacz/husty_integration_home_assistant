DOMAIN = "husty"

API_URL = "https://aplikacja.husty.pl"

LOGIN_URL = (
    API_URL +
    "/api/auth/sign-in/email"
)

SESSION_URL = (
    API_URL +
    "/api/auth/get-session"
)

DEVICE_URL = (
    API_URL +
    "/api/trpc/device.getSensorsForSoftener,device.getDevice"
)

SCAN_INTERVAL = 300