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

from confluent_kafka import Consumer, Producer
from typica.connection import KafkaMeta

from src.configs import CustomLogLevel, project_meta

LOGGER = logging.getLogger(project_meta.name)


class KafkaConnector:
    consumer: Consumer
    producer: Producer

    def __init__(self, meta: KafkaMeta) -> None:
        self._meta: KafkaMeta = meta

    def initialize_producer(self) -> None:
        try:
            self.producer = Producer(self._meta.basic_confluent_config_json)
            LOGGER.log(CustomLogLevel.CONNECTION, "Kafka connected.")
        except Exception as e:
            raise e

    def initialize_consumer(self) -> None:
        try:
            self.consumer = Consumer(self._meta.consumer_confluent_config_json)
            LOGGER.log(CustomLogLevel.CONNECTION, "Kafka connected.")
        except Exception as e:
            raise e

    def close(self) -> None:
        if hasattr(self, "consumer") and self.consumer:
            self.consumer.close()
        LOGGER.log(CustomLogLevel.CONNECTION, "Kafka disconnected.")
