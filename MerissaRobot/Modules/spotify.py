import os

import requests
import wget
from pyrogram import filters
from pyrogram.enums import ChatAction
from pyrogram.types import *

from MerissaRobot import pbot

spotregex = r"^https:\/\/open\.spotify\.com\/track"


@pbot.on_message(filters.regex(spotregex) & filters.incoming)
async def spotdown(_, message):
    m = await message.reply_text("🔄 Processing Query... Please Wait!", quote=True)
    link = message.text
    song_id = link.split("/")[4]
    result = requests.get(f"https://api.princexd.tech/sptrack?trackid={song_id}").json()
    name = result["name"]
    songurl = result["external_urls"]["spotify"]
    album_name = result["album"]["name"]
    albumurl = result["album"]["external_urls"]["spotify"]
    img = result["album"]["images"][0]["url"]
    thumbnail = wget.download(img, "thumbnail.png")
    result["album"]["artists"][0]["name"]
    capt = f"**Song Name: **[{name}]({songurl})\n**Album: **[{album_name}]({albumurl})"
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Download", callback_data=f"spdown|{song_id}")],
            [
                InlineKeyboardButton("Spotify", url=songurl),
                InlineKeyboardButton("Album", url=albumurl),
            ],
        ]
    )
    await message.reply_photo(thumbnail, caption=capt, reply_markup=buttons)
    await m.delete()
    os.remove(thumbnail)


@pbot.on_message(filters.command("spotify"))
async def spsearch(bot, m):
    if len(m.command) < 2:
        return await m.reply_text("Give me some text to search on Spotify")
    boo = await m.reply_text("🔄 Processing Query... Please Wait!")
    query = m.text.split(None, 1)[1]
    search = requests.get(f"https://api.princexd.tech/spsearch?query={query}").json()[
        "tracks"
    ]["items"]
    result = search[0]
    title = result["name"]
    songurl = result["external_urls"]["spotify"]
    artist = result["album"]["artists"][0]["name"]
    albumurl = result["album"]["external_urls"]["spotify"]
    id = result["id"]
    img = result["album"]["images"][0]["url"]
    capt = f"**Song Name: **[{title}]({songurl})\n**Album: **[{artist}]({albumurl})\n**Track** = 1 out of {len(search)}\n\n**Select your track from Below and Download It**:"
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Next Track ➡", callback_data=f"spnext|{query}|1"),
            ],
            [
                InlineKeyboardButton(
                    "📥 Download",
                    callback_data=f"spdown|{id}",
                ),
                InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
            ],
        ]
    )
    await m.reply_photo(img, caption=capt, reply_markup=buttons)
    await boo.delete()


@pbot.on_callback_query(filters.regex(pattern=r"spnext"))
async def callback_query(Client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback = callback_data.split("|")
    query = callback[1]
    page = int(callback[2])
    search = requests.get(f"https://api.princexd.tech/spsearch?query={query}").json()[
        "tracks"
    ]["items"]
    result = search[page]
    title = result["name"]
    songurl = result["external_urls"]["spotify"]
    artist = result["album"]["artists"][0]["name"]
    albumurl = result["album"]["external_urls"]["spotify"]
    id = result["id"]
    thumbnail = result["album"]["images"][0]["url"]
    tpage = len(search) - 1
    if page == 0:
        await CallbackQuery.edit_message_media(
            InputMediaPhoto(
                thumbnail,
                caption=f"**Song Name: **[{title}]({songurl})\n**Album: **[{artist}]({albumurl})\n**Track** = {page+1} out of {len(search)}\n\n**Select your track from Below and Download It**:",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Next Track ➡", callback_data=f"spnext|{query}|1"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"spdown|{id}",
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
                caption=f"**Song Name: **[{title}]({songurl})\n**Album: **[{artist}]({albumurl})\n**Track** = {page+1} out of {len(search)}\n\n**Select your track from Below and Download It**:",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Prev Track", callback_data=f"spnext|{query}|{page-1}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"spdown|{id}",
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
                caption=f"**Song Name: **[{title}]({songurl})\n**Album: **[{artist}]({albumurl})\n**Track** = {page+1} out of {len(search)}\n\n**Select your track from Below and Download It**:",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️", callback_data=f"spnext|{query}|{page-1}"
                        ),
                        InlineKeyboardButton(
                            "➡", callback_data=f"spnext|{query}|{page+1}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"spdown|{id}",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )


@pbot.on_callback_query(filters.regex(pattern=r"spdown"))
async def spotdl(Client, CallbackQuery):
    chatid = CallbackQuery.message.chat.id
    m = await CallbackQuery.edit_message_text(
        "Downloading Started\n\nDownload Speed could be slow. Please hold on.."
    )
    callback_data = CallbackQuery.data.strip()
    callback = callback_data.split("|")
    song_id = callback[1]
    result = requests.get(f"https://api.princexd.tech/sptrack?trackid={song_id}").json()
    name = result["name"]
    img = result["album"]["images"][0]["url"]
    artist = result["album"]["artists"][0]["name"]
    query = f"{name} {artist}"
    id = result["id"]
    thumbnail = wget.download(img, "thumbnail.png")
    search = requests.get(f"https://saavn.me/search/songs?query={query}").json()[
        "data"
    ]["results"][0]
    dlink = search["downloadUrl"][4]["link"]
    duration = search["duration"]
    performer = search["primaryArtists"]
    dl = wget.download(dlink)
    file = dl.replace("mp4", "mp3")
    os.rename(dl, file)
    med = InputMediaAudio(
        file, thumb=thumbnail, title=name, performer=artist, duration=int(duration)
    )
    try:
        lyrics = requests.get(
            f"https://editor-choice-api.vercel.app/lyrics?query={query}"
        ).json()["url"]
        link = lyrics.replace("https://telegra.ph", "https://graph.org")
        button = InlineKeyboardMarkup([[InlineKeyboardButton(text="🎵 Lyrics", url=link)]])
        try:
            await m.edit(
                "Uploading Started\n\nUpload Speed could be slow. Please hold on.."
            )
            await Client.send_chat_action(chatid, ChatAction.UPLOAD_AUDIO)
            await CallbackQuery.edit_message_media(media=med, reply_markup=button)
        except Exception as error:
            await CallbackQuery.edit_message_text(
                f"Something happened!\n<i>{error}</i>"
            )
    except KeyError:
        try:
            await m.edit(
                "Uploading Started\n\nUpload Speed could be slow. Please hold on.."
            )
            await Client.send_chat_action(chatid, ChatAction.UPLOAD_AUDIO)
            await CallbackQuery.edit_message_media(media=med)
        except Exception as error:
            await CallbackQuery.edit_message_text(
                f"Something happened!\n<i>{error}</i>"
            )
    os.remove(thumbnail)
    os.remove(file)
