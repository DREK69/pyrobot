from pyrogram import filters
from requests import get, post

from MerissaRobot import pbot


@pbot.on_message(filters.command("ask"))
async def ask(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some questions to ask ChatGPT. Example- /ask question"
        )
    m = await message.reply_text("Wait a moment looking for your answer..")
    query = message.text.split(None, 1)[1]
    try:
        json = {
            "message": query,
            "chat_mode": "assistant",
            "dialog_messages": '[{"bot":"Merissa","user":"Prince"}]',
        }
        x = post("https://api.safone.me/chatgpt", data=json).json()["message"]
    except:
        x = "Something went wrong"
    await m.edit(x, disable_web_page_preview=True)


@pbot.on_message(filters.command("bard"))
async def bard_chatbot(_, message):
    text = message.text.split(" ", 1)[1]
    if len(message.command) == 1:
        return await message.reply_msg(
            "Give me some questions to ask Bard AI. Example- /bard question"
        )
    msg = await message.reply_text(
        "Wait a moment looking for your answer..", quote=True
    )
    try:
        x = get(f"https://yasirapi.eu.org/bard?input={text}").json()["content"]
    except:
        x = "Something went wrong"
    await msg.edit_text(x)
