import logging
from typing import Any

from pandas import DataFrame
from sqlalchemy import URL, Connection, Engine, create_engine, text
from typica import BaseConnector, DBConnectionMeta

from src.configs import CustomLogLevel, project_meta

LOGGER = logging.getLogger(project_meta.name)


class PostgreAlchemyConnector(BaseConnector):
    _meta: DBConnectionMeta
    _conn: Connection | None = None
    _engine: Engine | None = None

    def __init__(self, meta: DBConnectionMeta) -> None:
        self._meta = meta
        # Build the engine immediately, but don't connect yet
        connection_url = URL.create(
            drivername="postgresql+psycopg",
            username=self._meta.username,
            password=self._meta.password,
            host=self._meta.host,
            port=self._meta.port,
            database=str(self._meta.database),
        )
        # pool_pre_ping is vital for long-running streaming pipelines
        self._engine = create_engine(connection_url, pool_pre_ping=True)

    def __enter__(self):
        """Standard Python Context Manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures the connection is closed even if an error occurs."""
        self.close()

    def refresh_schema(self, base_model: Any, drop_first: bool = False):
        """
        Syncs the ORM models with the database.
        :param base_model: Your SQLAlchemy Base (DeclarativeBase)
        :param drop_first: If True, deletes all tables before recreating (Full Reset)
        """
        if self._is_connected():
            try:
                # We use the engine directly for DDL (Data Definition Language)
                if drop_first:
                    LOGGER.warning("Dropping all tables in database...")
                    base_model.metadata.drop_all(self._engine)

                LOGGER.info("Creating/Updating tables from ORM metadata...")
                base_model.metadata.create_all(self._engine)
                LOGGER.info("Database schema is now up to date.")
            except Exception as e:
                LOGGER.error(f"Failed to refresh schema: {e}")
                raise e
            finally:
                self._conn.commit()
        raise ConnectionError("Database not connected.")

    def connect(self, **kwargs) -> None:
        try:
            if not self._conn or self._conn.closed:
                self._conn = self._engine.connect()
                LOGGER.log(CustomLogLevel.CONNECTION, "Database connection opened.")
        except Exception as e:
            LOGGER.critical(f"Failed to connect: {e}")
            raise

    def _is_connected(self) -> bool:
        return self._conn is not None and not self._conn.closed

    def get(self, query: str, **params):
        if self._is_connected():
            result = self._conn.execute(text(query), params)
            return result.fetchone()
        raise ConnectionError("Database not connected.")

    def get_all(self, query: str, as_dataframe: bool = False, **params):
        if self._is_connected():
            result = self._conn.execute(text(query), params)
            if as_dataframe:
                return DataFrame(result.fetchall(), columns=result.keys())
            return result.fetchall()
        raise ConnectionError("Database not connected.")

    def execute(self, query: str, **params):
        """Executes with automatic commit/rollback."""
        if self._is_connected():
            try:
                self._conn.execute(text(query), params)
                self._conn.commit()
            except Exception as e:
                self._conn.rollback()
                LOGGER.error(f"Transaction failed, rolled back: {e}")
                raise e
        else:
            raise ConnectionError("Database not connected.")

    def close(self):
        if self._is_connected():
            self._conn.close()
            self._conn = None
            LOGGER.log(CustomLogLevel.CONNECTION, "Database connection closed.")
