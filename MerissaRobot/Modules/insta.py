import random
from pyrogram import filters
from pyrogram.types import *
from requests import get
from telegram import InlineKeyboardButton

from MerissaRobot import pbot

instaregex = r"^https:\/\/(instagram\.com|www\.instagram\.com)\/(p|tv|reel|stories)\/([A-Za-z0-9\-_]*)"

apikey = ["22a34ac86fmsh648c15a7abb6555p1cb539jsn4b193ae50c9f",
          "287368f5b2msh208f356d1e50f41p1ee0a7jsn76de8c3178ef",
          "22188e6ed4msh1da912cb2478b78p16790ajsn4f7e95e8832a",
          "f7d5da343fmshb59c17556f98735p17d795jsn0470fdc50f47"]

@pbot.on_message(filters.regex(instaregex) & filters.private)
async def instadown(_, message):
    link = message.text   
    msg = await message.reply_text("Processing...")
    key = random.choice(apikey)
    posts = get(
        f"https://api.princexd.tech/igdown?apikey={key}&link={link}"
    ).json()["media"]
    if isinstance(posts, str):
        if ".mp4" in posts:
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


__help__ = """
@MerissaRobot Share Anything Download Anything

For YouTube:
 ❍ [/ytdl,/song,/music] <query> : To download song and video From Youtube
 ❍ `@MerissaRobot yt query` : For search link of Youtube Videos in MerissaRobot.
 ❍ Otherwise Send direct link of YouTube Video or Shorts For download Song or Video

For Instagram:
 ❍ Send direct link of Story, Reels, Post, IGTV Videos from Instagram to Download Video.

For Merissa-Hub(PHub):
 ❍ Send direct link of Phub Video from Phub website to Download Video.
 ❍ `@MerissaRobot ph query` : For search link of PHub Videos in MerissaRobot.
"""

__mod_name__ = "Downloaders 📥"

__helpbtns__ = [
    [
        InlineKeyboardButton("Youtube", switch_inline_query_current_chat="yt"),
        InlineKeyboardButton("P-Hub", switch_inline_query_current_chat="ph"),
    ],
    [InlineKeyboardButton("🔙 Back", callback_data="help_back")],
]
