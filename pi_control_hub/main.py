#!/usr/bin/env python3

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

import os
import argparse
import socket
import sys
import uvicorn
import zeroconf

from fastapi import FastAPI

from pi_control_hub_api.apis.default_api import router as DefaultApiRouter
from pi_control_hub_driver_api import DeviceDriverDescriptor

from pi_control_hub.database import Shelve

from .api_implementation import PiControlHubApi
from . import __version__


def get_ip_address() -> str:
    """Returns the IP address of this machine."""
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)



def create_argsparser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="pi-control-hub",
        description="The PiControl Hub server",
    )
    parser.add_argument(
        "--ip-address",
        action="store",
        default=get_ip_address(),
        help="The IP address from which the server is listining.",
    )
    parser.add_argument(
        "--port",
        action="store",
        default="8000",
        help="The port on wihich the server listens.",
    )
    parser.add_argument(
        "--config-path",
        action="store",
        default="/etc/pi-control-hub",
        help="Directory path where the configuration is stored. The directory must be writable by the server.",
    )
    parser.add_argument(
        "--db-filename",
        action="store",
        default="pi-control-hub.store",
        help="The name of the database file with any path component. The database is created in the configuration directory.",
    )
    parser.add_argument(
        "--instance-name",
        action="store",
        default="Pi Control Hub",
        help="The name of this instance.",
    )
    return parser


def create_app() -> FastAPI:
    """Create the FastAPI app."""
    app = FastAPI(
        title="PiControl Hub",
        description="The PiControl Hub server",
        version=__version__,
    )
    app.include_router(DefaultApiRouter)
    return app


def advertise_service(instance_name: str, ip_address: str, port: int):
    """Advertises this service via Zeroconf."""
    if ip_address == "127.0.0.1" or ip_address == "0.0.0.0":
        return None
    zc_type = "_pi-ctrl-hub._tcp.local."
    fq_hostname = socket.getfqdn()
    service_name = f"{instance_name}.{zc_type}"
    zc_info = zeroconf.ServiceInfo(
        zc_type,
        service_name,
        addresses=[socket.inet_aton(ip_address)],
        port=port,
        properties={"url": f"http://{fq_hostname}:{port}"},
        server=fq_hostname,
    )
    zconf = zeroconf.Zeroconf()
    zconf.register_service(zc_info)
    return zconf


def validate_args(args: argparse.ArgumentParser):
    """Validates the arguments."""
    cfg_path = os.path.expanduser(args.config_path)
    if cfg_path != os.path.abspath(cfg_path):
        raise ValueError("The value of the argument --config-path is not an absolute path.")

    db_path = os.path.join(cfg_path, args.db_filename)
    if db_path != os.path.abspath(db_path):
        raise ValueError("The value of the argument --db-filename contains relative path spcifiers.")


def main():
    """Entry point of the server."""
    args_parser = create_argsparser()
    args, _ = args_parser.parse_known_args(sys.argv)

    validate_args(args)

    DeviceDriverDescriptor.set_config_path(os.path.expanduser(args.config_path))
    Shelve.set_database_path(os.path.join(os.path.expanduser(args.config_path), args.db_filename))

    zconf = advertise_service(args.instance_name, args.ip_address, int(args.port))

    app = create_app()
    uvicorn.run(app, host=args.ip_address, port=int(args.port), loop="asyncio")

if __name__ == "__main__":
    main()
