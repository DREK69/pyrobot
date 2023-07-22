from pyrogram import filters
from requests import get

from MerissaRobot import pbot

pinregex = r"^https:\/\/(pin\.it|www\.pinterest\.com|pinterest\.com)"


@pbot.on_message(filters.regex(pinregex))
async def pindown(_, message):
    link = message.text
    m = await message.reply_text("Processing...")
    pin = get(f"https://api.princexd.tech/pin?link={link}").json()
    pin["media"]
    title = pin["title"]
    await message.reply_document(
        pinvid, caption=f"{title}\n\nUploaded by @MerissaRobot"
    )
    await m.delete()
