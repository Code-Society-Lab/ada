from os import environ

from .config import BotConfig


def _set_database_url(config: BotConfig) -> None:
    environ["DATABASE_URL"] = config.database_url


def generate_migration(config: BotConfig, name: str) -> None:
    from pelican.cli import generate

    _set_database_url(config)
    generate.main([name], standalone_mode=False)


def up_migration(config: BotConfig, revision: int | None = None) -> None:
    from pelican.cli import up

    _set_database_url(config)
    up.main([str(revision)] if revision is not None else [], standalone_mode=False)


def down_migration(config: BotConfig, revision: int | None = None) -> None:
    from pelican.cli import down

    _set_database_url(config)
    down.main([str(revision)] if revision is not None else [], standalone_mode=False)
