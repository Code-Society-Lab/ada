from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence

from bot.bot import AdaBot
from bot.logging_setup import configure_logging
from bot.settings import Settings

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Grace-style Matrix bot scaffold")
    parser.add_argument("--config-file", default="config/bot.yaml", help="Path to bot YAML config")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    settings = Settings.from_yaml(args.config_file)
    configure_logging(settings.log_level)
    try:
        AdaBot(settings).run()
    except Exception as exc:
        logger.error("%s", exc)
        return 1
    return 0
