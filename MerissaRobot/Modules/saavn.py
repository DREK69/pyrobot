import os

import requests
from mutagen.mp4 import MP4
from pyrogram import filters
from pyrogram.enums import ChatAction
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaPhoto,
)

from MerissaRobot import pbot
from MerissaRobot.helpers import embed_album_art, save_file

spregex = r"https:\/\/www\.jiosaavn\.com\/song\/"


async def convertmin(duration):
    seconds = int(duration)
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    result = f"{minutes} min {remaining_seconds} sec"
    return result


@pbot.on_message(filters.regex(spregex) & filters.incoming & filters.private)
async def song(client, message):
    link = message.text
    m = await message.reply_text("🔄 Processing Query... Please Wait!")
    search = requests.get(f"https://saavn.princexd.tech/songs?link={link}").json()
    result = search["data"][0]
    title = result["name"]
    duration = result["duration"]
    dur = await convertmin(duration)
    img = result["image"][2]["link"]
    id = result["id"]
    rights = result["copyright"]
    thumbnail = save_file(img, "thumbnail.jpg")
    await message.reply_photo(
        thumbnail,
        caption=f"**Title**: [{title}]({search['data'][0]['url']})\n**Duration**: {dur}\n\n**Copyright**: **{rights}**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📥 Download",
                        callback_data=f"svdown {id}",
                    ),
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ]
            ]
        ),
    )
    await m.delete()
    os.remove(file)
    os.remove(thumbnail)


@pbot.on_message(filters.command("saavn"))
async def saavn(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Give me some text to search on saavn")
    m = await message.reply_text("🔄 Processing Query... Please Wait!")
    query = message.text.split(None, 1)[1]
    try:
        search = requests.get(f"https://saavn.me/search/songs?query={query}").json()
    except Exception as e:
        await m.edit(str(e))
        return
    result = search["data"]["results"][0]
    title = result["name"]
    img = result["image"][2]["link"]
    duration = result["duration"]
    dur = await convertmin(duration)
    id = result["id"]
    rights = result["copyright"]
    page = 0
    thumbnail = save_file(img, "thumbnail.jpg")
    await message.reply_photo(
        thumbnail,
        caption=f"**Title**: [{title}]({search['data']['results'][0]['url']})\n**Duration**: {dur}\n**Track** = {page+1} out of {len(search['data']['results'])}\n\n**Copyright**: **{rights}**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Next Track ➡", callback_data=f"svnext|{query}|1"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "📥 Download",
                        callback_data=f"svdown {id}",
                    ),
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )
    os.remove(thumbnail)
    await m.delete()


@pbot.on_callback_query(filters.regex(pattern=r"svnext"))
async def callback_query(client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback = callback_data.split("|")
    query = str(callback[1])
    page = int(callback[2])
    search = requests.get(f"https://saavn.me/search/songs?query={query}").json()
    result = search["data"]["results"][page]
    title = result["name"]
    id = result["id"]
    thumbnail = result["image"][2]["link"]
    duration = result["duration"]
    dur = await convertmin(duration)
    rights = result["copyright"]
    tpage = len(search["data"]["results"]) - 1
    if page == 0:
        await CallbackQuery.edit_message_media(
            InputMediaPhoto(
                thumbnail,
                caption=f"**Title**: [{title}]({search['data']['results'][0]['url']})\n**Duration**: {dur}\n**Track** = {page+1} out of {len(search['data']['results'])}\n\n**Copyright**: **{rights}**",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Next Track ➡", callback_data=f"svnext|{query}|1"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"svdown {id}",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
    elif page == tpage:
        await CallbackQuery.edit_message_media(
            InputMediaPhoto(
                thumbnail,
                caption=f"**Title**:[{title}]({search['data']['results'][0]['url']})\n**Duration**: {dur}\n**Track** = {page+1} out of {len(search['data']['results'])}\n\n**Copyright**: **{rights}**",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Prev Track", callback_data=f"svnext|{query}|{page-1}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"svdown {id}",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
    else:
        await CallbackQuery.edit_message_media(
            InputMediaPhoto(
                thumbnail,
                caption=f"**Title**: [{title}]({search['data']['results'][0]['url']})\n**Duration**: {dur}\n**Track** = {page+1} out of {len(search['data']['results'])}\n\n**Copyright**: **{rights}**",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️", callback_data=f"svnext|{query}|{page-1}"
                        ),
                        InlineKeyboardButton(
                            "➡", callback_data=f"svnext|{query}|{page+1}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"svdown {id}",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )


@pbot.on_callback_query(filters.regex(pattern=r"svdown"))
async def callback_query(client, query):
    chatid = query.message.chat.id
    m = await query.edit_message_text(
        "Downloading Started\n\nDownload Speed could be slow. Please hold on.."
    )
    callback_data = query.data.strip()
    id = callback_data.split(None, 1)[1]
    search = requests.get(f"https://saavn.princexd.tech/songs?id={id}").json()
    result = search["data"][0]
    title = result["name"]
    dur = result["duration"]
    artist = result["primaryArtists"]
    album = result["album"]["name"]
    thumbnail = await query.message.download()
    dlink = result["downloadUrl"][4]["link"]
    file = save_file(dlink, f"{title}.m4a")
    audio = MP4(file)
    audio["\xa9nam"] = title
    audio["\xa9alb"] = album
    audio["\xa9ART"] = artist
    audio.save()
    embed_album_art(thumbnail, file)
    capt = f"{title} - {artist}"
    med = InputMediaAudio(
        file,
        thumb=thumbnail,
        caption=capt,
        title=title,
        performer=artist,
        duration=int(dur),
    )
    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="🎵 Lyrics", callback_data="lyrics")]]
    )
    await m.edit("Uploading Started\n\nUpload Speed could be slow. Please hold on..")
    await pbot.send_chat_action(chatid, ChatAction.UPLOAD_AUDIO)
    await query.edit_message_media(media=med, reply_markup=button)
    os.remove(file)
    os.remove(thumbnail)
