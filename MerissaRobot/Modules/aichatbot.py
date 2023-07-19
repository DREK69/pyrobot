from pyrogram import filters
from requests import post, get

from MerissaRobot import pbot


@pbot.on_message(filters.command("ask"))
async def ask(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some questions to ask ChatGPT. Example- /ask question"
        )
    m = await message.reply_text("Wait a moment looking for your answer..")
    query = message.text.split(None, 1)[1]
    json = {
        "message": query,
        "chat_mode": "assistant",
        "dialog_messages": '[{"bot":"Merissa","user":"Prince"}]',
    }
    x = post("https://api.safone.me/chatgpt", data=json).json()["message"]
    await m.edit(x, disable_web_page_preview=True)

@app.on_message(filters.command("bard"))
async def bard_chatbot(_, message):
    text = message.text.split(' ', 1)[1]
    if len(message.command) == 1:
        return await message.reply_msg("Give me some questions to ask Bard AI. Example- /bard question")
    msg = await message.reply_msg("Wait a moment looking for your answer..", quote=True)
    try:
        req = get(f"https://yasirapi.eu.org/bard?input={text}").json()["content"]
        await msg.edit_msg(req)
    except Exception as e:
        await msg.edit_msg(str(e))
