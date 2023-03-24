from pyrogram import enums, filters
from pyrogram.types import Message

from MerissaRobot import BOT_ID, eor
from MerissaRobot import pbot as app
from MerissaRobot.Utils.Helper.chatbot import add_chatbot, check_chatbot, rm_chatbot
from MerissaRobot.Utils.Helpers.errors import capture_err
import MerissaRobot.Database.sql.chatbot_sql as sql

chatbot_group = 2


async def chat_bot_toggle(message: Message, is_userbot: bool):
    status = message.text.split(None, 1)[1].lower()
    chat_id = message.chat.id
    db = await check_chatbot()
    db = db["userbot"] if is_userbot else db["bot"]
    if status == "enable":
        if chat_id not in db:            
            is_merissa = await sql.rem_merissa(chat_id)
            await add_chatbot(chat_id, is_userbot=is_userbot)
            text = "Chatbot Enabled!"
            return await eor(message, text=text)
        await eor(message, text="ChatBot Is Already Enabled.")
    elif status == "disable":
        if chat_id in db:        
            is_merissa = await sql.set_merissa(chat_id)    
            await rm_chatbot(chat_id, is_userbot=is_userbot)
            return await eor(message, text="Chatbot Disabled!")
        await eor(message, text="ChatBot Is Already Disabled.")
    else:
        await eor(message, text="**Usage:**\n/chatbot [ENABLE|DISABLE]")


# Enabled | Disable Chatbot


@app.on_message(filters.command("chatgpt"))
@capture_err
async def chatbot_status(_, message: Message):
    if len(message.command) != 2:
        return await eor(message, text="**Usage:**\n/chatgpt [ENABLE|DISABLE]")
    await chat_bot_toggle(message, is_userbot=False)


@app.on_message(
    filters.text & filters.reply & ~filters.bot & ~filters.via_bot & ~filters.forwarded,
    group=chatbot_group,
)
@capture_err
async def chatbot_talk(_, message: Message):
    db = await check_chatbot()
    if message.chat.id not in db["bot"]:
        return
    if not message.reply_to_message:
        return
    if not message.reply_to_message.from_user:
        return
    if message.reply_to_message.from_user.id != BOT_ID:
        return
    chat_id = message.chat.id
    message.from_user.id if message.from_user else 0
    text = message.text.replace(" ", "%20") if len(message.text) < 2 else message.text
    await app.send_chat_action(chat_id, enums.ChatAction.TYPING)
    response = requests.get(f"https://api.princexd.tech/ask?text={text}").json()[
        "answer"
    ]
    await message.reply_text(response)
    await app.send_chat_action(chat_id, enums.ChatAction.CANCEL)
