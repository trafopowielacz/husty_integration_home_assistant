import aiohttp
import json

from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator
)

from .const import (
    LOGIN_URL,
    DEVICE_URL,
    SCAN_INTERVAL
)


class HustyCoordinator(
    DataUpdateCoordinator
):

    def __init__(
        self,
        hass,
        email,
        password,
        device_id
    ):

        self.email = email
        self.password = password
        self.device_id = device_id

        self.session = aiohttp.ClientSession()
        self.cookies = None


        super().__init__(
            hass,
            name="Husty API",
            update_interval=timedelta(
                seconds=SCAN_INTERVAL
            ),
        )


    async def login(self):

        response = await self.session.post(
            LOGIN_URL,
            json={
                "email": self.email,
                "password": self.password
            }
        )


        response.raise_for_status()


        self.cookies = (
            response.cookies
        )


    async def _async_update_data(self):

        if not self.cookies:
            await self.login()


        query = {
            "batch": "1",
            "input": json.dumps({

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
                }

            })
        }


        response = await self.session.get(
            DEVICE_URL,
            params=query,
            cookies=self.cookies
        )


        response.raise_for_status()


        return await response.json()