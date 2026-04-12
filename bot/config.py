from collections.abc import Iterator
from matrix import Config, Extension

from bot.loader import ModuleType, find_all_importable, import_module

DEFAULT_CONFIG_FILE = "config/bot.yaml"
DEFAULT_ENVIRONMENT = "development"
DEFAULT_LOG_LEVEL = "INFO"


class BotConfig(Config):
    def __init__(self, config_file: str) -> None:
        super().__init__(config_file)

        self.config_file: str = config_file or DEFAULT_CONFIG_FILE
        self.environment: str = self.get("env", default=DEFAULT_ENVIRONMENT)
        self.log_level: str = self.get("log_level", default=DEFAULT_LOG_LEVEL)
        self.log_format: str = (
            "[%(asctime)s] %(programname)s %(funcName)s %(module)s %(levelname)s %(message)s"
        )

    @property
    def extensions(self) -> Iterator[Extension]:
        from bot import extensions

        for name in find_all_importable(extensions):
            imported: ModuleType = import_module(name)

            if not hasattr(imported, "extension"):
                raise RuntimeError(f"Module '{name}' does not define an extension.")

            yield imported.extension
