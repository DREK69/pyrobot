from pyrogram import filters
from requests import get

from MerissaRobot import pbot

instaregex = r"^https:\/\/(instagram\.com|www\.instagram\.com)\/(p|tv|reel|stories)\/([A-Za-z0-9\-_]*)"


@pbot.on_message(filters.regex(instaregex))
async def instadown(_, message):
    name = message.text
    msg = await message.reply_text("Please Wait Video Uploading...")
    url = get(f"https://api.princexd.tech/igdown?link={name}").json()
    vid = url["media"]
    if "[" in vid:
        for video in vid:
            await message.reply_document(file=video, caption="Powered by @MerissaRobot")
    else:
        video = url["media"]
        await message.reply_document(file=video, caption="Powered by @MerissaRobot")
    await msg.delete()
