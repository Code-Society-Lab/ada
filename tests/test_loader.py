from types import ModuleType
import tests.fake_extensions as fake_extensions
from bot.loader import find_all_importable, import_package_modules


def test_find_all_importable_returns_strings() -> None:
    result = find_all_importable(fake_extensions)
    assert all(isinstance(name, str) for name in result)


def test_find_all_importable_finds_all_modules() -> None:
    result = find_all_importable(fake_extensions)
    assert "tests.fake_extensions.ping" in result
    assert "tests.fake_extensions.pong" in result


def test_import_package_modules_yields_modules() -> None:
    for module in import_package_modules(fake_extensions):
        assert isinstance(module, ModuleType)


def test_import_package_modules_have_extension_attr() -> None:
    for module in import_package_modules(fake_extensions):
        assert hasattr(
            module, "extension"
        ), f"{module.__name__} is missing an 'extension' attribute"
