import asyncio
import os

import yt_dlp
from mutagen.mp4 import MP4
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
from youtubesearchpython import VideosSearch

from MerissaRobot import pbot as Client
from MerissaRobot.helpers import embed_album_art, get_ytthumb, getreq, subscribe

ytregex = r"^((?:https?:)?\/\/)?((?:www|m|music)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"


def convert_bytes(size: float) -> str:
    """humanize size"""
    if not size:
        return ""
    power = 1024
    t_n = 0
    power_dict = {0: " ", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size > power:
        size /= power
        t_n += 1
    return "{:.2f} {}B".format(size, power_dict[t_n])


async def run_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


async def convertmin(duration):
    seconds = int(duration)
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    result = f"{minutes} min {remaining_seconds} sec"
    return result


@Client.on_message(filters.regex(ytregex) & filters.incoming & filters.private)
@subscribe
async def ytregex(client, message):
    m = await message.reply_text("🔄 Processing Query... Please Wait!")
    link = message.text
    if "music" in link:
        resp = await getreq(f"https://api.princexd.tech/ytmsearch?query={link}")
        yt = resp["results"]["videoDetails"]
        videoid = yt["videoId"]
        title = yt["title"]
        duration = yt["lengthSeconds"]
        thumb = yt["thumbnail"]["thumbnails"][0]["url"]
        thumbnail = thumb.replace("60-", "500-")
        dur = await convertmin(duration)
        await message.reply_photo(
            thumbnail,
            caption=f"**Title**: {title}\n**Duration**: {dur}\n\n**Select Your Preferred Format from Below**:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"audio {videoid}",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ]
                ]
            ),
        )
        await m.delete()
    else:
        yt = await getreq(f"https://api.princexd.tech/ytinfo?link={link}")
        videoid = yt["id"]
        title = yt["title"]
        duration = yt["duration"]
        dur = await convertmin(duration)
        thumbnail = await get_ytthumb(videoid)
        await message.reply_photo(
            thumbnail,
            caption=f"**Title**: {title}\n**Duration**: {dur}\n\n**Select Your Preferred Format from Below**:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔊 Audio",
                            callback_data=f"audio {videoid}",
                        ),
                        InlineKeyboardButton(
                            "🎥 Video", callback_data=f"formats {videoid}"
                        ),
                    ],
                    [
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
        await m.delete()


@Client.on_message(filters.command(["ytdl", "video"]))
@subscribe
async def video(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Give me some text to search on Youtube")
    m = await message.reply_text("🔄 Processing Query... Please Wait!")
    query = message.text.split(None, 1)[1]
    search = VideosSearch(query, 20).result()
    yt = search["result"][0]
    title = yt["title"]
    dur = yt["duration"]
    videoid = yt["id"]
    link = f"https://m.youtube.com/watch?v={videoid}"
    thumbnail = await get_ytthumb(videoid)
    await message.reply_photo(
        thumbnail,
        caption=f"**Title**: [{title}]({link})\n**Duration**: {dur}\n**Results** = 1 out of {len(search['result'])}\n\n**Select Your Track from Below and Download It**:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Next Track ➡", callback_data=f"ytnext|{query}|1"
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
    await m.delete()


@Client.on_message(filters.command(["music", "ytmusic", "song"]))
@subscribe
async def song(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Give me some text to search on Youtube")
    m = await message.reply_text("🔄 Processing Query... Please Wait!")
    query = message.text.split(None, 1)[1]
    search = await getreq(f"https://api.princexd.tech/ytmsearch?query={query}")
    yt = search["results"][0]
    title = yt["title"]
    dur = yt["duration"]
    videoid = yt["videoId"]
    link = f"https://music.youtube.com/watch?v={yt['videoId']}&feature=share"
    thumb_url = yt["thumbnails"][0]["url"]
    thumbnail = thumb_url.replace("60-", "500-")
    await message.reply_photo(
        thumbnail,
        caption=f"**Title**: [{title}]({link})\n**Duration**: {dur}\n**Track** = 1 out of {len(search['results'])}\n\n**Click Below Button to Download**:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Next Track ➡", callback_data=f"ymnext|{query}|1"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "📥 Download",
                        callback_data=f"audio {videoid}",
                    ),
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )
    await m.delete()


@Client.on_callback_query(filters.regex("^ymnext"))
async def ymnext_query(client, callbackquery):
    callback_data = callbackquery.data.strip()
    callback = callback_data.split("|")
    query = callback[1]
    page = int(callback[2])
    search = await getreq(f"https://api.princexd.tech/ytmsearch?query={query}")
    yt = search["results"][page]
    title = yt["title"]
    dur = yt["duration"]
    videoid = yt["videoId"]
    link = f"https://music.youtube.com/watch?v={yt['videoId']}&feature=share"
    tpage = len(search["results"]) - 1
    thumb_url = yt["thumbnails"][0]["url"]
    thumbnail = thumb_url.replace("60-", "500-")
    if page == 0:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                thumbnail,
                caption=f"**Title**: [{title}]({link})\n**Duration**: {dur}\n**Results** = {page+1} out of {len(search['results'])}\n\n**Select your track from Below and Download It**:",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Next Track ➡", callback_data=f"ymnext|{query}|1"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"audio {videoid}",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
    elif page == tpage:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                thumbnail,
                caption=f"**Title**: [{title}]({link})\n**Duration**: {dur}\n**Results** = {page+1} out of {len(search['results'])}\n\n**Select your track from Below and Download It**:",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Prev Track", callback_data=f"ymnext|{query}|{page-1}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"audio {videoid}",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
    else:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                thumbnail,
                caption=f"**Title**: [{title}]({link})\n**Duration**: {dur}\n**Results** = {page+1} out of {len(search['results'])}\n\n**Select your track from Below and Download It**:",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️", callback_data=f"ymnext|{query}|{page-1}"
                        ),
                        InlineKeyboardButton(
                            "➡", callback_data=f"ymnext|{query}|{page+1}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"audio {videoid}",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )


@Client.on_callback_query(filters.regex("^ytnext"))
async def ytnext_query(client, callbackquery):
    callback_data = callbackquery.data.strip()
    callback = callback_data.split("|")
    query = callback[1]
    page = int(callback[2])
    search = VideosSearch(query, 20).result()
    yt = search["result"][page]
    title = yt["title"]
    dur = yt["duration"]
    videoid = yt["id"]
    link = f"https://m.youtube.com/watch?v={videoid}"
    tpage = len(search["result"]) - 1
    thumbnail = await get_ytthumb(videoid)
    if page == 0:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                thumbnail,
                caption=f"**Title**: [{title}]({link})\n**Duration**: {dur}\n**Results** = {page+1} out of {len(search['result'])}\n\n**Select your track from Below and Download It**:",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Next Track ➡", callback_data=f"ytnext|{query}|1"
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
    elif page == tpage:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                thumbnail,
                caption=f"**Title**: [{title}]({link})\n**Duration**: {dur}\n**Results** = {page+1} out of {len(search['result'])}\n\n**Select your track from Below and Download It**:",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Prev Track", callback_data=f"ytnext|{query}|{page-1}"
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
    else:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                thumbnail,
                caption=f"**Title**: [{title}]({link})\n**Duration**: {dur}\n**Results** = {page+1} out of {len(search['result'])}\n\n**Select your track from Below and Download It**:",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️", callback_data=f"ytnext|{query}|{page-1}"
                        ),
                        InlineKeyboardButton(
                            "➡", callback_data=f"ytnext|{query}|{page+1}"
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


@Client.on_callback_query(filters.regex("^ytdown"))
async def ytdown_query(client, callbackquery):
    callback_data = callbackquery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    await callbackquery.edit_message_reply_markup(
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


@Client.on_callback_query(filters.regex("^formats"))
async def formats_query(client, callbackquery):
    await callbackquery.answer("Getting Formats..\n\nPlease Wait..", show_alert=True)
    callback_data = callbackquery.data.strip()
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
        sz = convert_bytes(x["filesize"])
        ap = check.split("-")[1]
        to = f"{ap} = {sz}"
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
    await callbackquery.edit_message_reply_markup(reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^audio"))
async def audio_query(client, callbackquery):
    chatid = callbackquery.message.chat.id
    await callbackquery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Downloading...", callback_data="_DOWNLOADING"
                    )
                ]
            ]
        )
    )
    callback_data = callbackquery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    link = f"https://m.youtube.com/watch?v={videoid}"
    opts = {"format": "bestaudio[ext=m4a]", "outtmpl": "%(id)s.%(ext)s"}
    with yt_dlp.YoutubeDL(opts) as ydl:
        await run_async(ydl.download, [link])
        info_dict = ydl.extract_info(link, download=False)
    title = info_dict["title"]
    try:
        album = info_dict["album"]
    except:
        album = title
    resp = await getreq(f"https://api.princexd.tech/ytmsearch?query={link}")
    artist = resp["results"]["videoDetails"]["author"]
    thumb = await callbackquery.message.download()
    audio_file = f"{videoid}.m4a"
    audio = MP4(audio_file)
    audio["\xa9nam"] = title
    audio["\xa9alb"] = album
    audio["\xa9ART"] = artist
    audio.save()
    embed_album_art(thumb, audio_file)
    query = f"{info_dict['title']}-{artist}"
    med = InputMediaAudio(
        audio_file,
        caption=query,
        thumb=thumb,
        title=str(info_dict["title"]),
        performer=artist,
        duration=int(info_dict["duration"]),
    )
    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="🎵 Lyrics", callback_data="lyrics")]]
    )
    try:
        await callbackquery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Uploading...", callback_data="_UPLOADING"
                        )
                    ]
                ]
            )
        )
        await client.send_chat_action(chatid, ChatAction.UPLOAD_AUDIO)
        await callbackquery.edit_message_media(media=med, reply_markup=button)
    except Exception as error:
        await callbackquery.edit_message_text(f"Something happened!\n<i>{error}</i>")
    os.remove(thumb)
    os.remove(audio_file)


@Client.on_callback_query(filters.regex("^video"))
async def video_query(client, callbackquery):
    chatid = callbackquery.message.chat.id
    await callbackquery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Downloading...", callback_data="_DOWNLOADING"
                    )
                ]
            ]
        )
    )
    callback_data = callbackquery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    format_id, videoid = callback_request.split("|")
    link = f"https://m.youtube.com/watch?v={videoid}"
    formats = f"{format_id}+140"
    opts = {
        "format": formats,
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        await run_async(ydl.download, [link])
        info_dict = ydl.extract_info(link, download=False)
    download_720 = f"{info_dict['id']}.mp4"
    thumb = await callbackquery.message.download()
    width = callbackquery.message.photo.width
    height = callbackquery.message.photo.height
    med = InputMediaVideo(
        media=download_720,
        width=width,
        height=height,
        caption=str(info_dict["title"]),
        thumb=thumb,
        supports_streaming=True,
    )
    try:
        await callbackquery.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Uploading...", callback_data="_UPLOADING"
                        )
                    ]
                ]
            )
        )
        await client.send_chat_action(chatid, ChatAction.UPLOAD_VIDEO)
        await callbackquery.edit_message_media(media=med)
    except Exception as error:
        await callbackquery.edit_message_text(f"Error occurred!!\n<i>{error}</i>")
    os.remove(thumb)
    os.remove(download_720)


@Client.on_message(filters.command("lyrics"))
async def lyrics(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some text to find lyrics\n\nEx. /lyrics songname"
        )
    title = message.text.split(None, 1)[1]
    try:
        resp = await getreq(f"https://api.princexd.tech/lyrics/text?query={title}")
        lyrics = resp["lyrics"]
        await message.reply_text(lyrics)
    except:
        await message.reply_text("Lyrics Not Found")


@Client.on_callback_query(filters.regex("^lyrics"))
async def lyrics_cb(bot, query):
    qur = query.message.caption
    q = qur.replace("- ", "")
    if "," in q:
        q.split(",")[0]
    else:
        pass
    await query.answer("Getting lyrics...", show_alert=True)
    lyr = await getreq(f"https://editor-choice-api.vercel.app/lyrics?query={q}")
    if not lyr["error"]:
        link = lyr["url"]
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Listen with lyrics", url=link),
                ]
            ]
        )
        await query.edit_message_reply_markup(button)
    else:
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Sorry, Not Found.", callback_data="_LYR_NOT_FOUND"
                    )
                ]
            ]
        )
        await query.edit_message_reply_markup(button)
