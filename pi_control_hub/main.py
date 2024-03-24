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
import sys
import uvicorn

from fastapi import FastAPI

from pi_control_hub_api.apis.default_api import router as DefaultApiRouter
from pi_control_hub_driver_api import DeviceDriverDescriptor

from .api_implementation import PiControlHubApi
from . import __version__


def create_argsparser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="pi-control-hub",
        description="The PiControl Hub server",
    )
    parser.add_argument(
        "--ip-address",
        action="store",
        default="0.0.0.0",
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
        default="pi-control-hub.db",
        help="The name of the database file with any path component. The database is created in the configuration directory.",
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

def main():
    """Entry point of the server."""
    args_parser = create_argsparser()
    args, _ = args_parser.parse_known_args(sys.argv)

    DeviceDriverDescriptor.set_config_path(os.path.expanduser(args.config_path))

    app = create_app()
    uvicorn.run(app, host=args.ip_address, port=int(args.port))

if __name__ == "__main__":
    main()
