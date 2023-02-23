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
        await message.reply_document(posts, caption="Powered By @MerissaRobot")
    else:
        mg = []
        for post in posts:
            if str(post.split("https://")[1]).startswith("video"):
                mg.append(InputMediaVideo(post, caption="Powered By @MerissaRobot"))
            else:
                mg.append(InputMediaPhoto(post, caption="Powered By @MerissaRobot"))
        await message.reply_media_group(mg)
    await msg.delete()


__help__ = """
@MerissaRobot Share Anything Download Anything

For YouTube:
 ❍ [/ytdl,/song,/music] <query> : To download song and video From Youtube
 ❍ Otherwise Send direct link from YouTube To download Song or Video

For Instagram:
 ❍ Send direct link of Story, Reels, Post, IGTV Videos from Instagram to Download Video.

For Merissa-Hub(PHub):
 ❍ Send direct link of Phub Video from Phub website to Download Video.
 ❍ @MerissaRobot ph <query> : For search link of PHub Videos in MerissaRobot.
"""

__mod_name__ = "Downloaders 📥"
