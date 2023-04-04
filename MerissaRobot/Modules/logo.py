import os
import random

from pyrogram import filters
from pyrogram.types import *
from requests import get
from telegraph import upload_file as uf

from MerissaRobot import pbot

link = [
    "https://en.ephoto360.com/create-digital-glitch-text-effects-online-767.html",
    "https://en.ephoto360.com/online-blackpink-style-logo-maker-effect-711.html",
    "https://en.ephoto360.com/create-impressive-neon-glitch-text-effects-online-768.html",
    "https://en.ephoto360.com/create-blackpink-logo-online-free-607.html",
    "https://en.ephoto360.com/create-3d-gradient-text-effect-online-600.html",
    "https://en.ephoto360.com/neon-devil-wings-text-effect-online-683.html",
]


@pbot.on_message(filters.command("hqlogo") & filters.private)
async def movie(_, message):
    logo = await message.reply_text("Creating your logo...wait!")
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some text to make logo\n\nEx. /hqlogo MerissaRobot"
        )
    name = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    ranlink = random.choice(link)
    url = get(
        f"https://api.akuari.my.id/ephoto/scraper-1?text={name}&link={ranlink}"
    ).json()["respon"]
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Change 🔂", callback_data=f"hqlogo_{name}"),
            ],
        ]
    )
    await message.reply_photo(
        photo=url,
        caption="Powered by @MerissaRobot",
        reply_markup=button,
    )
    await logo.delete()


@pbot.on_message(filters.command("alogo") & filters.private)
async def movie(_, message):
    logo = await message.reply_text("Creating your logo...wait!")
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some text to make logo\n\nEx. /alogo MerissaRobot"
        )
    name = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    url = get(f"https://api.princexd.tech/anime-logo?text={name}").json()["url"]
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Change 🔂", callback_data=f"anilogo_{name}"),
            ],
        ]
    )
    await message.reply_photo(
        photo=url,
        caption="Powered by @MerissaRobot",
        reply_markup=button,
    )
    await logo.delete()


@pbot.on_message(filters.command("logo") & filters.private)
async def movie(client, message):
    reply = message.reply_to_message
    logo = await message.reply_text("Creating your logo...wait!")
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some text to make logo\n\nEx. /logo Merissa or Merissa;Robot"
        )
    name = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    if reply:
        download_location = await client.download_media(
            message=reply,
            file_name="root/downloads/",
        )
        x = uf(download_location)[0]
        imglink = "https://te.legra.ph" + x
        key = imglink.split("/")[4]
        url = get(
            f"https://api.princexd.tech/logoimg?imglink={imglink}&text={name}"
        ).url
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Change 🔂", callback_data=f"ilogo|{name}|{key}"
                    ),
                ],
            ]
        )
        await message.reply_photo(
            photo=url, caption="Powered by @MerissaRobot", reply_markup=button
        )
        await logo.delete()
        os.remove(download_location)
    else:
        x = get(f"https://api.princexd.tech/logo?text={name}").json()
        url = x["url"]
        font = x["font"]
        bg = x["img"]
        key = bg.split("/")[4]
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Image 🔂",
                        callback_data=f"flogo|{name}|{font}",
                    ),
                    InlineKeyboardButton(
                        text="Font 🔂",
                        callback_data=f"ilogo|{name}|{key}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Change Logo 🔂", callback_data=f"slogo|{name}|{key}|{font}"
                    ),
                ],
            ]
        )
        await message.reply_photo(
            photo=url,
            caption="Powered by @MerissaRobot",
            reply_markup=button,
        )
        await logo.delete()


@pbot.on_callback_query(filters.regex(pattern=r"flogo"))
async def hmeme(_, query: CallbackQuery):
    await query.answer("Generating Your Logo Please Wait....", show_alert=True)
    callback_data = query.data.strip()
    data = callback_data.split("|")
    name = data[1]
    font = data[2]
    url = get(f"https://api.princexd.tech/logofont?font={font}&text={name}").url
    await query.edit_message_media(
        InputMediaPhoto(url, caption="Powered by @MerissaRobot"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change Image 🔂",
                        callback_data=f"flogo|{name}|{font}",
                    ),
                ],
            ],
        ),
    )


@pbot.on_callback_query(filters.regex(pattern=r"ilogo"))
async def hmeme(_, query: CallbackQuery):
    await query.answer("Generating Your Logo Please Wait....", show_alert=True)
    callback_data = query.data.strip()
    data = callback_data.split("|")
    name = data[1]
    key = data[2]
    imglink = "https://te.legra.ph/file/" + key
    url = get(f"https://api.princexd.tech/logoimg?imglink={imglink}&text={name}").url
    await query.edit_message_media(
        InputMediaPhoto(url, caption="Powered by @MerissaRobot"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change Font 🔂",
                        callback_data=f"ilogo|{name}|{key}",
                    ),
                ],
            ],
        ),
    )


@pbot.on_callback_query(filters.regex(pattern=r"slogo"))
async def hmeme(_, query: CallbackQuery):
    await query.answer("Generating Your Logo Please Wait....", show_alert=True)
    callback_data = query.data.strip()
    data = callback_data.split("|")
    name = data[1]
    key = data[2]
    font = data[3]
    url = get(f"https://api.princexd.tech/logo?text={name}").json()["url"]
    await query.edit_message_media(
        InputMediaPhoto(url, caption="Powered by @MerissaRobot"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Image 🔂",
                        callback_data=f"flogo|{name}|{font}",
                    ),
                    InlineKeyboardButton(
                        text="Font 🔂",
                        callback_data=f"ilogo|{name}|{key}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Change Logo 🔂", callback_data=f"slogo|{name}|{key}|{font}"
                    ),
                ],
            ],
        ),
    )


@pbot.on_callback_query(filters.regex(pattern=r"anilogo"))
async def hmeme(_, query: CallbackQuery):
    await query.answer("Generating Your Logo Please Wait....", show_alert=True)
    callback_data = query.data.strip()
    name = callback_data.split("_")[1]
    url = get(f"https://api.princexd.tech/anime-logo?text={name}").json()["url"]
    await query.edit_message_media(
        InputMediaPhoto(url, caption="Powered by @MerissaRobot"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data=f"anilogo_{name}",
                    ),
                ],
            ],
        ),
    )


@pbot.on_callback_query(filters.regex(pattern=r"hqlogo"))
async def hmeme(_, query: CallbackQuery):
    await query.answer("Generating Your Logo Please Wait....", show_alert=True)
    callback_data = query.data.strip()
    name = callback_data.split("_")[1]
    ranlink = random.choice(link)
    url = get(
        f"https://api.akuari.my.id/ephoto/scraper-1?text={name}&link={ranlink}"
    ).json()["respon"]
    await query.edit_message_media(
        InputMediaPhoto(url, caption="Powered by @MerissaRobot"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data=f"hqlogo_{name}",
                    ),
                ],
            ],
        ),
    )


__mod_name__ = "Logo 🎇"

__help__ = """ 
- Logo Maker Command
❂ /logo <text/name> - Create a logo with random view.
❂ /logo Merissa;Robot -  use ; for write in next line
❂ /hqlogo <text> - To create random logo.
❂ /alogo <text> - To create anime logo.
❂ /write <text/name> - Write Text on Note Book
❂ /carbon <reply to text> - Create carbon Logo
"""
