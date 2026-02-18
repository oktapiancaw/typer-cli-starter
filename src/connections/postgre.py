import logging
import re
from typing import Any

import psycopg
from dateutil import parser
from psycopg import (
    Connection,
    Cursor,
    DatabaseError,
    OperationalError,
)
from typica.connection import DBConnectionMeta

from src.configs import project_meta
from src.connections.utils import pg_queries

LOGGER = logging.getLogger(project_meta.name)


class IngestionError(Exception):
    """Base for domain-level ingestion errors."""


class DateAnomalyError(IngestionError):
    """Raised when a datetime column contains unparseable data."""

    pass


class ValidationError(IngestionError):
    """Raised when there meta didnt match with standard"""

    pass


class PostgreConnector:
    _conn: Connection
    _cur: Cursor

    def __init__(self, meta: DBConnectionMeta) -> None:
        self.meta = meta

        dsn = {
            "dbname": meta.database,
            "host": meta.host,
            "port": meta.port,
        }
        if self.meta.username and self.meta.password:
            dsn.update({"user": self.meta.username, "password": self.meta.password})
        self._dsn = dsn

    def _sanitize_string(self, val: str) -> str:
        val = val.strip()
        val = re.sub(r"([-/\.])\s+(\d)", r"\1\2", val)
        return val

    def _normalize_row_dates(
        self, row: dict[str, Any], date_cols: set[str]
    ) -> dict[str, Any]:
        for col in date_cols:
            value = row.get(col)
            if isinstance(value, str):
                cleaned_value = self._sanitize_string(value)
                try:
                    parsed_date = parser.parse(cleaned_value, dayfirst=True)
                    row[col] = parsed_date.isoformat()
                except (ValueError, TypeError, OverflowError) as e:
                    raise DateAnomalyError(
                        f"Column '{col}' has invalid date: '{value}'"
                    ) from e
        return row

    def connect(self):
        if hasattr(self, "_conn") and self._conn and not self._conn.closed:
            return
        try:
            self._conn = psycopg.connect(**self._dsn)
            self._conn.autocommit = False
            self._cur = self._conn.cursor()
            LOGGER.info("PostgreSQL connection established.")
        except (OperationalError, DatabaseError) as e:
            LOGGER.exception("Failed to connect to PostgreSQL.")
            raise RuntimeError(f"Connection failure: {e}") from e

    def close(self) -> None:
        if hasattr(self, "_cur") and self._cur:
            try:
                self._cur.close()
                LOGGER.debug("Cursor closed.")
            except Exception:
                LOGGER.exception("Error closing cursor.")
        if hasattr(self, "_conn") and self._conn and not self._conn.closed:
            try:
                self._conn.close()
                LOGGER.info("PostgreSQL connection closed.")
            except Exception:
                LOGGER.exception("Error closing connection.")

    def _ensure_connection(self):
        if not hasattr(self, "_conn") or not self._conn or self._conn.closed:
            self.connect()
        if not hasattr(self, "_cur") or not self._cur:
            self._cur = self._conn.cursor()

    def _cached_required_columns(self, schema: str, table: str) -> list[str]:
        self._ensure_connection()
        self._cur.execute(pg_queries.format_query_required(schema=schema, table=table))
        return [r[0] for r in self._cur.fetchall()]

    def _cached_primary_key_columns(self, schema: str, table: str) -> list[str]:
        self._ensure_connection()
        self._cur.execute(pg_queries.format_query_primaries(schema=schema, table=table))
        return [r[0] for r in self._cur.fetchall()]

    def _get_datetime_columns(self, schema: str, table: str) -> set[str]:
        self._ensure_connection()
        self._cur.execute(
            pg_queries.format_query_get_datetime_column(schema=schema, table=table)
        )
        return {r[0] for r in self._cur.fetchall()}
