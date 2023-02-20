from pyrogram import filters
from requests import get

from MerissaRobot import pbot

instaregex = r"^https:\/\/(instagram\.com|www\.instagram\.com)\/(p|tv|reel|stories)\/([A-Za-z0-9\-_]*)"


@pbot.on_message(filters.regex(instaregex))
async def instadown(_, message):
    name = message.text
    msg = await message.reply_text("Processing...")
    posts = get(f"https://api.princexd.tech/igdown?link={name}").json()["media"]
    mg = []
    if isinstance(posts, str):
        mg.append(dllink)
    else:
        for post in dllink:
            mg.append(post)
    await message.reply_media_group(mg, caption="Powered by @MerissaRobot")
    await msg.delete()
