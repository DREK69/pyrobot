import json
import os
import random
from uuid import uuid4

import pyrogram
import requests
from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.types import ChatJoinRequest
from pyrogram.types import InlineKeyboardButton as Keyboard
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from telegram import InlineKeyboardButton

from MerissaRobot import FORCE_CHANNEL, pbot
from MerissaRobot.helpers import getreq, save_file, subscribe

instaregex = r"^https:\/\/(instagram\.com|www\.instagram\.com)\/(p|tv|reel|stories)\/([A-Za-z0-9\-_]*)"
tiktokregex = r"^https:\/\/(www\.tiktok.com|vm\.tiktok\.com|vt\.tiktok\.com)\/?(.*)"
snapregex = r"^https:\/\/www\.snapchat\.com\/add"
fbregex = r"^https:\/\/www\.facebook\.com\/reel\/"
pinregex = r"^https:\/\/(pin\.it|www\.pinterest\.com|pinterest\.com|in\.pinterest\.com)"


apikey = [
    "22a34ac86fmsh648c15a7abb6555p1cb539jsn4b193ae50c9f",
    "81b89ef962msh19a67d63d479365p122483jsn6af26adfd7a5",
]


@pbot.on_message(filters.command("premium") & filters.private)
async def premium(client, message):
    user_id = message.from_user.id
    try:
        member = await client.get_chat_member(chat_id=FORCE_CHANNEL, user_id=user_id)
        await message.reply_text(
            "You are already join our @MerissaxUpdates Channel, So you are Premium User in MerissaRobot"
        )
    except UserNotParticipant:
        await message.reply_photo(
            photo="https://te.legra.ph/file/2b3a7af1d01513c032739.jpg",
            caption="Join our Telegram Update Channel @MerissaxUpdates to Get Premium for free in MerissaRobot",
        )


@pbot.on_message(filters.regex(instaregex) & filters.incoming & filters.private)
@subscribe
async def instadown(client, message):
    message.from_user.id
    link = message.text
    msg = await message.reply_text("Processing...")
    if "reel" in link:
        try:
            dlink = link.replace("www.instagram.com", "ddinstagram.com")
            await message.reply_video(dlink)
            await msg.delete()
        except:
            try:
                data = await getreq(
                    f"https://igdownloader.onrender.com/dl?key=ashok&url={link}"
                )
                dlink = data["urls"][0]
                await message.reply_video(dlink, caption=data["caption"])
                await msg.delete()
            except:
                try:
                    response = await getreq(
                        f"https://wild-elnore-prince-xd.koyeb.app/instadown?link={link}"
                    )
                    video = response["media"][0]
                    try:
                        await message.reply_video(
                            video, caption="Downloaded By @MerissaRobot"
                        )
                        await msg.delete()
                    except:
                        x = await save_file(response, "video.mp4")
                        await message.reply_video(
                            x, caption="Uploaded By @MerissaRobot"
                        )
                        await msg.delete()
                        os.remove(x)
                except:
                    try:
                        key = random.choice(apikey)
                        resp = await getreq(
                            f"https://wild-elnore-prince-xd.koyeb.app/igdown?apikey={key}&link={link}"
                        )
                        video = resp["links"][0]["url"]
                        try:
                            await message.reply_video(video)
                            await msg.delete()
                        except:
                            x = await save_file(video, "video.mp4")
                            await message.reply_video(
                                x, caption="Downloaded By @MerissaRobot"
                            )
                            await msg.delete()
                            os.remove(x)
                    except:
                        await msg.edit_text(
                            "Something went Wrong Contact @MerissaxSupport"
                        )
    else:
        try:
            data = await getreq(
                f"https://igdownloader.onrender.com/dl?key=ashok&url={link}"
            )
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
                        mg.append(InputMediaVideo(post))
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
                resp = await getreq(
                    f"https://wild-elnore-prince-xd.koyeb.app//instadown?link={link}"
                )
                post = resp["media"]
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
                            mg.append(InputMediaPhoto(post))
                        else:
                            mg.append(
                                InputMediaVideo(
                                    post, caption="Uploaded By @MerissaRobot"
                                )
                            )
                    await message.reply_media_group(mg)
                await msg.delete()
            except:
                key = random.choice(apikey)
                resp = await getreq(
                    f"https://wild-elnore-prince-xd.koyeb.app/igdown?apikey={key}&link={link}"
                )
                posts = resp["links"]
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
                            mg.append(InputMediaVideo(post["url"]))
                        else:
                            mg.append(
                                InputMediaPhoto(
                                    post["url"], caption=f"Downloaded By @MerissaRobot"
                                )
                            )
                    await message.reply_media_group(mg)
                await msg.delete()


@pbot.on_message(filters.regex(pinregex))
@subscribe
async def pindown(client, message):
    message.from_user.id
    link = message.text
    m = await message.reply_text("Processing...")
    pin = getreq(f"https://api.princexd.tech/pin?link={link}")
    pinvid = pin["media"]
    title = pin["title"]
    await message.reply_document(
        pinvid, caption=f"{title}\n\nUploaded by @MerissaRobot"
    )
    await m.delete()


@pbot.on_message(filters.regex(fbregex) & filters.incoming & filters.private)
@subscribe
async def fbdown(client, message):
    message.from_user.id
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
@subscribe
async def tiktokdown(client, message):
    message.from_user.id
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
    await save_file(video, "tiktok.mp4")
    cover = f"{response['cover'][0]}"
    await save_file(cover, "cover.jpg")
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
@subscribe
async def snapdown(client, message):
    message.from_user.id
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


@pbot.on_chat_join_request(filters.channel)
async def autoapprovec(client, message: ChatJoinRequest):
    chat = message.chat
    user = message.from_user
    button = [
        [
            Keyboard(text="VERIFY", callback_data=f"verify {chat.id}"),
        ]
    ]
    await client.send_photo(
        chat_id=user.id,
        photo="https://te.legra.ph/file/90b1aa10cf8b77d5b781b.jpg",
        caption=f"{chat.title} is being protected by @MerissaRobot\n\nClick below to verify you're human",
        reply_markup=InlineKeyboardMarkup(button),
    )


@pbot.on_chat_join_request(filters.group)
async def autoapproveg(client, message: ChatJoinRequest):
    user = message.from_user
    chat = message.chat
    keyboard = InlineKeyboardMarkup(
        [
            [
                Keyboard("✅ Approve", callback_data="cb_approve={}".format(user.id)),
                Keyboard("❌ Decline", callback_data="cb_decline={}".format(user.id)),
            ]
        ]
    )
    await client.send_message(
        chat.id,
        "{} wants to join {}".format(user.first_name, chat.title),
        reply_markup=keyboard,
    )


@pbot.on_message(filters.command("packkang"))
@subscribe
async def _packkang(app: pbot, message):
    txt = await message.reply_text("**Processing....**")
    if not message.reply_to_message:
        await txt.edit("Reply to Sticker")
        return
    if not message.reply_to_message.sticker:
        await txt.edit("Reply to Sticker")
        return
    if (
        message.reply_to_message.sticker.is_animated
        or message.reply_to_message.sticker.is_video
    ):
        return await txt.edit("reply to non animated sticker")
    if len(message.command) < 2:
        pack_name = f"{message.from_user.first_name} :: @MerissaRobot"
    else:
        pack_name = message.text.split(maxsplit=1)[1] + " :: @MerissaRobot"
    short_name = message.reply_to_message.sticker.set_name
    stickers = await app.invoke(
        pyrogram.raw.functions.messages.GetStickerSet(
            stickerset=pyrogram.raw.types.InputStickerSetShortName(
                short_name=short_name
            ),
            hash=0,
        )
    )
    shits = stickers.documents
    sticks = []
    for i in shits:
        sex = pyrogram.raw.types.InputDocument(
            id=i.id, access_hash=i.access_hash, file_reference=i.thumbs[0].bytes
        )

        sticks.append(
            pyrogram.raw.types.InputStickerSetItem(
                document=sex, emoji=i.attributes[1].alt
            )
        )
    try:
        short_name = f'stikcer_pack_{str(uuid4()).replace("-","")}_by_{app.me.username}'
        user_id = await app.resolve_peer(message.from_user.id)
        await app.invoke(
            pyrogram.raw.functions.stickers.CreateStickerSet(
                user_id=user_id,
                title=pack_name,
                short_name=short_name,
                stickers=sticks,
            )
        )
        await txt.edit(
            f"**Here is Your Kanged Link**!\n**Total Stickers**: {len(sticks)}",
            reply_markup=InlineKeyboardMarkup(
                [[Keyboard("Pack Link", url=f"http://t.me/addstickers/{short_name}")]]
            ),
        )
    except Exception as e:
        await message.reply(str(e))


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
