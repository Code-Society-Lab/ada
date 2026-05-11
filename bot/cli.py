from os import getenv
import subprocess
import sys

from click import UsageError, pass_context, group, option, echo, style

from pelican import use_context
from pelican.cli import cli as pelican_cli

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

    if ctx.invoked_subcommand == "verify":
        return

    if env and config_file:
        raise UsageError("Use either --env or --config, not both.")

    path = config_file or resolve_config_path(env)
    config = BotConfig(path)

    ctx.obj["config"] = config
    ctx.with_resource(use_context(database_url=config.database_url))


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


@cli.command("verify", help="Verify the codebase is clean")
def verify_command() -> None:
    ok = style("✓", fg="green", bold=True)
    fail = style("✗", fg="red", bold=True)
    overall_exit = 0

    steps = [
        (
            "black ",
            "checking formatting...",
            ["black", "--check", "bot/", "tests/", "db/"],
        ),
        ("mypy  ", "type checking...", ["mypy", "bot/", "tests/"]),
        ("pytest", "running tests...", ["pytest", "tests/", "--color=yes"]),
    ]

    for label, description, args in steps:
        echo(style(label, bold=True) + f"  {description}", nl=False)
        result = subprocess.run(args, capture_output=True, text=True)

        if result.returncode == 0:
            echo(f"  {ok}")
        else:
            echo(f"  {fail}")

            if output := (result.stdout + result.stderr).strip():
                echo(output)
            overall_exit = result.returncode

    sys.exit(overall_exit)
