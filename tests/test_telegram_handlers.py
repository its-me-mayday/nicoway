from telegram.ext import CommandHandler, ConversationHandler

from app.infrastructure.telegram.handlers import build_handlers


def test_telegram_main_commands_are_registered():
    handlers = build_handlers()
    commands = {
        command
        for handler in handlers
        if isinstance(handler, CommandHandler)
        for command in handler.commands
    }

    expected = {
        "start",
        "help",
        "searches",
        "trips",
        "enable",
        "disable",
        "delete",
        "check",
        "best",
        "settings",
    }
    assert expected <= commands
    assert sum(isinstance(h, ConversationHandler) for h in handlers) == 2
