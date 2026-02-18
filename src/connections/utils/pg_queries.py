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

from psycopg import (
    sql,
)


def format_query_primaries(schema: str, table: str) -> sql.SQL:
    """
    Query for get primary key columns
    """
    return sql.SQL("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.constraint_schema = kcu.constraint_schema
            AND tc.table_name = kcu.table_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = {schema}
            AND tc.table_name = {table}
        ORDER BY kcu.ordinal_position;
        """).format(schema=schema, table=table)


def format_query_required(schema: str, table: str) -> sql.SQL:
    """
    Query for get required columns
    """
    return sql.SQL("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = {schema}
            AND table_name = {table}
            AND is_nullable = 'NO'
            AND column_default IS NULL
    """).format(schema=schema, table=table)


def format_query_table_schema(schema: str, table: str) -> sql.SQL:
    """
    Query for get schema of table
    """
    return sql.SQL("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = {schema} AND table_name = {table}
    """).format(schema=schema, table=table)


def format_query_get_datetime_column(schema: str, table: str) -> sql.SQL:
    """
    Query for get datetime columns
    """
    datetime_types = [
        "timestamp without time zone",
        "timestamp with time zone",
        "date",
        "timestamp",
    ]

    return sql.SQL("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = {schema}
            AND table_name = {table}
            AND data_type IN ({datetime_types})
    """).format(schema=schema, table=table, datetime_types=datetime_types)


def format_query_insert(
    schema: str, table: str, column_idents: list[str], all_columns: list[dict]
) -> sql.SQL:
    return sql.SQL(
        "INSERT INTO {schema}.{table} ({fields}) VALUES ({placeholders})"
    ).format(
        schema=sql.Identifier(schema),
        table=sql.Identifier(table),
        fields=sql.SQL(", ").join(column_idents),
        placeholders=sql.SQL(", ").join(sql.Placeholder() for _ in all_columns),
    )


def format_query_insert_conflict_nothing(
    schema: str,
    table: str,
    column_idents: list[str],
    all_columns: list[dict],
    constraint_fields: list[str] | None = None,
) -> sql.SQL:
    conflict_target = [sql.Identifier(f) for f in constraint_fields]
    return sql.SQL("""
                    INSERT INTO {schema}.{table} ({fields})
                    VALUES ({placeholders})
                    ON CONFLICT ({constraint})
                    DO NOTHING
                """).format(
        schema=sql.Identifier(schema),
        table=sql.Identifier(table),
        fields=sql.SQL(", ").join(column_idents),
        placeholders=sql.SQL(", ").join(sql.Placeholder() for _ in all_columns),
        constraint=sql.SQL(", ").join(conflict_target),
    )


def format_query_insert_conflict_update(
    schema: str,
    table: str,
    all_columns: list[dict],
    constraint_fields: list[str] | None = None,
) -> sql.SQL:
    col_idents = [sql.Identifier(c) for c in all_columns]
    conflict_target = [sql.Identifier(f) for f in constraint_fields]
    update_cols = [c for c in all_columns if c not in constraint_fields]
    if update_cols:
        assignment = sql.SQL(", ").join(
            sql.Composed(
                [
                    sql.Identifier(c),
                    sql.SQL(" = "),
                    sql.SQL("EXCLUDED.") + sql.Identifier(c),
                ]
            )
            for c in update_cols
        )
        update_clause = sql.SQL("DO UPDATE SET ") + assignment
    else:
        update_clause = sql.SQL("DO NOTHING")
    return sql.SQL(
        "INSERT INTO {schema}.{table} ({fields}) VALUES ({values}) "
        "ON CONFLICT ({conflict}) {update}"
    ).format(
        schema=sql.Identifier(schema),
        table=sql.Identifier(table),
        fields=sql.SQL(", ").join(col_idents),
        values=sql.SQL(", ").join(sql.Placeholder() for _ in all_columns),
        conflict=sql.SQL(", ").join(conflict_target),
        update=update_clause,
    )


def format_query_update(
    schema: str,
    table: str,
    set_fields: list[dict],
    constraint_present: list[str] | None = None,
) -> sql.SQL:
    set_clause = sql.SQL(", ").join(
        sql.Composed(
            [
                sql.Identifier(f),
                sql.SQL(" = "),
                sql.Placeholder(f),
            ]
        )
        for f in set_fields
    )

    where_clause = sql.SQL(" AND ").join(
        sql.Composed(
            [
                sql.Identifier(f),
                sql.SQL(" = "),
                sql.Placeholder(f),
            ]
        )
        for f in constraint_present
    )

    return sql.SQL(
        "UPDATE {schema}.{table} SET {set_clause} WHERE {where_clause}"
    ).format(
        schema=sql.Identifier(schema),
        table=sql.Identifier(table),
        set_clause=set_clause,
        where_clause=where_clause,
    )
