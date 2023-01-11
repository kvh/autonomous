from pprint import pprint

from fastapi import Request, FastAPI, APIRouter
import uvicorn

from base import get_current_graph, get_current_context, Event, execute_function
from table_api import memory_db

app = FastAPI()


def init(graph):
    graph = get_current_graph()

    for endpoint in graph.endpoints.values():
        app.post(endpoint.path)(graph.functions[endpoint.fn_name])

    print(app.routes)
    uvicorn.run(app=app, reload=False, port=5001)


def run():
    from simple import trigger

    graph = get_current_graph()
    init(graph)

    print(graph)
    execute_function(graph, trigger, Event(payload={"a": 1}))
    pprint(memory_db)


if __name__ == "__main__":
    run()
