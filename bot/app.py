import logging
from os import getpid

logging.basicConfig(level=logging.INFO)

logging.getLogger("nio").setLevel(logging.ERROR)
logging.getLogger("matrix").setLevel(logging.INFO)
logging.getLogger("apscheduler").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

import matrix
from click import group, option

from bot import extensions, ada
from bot.loader import find_all_importable, import_module

APP_INFO = """
| Matrix.py version: {matrixpy_version}
| PID: {pid}
| CONFIG: {config_file}
""".rstrip()

DEFAULT_CONFIG_FILE = "config/bot.yaml"


@group()
def cli():
    pass


@cli.command()
@option(
    "--config",
    help=f"Path to the config file.",
    default=DEFAULT_CONFIG_FILE,
    show_default=True,
)
def start(config: str):
    for extension in find_all_importable(extensions):
        module = import_module(extension)
        ada.bot.load_extension(module.extension)

    _show_application_info(config)
    ada.bot.start(config=config)


def _show_application_info(config_file: str):
    logger.info(
        APP_INFO.format(matrixpy_version=matrix.__version__, pid=getpid(), config_file=config_file)
    )
