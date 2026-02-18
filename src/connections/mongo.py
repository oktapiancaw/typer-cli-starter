# Copyright (C) 2026 Oktapiancaw
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ExecutionTimeout, NetworkTimeout
from typica import DBConnectionMeta

from src.configs import CustomLogLevel, project_meta

LOGGER = logging.getLogger(project_meta.name)


class MongoConnector:
    _meta: DBConnectionMeta
    _client: MongoClient
    _db: Database

    def __init__(self, meta: DBConnectionMeta) -> None:
        """
        Initialize the Mongo connector with the given connection metadata.

        :param meta: The metadata of the database connection.
        :type meta: DBConnectionMeta
        """
        self._meta = meta
        if not self._meta.uri:
            self._meta.uri = self._meta.uri_string(base="mongodb", with_db=False)

    def __enter__(self):
        """
        Connect to the MongoDB server and return the connection object.

        :return: The connection object.
        :rtype: MongoConnector
        :raises ValueError: If the connection to the MongoDB server fails.
        """
        self.connect()
        if self._client is None:
            raise ValueError("Mongo not connected.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Close the connection to the MongoDB server.

        This method is called when the context manager exits its scope.
        """
        self.close()

    def connect(self, **kwargs) -> None:
        """
        Establish a connection to the MongoDB server.

        :param kwargs: Additional keyword arguments for MongoClient.
        :raises ValueError: If the connection to the MongoDB server fails.
        :raises Exception: If any other error occurs during the connection.
        """

        try:
            self._client = MongoClient(self._meta.uri, **kwargs)
            self._db = self._client[str(self._meta.database)]
            LOGGER.log(CustomLogLevel.CONNECTION, "Mongo connected.")
        except (NetworkTimeout, ExecutionTimeout) as e:
            raise ValueError(f"Mongo connection timed out. cause {e}")
        except Exception as e:
            raise e

    def close(self) -> None:
        """
        Close the connection to the MongoDB server.

        This method is a no-op if the connection is already closed.
        """
        if hasattr(self, "_client") and self._client:
            self._client.close()

        LOGGER.log(CustomLogLevel.CONNECTION, "Mongo disconnected.")
