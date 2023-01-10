from pprint import pprint

from base import get_current_graph, get_current_context, Event, execute_function
from table_api import memory_db


def run():
    from simple import trigger

    graph = get_current_graph()
    print(graph)
    execute_function(graph, trigger, Event(payload={"a": 1}))
    pprint(memory_db)


run()
