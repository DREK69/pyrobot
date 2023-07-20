import os

from pyrogram import filters

from MerissaRobot import pbot as app


@app.on_message(filters.command(["write"]))
async def handwrite(client, message):
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
            "text": txt
        }
        file = requests.post("https://api.princexd.tech/write", json=data).json()['url']
        await message.reply_photo(
             photo=file, caption=f"<b>Written By :</b> {client.me.mention}"
        )
        await nan.delete()
    except Exception as e:
        return await message.reply(e)
