from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.application.services.scheduler_service import SchedulerService
from app.config import get_settings
from app.infrastructure.telegram.bot import TelegramBotRunner


class SecretRedactionFilter(logging.Filter):
    def __init__(self, secrets: list[str]) -> None:
        super().__init__()
        self.secrets = [secret for secret in secrets if secret]

    def filter(self, record: logging.LogRecord) -> bool:
        for secret in self.secrets:
            record.msg = str(record.msg).replace(secret, "[redacted-telegram-token]")
            if record.args:
                redacted_args = []
                for arg in record.args:
                    if isinstance(arg, str) and secret in arg:
                        redacted_args.append(arg.replace(secret, "[redacted-telegram-token]"))
                    else:
                        redacted_args.append(arg)
                record.args = tuple(redacted_args)
        return True


def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    redaction_filter = SecretRedactionFilter([settings.telegram_bot_token])
    root_logger = logging.getLogger()
    root_logger.addFilter(redaction_filter)
    for handler in root_logger.handlers:
        handler.addFilter(redaction_filter)
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.addFilter(redaction_filter)
        for handler in logger.handlers:
            handler.addFilter(redaction_filter)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging()
    scheduler = SchedulerService(settings)
    bot = TelegramBotRunner(settings)
    scheduler.start()
    await bot.start()
    app.state.scheduler = scheduler
    app.state.telegram_bot = bot
    try:
        yield
    finally:
        scheduler.shutdown()
        await bot.stop()


app = FastAPI(title="NicoWay", version="0.1.0", lifespan=lifespan)
app.include_router(router)
