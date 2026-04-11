import logging
from os import getpid, getenv

import matrix
from click import group, option

from bot import ada
from bot.config import BotConfig, setup_logging

logger = logging.getLogger(__name__)

APP_INFO = """
| matrix.py: {matrixpy_version}
| pid: {pid}
| config: {config_file}
| extensions: {extension_count}
""".rstrip()

DEFAULT_ENV = "development"
CONFIG_DIR = "config"


def resolve_config_path(env: str | None) -> str:
    environment = env or getenv("ADA_ENV", DEFAULT_ENV)
    return f"{CONFIG_DIR}/{environment}.yaml"


@group()
def cli():
    pass


@cli.command()
@option(
    "--config",
    "config_file_path",
    help=f"Path to the config file.",
    show_default=True,
)
def start(config_file_path: str | None = None):
    config = BotConfig(resolve_config_path(config_file_path))

    setup_logging(config)

    for extension in config.extensions:
        ada.bot.load_extension(extension)

    _show_application_info(config)
    ada.bot.start(config=config)


def _show_application_info(config: BotConfig) -> None:
    logger.info(
        APP_INFO.format(
            matrixpy_version=matrix.__version__,
            pid=getpid(),
            config_file=config.config_file,
            extension_count=len(list(config.extensions)),
        )
    )
