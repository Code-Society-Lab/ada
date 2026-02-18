import pytest

from bot.loader import ExtensionLoadError, discover_extensions, load_extension, load_extensions


def test_load_extensions_calls_setup() -> None:
    state: dict[str, list[str]] = {}
    loaded = load_extensions(state, ["tests.fake_extension"])
    assert loaded == ["tests.fake_extension"]
    assert state["loaded"] == ["tests.fake_extension"]


def test_load_extensions_requires_setup() -> None:
    with pytest.raises(ExtensionLoadError):
        load_extensions({}, ["tests"])


def test_load_extension_calls_setup() -> None:
    state: dict[str, list[str]] = {}
    load_extension(state, "tests.fake_extension")
    assert state["loaded"] == ["tests.fake_extension"]


def test_discover_extensions_for_package() -> None:
    discovered = discover_extensions("tests")
    assert "tests.fake_extension" in discovered
