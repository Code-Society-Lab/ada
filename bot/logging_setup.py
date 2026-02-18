import logging
import logging.config
from pathlib import Path

import yaml


def configure_logging(level: str = "INFO", config_file: str = "config/logging.yaml") -> None:
    path = Path(config_file)
    if path.exists():
        try:
            config = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            config = None
        if isinstance(config, dict):
            logging.config.dictConfig(config)
            logging.getLogger().setLevel(getattr(logging, level.upper(), logging.INFO))
            return

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
