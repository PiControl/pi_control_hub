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

from threading import Thread
from typing import List, Tuple

import pi_control_hub_driver_api
from cachetools import TTLCache
from pi_control_hub_driver_api import (DeviceCommand, DeviceDriver,
                                       DeviceDriverDescriptor,
                                       DeviceDriverException, DeviceInfo,
                                       installed_drivers)

from pi_control_hub.database import InvalidKeyException, PairedDevice, Shelve
from pi_control_hub.design_patterns import SingletonMeta


class DriverNotFoundException(Exception):
    """Exception that is thrown, if a driver is not installed."""
    def __init__(self, driver_id: str):
        self._driver_id = driver_id

    def __str__(self) -> str:
        return f"The driver with the ID '{self._driver_id}' is not installed."

class DeviceNotFoundException(Exception):
    """Exception that is thrown, if a device is not available."""
    def __init__(self, driver_id: str = None, device_id: str = None, message: str = None):
        self._driver_id = driver_id
        self._device_id = device_id
        self._message = message

    def __str__(self) -> str:
        if self._message is not None:
            return self._message
        return f"The driver with the ID '{self._driver_id}' doesn't find a device with ID '{self._device_id}'."

class PairingException(Exception):
    """Exception that is thrown in case of an error during pairing."""
    def __init__(self, driver_id: str, device_id: str, pairing_id: str):
        self._driver_id = driver_id
        self._device_id = device_id
        self._pairing_id = pairing_id

    def __str__(self) -> str:
        return f"Error while finalizing pairing for pairing ID '{self._pairing_id}' and driver ID '{self._driver_id}', device ID '{self._device_id}'"


class DriverManager(metaclass=SingletonMeta):
    """PluginManager is a singleton class that provides a cached access to installed
    PiControl Hub drivers.
    """

    def __init__(self):
        self._cache = TTLCache(maxsize=10, ttl=300)

    async def read_drivers(self) -> List[DeviceDriverDescriptor]:
        """This method returns DeviceDriverDescriptor instances of the
        installed drivers."""
        return installed_drivers()

    async def retrieve_driver(self, driver_id: str) -> DeviceDriverDescriptor:
        """Return the driver descriptor with the given ID."""
        result = list(
            filter(
                lambda descriptor: str(descriptor.driver_id) == driver_id,
                await self.read_drivers(),
            )
        )
        if len(result) > 0:
            return result[0]
        raise DriverNotFoundException(driver_id)

    async def read_devices(self, driver_id: str) -> List[DeviceInfo]:
        """Read the devices from a driver."""
        cache_key = f"devices({driver_id})"

        if cache_key in self._cache:
            return self._cache[cache_key]

        driver_descriptor = await self.retrieve_driver(driver_id)
        devices = await driver_descriptor.get_devices()
        self._cache[cache_key] = devices
        return devices

    async def retrieve_driver_and_device(self, driver_id: str, device_id: str) -> Tuple[DeviceDriverDescriptor, DeviceInfo]:
        """Retrieve the device info for the device identified by a driver ID and device ID."""
        driver = await self.retrieve_driver(driver_id)
        devices = list(filter(lambda d: d.device_id == device_id, await self.read_devices(driver_id)))
        if not devices or len(devices) == 0:
            raise DeviceNotFoundException(driver_id=driver_id, device_id=device_id)
        return driver, devices[0]

    async def start_pairing(self, driver_id: str, device_id: str, remote_name: str) -> Tuple[str, bool]:
        """Start the pairing process of the given device with the device driver descriptor."""
        driver, device = await self.retrieve_driver_and_device(driver_id, device_id)
        return await driver.start_pairing(
            device_info=device,
            remote_name=remote_name)

    async def finalize_pairing(
            self,
            driver_id: str,
            device_id: str,
            pairing_request_id: str,
            credentials: str,
            device_provides_pin: bool) -> bool:
        """Finalize the pairing process."""
        try:
            driver, device = await self.retrieve_driver_and_device(driver_id, device_id)
            paired =  await driver.finalize_pairing(
                pairing_request=pairing_request_id,
                credentials=credentials,
                device_provides_pin=device_provides_pin)
            if paired:
                paired_device = PairedDevice(
                    driver_id=driver_id,
                    device_id=device_id,
                    device_name=device.name)
                Shelve().save(paired_device.key, paired_device)
            return paired
        except (DeviceDriverException, InvalidKeyException) as ex:
            raise PairingException(driver_id, device_id, pairing_request_id) from ex

    @property
    def paired_devices(self) -> List[PairedDevice]:
        """All paired devices"""
        return PairedDevice.load_all(Shelve())

    def get_paired_device(self, pairing_id: str) -> PairedDevice:
        """Load the paired device with the given pairing ID."""
        try:
            return Shelve().load(PairedDevice.key_from_pairing_id(pairing_id))
        except KeyError as ex:
            raise DeviceNotFoundException(f"The device with the pairing ID '{pairing_id}' wasn't found.") from ex

    def unpair_device(self, pairing_id: str):
        """Deletes a device pairing"""
        try:
            Shelve().delete(PairedDevice.key_from_pairing_id(pairing_id))
        except (KeyError, pi_control_hub_driver_api.DeviceNotFoundException) as ex:
            raise DeviceNotFoundException(f"The device with the pairing ID '{pairing_id}' wasn't found.") from ex

    async def device_instance_for_pairing_id(self, pairing_id: str) -> DeviceDriver:
        if pairing_id in self._cache:
            return self._cache[pairing_id]
        paired_device = self.get_paired_device(pairing_id)
        driver, device = await self.retrieve_driver_and_device(
            paired_device.driver_id,
            paired_device.device_id)
        device_instance = await driver.create_device_instance(device.device_id)
        self._cache[pairing_id] = device_instance
        return device_instance

    async def read_device_commands(self, pairing_id: str) -> List[DeviceCommand]:
        """Reads the commands provided by the given paired device"""
        try:
            device_instance = await self.device_instance_for_pairing_id(pairing_id)
            commands = await device_instance.get_commands()
            return commands
        except KeyError as ex:
            raise DeviceNotFoundException(f"The device with the pairing ID '{pairing_id}' wasn't found.") from ex

    async def get_remote_layout(self, pairing_id: str) -> Tuple[int, int, List[List[int]]]:
        """"Reads the remote layout"""
        try:
            device_instance = await self.device_instance_for_pairing_id(pairing_id)
            width, height = device_instance.remote_layout_size
            buttons = device_instance.remote_layout
            return width, height, buttons
        except KeyError as ex:
            raise DeviceNotFoundException(f"The device with the pairing ID '{pairing_id}' wasn't found.") from ex

    async def execute_device_command(self, pairing_id: str, command_id: int):
        """Execute the command with the given ID."""
        try:
            device_instance = await self.device_instance_for_pairing_id(pairing_id)
            device_command = await device_instance.get_command(command_id)
            await device_instance.execute(device_command)
        except KeyError as ex:
            raise DeviceNotFoundException(f"The device with the pairing ID '{pairing_id}' wasn't found.") from ex

    async def is_device_ready(self, pairing_id: str) -> bool:
        try:
            device_instance = await self.device_instance_for_pairing_id(pairing_id)
            return await device_instance.is_device_ready
        except KeyError as ex:
            raise DeviceNotFoundException(f"The device with the pairing ID '{pairing_id}' wasn't found.") from ex
