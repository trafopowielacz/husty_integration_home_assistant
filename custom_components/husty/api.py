"""Client for the official Husty integration API."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp


class HustyApiError(Exception):
    """Base exception for the Husty API."""


class HustyAuthenticationError(HustyApiError):
    """Raised when the API key is invalid or revoked."""


class HustyConnectionError(HustyApiError):
    """Raised when communication with Husty fails."""


class HustyInvalidResponseError(HustyApiError):
    """Raised when Husty returns an invalid response."""


class HustyApiClient:
    """Client for the official Husty Home Assistant endpoint."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_key: str,
        device_url: str,
        request_timeout: int,
    ) -> None:
        """Initialize the client."""

        self._session = session
        self._api_key = api_key.strip()
        self._device_url = device_url
        self._request_timeout = request_timeout

    @property
    def api_key(self) -> str:
        """Return the configured API key."""

        return self._api_key

    async def async_get_device(self) -> dict[str, Any]:
        """Fetch device information from Husty."""

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
            "User-Agent": "HomeAssistant-Husty/0.1.0",
        }

        timeout = aiohttp.ClientTimeout(
            total=self._request_timeout,
        )

        try:
            async with self._session.get(
                self._device_url,
                headers=headers,
                timeout=timeout,
            ) as response:
                if response.status in (401, 403):
                    raise HustyAuthenticationError(
                        "Klucz API Husty jest nieprawidłowy "
                        "lub został unieważniony"
                    )

                if response.status == 429:
                    raise HustyConnectionError(
                        "Przekroczono limit zapytań API Husty"
                    )

                if response.status >= 400:
                    body = await response.text()

                    raise HustyConnectionError(
                        f"API Husty zwróciło HTTP "
                        f"{response.status}: {body[:200]}"
                    )

                try:
                    data = await response.json(
                        content_type=None,
                    )
                except ValueError as err:
                    raise HustyInvalidResponseError(
                        "API Husty nie zwróciło poprawnego JSON"
                    ) from err

        except (
            HustyAuthenticationError,
            HustyConnectionError,
            HustyInvalidResponseError,
        ):
            raise

        except asyncio.TimeoutError as err:
            raise HustyConnectionError(
                "Przekroczono czas oczekiwania na API Husty"
            ) from err

        except aiohttp.ClientError as err:
            raise HustyConnectionError(
                f"Błąd połączenia z API Husty: {err}"
            ) from err

        return self._validate_response(data)

    @staticmethod
    def _validate_response(
        data: Any,
    ) -> dict[str, Any]:
        """Validate the response returned by Husty."""

        if not isinstance(data, dict):
            raise HustyInvalidResponseError(
                "Odpowiedź Husty nie jest obiektem JSON"
            )

        device_id = data.get("deviceId")
        core = data.get("core")
        metadata = data.get("metadata")

        if not isinstance(device_id, str) or not device_id:
            raise HustyInvalidResponseError(
                "Brak identyfikatora urządzenia"
            )

        if not isinstance(core, dict):
            raise HustyInvalidResponseError(
                "Brak sekcji core w odpowiedzi Husty"
            )

        if not isinstance(metadata, dict):
            raise HustyInvalidResponseError(
                "Brak sekcji metadata w odpowiedzi Husty"
            )

        return data
