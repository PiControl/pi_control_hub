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

from peewee import Database, SqliteDatabase

from pi_control_hub.design_patterns import SingletonMeta


class DatabaseManager(metaclass=SingletonMeta):
    """Singleton that holds the database connection."""
    def __init__(self, database_path: str):
        self._database = SqliteDatabase(database_path)
        self._database.connect(True)

    def __del__(self):
        self._database.close()

    @property
    def database(self) -> Database:
        """Return the database connection."""
        return self._database
