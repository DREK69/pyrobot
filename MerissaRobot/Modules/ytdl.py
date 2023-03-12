import os

import lyricsgenius as lg
import requests
import yt_dlp
from pykeyboard import InlineKeyboard
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaPhoto,
    InputMediaVideo,
)
from pytube import YouTube

from MerissaRobot import pbot as Client
from MerissaRobot.Utils.http import http

ytregex = r"^((?:https?:)?\/\/)?((?:www|m|music)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"


@Client.on_message(filters.regex(ytregex) & filters.private)
async def song(client, message):
    m = await message.reply_text("🔄 Processing Query... Please Wait!")
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    link = message.text
    yt = YouTube(link)
    videoid = yt.video_id
    title = yt.title
    dur = yt.length
    thumbnail = await get_ytthumb(videoid)
    await m.delete()
    await message.reply_photo(
        thumbnail,
        caption=f"**Title**: {title}\n**Duration**: {dur} seconds\n\n**Select Your Preferred Format from Below**:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 Audio",
                        callback_data=f"audio {videoid}",
                    ),
                    InlineKeyboardButton("🎥 Video", callback_data=f"formats {videoid}"),
                ],
                [
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )


@Client.on_message(filters.command(["music", "ytdl", "song", "video"]))
async def song(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Give me some text to search on Youtube")
    m = await message.reply_text("🔄 Processing Query... Please Wait!")
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)
    print(query)
    search = requests.get(
        f"https://api.princexd.tech/ytsearch?query={query}&limit=50"
    ).json()
    yt = search["result"][0]
    title = yt["title"]
    dur = yt["duration"]
    videoid = yt["id"]
    link = f"https://m.youtube.com/watch?v={videoid}"
    thumbnail = await get_ytthumb(videoid)
    await m.delete()
    await message.reply_photo(
        thumbnail,
        caption=f"**Title**: {title}\n**Duration**: {dur}\n**Track** = 1 out of {len(search['result'])}\n\n**Select Your Track from Below and Download It**:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Next Track ➡", callback_data=f"next|{query}|1"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "📥 Download",
                        callback_data=f"ytdown {videoid}",
                    ),
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )


@Client.on_callback_query(filters.regex(pattern=r"next"))
async def callback_query(Client, CallbackQuery):
    callback = CallbackQuery.data.split("|")
    query = callback[1]
    page = int(callback[2])
    search = requests.get(
        f"https://api.princexd.tech/ytsearch?query={query}&limit=50"
    ).json()
    yt = search["result"][page]
    title = yt["title"]
    dur = yt["duration"]
    videoid = yt["id"]
    link = f"https://m.youtube.com/watch?v={videoid}"
    thumbnail = await get_ytthumb(videoid)
    await CallbackQuery.edit_message_media(
        InputMediaPhoto(
            thumbnail,
            caption=f"**Title**: {title}\n**Duration**: {dur}\n**Track** = {page+1} out of {len(search['result'])}\n\n**Select your track from Below and Download It**:",
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⬅️", callback_data=f"next|{query}|{page-1}"),
                    InlineKeyboardButton("➡", callback_data=f"next|{query}|{page+1}"),
                ],
                [
                    InlineKeyboardButton(
                        "📥 Download",
                        callback_data=f"ytdown {videoid}",
                    ),
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )


@Client.on_callback_query(filters.regex(pattern=r"ytdown"))
async def callback_query(Client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 Audio",
                        callback_data=f"audio {videoid}",
                    ),
                    InlineKeyboardButton("🎥 Video", callback_data=f"formats {videoid}"),
                ],
                [
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )


@Client.on_callback_query(filters.regex(pattern=r"formats"))
async def callback_query(Client, CallbackQuery):
    await CallbackQuery.answer("Getting Formats..\n\nPlease Wait..", show_alert=True)
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    link = f"https://m.youtube.com/watch?v={videoid}"
    ytdl_opts = {"quiet": True}
    ydl = yt_dlp.YoutubeDL(ytdl_opts)
    with ydl:
        formats_available = []
        r = ydl.extract_info(link, download=False)
        for format in r["formats"]:
            try:
                str(format["format"])
            except:
                continue
            if not "dash" in str(format["format"]).lower():
                try:
                    format["format"]
                    format["filesize"]
                    format["format_id"]
                    format["ext"]
                    format["format_note"]
                except:
                    continue
                formats_available.append(
                    {
                        "format": format["format"],
                        "filesize": format["filesize"],
                        "format_id": format["format_id"],
                        "ext": format["ext"],
                        "format_note": format["format_note"],
                        "yturl": link,
                    }
                )
    keyboard = InlineKeyboard()
    done = [160, 133, 134, 135, 136, 137, 298, 299, 264, 304, 266]
    for x in formats_available:
        check = x["format"]
        if x["filesize"] is None:
            continue
        if int(x["format_id"]) not in done:
            continue
        to = check.split("-")[1]
        keyboard.row(
            InlineKeyboardButton(
                text=to,
                callback_data=f"video {x['format_id']}|{videoid}",
            )
        )
    keyboard.row(
        InlineKeyboardButton(
            text="🔙 Back",
            callback_data=f"ytdown {videoid}",
        ),
        InlineKeyboardButton(text="🗑️ Close", callback_data=f"cb_close"),
    )
    await CallbackQuery.edit_message_reply_markup(reply_markup=keyboard)


@Client.on_callback_query(filters.regex(pattern=r"audio"))
async def callback_query(Client, CallbackQuery):
    chatid = CallbackQuery.message.chat.id
    m = await CallbackQuery.edit_message_text(
        "Downloading Started\n\nDownload Speed could be slow. Please hold on.."
    )
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    link = f"https://m.youtube.com/watch?v={videoid}"
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        audio_file = ydl.prepare_filename(info_dict)
        ydl.process_info(info_dict)
    thumb = await CallbackQuery.message.download()
    med = InputMediaAudio(
        audio_file,
        caption=str(info_dict["title"]),
        thumb=thumb,
        title=str(info_dict["title"]),
        performer=f"{info_dict['channel']}",
        duration=int(info_dict["duration"]),
    )
    try:
        await m.edit(
            "Uploading Started\n\nUpload Speed could be slow. Please hold on.."
        )
        await Client.send_chat_action(chatid, ChatAction.UPLOAD_AUDIO)
        await CallbackQuery.edit_message_media(media=med)
    except Exception as error:
        await CallbackQuery.edit_message_text(f"Something happened!\n<i>{error}</i>")
    os.remove(thumb)
    os.remove(audio_file)


@Client.on_callback_query(filters.regex(pattern=r"video"))
async def callback_query(Client, CallbackQuery):
    chatid = CallbackQuery.message.chat.id
    m = await CallbackQuery.edit_message_text(
        "Downloading Started\n\nDownload Speed could be slow. Please hold on.."
    )
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    format_id, videoid = callback_request.split("|")
    link = f"https://m.youtube.com/watch?v={videoid}"
    formats = f"{format_id}+140"
    fpath = f"downloads/{videoid}"
    ydl_optssx = {
        "format": formats,
        "outtmpl": fpath,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "prefer_ffmpeg": True,
        "merge_output_format": "mp4",
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ytdl:
            info_dict = ytdl.extract_info(link, download=True)
    except Exception as e:
        await m.edit(f"**ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ.** \n**ᴇʀʀᴏʀ :** `{str(e)}`")
        return
    download_720 = f"{info_dict['id']}.mp4"
    thumb = await CallbackQuery.message.download()
    width = CallbackQuery.message.photo.width
    height = CallbackQuery.message.photo.height
    med = InputMediaVideo(
        media=download_720,
        width=width,
        height=height,
        caption=str(info_dict["title"]),
        thumb=thumb,
        supports_streaming=True,
    )
    try:
        await m.edit(
            "Uploading Started\n\nUpload Speed could be slow. Please hold on.."
        )
        await Client.send_chat_action(chatid, ChatAction.UPLOAD_VIDEO)
        await CallbackQuery.edit_message_media(media=med)
    except Exception as error:
        await CallbackQuery.edit_message_text(f"Error occurred!!\n<i>{error}</i>")
    os.remove(thumb)
    os.remove(download_720)


@Client.on_message(filters.command("lyrics"))
async def lyrics(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some text to find lyrics\n\nEx. /lyrics songname"
        )
    query = message.text.split(None, 1)
    api_key = "3w1IXc4ipZ2D7Ef3g2dogPVXnr2VBeUhBqzn5Vr6D_wQVzFFsHRDo_ycV7f8hYwT"
    y = lg.Genius(
        api_key,
        skip_non_songs=True,
        excluded_terms=["(Remix)", "(Live)"],
        remove_section_headers=True,
    )
    y.verbose = False
    lyrics = y.search_song(query, get_full_info=False).lyrics
    await message.reply_text(lyrics)


async def get_ytthumb(videoid: str):
    thumb_quality = [
        "hq720.jpg",  # Best quality
        "hqdefault.jpg",
        "sddefault.jpg",
        "mqdefault.jpg",
        "default.jpg",  # Worst quality
    ]
    thumb_link = "https://i.imgur.com/4LwPLai.png"
    for qualiy in thumb_quality:
        link = f"https://i.ytimg.com/vi/{videoid}/{qualiy}"
        if (await http.get(link)).status_code == 200:
            thumb_link = link
            break
    return thumb_link
