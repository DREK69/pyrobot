import asyncio
import html
import os
import socket
from html import escape
from re import sub as re_sub
from time import ctime, time

import aiohttp
import requests
import yt_dlp
from bs4 import BeautifulSoup
from fuzzysearch import find_near_matches
from mutagen.mp4 import MP4
from pornhub_api import PornhubApi
from pornhub_api.backends.aiohttp import AioHttpBackend
from pykeyboard import InlineKeyboard
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.raw.functions import Ping
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputMediaAudio,
    InputMediaVideo,
    InputTextMessageContent,
)
from youtubesearchpython import VideosSearch

from MerissaRobot import DEV_USERS, EVENT_LOGS
from MerissaRobot import pbot as app
from MerissaRobot.helpers import embed_album_art, get_ytthumb, getreq, save_file
from MerissaRobot.Modules.info import get_chat_info, get_user_info
from MerissaRobot.Handler.pyro.pastebin import paste
from MerissaRobot.Handler.ptb.services.tasks import _get_tasks_text, all_tasks, rm_task
from MerissaRobot.Handler.ptb.services.types import InlineQueryResultCachedDocument

MESSAGE_DUMP_CHAT = EVENT_LOGS

arq = ""


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            try:
                data = await resp.json()
            except Exception:
                data = await resp.text()
    return data


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


keywords_list = [
    "alive",
    "image",
    "wall",
    "imdb",
    "lyrics",
    "github",
    "paste",
    "google",
    "torrent",
    "saavn",
    "ytdown",
    "ytlink",
    "ud",
    "ytmdown",
    "gh",
    "ytmlink",
]


async def _netcat(host, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    s.sendall(content.encode())
    s.shutdown(socket.SHUT_WR)
    while True:
        data = s.recv(4096).decode("utf-8").strip("\n\x00")
        if not data:
            break
        return data
    s.close()


async def paste(content):
    link = await _netcat("ezup.dev", 9999, content)
    return link


async def inline_help_func(answers):
    answerss = await about_function(answers)
    return answerss


async def vc_func(answers):
    answerss = [
        InlineQueryResultArticle(
            title="Pause Stream",
            description=f"Pause the current playout on group call.",
            thumb_url="https://telegra.ph/file/c0a1c789def7b93f13745.png",
            input_message_content=InputTextMessageContent("/pause"),
        ),
        InlineQueryResultArticle(
            title="Resume Stream",
            description=f"Resume the ongoing playout on group call.",
            thumb_url="https://telegra.ph/file/02d1b7f967ca11404455a.png",
            input_message_content=InputTextMessageContent("/resume"),
        ),
        InlineQueryResultArticle(
            title="Mute Stream",
            description=f"Mute the ongoing playout on group call.",
            thumb_url="https://telegra.ph/file/66516f2976cb6d87e20f9.png",
            input_message_content=InputTextMessageContent("/mute"),
        ),
        InlineQueryResultArticle(
            title="Unmute Stream",
            description=f"Unmute the ongoing playout on group call.",
            thumb_url="https://telegra.ph/file/3078794f9341ffd582e18.png",
            input_message_content=InputTextMessageContent("/unmute"),
        ),
        InlineQueryResultArticle(
            title="Skip Stream",
            description=f"Skip to next track. | For Specific track number: /skip [number] ",
            thumb_url="https://telegra.ph/file/98b88e52bc625903c7a2f.png",
            input_message_content=InputTextMessageContent("/skip"),
        ),
        InlineQueryResultArticle(
            title="End Stream",
            description="Stop the ongoing playout on group call.",
            thumb_url="https://telegra.ph/file/d2eb03211baaba8838cc4.png",
            input_message_content=InputTextMessageContent("/end"),
        ),
    ]
    return answerss


async def about_function(answers):
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Downloader",
                    callback_data="cbdownloader",
                ),
                InlineKeyboardButton(
                    text="Others",
                    callback_data="cbothers",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Updates",
                    url="https://t.me/MerissaxUpdates",
                ),
                InlineKeyboardButton(
                    text="Support",
                    url="https://t.me/MerissaxSupport",
                ),
            ],
        ]
    )
    msg = """
Merissa is a Telegram group managment bot made using Telethon and Pyrogram which makes it modern and faster than most of the exisitng Telegram Chat Managers.
"""
    answers.append(
        InlineQueryResultPhoto(
            photo_url="https://te.legra.ph/file/90b1aa10cf8b77d5b781b.jpg",
            title="About Merissa",
            description="To Know More About Merissa",
            caption=msg,
            thumb_url="https://te.legra.ph/file/867b6e75543fb2e4d25fc.jpg",
            reply_markup=buttons,
        ),
    )
    return answers


async def ytmdown_func(answers, text):
    results = requests.get(f"https://api.princexd.tech/ytmsearch?query={text}").json()[
        "results"
    ]
    for i in results:
        thumb = i["thumbnails"][0]["url"]
        thumbnail = thumb.replace("w60-h60", "w500-h500")
        description = (
            f"{i['title']} | {i['duration']} " + f"| {i['artists'][0]['name']}"
        )
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="📥 Download",
                        callback_data=f"inymaud {i['videoId']}",
                    ),
                    InlineKeyboardButton(
                        text="🗑️ Close",
                        callback_data="iclose",
                    ),
                ]
            ]
        )
        cap = f"**Title**: {i['title']}\n**Duration**: {i['duration']}\n\n**Click below button to Download Your Song:**"
        answers.append(
            InlineQueryResultPhoto(
                photo_url=thumbnail,
                title=i["title"],
                caption=cap,
                description=description,
                thumb_url=thumb,
                reply_markup=buttons,
            )
        )
    return answers


async def ytdown_func(answers, text):
    search = VideosSearch(text, limit=50)
    for result in search.result()["result"]:
        videoid = result["id"]
        thumbnail = result["thumbnails"][0]["url"]
        thumb = thumbnail.split("?")[0]
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 Audio",
                        callback_data=f"inytaud {videoid}",
                    ),
                    InlineKeyboardButton(
                        "🎥 Video", callback_data=f"informats {videoid}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🗑️ Close",
                        callback_data="iclose",
                    ),
                ],
            ]
        )
        cap = f"**Title**: {result['title']}\n**Duration**: {result['duration']}\n\n**Click below button to Download Your Song:**"
        answers.append(
            InlineQueryResultPhoto(
                photo_url=thumb,
                title=result["title"],
                description="{}, {} views.".format(
                    result["duration"], result["viewCount"]["short"]
                ),
                caption=cap,
                thumb_url=result["thumbnails"][0]["url"],
                reply_markup=buttons,
            )
        )
    return answers


@app.on_callback_query(filters.regex("cbdownloader"))
async def cbgames(_, cq):
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🎥 Youtube",
                    switch_inline_query_current_chat="ytdl",
                ),
                InlineKeyboardButton(
                    text="🎧 Saavn",
                    switch_inline_query_current_chat="saavn",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎵 Youtube Music",
                    switch_inline_query_current_chat="ymdl",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Back",
                    callback_data="cbback",
                ),
            ],
        ]
    )
    inline_message_id = cq.inline_message_id
    msg = """
Click Below Buttons To Search Videos.
"""
    await app.edit_inline_caption(inline_message_id, msg, reply_markup=buttons)


@app.on_callback_query(filters.regex("cbback"))
async def cbgames(_, cq):
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Downloader",
                    callback_data="cbdownloader",
                ),
                InlineKeyboardButton(
                    text="Others",
                    callback_data="cbothers",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Updates",
                    url="https://t.me/MerissaxUpdates",
                ),
                InlineKeyboardButton(
                    text="Support",
                    url="https://t.me/MerissaxSupport",
                ),
            ],
        ]
    )
    inline_message_id = cq.inline_message_id
    msg = """
Merissa is a Telegram group managment bot made using Telethon and Pyrogram which makes it modern and faster than most of the exisitng Telegram Chat Managers.
"""
    await app.edit_inline_caption(inline_message_id, msg, reply_markup=buttons)


@app.on_callback_query(filters.regex("informats"))
async def cbgames(_, cq):
    inline_message_id = cq.inline_message_id
    callback_data = cq.data.strip()
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
                callback_data=f"invideo {x['format_id']}|{videoid}",
            )
        )
    keyboard.row(
        InlineKeyboardButton(text="🗑️ Close", callback_data="inclose"),
    )
    await app.edit_inline_reply_markup(inline_message_id, reply_markup=keyboard)


@app.on_callback_query(filters.regex("invideo"))
async def cbgames(_, cq):
    inline_message_id = cq.inline_message_id
    callback_data = cq.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    format_id, videoid = callback_request.split("|")
    link = f"https://m.youtube.com/watch?v={videoid}"
    dbutton = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="📥 Downloading....", callback_data="agdjhdggd")]]
    )
    await app.edit_inline_reply_markup(inline_message_id, reply_markup=dbutton)
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
    try:
        with yt_dlp.YoutubeDL(opts) as ytdl:
            await run_async(ydl.download, [link])
            info_dict = ydl.extract_info(link, download=False)
    except Exception as e:
        await app.edit_inline_caption(
            inline_message_id, f"Failed to Download.** \n**Error :** `{str(e)}`"
        )
        return
    thumb = await get_ytthumb(info_dict["id"])
    thumbnail = await save_file(thumb, "thumb.jpg")
    download_720 = f"{info_dict['id']}.mp4"
    med = InputMediaVideo(
        media=download_720,
        thumb=thumbnail,
        caption=str(info_dict["title"]),
        supports_streaming=True,
    )
    ubutton = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="📤 Uploading....", callback_data="agdjhdggd")]]
    )
    await app.edit_inline_reply_markup(inline_message_id, reply_markup=ubutton)
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Search again", switch_inline_query_current_chat="ytdl"
                )
            ]
        ]
    )
    await app.edit_inline_media(inline_message_id, media=med, reply_markup=button)
    os.remove(download_720)
    os.remove(thumbnail)


@app.on_callback_query(filters.regex("inymaud"))
async def cbgames(_, cq):
    inline_message_id = cq.inline_message_id
    callback_data = cq.data.strip()
    videoid = callback_data.split(None, 1)[1]
    link = f"https://m.youtube.com/watch?v={videoid}"
    dbutton = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="📥 Downloading....", callback_data="agdjhdggd")]]
    )
    await app.edit_inline_reply_markup(inline_message_id, reply_markup=dbutton)
    ydl_opts = {"format": "bestaudio[ext=m4a]", "outtmpl": "%(id)s.%(ext)s"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        await run_async(ydl.download, [link])
        info_dict = ydl.extract_info(link, download=False)
    title = info_dict["title"]
    try:
        album = info_dict["album"]
    except:
        album = title
    yt = await getreq(f"https://api.princexd.tech/ytmsearch?query={link}").json()[
        "results"
    ]["videoDetails"]
    artist = yt["author"]
    thumb = info_dict["thumbnails"][0]["url"]
    thumb.replace("60-", "1080-")
    thumbnail = save_file(thumb, "thumbnail.png")
    audio_file = f"{videoid}.m4a"
    audio = MP4(audio_file)
    audio["\xa9nam"] = title
    audio["\xa9alb"] = album
    audio["\xa9ART"] = artist
    audio.save()
    embed_album_art(thumb, audio_file)
    med = InputMediaAudio(
        audio_file,
        caption=str(info_dict["title"]),
        thumb=thumbnail,
        title=str(info_dict["title"]),
        performer=yt["author"],
        duration=int(info_dict["duration"]),
    )
    ubutton = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="📤 Uploading....", callback_data="agdjhdggd")]]
    )
    await app.edit_inline_reply_markup(inline_message_id, reply_markup=ubutton)
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Search again", switch_inline_query_current_chat="ymdl"
                )
            ]
        ]
    )
    await app.edit_inline_media(inline_message_id, media=med, reply_markup=button)
    os.remove(audio_file)
    os.remove(thumbnail)


@app.on_callback_query(filters.regex("inytaud"))
async def cbgames(_, cq):
    inline_message_id = cq.inline_message_id
    callback_data = cq.data.strip()
    videoid = callback_data.split(None, 1)[1]
    link = f"https://m.youtube.com/watch?v={videoid}"
    dbutton = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="📥 Downloading....", callback_data="agdjhdggd")]]
    )
    await app.edit_inline_reply_markup(inline_message_id, reply_markup=dbutton)
    ydl_opts = {"format": "bestaudio[ext=m4a]", "outtmpl": "%(id)s.%(ext)s"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        await run_async(ydl.download, [link])
        info_dict = ydl.extract_info(link, download=False)
    title = info_dict["title"]
    try:
        album = info_dict["album"]
    except:
        album = title
    yt = await getreq(f"https://api.princexd.tech/ytmsearch?query={link}").json()[
        "results"
    ]["videoDetails"]
    artist = yt["author"]
    thumb = info_dict["thumbnails"][0]["url"]
    thumb.replace("60-", "1080-")
    thumbnail = save_file(thumb, "thumbnail.png")
    audio_file = f"{videoid}.m4a"
    audio = MP4(audio_file)
    audio["\xa9nam"] = title
    audio["\xa9alb"] = album
    audio["\xa9ART"] = artist
    audio.save()
    embed_album_art(thumb, audio_file)
    med = InputMediaAudio(
        audio_file,
        caption=str(info_dict["title"]),
        title=str(info_dict["title"]),
        duration=int(info_dict["duration"]),
    )
    ubutton = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="📤 Uploading....", callback_data="agdjhdggd")]]
    )
    await app.edit_inline_reply_markup(inline_message_id, reply_markup=ubutton)
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Search again", switch_inline_query_current_chat="ytdl"
                )
            ]
        ]
    )
    await app.edit_inline_media(inline_message_id, media=med, reply_markup=button)
    os.remove(audio_file)
    os.remove(thumbnail)


@app.on_callback_query(filters.regex("cbothers"))
async def cbothers(_, cq):
    buttons = InlineKeyboard(row_width=4)
    buttons.add(
        *[
            (InlineKeyboardButton(text=i, switch_inline_query_current_chat=i))
            for i in keywords_list
        ],
        *[(InlineKeyboardButton(text="🔙 Back", callback_data="cbback"))],
    )
    inline_message_id = cq.inline_message_id
    msg = """
Click Below Buttons to Search.
"""
    await app.edit_inline_caption(inline_message_id, msg, reply_markup=buttons)


async def translate_func(answers, lang, tex):
    result = await arq.translate(tex, lang)
    if not result.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=result.result,
                input_message_content=InputTextMessageContent(result.result),
            )
        )
        return answers
    result = result.result
    msg = f"""
__**Translated from {result.src} to {result.dest}**__
**INPUT:**
{tex}
**OUTPUT:**
{result.translatedText}"""
    answers.extend(
        [
            InlineQueryResultArticle(
                title=f"Translated from {result.src} to {result.dest}.",
                description=result.translatedText,
                input_message_content=InputTextMessageContent(msg),
            ),
            InlineQueryResultArticle(
                title=result.translatedText,
                input_message_content=InputTextMessageContent(result.translatedText),
            ),
        ]
    )
    return answers


async def urban_func(answers, text):
    results = await arq.urbandict(text)
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    results = results.result[0:48]
    for i in results:
        clean = lambda x: re_sub(r"[\[\]]", "", x)
        msg = f"""
**Query:** {text}
**Definition:** __{clean(i.definition)}__
**Example:** __{clean(i.example)}__"""

        answers.append(
            InlineQueryResultArticle(
                title=i.word,
                description=clean(i.definition),
                input_message_content=InputTextMessageContent(msg),
            )
        )
    return answers


async def google_search_func(answers, text):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edge/107.0.1418.42"
    }
    search_results = requests.get(
        f"https://www.google.com/search?q={text}&num=20", headers=headers
    )
    soup = BeautifulSoup(search_results.text, "lxml")
    for result in soup.select(".tF2Cxc"):
        link = result.select_one(".yuRUbf a")["href"]
        title = result.select_one(".DKV0Md").text
        try:
            snippet = result.select_one("#rso .lyLwlc").text
        except:
            snippet = "-"
        message_text = f"<a href='{link}'>{html.escape(title)}</a>\n"
        message_text += f"Description: {html.escape(snippet)}"
        answers.append(
            InlineQueryResultArticle(
                title=f"{title}",
                input_message_content=InputTextMessageContent(
                    message_text=message_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False,
                ),
                url=link,
                description=snippet,
                thumb_url="https://te.legra.ph/file/ed8ea62ae636793000bb4.jpg",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Open Website", url=link)]]
                ),
            )
        )
    return answers


async def spotify_func(answers, text):
    search = requests.get(f"https://api.princexd.tech/spsearch?query={text}").json()[
        "tracks"
    ]["items"]
    for result in search:
        answers.append(
            InlineQueryResultArticle(
                title=result["name"],
                description="{}".format(result["album"]["artists"][0]["name"]),
                input_message_content=InputTextMessageContent(
                    "{}".format(result["external_urls"]["spotify"]),
                    disable_web_page_preview=True,
                ),
                thumb_url=result["album"]["images"][0]["url"],
            )
        )
    return answers


async def wall_func(answers, text):
    results = await arq.wall(text)
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    results = results.result[0:48]
    for i in results:
        answers.append(
            InlineQueryResultPhoto(
                photo_url=i.url_image,
                thumb_url=i.url_thumb,
                caption=f"[Source]({i.url_image})",
            )
        )
    return answers


async def torrent_func(answers, text):
    results = await arq.torrent(text)
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    results = results.result[0:48]
    for i in results:
        title = i.name
        size = i.size
        seeds = i.seeds
        leechs = i.leechs
        upload_date = i.uploaded
        magnet = i.magnet
        caption = f"""
**Title:** __{title}__
**Size:** __{size}__
**Seeds:** __{seeds}__
**Leechs:** __{leechs}__
**Uploaded:** __{upload_date}__
**Magnet:** `{magnet}`"""

        description = f"{size} | {upload_date} | Seeds: {seeds}"
        answers.append(
            InlineQueryResultArticle(
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(
                    caption, disable_web_page_preview=True
                ),
            )
        )
    return answers


async def youtube_func(answers, text):
    search = VideosSearch(text, limit=50)
    for result in search.result()["result"]:
        answers.append(
            InlineQueryResultArticle(
                title=result["title"],
                description="{}, {} views.".format(
                    result["duration"], result["viewCount"]["short"]
                ),
                input_message_content=InputTextMessageContent(
                    "https://www.youtube.com/watch?v={}".format(result["id"]),
                    disable_web_page_preview=True,
                ),
                thumb_url=result["thumbnails"][0]["url"],
            )
        )
    return answers


async def anime_func(answers, text):
    return text


async def ph_func(answers, text):
    query = text
    backend = AioHttpBackend()
    api = PornhubApi(backend=backend)
    results = []
    try:
        src = await api.search.search(query)
    except ValueError:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    videos = src.videos
    await backend.close()
    for vid in videos:
        try:
            pornstars = ", ".join(v for v in vid.pornstars)
            categories = ", ".join(v for v in vid.categories)
            tags = ", #".join(v for v in vid.tags)
        except:
            pornstars = "N/A"
            categories = "N/A"
            tags = "N/A"
        capt = (
            f"Title: `{vid.title}`\n"
            f"Duration: `{vid.duration}`\n"
            f"Views: `{vid.views}`\n\n"
            f"**{pornstars}**\n"
            f"Category: {categories}\n\n"
            f"{tags}"
            f"Link: {vid.url}"
        )
        text = f"{vid.url}"
        answers.append(
            InlineQueryResultArticle(
                title=vid.title,
                input_message_content=InputTextMessageContent(
                    message_text=text,
                    disable_web_page_preview=True,
                ),
                description=f"Duration: {vid.duration}\nViews: {vid.views}\nRating: {vid.rating}",
                thumb_url=vid.thumb,
            ),
        )
    return answers


async def lyrics_func(answers, text):
    song = requests.get(f"https://api.princexd.tech/lyrics?query={text}").json()
    if song["error"] == True:
        answers.append(
            InlineQueryResultArticle(
                title="No Lyrics Found",
                description="404 Error | Please Enter Correct Song Name",
                input_message_content=InputTextMessageContent(
                    "404 error | Song Lyrics Not Found"
                ),
            )
        )
        return answers

    song_name = song["title"]
    artist = song["artist"]
    lyrics = song["lyrics"]
    thumb = song["thumb"]
    if len(lyrics) > 4095:
        lyrics = await paste(lyrics)
        lyrics = f"**LYRICS_TOO_LONG:** [URL]({lyrics})"

    answers.append(
        InlineQueryResultArticle(
            title=song_name,
            description=artist,
            input_message_content=InputTextMessageContent(lyrics),
            thumb_url=thumb,
        )
    )
    return answers


async def tg_search_func(answers, text, user_id):
    if user_id not in DEV_USERS:
        msg = "**ERROR**\n__THIS FEATURE IS ONLY FOR DEV USERS__"
        answers.append(
            InlineQueryResultArticle(
                title="ERROR",
                description="THIS FEATURE IS ONLY FOR SUDO USERS",
                input_message_content=InputTextMessageContent(msg),
            )
        )
        return answers
    if str(text)[-1] != ":":
        msg = "**ERROR**\n__Put A ':' After The Text To Search__"
        answers.append(
            InlineQueryResultArticle(
                title="ERROR",
                description="Put A ':' After The Text To Search",
                input_message_content=InputTextMessageContent(msg),
            )
        )

        return answers
    text = text[0:-1]
    async for message in ubot2.search_global(text, limit=49):
        buttons = InlineKeyboard(row_width=2)
        buttons.add(
            InlineKeyboardButton(
                text="Origin",
                url=message.link if message.link else "https://t.me/telegram",
            ),
            InlineKeyboardButton(
                text="Search again",
                switch_inline_query_current_chat="search",
            ),
        )
        name = (
            message.from_user.first_name if message.from_user.first_name else "NO NAME"
        )
        caption = f"""
**Query:** {text}
**Name:** {str(name)} [`{message.from_user.id}`]
**Chat:** {str(message.chat.title)} [`{message.chat.id}`]
**Date:** {ctime(message.date)}
**Text:** >>
{message.text.markdown if message.text else message.caption if message.caption else '[NO_TEXT]'}
"""
        result = InlineQueryResultArticle(
            title=name,
            description=message.text if message.text else "[NO_TEXT]",
            reply_markup=buttons,
            input_message_content=InputTextMessageContent(
                caption, disable_web_page_preview=True
            ),
        )
        answers.append(result)
    return answers


async def music_inline_func(answers, query):
    chat_id = -1002345689
    group_invite = "https://t.me/joinchat/vSDE2DuGK4Y4Nzll"
    try:
        messages = [
            m
            async for m in user.search_messages(
                chat_id, query, filter="audio", limit=100
            )
        ]
    except Exception as e:
        print(e)
        msg = f"You Need To Join Here With Your Bot And Userbot To Get Cached Music.\n{group_invite}"
        answers.append(
            InlineQueryResultArticle(
                title="ERROR",
                description="Click Here To Know More.",
                input_message_content=InputTextMessageContent(
                    msg, disable_web_page_preview=True
                ),
            )
        )
        return answers
    messages_ids_and_duration = []
    for f_ in messages:
        messages_ids_and_duration.append(
            {
                "message_id": f_.message_id,
                "duration": f_.audio.duration if f_.audio.duration else 0,
            }
        )
    messages = list({v["duration"]: v for v in messages_ids_and_duration}.values())
    messages_ids = [ff_["message_id"] for ff_ in messages]
    messages = await app.get_messages(chat_id, messages_ids[0:48])
    return [
        InlineQueryResultCachedDocument(
            file_id=message_.audio.file_id,
            title=message_.audio.title,
        )
        for message_ in messages
    ]


async def paste_func(answers, text):
    start_time = time()
    url = await paste(text)
    msg = f"__**{url}**__"
    end_time = time()
    answers.append(
        InlineQueryResultArticle(
            title=f"Pasted In {round(end_time - start_time)} Seconds.",
            description=url,
            input_message_content=InputTextMessageContent(msg),
        )
    )
    return answers


async def webss(url):
    start_time = time()
    if "." not in url:
        return
    screenshot = await fetch(f"https://api.princexd.tech/webss?url={url}")
    end_time = time()
    # m = await app.send_photo(LOG_GROUP_ID, photo=screenshot["url"])
    await m.delete()
    a = []
    pic = InlineQueryResultPhoto(
        photo_url=screenshot["url"],
        caption=(f"`{url}`\n__Took {round(end_time - start_time)} Seconds.__"),
    )
    a.append(pic)
    return a


async def saavn_func(answers, text):
    results = requests.get(f"https://saavn.me/search/songs?query={text}").json()[
        "data"
    ]["results"]
    for i in results:
        caption = f"{i['url']}"
        description = (
            f"{i['album']['name']} | {i['duration']} "
            + f"| {i['primaryArtists']} ({i['year']})"
        )
        answers.append(
            InlineQueryResultArticle(
                title=i["name"],
                input_message_content=InputTextMessageContent(
                    caption, disable_web_page_preview=True
                ),
                description=description,
                thumb_url=i["image"][2]["link"],
            )
        )
    return answers


async def ytmusic_func(answers, text):
    results = requests.get(f"https://api.princexd.tech/ytmusic?query={text}").json()[
        "results"
    ]
    for i in results:
        caption = f"https://music.youtube.com/watch?v={i['videoId']}&feature=share"
        description = (
            f"{i['title']} | {i['duration']} " + f"| {i['artists'][0]['name']}"
        )
        answers.append(
            InlineQueryResultArticle(
                title=i["title"],
                input_message_content=InputTextMessageContent(
                    caption, disable_web_page_preview=True
                ),
                description=description,
                thumb_url=i["thumbnails"][0]["url"],
            )
        )
    return answers


async def wiki_func(answers, text):
    data = await arq.wiki(text)
    if not data.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=data.result,
                input_message_content=InputTextMessageContent(data.result),
            )
        )
        return answers
    data = data.result
    msg = f"""
**QUERY:**
{data.title}
**ANSWER:**
__{data.answer}__"""
    answers.append(
        InlineQueryResultArticle(
            title=data.title,
            description=data.answer,
            input_message_content=InputTextMessageContent(msg),
        )
    )
    return answers


# CallbackQuery for the function above


@app.on_callback_query(filters.regex("test_speedtest"))
async def test_speedtest_cq(_, cq):
    if cq.from_user.id not in DEV_USERS:
        return await cq.answer("This Isn't For You!")
    inline_message_id = cq.inline_message_id
    await app.edit_inline_text(inline_message_id, "**Testing**")
    loop = asyncio.get_running_loop()
    download, upload, info = await loop.run_in_executor(None, test_speedtest)
    msg = f"""
**Download:** `{download}`
**Upload:** `{upload}`
**Latency:** `{info['latency']} ms`
**Country:** `{info['country']} [{info['cc']}]`
**Latitude:** `{info['lat']}`
**Longitude:** `{info['lon']}`
"""
    await app.edit_inline_text(inline_message_id, msg)


async def ping_func(answers):
    ping = Ping(ping_id=app.rnd_id())
    t1 = time()
    await app.send(ping)
    t2 = time()
    ping = f"{str(round((t2 - t1) * 1000, 2))} ms"
    answers.append(
        InlineQueryResultArticle(
            title=ping,
            input_message_content=InputTextMessageContent(f"__**{ping}**__"),
        )
    )
    return answers


async def info_inline_func(answers, peer):
    not_found = InlineQueryResultArticle(
        title="PEER NOT FOUND",
        input_message_content=InputTextMessageContent("PEER NOT FOUND"),
    )
    try:
        user = await app.get_users(peer)
        caption, _ = await get_user_info(user, True)
    except IndexError:
        try:
            chat = await app.get_chat(peer)
            caption, _ = await get_chat_info(chat, True)
        except Exception:
            return [not_found]
    except Exception:
        return [not_found]

    answers.append(
        InlineQueryResultArticle(
            title="Found Peer.",
            input_message_content=InputTextMessageContent(
                caption, disable_web_page_preview=True
            ),
        )
    )
    return answers


async def tmdb_func(answers, query):
    response = await arq.tmdb(query)
    if not response.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=response.result,
                input_message_content=InputTextMessageContent(response.result),
            )
        )
        return answers
    results = response.result[:49]
    for result in results:
        if not result.poster and not result.backdrop:
            continue
        if not result.genre:
            genre = None
        else:
            genre = " | ".join(result.genre)
        description = result.overview[0:900] if result.overview else "None"
        caption = f"""
**{result.title}**
**Type:** {result.type}
**Rating:** {result.rating}
**Genre:** {genre}
**Release Date:** {result.releaseDate}
**Description:** __{description}__
"""
        buttons = InlineKeyboard(row_width=1)
        buttons.add(
            InlineKeyboardButton(
                "Search Again",
                switch_inline_query_current_chat="tmdb",
            )
        )
        answers.append(
            InlineQueryResultPhoto(
                photo_url=result.backdrop if result.backdrop else result.poster,
                caption=caption,
                title=result.title,
                description=f"{genre} • {result.releaseDate} • {result.rating} • {description}",
                reply_markup=buttons,
            )
        )
    return answers


async def image_func(answers, query):
    results = await arq.image(query)
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    results = results.result[:49]
    buttons = InlineKeyboard(row_width=2)
    buttons.add(
        InlineKeyboardButton(
            text="Search again",
            switch_inline_query_current_chat="image",
        ),
    )
    for i in results:
        answers.append(
            InlineQueryResultPhoto(
                title=i.title,
                photo_url=i.url,
                thumb_url=i.url,
                reply_markup=buttons,
            )
        )
    return answers


async def pokedexinfo(answers, pokemon):
    Pokemon = f"https://some-random-api.ml/pokedex?pokemon={pokemon}"
    result = await fetch(Pokemon)
    buttons = InlineKeyboard(row_width=1)
    buttons.add(
        InlineKeyboardButton("Pokedex", switch_inline_query_current_chat="pokedex")
    )
    caption = f"""
**Pokemon:** `{result['name']}`
**Pokedex:** `{result['id']}`
**Type:** `{result['type']}`
**Abilities:** `{result['abilities']}`
**Height:** `{result['height']}`
**Weight:** `{result['weight']}`
**Gender:** `{result['gender']}`
**Stats:** `{result['stats']}`
**Description:** `{result['description']}`"""
    answers.append(
        InlineQueryResultPhoto(
            photo_url=f"https://img.pokemondb.net/artwork/large/{pokemon}.jpg",
            title=result["name"],
            description=result["description"],
            caption=caption,
            reply_markup=buttons,
        )
    )
    return answers


async def execute_code(query):
    text = query.query.strip()
    offset = int((query.offset or 0))
    answers = []
    languages = (await arq.execute()).result
    if len(text.split()) == 1:
        answers = [
            InlineQueryResultArticle(
                title=lang,
                input_message_content=InputTextMessageContent(lang),
            )
            for lang in languages
        ][offset : offset + 25]
        await query.answer(
            next_offset=str(offset + 25),
            results=answers,
            cache_time=1,
        )
    elif len(text.split()) == 2:
        text = text.split()[1].strip()
        languages = list(
            filter(
                lambda x: find_near_matches(text, x, max_l_dist=1),
                languages,
            )
        )
        answers.extend(
            [
                InlineQueryResultArticle(
                    title=lang,
                    input_message_content=InputTextMessageContent(lang),
                )
                for lang in languages
            ][:49]
        )
    else:
        lang = text.split()[1]
        code = text.split(None, 2)[2]
        response = await arq.execute(lang, code)
        if not response.ok:
            answers.append(
                InlineQueryResultArticle(
                    title="Error",
                    input_message_content=InputTextMessageContent(response.result),
                )
            )
        else:
            res = response.result
            stdout, stderr = escape(res.stdout), escape(res.stderr)
            output = stdout or stderr
            out = "STDOUT" if stdout else ("STDERR" if stderr else "No output")

            msg = f"""
**{lang.capitalize()}:**
```{code}```
**{out}:**
```{output}```
            """
            answers.append(
                InlineQueryResultArticle(
                    title="Executed",
                    description=output[:20],
                    input_message_content=InputTextMessageContent(msg),
                )
            )
    await query.answer(results=answers, cache_time=1)


async def task_inline_func(user_id):
    if user_id not in DEV_USERS:
        return

    tasks = all_tasks()
    text = await _get_tasks_text()
    keyb = None

    if tasks:
        keyb = ikb(
            {i: f"cancel_task_{i}" for i in list(tasks.keys())},
            row_width=4,
        )

    return [
        InlineQueryResultArticle(
            title="Tasks",
            reply_markup=keyb,
            input_message_content=InputTextMessageContent(
                text,
            ),
        )
    ]


@app.on_callback_query(filters.regex("^cancel_task_"))
async def cancel_task_button(_, query: CallbackQuery):
    user_id = query.from_user.id

    if user_id not in DEV_USERS:
        return await query.answer("This is not for you.")

    task_id = int(query.data.split("_")[-1])
    await rm_task(task_id)

    tasks = all_tasks()
    text = await _get_tasks_text()
    keyb = None

    if tasks:
        keyb = ikb({i: f"cancel_task_{i}" for i in list(tasks.keys())})

    await app.edit_inline_text(
        query.inline_message_id,
        text,
    )

    if keyb:
        await app.edit_inline_reply_markup(
            query.inline_message_id,
            keyb,
        )
