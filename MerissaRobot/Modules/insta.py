from pyrogram import filters
from pyrogram.types import InputMediaPhoto, InputMediaVideo
from requests import get

from MerissaRobot import pbot

instaregex = r"^https:\/\/(instagram\.com|www\.instagram\.com)\/(p|tv|reel|stories)\/([A-Za-z0-9\-_]*)"


@pbot.on_message(filters.regex(instaregex))
async def instadown(_, message):
    link = message.text
    msg = await message.reply_text("Processing...")
    posts = get(
        f"https://api.princexd.tech/igdown?apikey=22a34ac86fmsh648c15a7abb6555p1cb539jsn4b193ae50c9f&link={link}"
    ).json()["media"]
    if isinstance(posts, str):
        if str(posts.split("https://")[1]).startswith("video"):
            await message.reply_video(posts, caption=f"Powered By @MerissaRobot")
        else:
            await message.reply_photo(posts, caption=f"Powered By @MerissaRobot")
    else:
        mg = []
        for post in posts:
            if str(post.split("https://")[1]).startswith("video"):
                mg.append(InputMediaVideo(post, caption=f"Powered By @MerissaRobot"))
            else:
                mg.append(InputMediaPhoto(post, caption=f"Powered By @MerissaRobot"))
        await message.reply_media_group(mg)
    await msg.delete()
