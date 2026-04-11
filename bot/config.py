import logging
from collections.abc import Iterator
from logging.handlers import RotatingFileHandler

from coloredlogs import install
from envyaml import EnvYAML
from matrix import Config, Extension

from bot.loader import ModuleType, find_all_importable, import_module

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_CONFIG_FILE = "config/bot.yaml"
DEFAULT_ENVIRONMENT = "development"


class BotConfig(Config):
    def __init__(self, config_file: str) -> None:
        data = EnvYAML(config_file)

        super().__init__(
            username=data["ADA_USERNAME"],
            password=data.get("ADA_PASSWORD"),
            token=data.get("ADA_TOKEN"),
            homeserver=data.get("ADA_HOMESERVER", "https://matrix.org"),
            prefix=data.get("ADA_PREFIX", "!"),
        )

        self.config_file: str = config_file or DEFAULT_CONFIG_FILE
        self.environment: str = data.get("ENV", DEFAULT_ENVIRONMENT)
        self.log_level: str = data.get("LOG_LEVEL", DEFAULT_LOG_LEVEL)

    @property
    def extensions(self) -> Iterator[Extension]:
        from bot import extensions

        for name in find_all_importable(extensions):
            imported: ModuleType = import_module(name)

            if not hasattr(imported, "extension"):
                raise RuntimeError(f"Module '{name}' does not define an extension.")

            yield imported.extension


def setup_logging(config: BotConfig) -> None:
    file_handler: RotatingFileHandler = RotatingFileHandler(
        f"logs/{config.environment}.log", maxBytes=10000, backupCount=5
    )

    logging.basicConfig(
        level=config.log_level,
        format="[%(asctime)s] %(funcName)s:%(lineno) %(levelname)s %(message)s",
        handlers=[file_handler],
    )

    # eventually could be more flexible/configurable
    logging.getLogger("nio").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)

    install(
        config.log_level,
        fmt="[%(asctime)s] %(programname)s %(funcName)s %(module)s %(levelname)s %(message)s",
        programname=config.environment,
    )
