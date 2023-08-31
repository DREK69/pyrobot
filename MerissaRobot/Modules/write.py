from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters

from MerissaRobot import pbot as app


@app.on_message(filters.command(["write"]))
async def handwrite(client, message):
    if message.reply_to_message and message.reply_to_message.text:
        message.reply_to_message.text
    elif len(message.command) > 1:
        message.text.split(None, 1)[1]
    else:
        return await message.reply(
            "Please reply to message or write after command to use write CMD."
        )
    await message.reply_text("Processing...")
    try:
        img = Image.open("./MerissaRobot/Utils/Resources/template.jpg")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("./MerissaRobot/Utils/Resources/font/assfont.ttf", 30)
        x, y = 150, 140
        lines = text_set(data.text)
        line_height = font.getsize("hg")[1]
        for line in lines:
            draw.text((x, y), line, fill=(1, 22, 55), font=font)
            y = y + line_height - 5
        file = "generated.jpg"
        img.save(file)
        await message.reply_photo(
            photo=file, caption=f"<b>Written By :</b> {client.me.mention}"
        )
    except Exception as e:
        return await message.reply(e)
