import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from matrix import Config

from bot.loader import ModuleType, find_all_importable, import_module

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_CONFIG_FILE = "config/bot.yaml"


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def _read_yaml_config(path: str | Path) -> dict[str, object]:
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file '{path}' does not exist.")

    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        raise ValueError(f"Config file '{path}' is not valid YAML.") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Config file '{path}' must contain a top-level mapping.")

    return data


def _discover_extensions() -> Iterator[ModuleType]:
    from bot import extensions

    for name in find_all_importable(extensions):
        imported: ModuleType = import_module(name)

        if not hasattr(imported, "extension"):
            raise RuntimeError(f"Module '{name}' does not define an extension.")

        yield imported


@dataclass(frozen=True, slots=True)
class Settings:
    matrix_config: Config
    config_file_path: str = DEFAULT_CONFIG_FILE
    log_level: str = DEFAULT_LOG_LEVEL
    extensions: tuple[ModuleType, ...] = field(default_factory=tuple)

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> Self:
        config_file_path = str(config_path).strip() or DEFAULT_CONFIG_FILE
        config = Config(config_file_path)

        return cls(
            config_file_path=config_file_path,
            matrix_config=config,
            extensions=tuple(_discover_extensions()),
        )
