from os import getenv
from click import UsageError, pass_context, group, option, argument

from bot.app import start
from bot.config import BotConfig
from bot.migration import generate_migration, up_migration, down_migration

DEFAULT_ENV = "development"
CONFIG_DIR = "config"


def resolve_config_path(env: str | None) -> str:
    environment = env or getenv("ADA_ENV", DEFAULT_ENV)
    return f"{CONFIG_DIR}/{environment}.yaml"


@group()
@option(
    "--env", default=None, help="Environment (development, production, staging, ...)"
)
@option("--config", "config_file", default=None, help="Explicit path to a config file")
@pass_context
def cli(ctx, env: str | None, config_file: str | None) -> None:
    ctx.ensure_object(dict)

    if env and config_file:
        raise UsageError("Use either --env or --config, not both.")

    path = config_file or resolve_config_path(env)
    ctx.obj["config"] = BotConfig(path)


@cli.command("start")
@pass_context
def start_command(ctx):
    config = ctx.obj["config"]
    start(config.config_file)


@cli.command()
@argument("name")
@pass_context
def generate(ctx, name: str):
    config = ctx.obj["config"]
    generate_migration(config, name)


@cli.command()
@argument("revision", default=None, required=False, type=int)
@pass_context
def up(ctx, revision: int | None):
    config = ctx.obj["config"]
    up_migration(config, revision)


@cli.command()
@argument("revision", default=None, required=False, type=int)
@pass_context
def down(ctx, revision: int | None):
    config = ctx.obj["config"]
    down_migration(config, revision)
