import random

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
                InlineKeyboardButton("Telegraph Link 🔗", url=f"{url}"),
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
                InlineKeyboardButton("Telegraph Link 🔗", url=f"{url}"),
            ],
        ]
    )
    await message.reply_photo(
        photo=url,
        caption="Powered by @MerissaRobot",
        reply_markup=button,
    )
    await logo.delete()
