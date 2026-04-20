from os import environ
from logging import info, fatal

from .config import BotConfig


def _set_database_url(config: BotConfig) -> None:
    environ["DATABASE_URL"] = config.database_url


def generate_migration(config: BotConfig, name: str) -> None:
    _set_database_url(config)
    from pelican.generator import generate_migration as _generate
    _generate(name=name)


def up_migration(config: BotConfig, revision: int | None = None) -> None:
    _set_database_url(config)
    from pelican import loader, runner, registry
    loader.load_migrations()
    if revision is not None:
        migration = registry.get(revision)
        if not migration:
            fatal(f"Migration {revision} not found.")
            return
        runner.upgrade(migration)
    else:
        applied = list(runner.get_applied_versions())
        for migration in registry.get_all():
            if migration.revision not in applied:
                runner.upgrade(migration)


def down_migration(config: BotConfig, revision: int | None = None) -> None:
    _set_database_url(config)
    from pelican import loader, runner, registry
    loader.load_migrations()
    if revision is None:
        applied = list(runner.get_applied_versions())
        if not applied:
            info("No migrations have been applied.")
            return
        revision = max(applied)
    migration = registry.get(revision)
    if not migration:
        fatal(f"Migration {revision} not found.")
        return
    runner.downgrade(migration)
