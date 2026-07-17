"""Communication with the Husty cloud API."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aiohttp

from .const import (
    DEVICE_URL,
    LOGIN_URL,
    REQUEST_TIMEOUT,
    SESSION_URL,
)

_LOGGER = logging.getLogger(__name__)


class HustyApiError(Exception):
    """Base Husty API exception."""


class HustyAuthenticationError(HustyApiError):
    """Raised when authentication fails."""


class HustyConnectionError(HustyApiError):
    """Raised when communication with Husty fails."""


class HustyInvalidResponseError(HustyApiError):
    """Raised when Husty returns an unexpected response."""


class HustyApiClient:
    """Husty cloud API client."""

    def __init__(
        self,
        email: str,
        password: str,
        device_id: str,
    ) -> None:
        """Initialize the API client."""

        self.email = email.strip()
        self.password = password
        self.device_id = device_id.strip()

        self._session: aiohttp.ClientSession | None = None
        self._authenticated = False

    async def async_close(self) -> None:
        """Close the HTTP session."""

        if self._session is not None and not self._session.closed:
            await self._session.close()

        self._session = None
        self._authenticated = False

    async def _async_get_session(self) -> aiohttp.ClientSession:
        """Return or create the private HTTP session."""

        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

            self._session = aiohttp.ClientSession(
                timeout=timeout,
                cookie_jar=aiohttp.CookieJar(),
                headers={
                    "Accept": "application/json",
                    "User-Agent": "HomeAssistant-Husty/0.0.6",
                },
            )

        return self._session

    async def async_login(self) -> None:
        """Log in to Husty."""

        session = await self._async_get_session()

        payload = {
            "email": self.email,
            "password": self.password,
        }

        try:
            async with session.post(
                LOGIN_URL,
                json=payload,
            ) as response:
                _LOGGER.debug(
                    "Husty login status: %s cookies: %s",
                     response.status,
                     list(session.cookie_jar),
                )
                if response.status in (401, 403):
                    self._authenticated = False
                    raise HustyAuthenticationError(
                        "Nieprawidłowy login lub hasło Husty"
                    )

                if response.status >= 400:
                    body = await response.text()

                    raise HustyConnectionError(
                        f"Logowanie Husty zwróciło HTTP "
                        f"{response.status}: {body[:200]}"
                    )

                # Odczyt odpowiedzi, aby połączenie zostało poprawnie zwolnione.
                await response.read()

        except HustyAuthenticationError:
            raise

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            self._authenticated = False

            raise HustyConnectionError(
                f"Błąd połączenia podczas logowania: {err}"
            ) from err

        self._authenticated = True
        _LOGGER.debug("Logowanie do Husty zakończone powodzeniem")

    async def async_check_session(self) -> bool:
        """Check whether the current Husty session is valid."""

        if not self._authenticated:
            return False

        session = await self._async_get_session()

        try:
            async with session.get(SESSION_URL) as response:
                if response.status in (401, 403):
                    self._authenticated = False
                    return False

                if response.status >= 400:
                    return False

                data = await response.json(content_type=None)

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
            ValueError,
        ):
            return False

        return bool(data)

    async def async_get_data(self) -> dict[str, Any]:
        """Fetch and normalize Husty data."""

        if not await self.async_check_session():
            await self.async_login()

        try:
            return await self._async_request_device_data()

        except HustyAuthenticationError:
            # Sesja mogła wygasnąć pomiędzy sprawdzeniem a odczytem.
            self._authenticated = False
            await self.async_login()

            return await self._async_request_device_data()

    async def _async_request_device_data(self) -> dict[str, Any]:
        """Fetch device data from the tRPC endpoint."""

        session = await self._async_get_session()

        params = {
            "batch": "1",
            "input": json.dumps(
                {
                    "0": {
                        "json": {
                            "softenerDeviceId": self.device_id,
                        }
                    },
                    "1": {
                        "json": {
                            "deviceId": self.device_id,
                        }
                    },
                },
                separators=(",", ":"),
            ),
        }

        try:
            async with session.get(
                DEVICE_URL,
                params=params,
            ) as response:
                if response.status in (401, 403):
                    self._authenticated = False
                    raise HustyAuthenticationError(
                        "Sesja Husty wygasła"
                    )

                if response.status >= 400:
                    body = await response.text()

                    raise HustyConnectionError(
                        f"API Husty zwróciło HTTP "
                        f"{response.status}: {body[:200]}"
                    )

                raw_data = await response.json(content_type=None)

        except HustyAuthenticationError:
            raise

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise HustyConnectionError(
                f"Błąd komunikacji z API Husty: {err}"
            ) from err

        except ValueError as err:
            raise HustyInvalidResponseError(
                "API Husty nie zwróciło poprawnego JSON"
            ) from err

        return self._normalize_response(raw_data)

    def _normalize_response(
        self,
        raw_data: Any,
    ) -> dict[str, Any]:
        """Normalize the tRPC batch response."""

        if not isinstance(raw_data, list) or len(raw_data) < 2:
            raise HustyInvalidResponseError(
                "Nieprawidłowa odpowiedź zbiorcza tRPC"
            )

        try:
            sensor_modules = raw_data[0]["result"]["data"]["json"]
            device = raw_data[1]["result"]["data"]["json"]

        except (KeyError, IndexError, TypeError) as err:
            raise HustyInvalidResponseError(
                "Brak wymaganych danych urządzenia w odpowiedzi Husty"
            ) from err

        if not isinstance(device, dict):
            raise HustyInvalidResponseError(
                "Dane urządzenia Husty mają nieprawidłowy format"
            )

        returned_device_id = str(device.get("deviceId", ""))

        if returned_device_id != self.device_id:
            raise HustyInvalidResponseError(
                "API Husty zwróciło inne urządzenie niż skonfigurowane"
            )

        return {
            "device": device,
            "sensor_modules": (
                sensor_modules
                if isinstance(sensor_modules, list)
                else []
            ),
        }
