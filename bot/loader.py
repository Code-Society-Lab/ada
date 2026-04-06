from collections.abc import Iterator
from importlib import import_module
from itertools import chain
from logging import warning
from os import walk
from pathlib import Path, PurePath
from pkgutil import walk_packages
from types import ModuleType
from typing import Set


def import_package_modules(package: ModuleType, shallow: bool = True) -> Iterator[ModuleType]:
    """Import all modules in the package and yield them in order."""
    for module in find_all_importable(package, shallow):
        yield import_module(module)


def find_all_importable(package: ModuleType, shallow: bool = True) -> Set[str]:
    """Find importable modules in the project and return them in order."""
    return set(
        chain.from_iterable(
            _discover_importable_path(Path(p), package.__name__, shallow) for p in package.__path__
        )
    )


def _discover_importable_path(pkg_pth: Path, pkg_name: str, shallow: bool) -> Iterator[str]:
    """Yield all importable packages under a given path and package.

    This solution is based on a solution by Sviatoslav Sydorenko (webknjaz)
    * https://github.com/sanitizers/octomachinery/blob/2428877/tests/circular_imports_test.py
    """
    for dir_path, _d, file_names in walk(pkg_pth):
        pkg_dir_path: Path = Path(dir_path)

        if pkg_dir_path.parts[-1] == "__pycache__":
            continue

        if all(Path(_).suffix != ".py" for _ in file_names):
            continue

        rel_pt: PurePath = pkg_dir_path.relative_to(pkg_pth)
        pkg_pref: str = ".".join((pkg_name,) + rel_pt.parts)

        if "__init__.py" not in file_names:
            warning(
                f"'{pkg_dir_path}' seems to be missing an '__init__.py'. This might cause issues."
            )

        yield from (
            pkg_path
            for _, pkg_path, is_pkg in walk_packages(
                (str(pkg_dir_path),),
                prefix=f"{pkg_pref}.",
            )
            if not is_pkg
        )

        if not shallow:
            break
