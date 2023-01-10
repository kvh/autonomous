from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from pydantic import BaseModel

from table_api import (
    TableMetadata,
    create_table,
    append_to_table,
    DatabaseTable,
    Records,
    TableAction,
    Record,
    read_from_table,
)


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

    def get_out_edges(self, table_name: str) -> list[EdgeConfig]:
        return [e for e in self.edges if e.table_name == table_name]


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
        return fn

    # I/O
    def append(self, records: Record | Records):
        if isinstance(records, dict):
            records = [records]
        if not self.table.exists:
            create_table(self.table, records)
        append_to_table(self.table, records)
        self.send_updated_event()

    def read(self):
        return read_from_table(self.table)

    # def send_created_event(self):
    #     self.ctx.table_event(
    #         TableVersionAction.SetActiveVersion,
    #         self.table,  # record_count=len(records)
    #     )

    def send_updated_event(self):
        self.ctx.table_event(
            TableAction.Update,
            self,  # record_count=len(records)
        )


@dataclass
class Event:
    table: Table | None = None
    action: TableAction | None = None
    payload: dict | None = None


@dataclass
class ExecutionContext:
    events: list[Event] = field(default_factory=list)

    def table_event(self, action: TableAction, table: Table):
        self.events.append(Event(table=table, action=action))


CURRENT_CONTEXT = ExecutionContext()


def get_current_context():
    return CURRENT_CONTEXT


def manual(fn: Callable):
    get_current_graph()
    return fn


def execute_function(graph: Graph, fn: Callable, event):
    print("Executing", fn)
    ctx = get_current_context()
    fn(event)
    events = ctx.events
    ctx.events = []
    for event in events:
        downstreams = graph.get_out_edges(event.table.table_md.name)
        for d in downstreams:
            execute_function(graph, graph.functions[d.fn_name], event)
