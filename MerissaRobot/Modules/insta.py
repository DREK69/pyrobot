from pyrogram import filters
from requests import get

from MerissaRobot import pbot

instaregex = r"^https:\/\/www\.instagram\.com\/(p|tv|reel|stories)\/([A-Za-z0-9\-_]*)"


@pbot.on_message(filters.regex(instaregex))
async def instadown(_, message):
    name = message.text
    x = get(f"https://api.princexd.tech/igdown?link={name}").json()["media"]
    await message.reply_video(
        x,
        caption="Powered by @MerissaRobot",
    )
