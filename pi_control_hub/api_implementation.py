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

import base64
from typing import List

from fastapi import HTTPException
from pi_control_hub_api.apis.default_api_base import BaseDefaultApi
from pi_control_hub_api.models.device_command import DeviceCommand
from pi_control_hub_api.models.device_driver import DeviceDriver
from pi_control_hub_api.models.device_info import DeviceInfo
from pi_control_hub_api.models.finalize_pairing_request import FinalizePairingRequest
from pi_control_hub_api.models.finalize_pairing_response import FinalizePairingResponse
from pi_control_hub_api.models.paired_device import PairedDevice
from pi_control_hub_api.models.remote_layout import RemoteLayout
from pi_control_hub_api.models.start_pairing_request import StartPairingRequest
from pi_control_hub_api.models.start_pairing_response import StartPairingResponse
from pydantic import StrictBytes

from pi_control_hub.design_patterns import SingletonMeta
from pi_control_hub.driver_manager import DeviceNotFoundException, DriverManager, DriverNotFoundException, PairingException

class PiControlHubApi(BaseDefaultApi, metaclass=SingletonMeta):
    """Implementation of the PiControl Hub REST API."""

    def read_device_drivers(self) -> List[DeviceDriver]:
        """Read all installed device drivers"""
        driver_descriptors = DriverManager().read_drivers()
        drivers = map(
            lambda descriptor: DeviceDriver(
                driverId=str(descriptor.driver_id),
                displayName=descriptor.display_name,
                description=descriptor.description,
                authenticationMethod=descriptor.authentication_method.name,
            ),
            driver_descriptors,
        )
        return list(drivers)

    def read_devices(self, driverId: str) -> List[DeviceInfo]:
        """Read all devices that are supported by the driver with the given driver ID"""
        try:
            result = list(
                    map(
                    lambda dinfo: DeviceInfo(
                        deviceId=dinfo.device_id,
                        name=dinfo.name,
                    ),
                    DriverManager().read_devices(driverId),
                )
            )
            return result
        except DriverNotFoundException as ex:
            raise HTTPException(status_code=404, detail=str(ex)) from ex

    def start_pairing(
        self,
        driverId: str,
        deviceId: str,
        start_pairing_request: StartPairingRequest,
    ) -> StartPairingResponse:
        """Start the pairing process for the device with the given device ID."""
        try:
            pairing_request, device_provides_pin = DriverManager().start_pairing(
                driver_id=driverId,
                device_id=deviceId,
                remote_name=start_pairing_request.remote_name)
            return StartPairingResponse(
                pairingRequest=pairing_request,
                deviceProvidesPin=device_provides_pin)
        except DriverNotFoundException as ex:
            raise HTTPException(status_code=404, detail=str(ex)) from ex
        except DeviceNotFoundException as ex:
            raise HTTPException(status_code=404, detail=str(ex)) from ex

    def finalize_pairing(
        self,
        driverId: str,
        deviceId: str,
        pairingRequestId: str,
        finalize_pairing_request: FinalizePairingRequest,
    ) -> FinalizePairingResponse:
        """Finalize the pairing process for the device with the given device ID."""
        try:
            paired = DriverManager().finalize_pairing(
                driver_id=driverId,
                device_id=deviceId,
                pairing_request_id=pairingRequestId,
                credentials=finalize_pairing_request.pin,
                device_provides_pin=finalize_pairing_request.device_provides_pin)
            return FinalizePairingResponse(deviceHasPaired=paired)
        except DriverNotFoundException as ex:
            raise HTTPException(status_code=404, detail=str(ex)) from ex
        except DeviceNotFoundException as ex:
            raise HTTPException(status_code=404, detail=str(ex)) from ex
        except PairingException as ex:
            raise HTTPException(status_code=400, detail=str(ex)) from ex

    def read_paired_devices(self) -> List[PairedDevice]:
        """Read the list of paired devices."""
        return list(
            map(
                lambda d: PairedDevice(
                    pairingId=d.pairing_id,
                    driverId=d.driver_id,
                    deviceId=d.device_id,
                    deviceName=d.device_name
                ),
                DriverManager().paired_devices))

    def unpair_device(self,pairingId: str) -> None:
        """Unpair the device."""
        try:
            DriverManager().unpair_device(pairingId)
        except DeviceNotFoundException as ex:
            raise HTTPException(status_code=404, detail=str(ex)) from ex

    def read_device_commands(self, pairingId: str) -> List[DeviceCommand]:
        """Get the commands supported by the device."""
        try:
            driver_manager = DriverManager()
            paired_device = driver_manager.get_paired_device(pairingId)
            commands = list(
                map(
                    lambda c: DeviceCommand(
                        pairing_id=pairingId,
                        driver_id=paired_device.driver_id,
                        device_id=paired_device.device_id,
                        command_id=c.id,
                        name=c.title,
                        icon=base64.b64encode(c.icon).decode('ascii'),
                    ),
                    driver_manager.read_device_commands(pairingId)))
            return commands
        except DeviceNotFoundException as ex:
            raise HTTPException(status_code=404, detail=str(ex)) from ex

    def read_device_remote_layout(self,pairingId: str) -> RemoteLayout:
        """Get the layout of the remote control for the device."""
        try:
            driver_manager = DriverManager()
            width, height, buttons = driver_manager.get_remote_layout(pairingId)
            return RemoteLayout(width=width, height=height, buttons=buttons)
        except DeviceNotFoundException as ex:
            raise HTTPException(status_code=404, detail=str(ex)) from ex

    def execute_device_command(self, pairingId: str, commandId: int) -> int:
        """Execute the command on the paired device."""
        try:
            DriverManager().execute_device_command(pairingId, commandId)
            raise HTTPException(status_code=204, detail="All is good")
        except DeviceNotFoundException as ex:
            raise HTTPException(status_code=404, detail=str(ex)) from ex


    def is_device_ready(self, pairingId: str) -> bool:
        """Check whether the device is ready for executing commands."""
        # TODO
        return None
