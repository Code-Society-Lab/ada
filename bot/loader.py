from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType
from typing import Any, Iterable, Protocol


class SetupCallable(Protocol):
    def __call__(self, bot: Any) -> None: ...


class ExtensionLoadError(RuntimeError):
    """Raised when an extension cannot be imported or registered."""


def _resolve_setup(module: ModuleType, extension: str) -> SetupCallable:
    setup = getattr(module, "setup", None)
    if not callable(setup):
        raise ExtensionLoadError(
            f"Extension '{extension}' is missing a callable setup(bot) function."
        )
    return setup


def discover_extensions(package: str) -> list[str]:
    """Discover importable extension modules under a package path."""
    package_module = importlib.import_module(package)
    package_paths = getattr(package_module, "__path__", None)
    if package_paths is None:
        raise ExtensionLoadError(f"Package '{package}' is not a package.")

    discovered: list[str] = []
    for info in pkgutil.walk_packages(package_paths, prefix=f"{package}."):
        if info.ispkg:
            continue
        discovered.append(info.name)
    return discovered


def load_extension(bot: Any, extension: str) -> None:
    """Load and register a single extension."""
    try:
        module = importlib.import_module(extension)
    except Exception as exc:
        raise ExtensionLoadError(f"Failed to import extension '{extension}'.") from exc

    setup = _resolve_setup(module, extension)
    try:
        setup(bot)
    except Exception as exc:
        raise ExtensionLoadError(f"Extension '{extension}' setup(bot) failed.") from exc


def load_extensions(bot: Any, extensions: Iterable[str]) -> list[str]:
    loaded: list[str] = []
    for extension in extensions:
        load_extension(bot, extension)
        loaded.append(extension)
    return loaded
