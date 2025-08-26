import os
import asyncio

from telegram import Update
from telegram.exceptions import BadRequest, RetryAfter, Unauthorized
from telegram.ext import ContextTypes, CommandHandler, filters

from MerissaRobot import OWNER_ID, application
from MerissaRobot.Database.sql.users_sql import get_user_com_chats
from MerissaRobot.Handler.ptb.extraction import extract_user


async def get_user_common_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot, args = context.bot, context.args
    msg = update.effective_message
    user = extract_user(msg, args)
    if not user:
        await msg.reply_text("I share no common chats with the void.")
        return
    
    common_list = get_user_com_chats(user)
    if not common_list:
        await msg.reply_text("No common chats with this user!")
        return
    
    try:
        user_chat = await bot.get_chat(user)
        name = user_chat.first_name
    except (BadRequest, Unauthorized):
        await msg.reply_text("Could not get user information.")
        return
    
    text = f"<b>Common chats with {name}</b>\n"
    for chat in common_list:
        try:
            chat_obj = await bot.get_chat(chat)
            chat_name = chat_obj.title
            await asyncio.sleep(0.3)  # Rate limiting
            text += f"• <code>{chat_name}</code>\n"
        except (BadRequest, Unauthorized):
            pass
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)

    if len(text) < 4096:
        await msg.reply_text(text, parse_mode="HTML")
    else:
        with open("common_chats.txt", "w", encoding="utf-8") as f:
            f.write(text)
        with open("common_chats.txt", "rb") as f:
            await msg.reply_document(f)
        os.remove("common_chats.txt")


COMMON_CHATS_HANDLER = CommandHandler(
    "getchats",
    get_user_common_chats,
    filters=filters.User(OWNER_ID),
    block=False,
)

application.add_handler(COMMON_CHATS_HANDLER)
