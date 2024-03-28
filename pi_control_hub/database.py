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

import json
import shelve
from typing import Any, List, TypeVar

from pi_control_hub.design_patterns import SingletonMeta


class InvalidKeyException(Exception):
    """Excpetion that is thrown, if one key component is None."""
    def __str__(self) -> str:
        return "One key component is 'None'."


ENTITY = TypeVar("ENTITY")

class Shelve(metaclass=SingletonMeta):
    """Shelve that stores the persitent data."""
    @staticmethod
    def set_database_path(db_path: str):
        """Sets the database path for the shelve."""
        Shelve.__database_path = db_path

    def __init__(self):
        self._db = shelve.open(Shelve.__database_path)

    def __del__(self):
        self._db.close()

    def open_shelf(self) -> shelve.Shelf[Any]:
        """Open the shelf"""
        return shelve.open(Shelve.__database_path, flag="c")

    def load(self, key: dict) -> ENTITY:
        """Load the object for the given key. Raises a KeyError if there
        is no such key."""
        key_str = json.dumps(key)
        with self.open_shelf() as db:
            return db[key_str]

    def save(self, key: dict, entity: ENTITY):
        """Save the given entity under the key."""
        key_str = json.dumps(key)
        with self.open_shelf() as db:
            db[key_str] = entity
            db.sync()

    def delete(self, key: dict):
        """Delete the entity with the given key. Raises KeyError
        if there is no such key."""
        key_str = json.dumps(key)
        with self.open_shelf() as db:
            del db[key_str]

    def keys(self) -> List[str]:
        """Returns a list with all keys. Might be slow."""
        with self.open_shelf() as db:
            return list(db.keys())


class PairedDevice:
    """This class represents a paired device consisting of teh driver ID,
    device ID and a device name."""
    def __init__(self, driver_id: str, device_id: str, device_name: str = None):
        self._driver_id = driver_id
        self._device_id = device_id
        self._device_name = device_name

    @property
    def pairing_id(self) -> str:
        """Returns the pairing ID for this paired device object.
        Throws an InvalidKeyException, if one key component is None."""
        if self._driver_id is None or self._device_id is None:
            raise InvalidKeyException()
        return f"{self._driver_id}.{self._device_id}"

    @property
    def driver_id(self) -> str:
        """Returns the driver ID."""
        return self._driver_id

    @property
    def device_id(self) -> str:
        """Returns the device ID."""
        return self._device_id

    @property
    def device_name(self) -> str:
        """Returns the device name."""
        return self._device_name

    @property
    def key(self) -> dict:
        """Returns the key for this paired device object.
        Throws an InvalidKeyException, if one key component is None."""
        return PairedDevice.key_from_pairing_id(self.pairing_id)

    @staticmethod
    def key_from_pairing_id(pairing_id: str) -> dict:
        """Returns the key for a pairing ID."""
        return {
            "class": PairedDevice.__name__,
            "pairing_id": pairing_id
        }

    @staticmethod
    def load_all(db: Shelve) -> List:
        """Returns a list with all paired devices."""
        return list(
            map(
                lambda k: db.load(k),
                list(
                    filter(
                        lambda k: k["class"] == PairedDevice.__name__,
                        list(
                            map(
                                lambda k: json.loads(k),
                                db.keys()))))))
