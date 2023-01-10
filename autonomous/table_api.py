from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any

from commonmodel import Schema
from commonmodel.base import create_quick_schema

Record = dict[str, Any]
Records = list[Record]

memory_db = defaultdict(dict)


@dataclass(frozen=True)
class Database:
    url: str


@dataclass(frozen=True)
class TableMetadata:
    name: str
    namespace: str | None = None
    data_schema: Schema | None = None

    def get_key(self):
        return self.namespace + "." + self.name if self.namespace else self.name


@dataclass
class DatabaseApi:
    db: Database

    def format_full_name(self, metadata: TableMetadata):
        if metadata.namespace:
            name = metadata.namespace + "." + metadata.name
        else:
            name = metadata.name
        return name

    def create_table(self, metadata: TableMetadata, schema: Schema):
        memory_db[self.db.url][self.format_full_name(metadata)] = []

    def bulk_insert(self, metadata: TableMetadata, records: Records):
        memory_db[self.db.url][self.format_full_name(metadata)].extend(records)

    def read(self, metadata: TableMetadata) -> Records:
        return memory_db[self.db.url][self.format_full_name(metadata)]


def infer_schema_from_records(*args):
    return create_quick_schema("None", [])


def get_database_api(db: Database):
    return DatabaseApi(db)


class TableAction(str, Enum):
    Update = "update"


def create_table(table: DatabaseTable, records: Records):
    schema = table.declared_schema
    if schema is None:
        schema = infer_schema_from_records(records)
    get_database_api(table.database).create_table(table.metadata, schema)
    table.exists = True


def append_to_table(table: DatabaseTable, records: Records):
    assert table.exists
    api = get_database_api(table.database)
    api.bulk_insert(table.metadata, records)


def read_from_table(table: DatabaseTable) -> Records:
    if not table.exists:
        return []
    api = get_database_api(table.database)
    return api.read(table.metadata)


@dataclass
class DatabaseTable:
    metadata: TableMetadata
    database: Database = Database("local")
    exists: bool = False
    declared_schema: Schema | None = None
    # active_config: TableConfiguration | None = None
    # snapshots: dict[str, TableVersion] | None = None

    def get_key(self):
        return self.metadata.get_key()
