from os import getenv
from click import group, option, UsageError

from bot.app import start

DEFAULT_ENV = "development"
CONFIG_DIR = "config"


def resolve_config_path(env: str | None) -> str:
    environment = env or getenv("ADA_ENV", DEFAULT_ENV)
    return f"{CONFIG_DIR}/{environment}.yaml"


@group()
def cli():
    pass


@cli.command("start")
@option("--env", default=None, help="Environment (development, production, staging, ...)")
@option("--config", "config_file", default=None, help="Explicit path to a config file")
def start_command(env: str | None, config_file: str | None):
    if env and config_file:
        raise UsageError("Use either --env or --config, not both.")

    path = config_file or resolve_config_path(env)
    start(path)
