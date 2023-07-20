import requests

from pyrogram import filters
from MerissaRobot import pbot as app


@app.on_message(filters.command(["carbon"]))
async def carbon(client, message):
    if message.reply_to_message and message.reply_to_message.text:
        txt = message.reply_to_message.text
    elif len(message.command) > 1:
        txt = message.text.split(None, 1)[1]
    else:
        return await message.reply(
            "Please reply to message or write after command to use write CMD."
        )
    nan = await message.reply_text("Processing...")
    try:
        data = {
            "code": txt,
            "bgcolor": "white"
        }
        file = requests.post("https://api.princexd.tech/carbon", json=data).json()["url"]
        await message.reply_photo(
            photo=file, caption=f"<b>Carbonimg By :</b> {client.me.mention}"
        )
        await nan.delete()
    except Exception as e:
        return await message.reply(e)

@app.on_message(filters.command(["rayso"]))
async def carbon(client, message):
    if message.reply_to_message and message.reply_to_message.text:
        txt = message.reply_to_message.text
        if len(message.command) > 1:
            title = message.text.split(None, 1)[1]
        else:
            title = message.from_user.username
    else:
        return await message.reply(
            "Please reply to message or write after command to use write CMD."
        )
    nan = await message.reply_text("Processing...")
    try:
        data = {
           "code": txt,
           "title": title,
           "theme": "breeze",
           "darkMode": true
        }
        file = requests.post("https://api.princexd.tech/rayso", json=data).json()["url"]
        await message.reply_photo(
            photo=file, caption=f"<b>Raysoimg By :</b> {client.me.mention}"
        )
        await nan.delete()
    except Exception as e:
        return await message.reply(e)
