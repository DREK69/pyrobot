from pyrogram import filters
from requests import get

from MerissaRobot import pbot

instaregex = r"^https:\/\/(instagram\.com|www\.instagram\.com)\/(p|tv|reel|stories)\/([A-Za-z0-9\-_]*)"


@pbot.on_message(filters.regex(instaregex))
async def instadown(_, message):
    link = message.text
    msg = await message.reply_text("Processing...")
    posts = get(f"https://api.princexd.tech/igdown?link={link}").json()["media"]
    if isinstance(posts, str):
        await message.reply_document(posts, caption="Powered By @MerissaRobot")
    else:
        for post in posts:
            await message.reply_document(post)
    await msg.delete()
