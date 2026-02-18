from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from bot.loader import discover_extensions

DEFAULT_EXTENSION_PACKAGE = "bot.extensions"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_CONFIG_FILE = "config/bot.yaml"


def _parse_extensions_list(items: object) -> tuple[str, ...]:
    if not isinstance(items, list):
        return ()
    parsed = tuple(str(item).strip() for item in items if str(item).strip())
    return parsed


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


def _discover_extensions(package: str) -> tuple[str, ...]:
    discovered = tuple(sorted(discover_extensions(package)))
    if discovered:
        return discovered
    raise ValueError(f"No extensions discovered in package '{package}'.")


def _validate_matrix_auth(path: str | Path, data: dict[str, object]) -> None:
    password = str(data.get("PASSWORD", "")).strip()
    token = str(data.get("TOKEN", "")).strip()
    has_password = bool(password)
    has_token = bool(token)

    if has_password and has_token:
        raise ValueError(f"{path} sets both PASSWORD and TOKEN. Set only one auth method.")

    if not has_password and not has_token:
        raise ValueError(f"{path} must set PASSWORD or TOKEN.")


@dataclass(frozen=True, slots=True)
class Settings:
    matrix_config_file: str = DEFAULT_CONFIG_FILE
    log_level: str = DEFAULT_LOG_LEVEL
    extensions: tuple[str, ...] = ()

    @classmethod
    def from_yaml(
        cls,
        matrix_config_file: str | Path = DEFAULT_CONFIG_FILE,
    ) -> Settings:
        config_file = str(matrix_config_file).strip() or DEFAULT_CONFIG_FILE
        config_data = _read_yaml_config(config_file)
        _validate_matrix_auth(config_file, config_data)

        extensions = _discover_extensions(DEFAULT_EXTENSION_PACKAGE)

        return cls(
            matrix_config_file=config_file,
            extensions=extensions,
        )
