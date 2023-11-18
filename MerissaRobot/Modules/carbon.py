import io

import requests
from pyrogram import filters

from MerissaRobot import pbot as app
from MerissaRobot.helpers import postreq


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
        data = {"code": txt}
        resp = requests.post(
            "https://carbonbyprince-cb2b465f5222.herokuapp.com/", json=data
        ).content
        phu = io.BytesIO(resp)
        phu.name = "huhu.png"
        await message.reply_photo(
            photo=phu, caption=f"<b>Carbonimg By :</b> {client.me.mention}"
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
        data = {"code": txt, "title": title, "theme": "breeze", "darkMode": True}
        resp = await postreq("https://api.princexd.tech/rayso", data)
        file = resp["url"]
        await message.reply_photo(
            photo=file, caption=f"<b>Raysoimg By :</b> {client.me.mention}"
        )
        await nan.delete()
    except Exception as e:
        return await message.reply(e)
