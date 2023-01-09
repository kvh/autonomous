from __future__ import annotations

import os
from contextlib import contextmanager
from copy import deepcopy
from typing import Any, Dict, Optional

from dcp.utils.common import rand_str


class MemoryStoreApi:
    store: MemoryStore
    
    def get_key(self, obj: PythonObject) -> str:
        return obj.name

    def get(self, obj: PythonObject) -> Any:
        key = self.get_key(obj)
        return self.store.get(key)

    def put(self, obj: PythonObject):
        key = self.get_key(obj)
        self.store[key] = obj

