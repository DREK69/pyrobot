import requests
from pyrogram import filters
from pyrogram.types import *

from MerissaRobot import pbot as bot


@bot.on_message(filters.command(["ameme", "animememe"]))
async def animememes(_, m):
    res = requests.get("https://api.princexd.tech/reddit?query=Animememe").json()[
        "data"
    ]
    url = res["image_url"]
    text = res["title"]
    link = res["post_url"]
    await m.reply_photo(
        url,
        caption=f"[{text}]({link})",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="ameme",
                    ),
                ],
            ],
        ),
    )


@bot.on_message(filters.command("meme"))
async def memes(_, m):
    res = requests.get("https://api.princexd.tech/meme").json()
    url = res["image"]
    text = res["title"]
    link = res["postLink"]
    await m.reply_photo(
        url,
        caption=f"[{text}]({link})",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="bmeme",
                    ),
                ],
            ],
        ),
    )


@bot.on_message(filters.command(["hmeme", "hentaimeme"]))
async def hetaimemes(_, m):
    res = requests.get("https://meme-api.herokuapp.com/gimme/hentaimemes").json()
    url = res["url"]
    text = res["title"]
    link = res["postLink"]
    await m.reply_photo(
        url,
        caption=f"[{text}]({link})",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="cmeme",
                    ),
                ],
            ],
        ),
    )
