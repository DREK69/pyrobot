from pyrogram import filters
from requests import get

from MerissaRobot import pbot

instaregex = r"^https:\/\/(instagram\.com|www\.instagram\.com)\/(p|tv|reel|stories)\/([A-Za-z0-9\-_]*)"


@pbot.on_message(filters.regex(instaregex))
async def instadown(_, message):
    name = message.text
    url = get(f"https://api.princexd.tech/igdown?link={name}").json()["media"]
    if "[" in url:
        for i in url:
            media = i
        video = media
    else:
        video = url
    await message.reply_video(
        video,
        caption="Powered by @MerissaRobot",
    )
