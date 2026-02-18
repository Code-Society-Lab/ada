import pytest

from bot.settings import Settings


def test_settings_from_env_file(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("MATRIX_CONFIG_FILE", "BOT_EXTENSIONS", "LOG_LEVEL", "LOGGING_CONFIG_FILE"):
        monkeypatch.delenv(key, raising=False)

    config_file = tmp_path / "bot.yaml"
    config_file.write_text(
        "HOMESERVER: https://matrix.org\n"
        "USERNAME: '@bot:matrix.org'\n"
        "PASSWORD: secret\n"
        "APP:\n"
        "  EXTENSIONS:\n"
        "    - tests.fake_extension\n",
        encoding="utf-8",
    )

    env_file = tmp_path / ".env"
    env_file.write_text(
        f"MATRIX_CONFIG_FILE={config_file}\n" "LOG_LEVEL=debug\n",
        encoding="utf-8",
    )

    settings = Settings.from_env(env_file)

    assert settings.matrix_config_file == str(config_file)
    assert settings.logging_config_file == "config/logging.yaml"
    assert settings.extensions_package == "bot.extensions"
    assert settings.extensions == ("tests.fake_extension",)
    assert settings.log_level == "DEBUG"


def test_settings_uses_default_extensions_without_env_or_yaml(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("MATRIX_CONFIG_FILE", raising=False)
    monkeypatch.delenv("BOT_EXTENSIONS", raising=False)
    monkeypatch.delenv("BOT_EXTENSIONS_PACKAGE", raising=False)
    monkeypatch.setattr(
        "bot.settings.discover_extensions",
        lambda package: ["bot.extensions.fun.echo", "bot.extensions.core.ping"],
    )
    env_file = tmp_path / ".env"
    env_file.write_text("MATRIX_CONFIG_FILE=missing.yaml\n", encoding="utf-8")

    settings = Settings.from_env(env_file)

    assert settings.extensions == (
        "bot.extensions.core.ping",
        "bot.extensions.fun.echo",
    )


def test_settings_extension_package_override(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MATRIX_CONFIG_FILE", raising=False)
    monkeypatch.delenv("BOT_EXTENSIONS", raising=False)
    monkeypatch.setattr(
        "bot.settings.discover_extensions",
        lambda package: [f"{package}.a", f"{package}.b"],
    )
    env_file = tmp_path / ".env"
    env_file.write_text(
        "MATRIX_CONFIG_FILE=missing.yaml\n"
        "BOT_EXTENSIONS_PACKAGE=custom.extensions\n",
        encoding="utf-8",
    )

    settings = Settings.from_env(env_file)
    assert settings.extensions_package == "custom.extensions"
    assert settings.extensions == ("custom.extensions.a", "custom.extensions.b")


def test_settings_env_extensions_override_yaml(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MATRIX_CONFIG_FILE", raising=False)
    monkeypatch.delenv("BOT_EXTENSIONS", raising=False)
    config_file = tmp_path / "bot.yaml"
    config_file.write_text(
        "PASSWORD: secret\n" "APP:\n" "  EXTENSIONS:\n" "    - bot.extensions.core.ping\n",
        encoding="utf-8",
    )
    env_file = tmp_path / ".env"
    env_file.write_text(
        f"MATRIX_CONFIG_FILE={config_file}\n" "BOT_EXTENSIONS=tests.fake_extension\n",
        encoding="utf-8",
    )

    settings = Settings.from_env(env_file)
    assert settings.extensions == ("tests.fake_extension",)


def test_settings_uses_yaml_log_level_when_env_missing(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for key in ("MATRIX_CONFIG_FILE", "BOT_EXTENSIONS", "LOG_LEVEL"):
        monkeypatch.delenv(key, raising=False)

    config_file = tmp_path / "bot.yaml"
    config_file.write_text(
        "PASSWORD: secret\n" "APP:\n" "  LOG_LEVEL: warning\n",
        encoding="utf-8",
    )
    env_file = tmp_path / ".env"
    env_file.write_text(f"MATRIX_CONFIG_FILE={config_file}\n", encoding="utf-8")

    settings = Settings.from_env(env_file)
    assert settings.log_level == "WARNING"


def test_settings_allows_logging_config_override(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("MATRIX_CONFIG_FILE", "LOGGING_CONFIG_FILE"):
        monkeypatch.delenv(key, raising=False)

    config_file = tmp_path / "bot.yaml"
    config_file.write_text("PASSWORD: secret\n", encoding="utf-8")
    env_file = tmp_path / ".env"
    env_file.write_text(
        f"MATRIX_CONFIG_FILE={config_file}\n" "LOGGING_CONFIG_FILE=config/custom-logging.yaml\n",
        encoding="utf-8",
    )

    settings = Settings.from_env(env_file)
    assert settings.logging_config_file == "config/custom-logging.yaml"


def test_settings_rejects_both_password_and_token(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("MATRIX_CONFIG_FILE", raising=False)
    config_file = tmp_path / "bot.yaml"
    config_file.write_text(
        "PASSWORD: secret\n" "TOKEN: abc123\n",
        encoding="utf-8",
    )
    env_file = tmp_path / ".env"
    env_file.write_text(f"MATRIX_CONFIG_FILE={config_file}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="both PASSWORD and TOKEN"):
        Settings.from_env(env_file)


def test_settings_requires_password_or_token(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MATRIX_CONFIG_FILE", raising=False)
    config_file = tmp_path / "bot.yaml"
    config_file.write_text("PREFIX: '!'\n", encoding="utf-8")
    env_file = tmp_path / ".env"
    env_file.write_text(f"MATRIX_CONFIG_FILE={config_file}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must set PASSWORD or TOKEN"):
        Settings.from_env(env_file)
