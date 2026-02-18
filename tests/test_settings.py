import pytest

from bot.settings import Settings


def test_settings_from_yaml_file_uses_defaults(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "bot.settings.discover_extensions", lambda package: ["tests.fake_extension"]
    )
    config_file = tmp_path / "bot.yaml"
    config_file.write_text(
        "HOMESERVER: https://matrix.org\n" "USERNAME: '@bot:matrix.org'\n" "PASSWORD: secret\n",
        encoding="utf-8",
    )

    settings = Settings.from_yaml(matrix_config_file=config_file)

    assert settings.matrix_config_file == str(config_file)
    assert settings.log_level == "INFO"
    assert settings.extensions == ("tests.fake_extension",)


def test_settings_auto_discovers_extensions_when_yaml_has_none(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "bot.settings.discover_extensions",
        lambda package: ["bot.extensions.fun.echo", "bot.extensions.core.ping"],
    )
    config_file = tmp_path / "bot.yaml"
    config_file.write_text(
        "HOMESERVER: https://matrix.org\n" "USERNAME: '@bot:matrix.org'\n" "TOKEN: abc123\n",
        encoding="utf-8",
    )

    settings = Settings.from_yaml(matrix_config_file=config_file)

    assert settings.extensions == ("bot.extensions.core.ping", "bot.extensions.fun.echo")


def test_settings_raises_when_no_extensions_are_discovered(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("bot.settings.discover_extensions", lambda package: [])
    config_file = tmp_path / "bot.yaml"
    config_file.write_text(
        "HOMESERVER: https://matrix.org\n" "USERNAME: '@bot:matrix.org'\n" "TOKEN: abc123\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="No extensions discovered"):
        Settings.from_yaml(matrix_config_file=config_file)


def test_settings_uses_default_log_level(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "bot.settings.discover_extensions", lambda package: ["tests.fake_extension"]
    )
    config_file = tmp_path / "bot.yaml"
    config_file.write_text(
        "HOMESERVER: https://matrix.org\n" "USERNAME: '@bot:matrix.org'\n" "TOKEN: abc123\n",
        encoding="utf-8",
    )

    settings = Settings.from_yaml(matrix_config_file=config_file)
    assert settings.log_level == "INFO"


def test_settings_rejects_both_password_and_token(tmp_path) -> None:
    config_file = tmp_path / "bot.yaml"
    config_file.write_text(
        "PASSWORD: secret\n" "TOKEN: abc123\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="both PASSWORD and TOKEN"):
        Settings.from_yaml(matrix_config_file=config_file)


def test_settings_requires_password_or_token(tmp_path) -> None:
    config_file = tmp_path / "bot.yaml"
    config_file.write_text("PREFIX: '!'\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must set PASSWORD or TOKEN"):
        Settings.from_yaml(matrix_config_file=config_file)


def test_settings_requires_existing_config_file(tmp_path) -> None:
    config_file = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError, match="does not exist"):
        Settings.from_yaml(matrix_config_file=config_file)
