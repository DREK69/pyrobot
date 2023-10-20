from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters

from MerissaRobot import pbot as app
from MerissaRobot.helpers import subscribe


def text_set(text):
    lines = []
    if len(text) <= 55:
        lines.append(text)
    else:
        all_lines = text.split("\n")
        for line in all_lines:
            if len(line) <= 55:
                lines.append(line)
            else:
                y = len(line) // 55
                lines.extend(line[((x - 1) * 55) : (x * 55)] for x in range(1, y + 2))
    return lines[:25]


@app.on_message(filters.command(["write"]))
async def handwrite(client, message):
    userid = message.from_user.id
    sub = await subscribe(client, userid)
    if sub == False:
        return await message.reply_text(
            "Please Join @MerissaxUpdates to Use Premium Features"
        )
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply(
            "Please reply to message or write after command to use write CMD."
        )
    w = await message.reply_text("Processing...")
    try:
        img = Image.open("./MerissaRobot/Utils/Resources/template.jpg")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("./MerissaRobot/Utils/Resources/font/assfont.ttf", 30)
        x, y = 150, 140
        lines = text_set(text)
        line_height = font.getsize("hg")[1]
        for line in lines:
            draw.text((x, y), line, fill=(1, 22, 55), font=font)
            y = y + line_height - 5
        file = "generated.jpg"
        img.save(file)
        await message.reply_photo(
            photo=file, caption=f"<b>Written By :</b> {client.me.mention}"
        )
        await w.delete()
    except Exception as e:
        return await w.edit(e)
