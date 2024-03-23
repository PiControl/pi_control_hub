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

from pi_control_hub.plugin_manager import PluginManager

class PiControlHubApi(BaseDefaultApi):
    """Implementation of the PiControl Hub REST API."""

    def read_device_drivers(self) -> List[DeviceDriver]:
        """Read all installed device drivers"""
        # TODO
        plugins = PluginManager().retrieve_plugins()
        return [DeviceDriver(driverId="ABCD", displayName="NAME", description="TEST", authenticationMethod="NONE")]

    def read_devices(self, driverId: str) -> List[DeviceInfo]:
        """Read all devices that are supported by the driver with the given driver ID"""
        # TODO
        return []

    def start_pairing(
        self,
        driverId: str,
        deviceId: str,
        start_pairing_request: StartPairingRequest,
    ) -> StartPairingResponse:
        """Start the pairing process for the device with the given device ID."""
        # TODO
        return None

    def finalize_pairing(
        self,
        driverId: str,
        deviceId: str,
        pairingRequestId: str,
        finalize_pairing_request: FinalizePairingRequest,
    ) -> FinalizePairingResponse:
        """Finalize the pairing process for the device with the given device ID."""
        # TODO
        return None

    def read_paired_devices(self) -> List[PairedDevice]:
        """Read the list of paired devices."""
        # TODO
        return []

    def unpair_device(self,pairingId: str) -> None:
        """Unpair the device."""
        # TODO
        return None

    def read_device_commands(self, pairingId: str) -> List[DeviceCommand]:
        """Get the commands supported by the device."""
        # TODO
        return []

    def read_device_remote_layout(self,pairingId: str) -> RemoteLayout:
        """Get the layout of the remote control for the device."""
        # TODO
        return None

    def execute_device_command(self, pairingId: str, commandId: int) -> None:
        """Execute the command on the paired device."""
        # TODO
        return None

    def is_device_ready(self, pairingId: str) -> bool:
        """Check whether the device is ready for executing commands."""
        # TODO
        return False