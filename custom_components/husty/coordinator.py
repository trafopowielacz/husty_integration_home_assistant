import aiohttp
import json
import logging

from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .const import (
    LOGIN_URL,
    DEVICE_URL,
    SCAN_INTERVAL,
)


_LOGGER = logging.getLogger(__name__)


class HustyCoordinator(DataUpdateCoordinator):
    """Husty API coordinator."""

    def __init__(
        self,
        hass,
        email,
        password,
        device_id,
    ):

        self.email = email
        self.password = password
        self.device_id = device_id

        self.session = aiohttp.ClientSession()
        self.cookies = None

        super().__init__(
            hass,
            _LOGGER,
            name="Husty API",
            update_interval=timedelta(
                seconds=SCAN_INTERVAL
            ),
        )


    async def login(self):
        """Login to Husty."""

        _LOGGER.debug(
            "Logging into Husty API"
        )

        response = await self.session.post(
            LOGIN_URL,
            json={
                "email": self.email,
                "password": self.password,
            },
        )

        response.raise_for_status()


        self.cookies = {
            key: morsel.value
            for key, morsel in response.cookies.items()
        }


        _LOGGER.info(
            "Husty login successful"
        )



    async def _async_update_data(self):
        """Fetch data from Husty API."""

        if not self.cookies:
            await self.login()


        query = {
            "batch": "1",
            "input": json.dumps(
                {
                    "0": {
                        "json": {
                            "softenerDeviceId":
                                self.device_id
                        }
                    },

                    "1": {
                        "json": {
                            "deviceId":
                                self.device_id
                        }
                    },
                }
            ),
        }


        try:

            response = await self.session.get(
                DEVICE_URL,
                params=query,
                cookies=self.cookies,
            )


            # sesja wygasła
            if response.status in (401, 403):

                _LOGGER.warning(
                    "Husty session expired, relogin"
                )


                await self.login()


                response = await self.session.get(
                    DEVICE_URL,
                    params=query,
                    cookies=self.cookies,
                )


            response.raise_for_status()


            return await response.json()



        except aiohttp.ClientError as err:

            _LOGGER.error(
                "Husty API error: %s",
                err
            )

            raise



    async def async_shutdown(self):

        """Close HTTP session."""

        if self.session:

            await self.session.close()
