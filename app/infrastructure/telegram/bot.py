from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from telegram.ext import Application

from app.config import Settings
from app.infrastructure.telegram.handlers import build_handlers

logger = logging.getLogger(__name__)


class TelegramBotRunner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.application: Application | None = None
        self.task: asyncio.Task | None = None

    async def start(self) -> None:
        if not self.settings.telegram_bot_token:
            logger.warning("Telegram bot token missing; bot polling disabled")
            return
        self.application = Application.builder().token(self.settings.telegram_bot_token).build()
        for handler in build_handlers():
            self.application.add_handler(handler)
        await self.application.initialize()
        await self.application.start()
        self.task = asyncio.create_task(self.application.updater.start_polling())
        logger.info("Telegram bot polling started")

    async def stop(self) -> None:
        if not self.application:
            return
        if self.task:
            self.task.cancel()
            with suppress(asyncio.CancelledError):
                await self.task
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()
