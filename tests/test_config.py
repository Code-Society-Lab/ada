import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
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


@pytest.fixture
def extension_module() -> MagicMock:
    module = MagicMock()
    module.extension = MagicMock()
    return module


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


def test_extensions_yields_valid_extension(
    bot_config: BotConfig, extension_module: MagicMock
) -> None:
    with (
        patch.dict(sys.modules, {"bot.extensions": MagicMock()}),
        patch(
            "bot.config.find_all_importable",
            return_value={"bot.extensions.foo_extension"},
        ),
        patch("bot.config.import_module", return_value=extension_module),
    ):
        result = list(bot_config.extensions)

    assert result == [extension_module.extension]


def test_extensions_skips_tests_folder(
    bot_config: BotConfig, extension_module: MagicMock
) -> None:
    with (
        patch.dict(sys.modules, {"bot.extensions": MagicMock()}),
        patch(
            "bot.config.find_all_importable",
            return_value={"bot.extensions.tests.foo_extension"},
        ),
        patch("bot.config.import_module") as mock_import,
    ):
        result = list(bot_config.extensions)

    assert result == []
    mock_import.assert_not_called()


def test_extensions_skips_test_modules(
    bot_config: BotConfig, extension_module: MagicMock
) -> None:
    with (
        patch.dict(sys.modules, {"bot.extensions": MagicMock()}),
        patch(
            "bot.config.find_all_importable",
            return_value={"bot.extensions.test_foo_extension"},
        ),
        patch("bot.config.import_module") as mock_import,
    ):
        result = list(bot_config.extensions)

    assert result == []
    mock_import.assert_not_called()


def test_extensions_skips_non_extension_modules(
    bot_config: BotConfig, extension_module: MagicMock
) -> None:
    with (
        patch.dict(sys.modules, {"bot.extensions": MagicMock()}),
        patch(
            "bot.config.find_all_importable", return_value={"bot.extensions.helpers"}
        ),
        patch("bot.config.import_module") as mock_import,
    ):
        result = list(bot_config.extensions)

    assert result == []
    mock_import.assert_not_called()


def test_extensions_raises_if_missing_extension_attribute(
    bot_config: BotConfig,
) -> None:
    module = MagicMock(spec=[])

    with (
        patch.dict(sys.modules, {"bot.extensions": MagicMock()}),
        patch(
            "bot.config.find_all_importable",
            return_value={"bot.extensions.foo_extension"},
        ),
        patch("bot.config.import_module", return_value=module),
    ):
        with pytest.raises(RuntimeError, match="does not define an extension"):
            list(bot_config.extensions)
