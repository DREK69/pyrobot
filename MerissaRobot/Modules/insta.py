from pyrogram import filters
from requests import get

from MerissaRobot import pbot

instaregex = (
    r"^https:\/\/(instagram\.com|www\.instagram\.com)\/(p|tv|reel)\/([A-Za-z0-9\-_]*)"
)
storyregex = (
    r"^https:\/\/(instagram\.com|www\.instagram\.com)\/(stories)\/([A-Za-z0-9\-_]*)"
)


@pbot.on_message(filters.regex(instaregex))
async def instadown(_, message):
    link = message.text
    m = await message.reply_text("Processing...")
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
    await m.delete()


@pbot.on_message(filters.regex(storyregex))
async def instadown(_, message):
    m = await message.reply_text("Processing...")
    link = message.text
    story = get(f"https://api.princexd.tech/igdown?link={link}").json()["media"]
    await message.reply_document(story, caption="Powered By @MerissaRobot")
    await m.delete()


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
