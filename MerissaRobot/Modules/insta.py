import json
import os
import random

import requests
import wget
from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton as Keyboard
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from telegram import InlineKeyboardButton

from MerissaRobot import pbot
from MerissaRobot.helpers import save_file

instaregex = r"^https:\/\/(instagram\.com|www\.instagram\.com)\/(p|tv|reel|stories)\/([A-Za-z0-9\-_]*)"
tiktokregex = r"^https:\/\/(www\.tiktok.com|vm\.tiktok\.com|vt\.tiktok\.com)\/?(.*)"
snapregex = r"^https:\/\/www\.snapchat\.com\/add"
fbregex = r"^https:\/\/www\.facebook\.com\/reel\/"

apikey = [
    "22a34ac86fmsh648c15a7abb6555p1cb539jsn4b193ae50c9f",
    "81b89ef962msh19a67d63d479365p122483jsn6af26adfd7a5",
]


@pbot.on_message(filters.regex(instaregex) & filters.incoming & filters.private)
async def instadown(_, message):
    link = message.text
    msg = await message.reply_text("Processing...")
    if "reel" in link:
        try:
            dlink = link.replace("www.instagram.com", "ddinstagram.com")
            await message.reply_video(dlink)
            await msg.delete()
        except:
            try:
                response = requests.get(
                    f"https://igdownloader.onrender.com/dl?key=ashok&url={link}"
                )
                data = response.json()
                dlink = data["urls"][0]
                await message.reply_video(dlink, caption=data["caption"])
                await msg.delete()
            except:
                try:
                    response = requests.get(
                        f"https://api.princexd.tech/instadown?link={link}"
                    ).json()
                    try:
                        await message.reply_video(
                            response["media"][0], caption="Downloaded By @MerissaRobot"
                        )
                    except:
                        x = save_file(video, "video.mp4")
                        await message.reply_video(x)
                        await msg.delete()
                        os.remove(x)
                except:
                    try:
                        key = random.choice(apikey)
                        video = requests.get(
                            f"https://api.princexd.tech/igdown?apikey={key}&link={link}"
                        ).json()["links"][0]["url"]
                        try:
                            await message.reply_video(video)
                            await msg.delete()
                        except:
                            x = save_file(video, "video.mp4")
                            await message.reply_video(x)
                            await msg.delete()
                            os.remove(x)
                    except:
                        await msg.edit_text(
                            "Something went Wrong Contact @MerissaxSupport"
                        )
    else:
        try:
            response = requests.get(
                f"https://igdownloader.onrender.com/dl?key=ashok&url={link}"
            )
            data = response.json()
            if len(data["urls"]) == 1:
                for i in data["urls"]:
                    if i == "":
                        await message.reply_text("failed to Fetch URL")
                    else:
                        if "mp4" in i:
                            await message.reply_video(
                                i,
                                caption=f"{data['caption']}\nDownloaded by @MerissaRobot",
                            )
                        else:
                            await message.reply_photo(
                                i,
                                caption=f"{data['caption']}\nDownloaded by @MerissaRobot",
                            )
            else:
                mg = []
                for post in data:
                    if post == "":
                        await message.reply_text("failed to Fetch URL")
                    elif "mp4" in post:
                        mg.append(
                            InputMediaVideo(
                                post,
                                caption=f"{data['caption']}\nDownloaded by @MerissaRobot",
                            )
                        )
                    else:
                        mg.append(
                            InputMediaPhoto(
                                post,
                                caption=f"{data['caption']}\nDownloaded by @MerissaRobot",
                            )
                        )
                await message.reply_media_group(mg)
            await msg.delete()
        except:
            try:
                posts = requests.get(
                    f"https://api.princexd.tech/instadown?link={link}"
                ).json()["media"]
                singlelink = posts[0]
                if len(posts) == 1:
                    if "jpg" in singlelink:
                        await message.reply_photo(
                            singlelink, caption="Downloaded By @MerissaRobot"
                        )
                    else:
                        await message.reply_video(
                            singlelink, caption="Downloaded By @MerissaRobot"
                        )
                else:
                    mg = []
                    for post in posts:
                        if "jpg" in post:
                            mg.append(
                                InputMediaPhoto(
                                    post, caption=f"Uploaded By @MerissaRobot"
                                )
                            )
                        else:
                            mg.append(
                                InputMediaVideo(
                                    post, caption=f"Uploaded By @MerissaRobot"
                                )
                            )
                    await message.reply_media_group(mg)
                await msg.delete()
            except:
                key = random.choice(apikey)
                posts = requests.get(
                    f"https://api.princexd.tech/igdown?apikey={key}&link={link}"
                ).json()["links"]
                singlelink = posts[0]
                if len(posts) == 1:
                    if singlelink["type"] == "video":
                        await message.reply_video(
                            singlelink["url"], caption=f"Downloaded By @MerissaRobot"
                        )
                    else:
                        await message.reply_photo(
                            singlelink["url"], caption=f"Downloaded By @MerissaRobot"
                        )
                else:
                    mg = []
                    for post in posts:
                        if post["type"] == "video":
                            mg.append(
                                InputMediaVideo(
                                    post["url"], caption=f"Downloaded By @MerissaRobot"
                                )
                            )
                        else:
                            mg.append(
                                InputMediaPhoto(
                                    post["url"], caption=f"Downloaded By @MerissaRobot"
                                )
                            )
                    await message.reply_media_group(mg)
                await msg.delete()


@pbot.on_message(filters.regex(fbregex) & filters.incoming & filters.private)
async def fbdown(_, message):
    link = message.text
    msg = await message.reply_text("Processing...")
    url = "https://facebook-reel-and-video-downloader.p.rapidapi.com/app/main.php"
    querystring = {"url": link}
    headers = {
        "X-RapidAPI-Key": "6a90d6d4efmsh32f9758380f3589p11e571jsn642878f330b1",
        "X-RapidAPI-Host": "facebook-reel-and-video-downloader.p.rapidapi.com",
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    result = response.json()["links"]["Download High Quality"]
    await message.reply_video(result)
    await msg.delete()


@pbot.on_message(filters.regex(tiktokregex) & filters.incoming & filters.private)
async def tiktokdown(_, message):
    link = message.text
    msg = await message.reply_text("Processing...")
    url = "https://tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com/index"
    querystring = {"url": link}
    headers = {
        "X-RapidAPI-Key": "22a34ac86fmsh648c15a7abb6555p1cb539jsn4b193ae50c9f",
        "X-RapidAPI-Host": "tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com",
    }

    response = requests.request("GET", url, headers=headers, params=querystring).json()
    video = f"{response['video'][0]}"
    music = f"{response ['music'][0]}"
    buttons = InlineKeyboardMarkup([[Keyboard(text="🎧 Audio", url=music)]])
    wget.download(video, "tiktok.mp4")
    cover = f"{response['cover'][0]}"
    wget.download(cover, "cover.jpg")
    await msg.delete()
    await message.reply_video(
        video="tiktok.mp4",
        caption="For Music Click Below Button",
        reply_markup=buttons,
        thumb="cover.jpg",
    )
    os.remove("tiktok.mp4")
    os.remove("cover.jpg")


@pbot.on_message(filters.regex(snapregex) & filters.incoming & filters.private)
async def snapdown(_, message):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    }
    base_url = "https://story.snapchat.com/@"
    username = message.text.split("/")[4].split("?")[0]
    S = base_url + username
    x = requests.get(S, headers=headers)
    soup = BeautifulSoup(x.content, "html.parser")
    snaps = soup.find(id="__NEXT_DATA__").string.strip()
    data = json.loads(snaps)
    try:
        for i in data["props"]["pageProps"]["story"]["snapList"]:
            post = i["snapUrls"]["mediaUrl"]
        await message.reply_document(post, caption="By: @MerissaRobot")
    except KeyError:
        await message.reply_text(
            text="No Public Stories for past 24Hrs\n\n❌ OR INVALID USERNAME", quote=True
        )


__help__ = """
@MerissaRobot Share Anything Download Anything

For Movie/Anime:
 ❍ /moviedl <movie name> : To Download Movie/Series from MkvCinemas.
 ❍ /animedl <anime name> : To Download Anime Movie/Series from MkvCinemas.
Note- You get Download links of Movie/Series If Available on MkvCinemas Database.

For YouTube:
 ❍ [/ytdl,/song,/music] <query> : To download song and video From Youtube
 ❍ `@MerissaRobot yt query` : For search link of Youtube Videos in MerissaRobot.
 ❍ Otherwise Send direct link of YouTube Video or Shorts For download Song or Video

For Instagram:
 ❍ Send direct link of Story, Reels, Post, IGTV Videos from Instagram to Download Video.

For Tiktok:
 ❍ Send direct link of any Tiktok Video from Tiktok to Download Video.

For Snapchat Stories:
 ❍ Send direct link of any Snapchat Users Profile Link from Snapchat to Download All Stories.

For Pinterest:
 ❍ Send direct link of Pinterest Video. Photo link will be Not Supported.

For Merissa-Hub(PHub):
 ❍ Send direct link of Phub Video from Phub website to Download Video.
 ❍ `@MerissaRobot ph query` : For search link of PHub Videos in MerissaRobot.
"""

__mod_name__ = "Downloaders 📥"

__helpbtns__ = [
    [
        InlineKeyboardButton("Youtube", switch_inline_query_current_chat="ytdl"),
        InlineKeyboardButton("🔙 Back", callback_data="help_back"),
    ]
]
