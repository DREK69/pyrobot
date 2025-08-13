from functools import wraps
from telegram.constants import ChatAction
from telegram import error, Message
from telegram.ext import ContextTypes
from typing import Callable, Any, Coroutine


async def send_message(message: Message, text: str, *args, **kwargs):
    try:
        return await message.reply_text(text, *args, **kwargs)
    except error.BadRequest as err:
        if str(err) == "Reply message not found":
            return await message.reply_text(text, quote=False, *args, **kwargs)


def typing_action(func: Callable[..., Coroutine[Any, Any, Any]]):
    """Sends typing action while processing func command."""

    @wraps(func)
    async def command_func(update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )
        return await func(update, context, *args, **kwargs)

    return command_func


def send_action(action: ChatAction):
    """Sends `action` while processing func command."""

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def command_func(update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=action
            )
            return await func(update, context, *args, **kwargs)

        return command_func

    return decorator
