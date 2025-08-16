from functools import wraps
from typing import Callable, Any, Coroutine

from telegram import Update, Message
from telegram.error import BadRequest
from telegram.constants import ChatAction
from telegram.ext import ContextTypes


async def send_message(message: Message, text: str, *args, **kwargs):
    """Safe reply_text that falls back if original message is missing."""
    try:
        return await message.reply_text(text, *args, **kwargs)
    except BadRequest as err:
        if "Reply message not found" in str(err):
            return await message.reply_text(text, reply_to_message_id=None, *args, **kwargs)


def typing_action(func: Callable[..., Coroutine[Any, Any, Any]]):
    """Decorator: sends 'typing' action while processing the command."""

    @wraps(func)
    async def command_func(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING,
        )
        return await func(update, context, *args, **kwargs)

    return command_func


def send_action(action: ChatAction):
    """Decorator: sends custom chat action (e.g. UPLOAD_PHOTO) while processing."""

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def command_func(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=action,
            )
            return await func(update, context, *args, **kwargs)

        return command_func

    return decorator
