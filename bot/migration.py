from logging import fatal, info

from alembic.command import downgrade, revision, upgrade
from alembic.config import Config
from alembic.util.exc import CommandError

from .config import BotConfig


def generate_migration(config: BotConfig, message: str):
    try:
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.config_ini_section = config.environment

        revision(alembic_cfg, message=message, autogenerate=True, sql=False)
    except CommandError as e:
        fatal(f"Error creating migration: {e}")


def up_migration(config: BotConfig, revision_: str = "head"):
    info(f"Upgrading revision {revision_}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.config_ini_section = config.environment

    upgrade(alembic_cfg, revision=revision_)


def down_migration(config: BotConfig, revision_: str = "head"):
    info(f"Downgrading revision {revision_}")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.config_ini_section = config.environment

    downgrade(alembic_cfg, revision=revision_)
