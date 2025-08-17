import os
from PIL import Image, ImageDraw, ImageFont
from pyrogram import filters
from MerissaRobot import pbot as app
from MerissaRobot.helpers import subscribe


def text_set(text: str):
    """Split text into lines of max 55 chars, max 25 lines"""
    lines = []
    if len(text) <= 55:
        lines.append(text)
    else:
        for line in text.splitlines():
            if len(line) <= 55:
                lines.append(line)
            else:
                while len(line) > 55:
                    lines.append(line[:55])
                    line = line[55:]
                if line:
                    lines.append(line)
    return lines[:25]


@app.on_message(filters.command("write"))
@subscribe
async def handwrite(client, message):
    # Get input text
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await message.reply_text(
            "✍️ **Usage:**\nReply to a text or type `/write your text here`"
        )

    status = await message.reply_text("🖋️ Generating handwriting...")

    try:
        # Load paper template & font
        img = Image.open("./MerissaRobot/Resources/write.jpg")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("./MerissaRobot/Resources/font/assfont.ttf", 30)

        # Starting coords
        x, y = 150, 140
        line_height = font.getbbox("hg")[3] - font.getbbox("hg")[1]  # better than getsize

        # Wrap text
        lines = text_set(text)

        # Draw text
        for line in lines:
            draw.text((x, y), line, fill=(10, 20, 40), font=font)
            y += line_height - 5

        # Save temporary image
        file = f"handwrite_{message.from_user.id}.jpg"
        img.save(file)

        # Send result
        await message.reply_photo(
            photo=file,
            caption=f"📝 **Handwritten by:** {client.me.mention}"
        )
        await status.delete()

        # Cleanup temp file
        if os.path.exists(file):
            os.remove(file)

    except Exception as e:
        await status.edit(f"❌ Error: `{e}`")
