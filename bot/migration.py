from logging import fatal, info

from alembic.command import downgrade, revision, upgrade
from alembic.config import Config
from alembic.util.exc import CommandError

from .config import BotConfig


def _make_alembic_config(config: BotConfig) -> Config:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", config.database_url)
    return alembic_cfg


def generate_migration(config: BotConfig, message: str):
    try:
        alembic_cfg = _make_alembic_config(config)
        revision(alembic_cfg, message=message, autogenerate=True, sql=False)
    except CommandError as e:
        fatal(f"Error creating migration: {e}")


def up_migration(config: BotConfig, revision_: str = "head"):
    info(f"Upgrading revision {revision_}")
    alembic_cfg = _make_alembic_config(config)
    upgrade(alembic_cfg, revision=revision_)


def down_migration(config: BotConfig, revision_: str = "head"):
    info(f"Downgrading revision {revision_}")
    alembic_cfg = _make_alembic_config(config)
    downgrade(alembic_cfg, revision=revision_)
