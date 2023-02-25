from pyrogram import filters
from requests import get

from MerissaRobot import pbot

instaregex = r"^https:\/\/(instagram\.com|www\.instagram\.com)\/(p|tv|reel|stories)\/([A-Za-z0-9\-_]*)"


@pbot.on_message(filters.regex(instaregex))
async def instadown(_, message):
    link = message.text
    await message.reply_text("Processing...")
    url = f"https://igdl.in/apis.php?url={link}"
    data = get(url).json()
    type = data["graphql"]["shortcode_media"]["__typename"]
    if type == "GraphImage":
        h = data["graphql"]["shortcode_media"]["display_resources"][0]["src"]
        await message.reply_photo(h)
    elif type == "GraphSidecar":
        cnt = len(
            data["graphql"]["shortcode_media"]["edge_sidecar_to_children"]["edges"]
        )
        for i in range(0, cnt):
            node = data["graphql"]["shortcode_media"]["edge_sidecar_to_children"][
                "edges"
            ][i]["node"]
            if "video_url" in node:
                video = node["video_url"]
                await message.reply_video(video)
            else:
                photo = node["display_resources"][0]["src"]
                await message.reply_photo(photo)

    else:
        x = data["graphql"]["shortcode_media"]["video_url"]
        await message.reply_video(x)


__help__ = """
@MerissaRobot Share Anything Download Anything

For YouTube:
 ❍ [/ytdl,/song,/music] <query> : To download song and video From Youtube
 ❍ `@MerissaRobot yt query` : For search link of Youtube Videos in MerissaRobot.
 ❍ Otherwise Send direct link from YouTube To download Song or Video

For Instagram:
 ❍ Send direct link of Story, Reels, Post, IGTV Videos from Instagram to Download Video.

For Merissa-Hub(PHub):
 ❍ Send direct link of Phub Video from Phub website to Download Video.
 ❍ `@MerissaRobot ph query` : For search link of PHub Videos in MerissaRobot.
"""

__mod_name__ = "Downloaders 📥"
