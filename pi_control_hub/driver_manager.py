"""
   Copyright 2024 Thomas Bonk

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from typing import List
from pi_control_hub_driver_api import installed_drivers
from pi_control_hub_driver_api import DeviceDriverDescriptor
from pi_control_hub.design_patterns import SingletonMeta


class DriverNotFoundException(Exception):
    """Exception that is thrown, if a driver is not installed."""
    def __init__(self, driver_id: str):
        self._driver_id = driver_id

    def __str__(self) -> str:
        return f"The driver with the ID '{self._driver_id}' is not installed."


class DriverManager(metaclass=SingletonMeta):
    """PluginManager is a singleton class that provides a cached access to installed
    PiControl Hub drivers.
    """

    def retrieve_drivers(self) -> List[DeviceDriverDescriptor]:
        """This method returns DeviceDriverDescriptor instances of the
        installed drivers."""
        return installed_drivers()

    def retrieve_driver(self, driver_id: str) -> DeviceDriverDescriptor:
        """Return the driver descriptor with the given ID."""
        result = list(
            filter(
                lambda descriptor: str(descriptor.driver_id) == driver_id,
                self.retrieve_drivers(),
            )
        )
        if result.count() > 0:
            return result[0]
        raise DriverNotFoundException(driver_id)
