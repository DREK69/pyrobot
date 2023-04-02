import requests
from pyrogram import filters
from pyrogram.enums import ChatAction
from pyrogram.types import Message

from MerissaRobot import BOT_ID, eor
from MerissaRobot import pbot as app
from MerissaRobot.Utils.Helpers.errors import capture_err
from MerissaRobot.Utils.Helpers.filter_groups import chatbot_group

active_chats_bot = []


async def chat_bot_toggle(db, message: Message):
    status = message.text.split(None, 1)[1].lower()
    chat_id = message.chat.id
    if status == "on":
        if chat_id not in db:
            db.append(chat_id)
            text = "Chatbot Enabled!"
            return await eor(message, text=text)
        await eor(message, text="ChatBot Is Already Enabled.")
    elif status == "off":
        if chat_id in db:
            db.remove(chat_id)
            return await eor(message, text="Chatbot Disabled!")
        await eor(message, text="ChatBot Is Already Disabled.")
    else:
        await eor(message, text="**Usage:**\n/chatgpt [on|off]")


# Enabled | Disable Chatbot


@app.on_message(filters.command("chatgpt"))
@capture_err
async def chatbot_status(_, message: Message):
    if len(message.command) != 2:
        return await message.ra(message, text="**Usage:**\n/chatgpt [on|off]")
    await chat_bot_toggle(active_chats_bot, message)


async def type_and_send(message: Message):
    chat_id = message.chat.id
    message.from_user.id if message.from_user else 0
    query = message.text.strip()
    await message._client.send_chat_action(chat_id, ChatAction.TYPING)
    response = requests.get(f"https://api.princexd.tech/ask?text={query}").json()[
        "answer"
    ]
    await message.reply_text(response)   


@app.on_message(
    filters.text & filters.reply & ~filters.bot & ~filters.via_bot & ~filters.forwarded,
    group=chatbot_group,
)
@capture_err
async def chatbot_talk(_, message: Message):
    if message.chat.id not in active_chats_bot:
        return
    if not message.reply_to_message:
        return
    if not message.reply_to_message.from_user:
        return
    if message.reply_to_message.from_user.id != BOT_ID:
        return
    await type_and_send(message)
