from pyrogram import filters
from requests import get

from MerissaRobot import pbot

pinregex = r"^https:\/\/(pin\.it|www\.pinterest\.com|pinterest\.com)"


@pbot.on_message(filters.regex(pinregex))
async def pindown(_, message):
    link = message.text
    m = await message.reply_text("Processing...")
    if link == "pinterest.com":
        pin_id = link.split("/", 4)[4]
        pinvid = get(
            f"https://api.princexd.tech/pin2?link=https://pin.it/{pin_id}"
        ).json()["media"]
        await message.reply_video(pinvid, caption="Powered By @MerissaRobot")
        await m.delete()
    else:
        pinvid = get(f"https://api.princexd.tech/pin2?link={link}").json()["media"]
        await message.reply_video(pinvid, caption="Powered By @MerissaRobot")
        await m.delete()
