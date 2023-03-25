import random

from pyrogram import filters
from pyrogram.types import *
from requests import get

from MerissaRobot import pbot

link = [
    "https://en.ephoto360.com/create-digital-glitch-text-effects-online-767.html",
    "https://en.ephoto360.com/online-blackpink-style-logo-maker-effect-711.html",
    "https://en.ephoto360.com/create-impressive-neon-glitch-text-effects-online-768.html",
    "https://en.ephoto360.com/create-blackpink-logo-online-free-607.html",
    "https://en.ephoto360.com/create-3d-gradient-text-effect-online-600.html",
    "https://en.ephoto360.com/neon-devil-wings-text-effect-online-683.html",
]


@pbot.on_message(filters.command("hqlogo"))
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
                InlineKeyboardButton("Change 🔄", callback_data=f"hqlogo_{name}"),
            ],
        ]
    )
    await message.reply_photo(
        photo=url,
        caption="Powered by @MerissaRobot",
        reply_markup=button,
    )
    await logo.delete()


@pbot.on_message(filters.command("alogo"))
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
                InlineKeyboardButton("Change 🔄", callback_data=f"anilogo_{name}"),
            ],
        ]
    )
    await message.reply_photo(
        photo=url,
        caption="Powered by @MerissaRobot",
        reply_markup=button,
    )
    await logo.delete()


@pbot.on_message(filters.command("logo"))
async def movie(_, message):
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
    url = get(f"https://api.princexd.tech/logo?text={name}").url
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Change 🔄", callback_data=f"logo_{name}"),
            ],
        ]
    )
    await message.reply_photo(
        photo=url,
        caption="Powered by @MerissaRobot",
        reply_markup=button,
    )
    await logo.delete()


@pbot.on_callback_query(filters.regex(pattern="^logo"))
async def hmeme(_, query: CallbackQuery):
    callback_data = query.data
    name = callback_data.split("_", 1)[1]
    url = get(f"https://api.princexd.tech/logo?text={name}").url
    await query.edit_message_media(
        InputMediaPhoto(url, caption="Powered by @MerissaRobot"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data=f"logo_{name}",
                    ),
                ],
            ],
        ),
    )

@pbot.on_callback_query(filters.regex(pattern="^anilogo"))
async def hmeme(_, query: CallbackQuery):
    callback_data = query.data
    name = callback_data.split("_", 1)[1]
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

@pbot.on_callback_query(filters.regex(pattern="^hqlogo"))
async def hmeme(_, query: CallbackQuery):
    callback_data = query.data
    name = callback_data.split("_", 1)[1]
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
