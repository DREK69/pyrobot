from pyrogram import filters
from requests import get, post

from MerissaRobot import pbot


@pbot.on_message(filters.command("ask"))
async def ask(_, message):
    m = await message.reply_text("Wait a moment looking for your answer..")
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some questions to ask ChatGPT. Example- /ask question"
        )
    query = message.text.split(None, 1)[1]
    json = {
        "message": query,
        "chat_mode": "assistant",
        "dialog_messages": '[{"bot":"Merissa","user":"Prince"}]',
    }
    x = post("https://api.safone.me/chatgpt", data=json).json()["message"]
    await m.edit(x, disable_web_page_preview=True)
