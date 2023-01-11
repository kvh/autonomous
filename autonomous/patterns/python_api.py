from __future__ import annotations

import contextlib
import importlib
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Iterator

from commonmodel import Schema
from dcp import Storage
from dcp.utils.common import ensure_datetime, utcnow

Record = dict[str, Any]
Records = list[Record]

memory_db = defaultdict(lambda: defaltdict(list))


@dataclass
class DatabaseApi:
    db: Database
    
    def format_full_name(self, metadata: TableMetadata):
        if metadata.namespace:
            name = metadata.namespace + "." + metadata.name
        else:
            name = metadata.name
        return name

    def bulk_insert(self, metadata: TableMetadata, records: Records):
        memory_db[db.url][self.format_full_name(metadata)].append(records)
        
        
    

def infer_schema_from_records(*args):
    return create_quick_schema("None")

def get_database_api(db: Database):
    return DatabaseApi(db)

@dataclass
class TableVersion:
    metadata: TableMetadata
    database: Database

v = 0
def create_version_name(table_name: str)->str:
    global v
    v += 1
    return table_name + f"_version_{v}"


def create_table_version(table: _Table, records: Records) -> TableVersion:
    schema = table.declared_schema
    if schema is None:
        schema = infer_schema_from_records(records)
    version_name = create_version_name(table.metadata.name)
    return TableVersion(
        metadata=replace(table.metadata, name=version_name)
    )    


def append_to_table(table_version: TableVersion, records: Records):
    api = get_database_api(table_version.database)
    api.bulk_insert(table_version.metadata, records)


@dataclass
class _Table:
    metadata: TableMetadata
    database: Database
    active_version: TableVersion | None
    declared_schema: Schema | None = None
    active_config: TableConfiguration | None = None
    snapshots: dict[str, TableVersion] | None = None


@dataclass
class TableApi:
    table: _Table
    ctx: ExecutionContext

    def append(self, records: Records):
        if self.table.active_version is None:
            tv = create_table_version(self.table, records)
            self.set_active(tv)
        append_to_table(
            self.table.active_version, records
        )
        self.send_version_updated_event()

    def set_active(self, version: TableVersion):
        self.send_version_activated_event()
        self.table.active_version = version

    def send_version_activated_event(self):
        ctx.table_event(
            TableVersionAction.SetActiveVersion, self.table, record_count=len(records)
        )

    def send_version_created_event(self):
        ctx.table_event(
            TableVersionAction.SetActiveVersion, self.table, record_count=len(records)
        )

    def send_version_updated_event(self):
        ctx.table_event(
            TableVersionAction.Update, self.table, record_count=len(records)
        )


Table = TableApi
