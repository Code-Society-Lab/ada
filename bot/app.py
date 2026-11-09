import logging
from logging.handlers import RotatingFileHandler
from os import getpid

import matrix
from coloredlogs import install
from sqlmodel import SQLModel
from pelican import get_runner, get_registry

from bot import ada
from bot.dashboard import dashboard
from bot.config import BotConfig

logger = logging.getLogger(__name__)

APP_INFO = """
| matrix.py: {matrixpy_version}
| pid: {pid}
| config: {config_file}
| database_url={database_url}
| environment: {environment}
| extensions: {extension_count}
""".rstrip()


def start(config_file: str) -> None:
    config = BotConfig(config_file)

    _load_logging(config)
    # Before extensions, whose on_load emits to the dashboard.
    _load_dashboard(config)
    _load_extensions(config)
    _load_database(config)
    _start_dashboard(config)
    _show_app_info(config)

    ada.bot.start(config=config)


def _load_extensions(config: BotConfig) -> None:
    for extension in config.extensions:
        ada.bot.load_extension(extension)


def _load_dashboard(config: BotConfig) -> None:
    dashboard.init_dachshund(_event_store(config))
    dashboard.build_dashboard()


def _start_dashboard(config: BotConfig) -> None:
    dashboard.start_dashboard(
        path=_event_store(config),
        host=config.get("host", section="dashboard", default="127.0.0.1"),
        port=int(config.get("port", section="dashboard", default=1212)),
    )


def _event_store(config: BotConfig) -> str:
    return str(config.get("event_store", section="dashboard", default="dachshund.db"))


def _load_logging(config: BotConfig) -> None:
    file_handler: RotatingFileHandler = RotatingFileHandler(
        f"logs/{config.environment}.log", maxBytes=10000, backupCount=5
    )

    logging.basicConfig(
        level=config.log_level,
        format=config.log_format,
        handlers=[file_handler],
    )

    # eventually could be more flexible/configurable
    logging.getLogger("nio").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)

    install(
        config.log_level,
        fmt=config.log_format,
        programname=config.environment,
    )


def _load_database(config: BotConfig) -> None:
    from sqlmodel_toolkit import Model
    from sqlalchemy.exc import OperationalError
    from sqlmodel import create_engine

    engine = create_engine(
        config.database_url,
        echo=config.get("sqlalchemy_echo", default=False),
    )

    try:
        engine.connect()
    except OperationalError as e:
        logger.critical(f"Unable to load the 'database': {e}")

    Model.set_engine(engine)
    SQLModel.metadata.create_all(engine)

    if config.is_production:
        _run_migrations()


def _run_migrations() -> None:
    runner = get_runner()
    registry = get_registry()

    applied = list(runner.get_applied_versions())
    migrations = [m for m in registry.get_all() if m.revision not in applied]

    for migration in migrations:
        runner.upgrade(migration)


def _show_app_info(config: BotConfig) -> None:
    logger.info(
        APP_INFO.format(
            matrixpy_version=matrix.__version__,
            pid=getpid(),
            config_file=config.config_file,
            environment=config.environment,
            database_url=config.database_url,
            extension_count=len(list(config.extensions)),
        )
    )
