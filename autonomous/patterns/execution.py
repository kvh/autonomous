
@dataclass
class ProtocolObjects:
    function_kwargs: dict

    def get_state(self, *args, **kwargs):
        return self.function_kwargs["state"]

    def get_param_by_name(self, name: str, *args, **kwargs):
        return self.function_kwargs.get(
            name, None
        )  # TODO: this should be default value

    def get_table_by_name(self, name: str, *args, **kwargs):
        return self.function_kwargs.get(name, MockUnconnectedTable())


@contextlib.contextmanager
def patch_patterns(protocol_objects: ProtocolObjects) -> ModuleType:
    import patterns

    originals = {}
    for cls in [
        "State",
        "Parameter",
        "Table",
        "Stream",
    ]:
        if hasattr(patterns, cls):
            originals[cls] = getattr(patterns, cls)

    setattr(patterns, "State", protocol_objects.get_state)
    setattr(patterns, "Parameter", protocol_objects.get_param_by_name)
    setattr(patterns, "Stream", protocol_objects.get_table_by_name)
    setattr(patterns, "Table", protocol_objects.get_table_by_name)

    try:
        yield patterns
    finally:
        for name, obj in originals.items():
            setattr(patterns, name, obj)


def _import_module(module_name: str, pth: str) -> ModuleType:
    # Required to use spec to import dynamically with relative imports
    spec = importlib.util.spec_from_file_location(module_name, pth)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@dataclass
class PythonScriptCallable:
    module_path: str
    node_file_full_path: str

    def __call__(self, **function_kwargs):
        self.function_kwargs = function_kwargs
        with patch_patterns(ProtocolObjects(function_kwargs)):
            self.import_and_run()

    def import_and_run(self):
        _import_module(self.module_path, str(self.node_file_full_path))


def get_node_as_callable(
    path_to_graph_root: Path,
    node_file_path: str,
):
    mod_path = ".".join(Path(node_file_path).with_suffix("").parts)
    pkg_mod_path = path_to_graph_root / "__init__.py"
    if pkg_mod_path.exists():
        # Import root package if it exists, this enables relative imports
        mod_path = path_to_graph_root.name + "." + mod_path
        _import_module(path_to_graph_root.name, str(pkg_mod_path))

    node_file_full_path = path_to_graph_root / node_file_path

    return PythonScriptCallable(
        module_path=mod_path, node_file_full_path=str(node_file_full_path)
    )


def execute_node():
    pass