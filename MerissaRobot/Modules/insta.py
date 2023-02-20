from pyrogram import filters
from requests import get

from MerissaRobot import pbot

instaregex = r"^https:\/\/(instagram\.com|www\.instagram\.com)\/(p|tv|reel|stories)\/([A-Za-z0-9\-_]*)"


@pbot.on_message(filters.regex(instaregex))
async def instadown(_, message):
    link = message.text
    msg = await message.reply_text("Processing...")
    dllink = get(f"https://api.princexd.tech/igdown?link={link}").json()["media"]
    mg = []
    if isinstance(dllink, str):
        mg.append(dllink)
    else:
        for post in dllink:
            mg.append(post)
    await message.reply_media_group(mg, caption="Powered by @MerissaRobot")
    await msg.delete()
