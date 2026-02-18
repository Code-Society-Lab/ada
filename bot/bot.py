from __future__ import annotations

import logging

from matrix import Bot

from bot.loader import load_extensions
from bot.settings import Settings

logger = logging.getLogger(__name__)


class AdaBot:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.bot = Bot(config=settings.matrix_config_file)

    def bootstrap(self) -> None:
        loaded = load_extensions(self.bot, self.settings.extensions)
        logger.info("Loaded %s extensions: %s", len(loaded), ", ".join(loaded))

    def run(self) -> None:
        self.bootstrap()
        logger.info("Starting Matrix bot with config %s", self.settings.matrix_config_file)
        self.bot.start()
