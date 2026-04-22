from os import getenv, environ
from click import UsageError, pass_context, group, option, argument
from pelican.cli import cli as pelican_cli
from pelican import runner

from bot.app import start
from bot.config import BotConfig

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
    config = BotConfig(path)

    ctx.obj["config"] = config
    runner.database_url = config.database_url


@cli.command("start", help="Start the bot")
@pass_context
def start_command(ctx):
    config = ctx.obj["config"]
    start(config.config_file)


@cli.group(help="Database utilities commands")
def db():
    pass


# we add each pelican command to the db group
for cmd in pelican_cli.commands.values():
    db.add_command(cmd)
