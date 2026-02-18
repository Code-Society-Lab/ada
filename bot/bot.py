from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable

from matrix import Bot
from nio import AsyncClient, AsyncClientConfig, WhoamiError

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

    async def _preflight_token_auth(self) -> None:
        cfg = self.bot.config
        client = AsyncClient(
            cfg.homeserver,
            config=AsyncClientConfig(
                max_timeouts=2,
                request_timeout=5,
                backoff_factor=0.1,
                max_timeout_retry_wait_time=2,
            ),
        )
        client.user = cfg.user_id
        client.access_token = cfg.token
        try:
            response = await client.whoami()
        finally:
            await client.close()

        if isinstance(response, WhoamiError):
            raise RuntimeError(
                "Token auth failed before sync: "
                f"{response}. Set a valid TOKEN or switch to PASSWORD auth in config/bot.yaml."
            )

    def _preflight_auth(self) -> None:
        cfg = self.bot.config
        if cfg.token:
            logger.info("Using token auth for %s", cfg.user_id)
            try:
                asyncio.run(self._preflight_token_auth())
            except RuntimeError:
                raise
            except Exception as exc:
                raise RuntimeError(
                    "Token auth preflight failed due to connectivity or homeserver settings: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
        else:
            logger.info("Using password auth for %s", cfg.user_id)

    def run(self) -> None:
        self.bootstrap()
        self._preflight_auth()
        logger.info("Starting Matrix bot with config %s", self.settings.matrix_config_file)
        self.bot.start()
