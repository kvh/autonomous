"""
Notes:
    - build steps:
        1. Static: things known statically (just the app python files) (graph, fn, table defs)
        2. Configured: things known after anton configuration (storage, params, endpoint urls, etc)
        3. Dynamic: things known in an execution context (state of the data, events, active table versions, etc)
    - state:
        - Table and File stores, application data
        - Events - ephemeral messages passed between functions for notification
            - if graph changes in middle of message, will just be dropped on floor or whatevs
        - how to handle stream
            - event message can contain full info (start/end id), and fn is responsible for safe handling
            - can store consumer state like we do now (not great, hidden)
            - what if an error?
    - changing a fn name (any graph edge change) requires no re-mapping
    - how to handle parallel execution? (these are solved problems...)
        - can add execution id to record_id or sep col
        - if we are processing based on event messages, thaz fine
        - but if we want to allow incremental processing by downstream
        - downstream responsible for each batch? can always try/catch its own stuff and send new event?
"""

from commonmodel.utils import PydanticBase


class Graph(PydanticBase):
    functions: dict[str, FunctionConfig]
    tables: dict[str, TableConfig]
    files: dict[str, FileConfig]
    edges: list[EdgeConfig]


class EdgeConfig(PydanticBase):
    pass


class TableRegistry:
    def __init__(self):
        self.table_config = table_config

    def _register_edge(fn: Callable, trigger_type):
        fn_config = process_function(fn)
        register_edge(self.table_config, fn_config, trigger_type)

    def on_update(self, fn: Callable):
        self._register_edge(fn, TriggerType.Update)


def on_update(table_config: TableConfig):
    def _on_update(fn: Callable):
        fn_config = process_function(fn)
        register_edge(table_config, fn_config, trigger_type)

    return _on_update


def execute_function(graph, fn, event):
    with patch_objects() as event_collector:
        call_function(event, fn)

    for event in event_collector:
        downstream = graph.get_out_edges(event.table)
        execute_function(downstream, event)
