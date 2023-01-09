

class AppConfig(PydanticBase):
    name: str
    scripts: list[ScriptConfig]
    tables: list[TableConfig]
    files: list[FileConfig]


class StorageConfig(PydanticBase):
    url: str
    type: str = "database"


class DeployConfig(PydanticBase):
    name: str
    storages: list[StorageConfig]
    runtimes: list[RuntimeConfig]
    secret_managers: list[SecretManagerConfig]

