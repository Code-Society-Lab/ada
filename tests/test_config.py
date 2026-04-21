import pytest
from pathlib import Path
from bot.config import BotConfig, DEFAULT_LOG_LEVEL, DEFAULT_ENVIRONMENT


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    config = tmp_path / "test.yaml"
    config.write_text(
        "USERNAME: '@ada:matrix.org'\n"
        "PASSWORD: 'secret'\n"
        "HOMESERVER: 'https://matrix.org'\n"
        "PREFIX: '!'\n"
        "database_url: 'sqlite:///test.db'\n"
    )
    return config


@pytest.fixture
def bot_config(config_file: Path) -> BotConfig:
    return BotConfig(str(config_file))


def test_config_loads_username(bot_config: BotConfig) -> None:
    assert bot_config.username == "@ada:matrix.org"


def test_config_loads_homeserver(bot_config: BotConfig) -> None:
    assert bot_config.homeserver == "https://matrix.org"


def test_config_loads_prefix(bot_config: BotConfig) -> None:
    assert bot_config.prefix == "!"


def test_config_defaults_log_level(bot_config: BotConfig) -> None:
    assert bot_config.log_level == DEFAULT_LOG_LEVEL


def test_config_defaults_environment(bot_config: BotConfig) -> None:
    assert bot_config.environment == DEFAULT_ENVIRONMENT


def test_config_stores_config_file_path(config_file: Path) -> None:
    config = BotConfig(str(config_file))
    assert config.config_file == str(config_file)


def test_config_overrides_log_level(tmp_path: Path) -> None:
    config_file = tmp_path / "test.yaml"
    config_file.write_text(
        "USERNAME: '@ada:matrix.org'\n"
        "PASSWORD: 'secret'\n"
        "log_level: DEBUG\n"
        "database_url: 'sqlite:///test.db'\n"
    )
    config = BotConfig(str(config_file))
    assert config.log_level == "DEBUG"


def test_config_overrides_environment(tmp_path: Path) -> None:
    config_file = tmp_path / "test.yaml"
    config_file.write_text(
        "USERNAME: '@ada:matrix.org'\n"
        "PASSWORD: 'secret'\n"
        "env: production\n"
        "database_url: 'sqlite:///test.db'\n"
    )
    config = BotConfig(str(config_file))
    assert config.environment == "production"
