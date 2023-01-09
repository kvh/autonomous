from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union, cast
from urllib.parse import urlparse

from commonmodel import Schema


@dataclass(frozen=True)
class TableMetadata:
    name: str
    namespace: str | None = None
    data_schema: Schema | None = None


@dataclass(frozen=True)
class FileMetadata:
    name: str
    path: list[str] | None = None
    file_type: str | None = None
    data_schema: Schema | None = None


@dataclass(frozen=True)
class PythonObject:
    name: str
    obj: Any
    obj_type: str | None = None
    data_schema: Schema | None = None


@dataclass(frozen=True)
class Database:
    url: str
    
    
@dataclass(frozen=True)
class FileSystem:
    url: str


@dataclass(frozen=True)
class MemoryStore:
    store: dict | None = None

