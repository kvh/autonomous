from enum import Enum
from typing import Callable

from pydantic import BaseModel

from .table_api import TableApi, TableMetadata, create_table, append_to_table, DatabaseTable, Records, TableAction


class TriggerType(str, Enum):
    Update = "update"
    NewRecords = "new_records"


class EdgeConfig(BaseModel):
    table_name: str
    fn_name: str
    trigger_type: TriggerType


class Graph(BaseModel):
    functions: dict[str, Callable] = {}
    tables: dict[str, TableMetadata] = {}
    edges: list[EdgeConfig] = []


GRAPH = Graph()


def get_current_graph():
    return GRAPH


class Table:
    def __init__(self, name: str):
        self.table_md = TableMetadata(name=name)
        self.graph = get_current_graph()
        self.ctx = get_current_context()
        self.graph.tables[self.table_md.name] = self.table_md
        self.table = DatabaseTable(metadata=self.table_md)

    # Registration
    def _register_edge(self, fn: Callable, trigger_type: TriggerType):
        self.graph.functions[fn.__name__] = fn
        self.graph.edges.append(
            EdgeConfig(
                fn_name=fn.__name__,
                table_name=self.table_md.name,
                trigger_type=trigger_type,
            )
        )

    def on_update(self, fn: Callable):
        self._register_edge(fn, TriggerType.Update)

    # I/O
    def append(self, records: Records):
        if not self.table.exists:
            create_table(self.table, records)
        append_to_table(self.table, records)
        self.send_updated_event()

    # def send_created_event(self):
    #     self.ctx.table_event(
    #         TableVersionAction.SetActiveVersion,
    #         self.table,  # record_count=len(records)
    #     )

    def send_updated_event(self):
        self.ctx.table_event(
            TableAction.Update,
            self.table,  # record_count=len(records)
        )


class Event(BaseModel):
    table: Table
    action: TableAction


class ExecutionContext(BaseModel):
    events: list[Event] = []

    def table_event(self, action: TableAction, table: Table):
        self.events.append(Event(table=table, action=action))


CURRENT_CONTEXT = ExecutionContext()


def get_current_context():
    return CURRENT_CONTEXT
