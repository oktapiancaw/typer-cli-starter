import json
import logging
import ssl
from ssl import SSLContext
from typing import Any

from pika import BasicProperties, BlockingConnection, SSLOptions
from pika.adapters.blocking_connection import BlockingChannel
from pika.connection import ConnectionParameters
from pika.credentials import PlainCredentials
from pika.exceptions import (
    AMQPHeartbeatTimeout,
    ConnectionBlockedTimeout,
    StreamLostError,
)
from typica.connection import RMQConnectionMeta

from src.configs import CustomLogLevel, config, project_meta

LOGGER = logging.getLogger(project_meta.name)


class RMQConnector:
    _meta: RMQConnectionMeta
    _conn: BlockingConnection
    _channel: BlockingChannel

    def __init__(self, meta: RMQConnectionMeta) -> None:
        """
        Initialize the RMQ connector with the given connection metadata.

        :param meta: The metadata of the database connection.
        :type meta: RMQConnectionMeta
        """
        self._meta = meta

    def __enter__(self) -> "RMQConnector":
        """
        Connect to the RabbitMQ server and return the connection object.

        :return: The connection object.
        :rtype: RMQConnector
        :raises ValueError: If the connection to the RabbitMQ server fails.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Close the connection to the RabbitMQ server.

        This method is called when the context manager exits its scope.
        """
        self.close()

    def connect(self, with_ssl: bool = False, use_case: str = "consumer") -> None:
        """
        Establish a connection to the RabbitMQ server.

        :raises ValueError: If the connection to the RabbitMQ server fails.
        :raises Exception: If any other error occurs during the connection.
        """

        # ? Validating use case
        self._meta.validate_use_case(use_case)

        try:
            parameters = ConnectionParameters(
                host=self._meta.host,
                port=self._meta.port,
                virtual_host=self._meta.vhost,
            )

            if self._meta.username and self._meta.password:
                parameters.credentials = PlainCredentials(
                    username=self._meta.username,
                    password=self._meta.password,
                )
            if with_ssl:
                context: SSLContext = ssl._create_unverified_context()  # noqa: S323
                parameters.ssl_options = SSLOptions(context=context)
            self._conn = BlockingConnection(parameters)
            self._channel = self._conn.channel()
            LOGGER.log(CustomLogLevel.CONNECTION, "RMQ connected.")

        except (AMQPHeartbeatTimeout, ConnectionBlockedTimeout):
            raise ValueError("RMQ connection timed out.")
        except Exception as e:
            raise e

    def setup_producer(self):
        if not hasattr(self, "_channel") or self._channel is None:
            raise RuntimeError("No channel: _channel has not been initialized.")

        if not self._meta.routing_key:
            raise ValueError("exchange must be set to setup the producer.")

        self._channel.exchange_declare(
            exchange=self._meta.exchange,
            durable=self._meta.exchange_durable,
            exchange_type=self._meta.exchange_type or "topic",
        )

        self._channel.confirm_delivery()
        LOGGER.log(CustomLogLevel.CONNECTION, "RMQ producer setup is success.")

    def setup_client_logger(self):
        if not hasattr(self, "_channel") or self._channel is None:
            raise RuntimeError("No channel: _channel has not been initialized.")

        if (
            not config.app.client_logger_queue
            or not config.app.client_logger_exchange
            or not config.app.client_logger_exchange
        ):
            raise ValueError(
                "Exchange, Routing, and Queue of client Logger must be defined"
            )

        self._channel.exchange_declare(
            exchange=config.app.client_logger_exchange,
            durable=True,
            exchange_type="topic",
        )
        self._channel.queue_declare(
            queue=config.app.client_logger_queue,
            durable=True,
            auto_delete=True,
            arguments={
                "x-message-ttl": 1000 * 60 * 60 * 2  # 2 Hours
            },
        )
        self._channel.queue_bind(
            queue=config.app.client_logger_queue,
            routing_key=config.app.client_logger_route,
            exchange=config.app.client_logger_exchange,
        )

        self._channel.confirm_delivery()
        LOGGER.log(CustomLogLevel.CONNECTION, "RMQ producer setup is success.")

    def setup_consumer(self) -> None:
        if not hasattr(self, "_channel") or self._channel is None:
            raise RuntimeError("No channel: _channel has not been initialized.")

        if not self._meta.routing_key or not self._meta.queue:
            raise ValueError("Routing key must be set to consume a message.")

        self._channel.queue_declare(
            self._meta.queue,
            durable=self._meta.queue_durable_value,
            auto_delete=self._meta.queue_auto_delete or False,
        )
        self._channel.queue_bind(
            queue=self._meta.queue,
            routing_key=self._meta.routing_key,
            exchange=self._meta.exchange,
        )
        LOGGER.log(CustomLogLevel.CONNECTION, "RMQ consumter setup is success.")

    def produce(
        self,
        message: Any,
        routing_key: str = None,
        exchange: str = None,
        content_encoding: str = None,
    ) -> None:
        if not hasattr(self, "_channel") or self._channel is None:
            raise RuntimeError("No channel: _channel has not been initialized.")

        if not message:
            raise ValueError("Message cannot be empty or None.")

        if not self._meta.routing_key:
            raise ValueError("Routing key must be set to produce a message.")
        if not isinstance(message, str | bytes):
            try:
                message = json.dumps(message)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Failed to serialize message to JSON: {e}")

        properties = BasicProperties(
            content_type="application/json",
            content_encoding=content_encoding,
            delivery_mode=2,
        )
        if isinstance(message, str):
            message = message.encode("utf-8")

        try:
            if not self._channel.is_open:
                LOGGER.warning("Channel is closed. Reconnecting to RMQ...")
                self.connect(use_case="producer", with_ssl=self._meta.with_ssl)
                self.setup_producer()
            self._channel.basic_publish(
                exchange=exchange if exchange else self._meta.exchange,
                routing_key=routing_key if routing_key else self._meta.routing_key,
                body=message,
                mandatory=True,
                properties=properties,
            )
        except (StreamLostError, Exception) as e:
            LOGGER.error(f"Error during publishing: {e}")
            LOGGER.warning("Reconnecting to RMQ...")
            self.connect(use_case="producer", with_ssl=self._meta.with_ssl)
            self.setup_producer()

            # Retry once after reconnecting
            self._channel.basic_publish(
                exchange=exchange if exchange else self._meta.exchange,
                routing_key=routing_key if routing_key else self._meta.routing_key,
                body=message,
                mandatory=True,
                properties=properties,
            )

    def close(self) -> None:
        """
        Close the connection to the RabbitMQ server.

        This method is a no-op if the connection is already closed.
        """
        if self._conn:
            self._conn.close()

        LOGGER.log(CustomLogLevel.CONNECTION, "RMQ disconnected.")
