from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatAction

import MerissaRobot.Database.sql.chatbot_sql as sql
from MerissaRobot import pbot
from MerissaRobot.helpers import getreq


@pbot.on_callback_query(filters.regex("^merissa"))
async def merissachatbot(client, query):
    mode = query.data.split(None, 1)[1]
    chat = query.message.chat
    user = query.from_user
    if mode == "add":
        is_merissa = sql.set_merissa(chat.id)
        if is_merissa:
            is_merissa = sql.set_merissa(user.id)
            await query.edit_message_text(
                f"<b>{chat.title}:</b>\n"
                f"Merissa Chatbot Enable\n"
                f"<b>Admin:</b> {user.mention}\n"
            )
        else:
            await query.edit_message_text(f"Merissa Chatbot enable by {user.mention}.")
    else:
        is_merissa = sql.rem_merissa(chat.id)
        if is_merissa:
            is_merissa = sql.rem_merissa(user.id)
            await query.edit_message_text(
                f"<b>{chat.title}:</b>\n"
                f"Merissa Chatbot Disable\n"
                f"<b>Admin:</b> {user.mention}\n"
            )
        else:
            await query.edit_message_text(f"Merissa Chatbot disable by {user.mention}.")


@pbot.on_message(filters.command("chatbot"))
async def merissa(_, message):
    message.chat.id
    msg = """**Welcome To Control Panal Of Merissa ChatBot**

**Here You Will Find Two Buttons Select AnyOne Of Them**"""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="On", callback_data=f"merissa add"),
                InlineKeyboardButton(text="Off", callback_data=f"merissa rm"),
            ]
        ]
    )
    await message.reply_text(
        msg,
        reply_markup=keyboard,
    )


def merissa_message(bot, message):
    reply_message = message.reply_to_message
    if message.text.lower() == "merissa":
        return True
    if reply_message:
        if reply_message.from_user.id == bot.me.id:
            return True
    else:
        return False


@pbot.on_message(
    filters.text & filters.reply & ~filters.bot & ~filters.via_bot & ~filters.forwarded,
    group=2,
)
async def chatbot(bot, message):
    chat_id = message.chat.id
    is_merissa = sql.is_merissa(chat_id)
    if not is_merissa:
        return
    if message.text and not message.document:
        if not merissa_message(bot, message):
            return
        await bot.send_chat_action(chat_id, ChatAction.TYPING)
        results = await getreq(
            f"https://chat.merissabot.me/api/apikey=2030709195:Ofe_G5n4DZMPxnTgTXaSwvRqPXHhqpVMFqzWRNQ/message={message.text}"
        )
        await message.reply_text(results["reply"])


__mod_name__ = "Chatbot 🤖"

__help__ = """
Merissa AI ChatBot is the only ai system which can detect & reply upto 200 language's

For Chatbot turn on/off:
❂ `/chatbot`: To On Or Off ChatBot In Your Chat.

For Merissa Chatbot Api:
❂ `/token` : To get your Merissa Chatbot Token.
❂ `/revoke` : To revoke/delete Merissa Chatbot Token.

For Asking Questions to ChatGPT:
❂ `/ask question` : To get answer from Chatgpt By OpenAI.
❂ `/bard question` : To get answer from BardAI By Google.
"""
