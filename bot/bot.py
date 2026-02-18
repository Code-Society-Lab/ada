from __future__ import annotations

import logging
from collections.abc import Iterable

from matrix import Bot

from bot.loader import load_extension, load_extensions
from bot.settings import Settings

logger = logging.getLogger(__name__)


class AdaBot:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.bot = Bot(config=settings.matrix_config_file)
        self.loaded_extensions: list[str] = []

    def load_modules(self, extensions: Iterable[str]) -> list[str]:
        loaded = load_extensions(self.bot, extensions)
        self.loaded_extensions.extend(loaded)
        return loaded

    def load_module(self, extension: str) -> None:
        load_extension(self.bot, extension)
        self.loaded_extensions.append(extension)

    def bootstrap(self) -> None:
        loaded = self.load_modules(self.settings.extensions)
        logger.info("Loaded %s extensions: %s", len(loaded), ", ".join(loaded))

    def run(self) -> None:
        self.bootstrap()
        logger.info("Starting Matrix bot with config %s", self.settings.matrix_config_file)
        self.bot.start()
