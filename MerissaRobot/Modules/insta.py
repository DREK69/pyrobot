from pyrogram import filters
from requests import get

from MerissaRobot import pbot

instaregex = r"^https:\/\/www\.instagram\.com\/(p|tv|reel|stories)\/([A-Za-z0-9\-_]*)"


@pbot.on_message(filters.regex(instaregex))
async def instadown(_, message):
    name = message.text
    url = get(f"https://api.princexd.tech/igdown?link={name}").json()
    if url.startswith([):
        for i in url:
            i["media"] = medias
        video = medias
    else:
        video = url["media"]
    await message.reply_video(
        video,
        caption="Powered by @MerissaRobot",
    )
