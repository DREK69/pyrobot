import requests
from pyrogram import filters
from pyrogram.types import *

from MerissaRobot import pbot as bot


@bot.on_callback_query(filters.regex("boob"))
async def boobsc(_, query: CallbackQuery):
    res = requests.get("https://api.princexd.tech/boobs").json()
    await query.edit_message_media(
        InputMediaPhoto(res, caption="Powered By @MerissaRobot"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="boob",
                    ),
                ],
            ],
        ),
    )


@bot.on_callback_query(filters.regex("animepfp"))
async def animepfpc(_, query: CallbackQuery):
    res = requests.get("https://api.princexd.tech/animepfp").json()["url"]
    await query.edit_message_media(
        InputMediaPhoto(res, caption="Powered By @MerissaRobot"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="animepfp",
                    ),
                ],
            ],
        ),
    )


@bot.on_callback_query(filters.regex("ameme"))
async def ameme(_, query: CallbackQuery):
    res = requests.get("https://api.princexd.tech/reddit?query=Animememe").json()[
        "data"
    ]
    url = res["image_url"]
    text = res["title"]
    link = res["post_url"]
    await query.edit_message_media(
        InputMediaPhoto(url, caption=f"[{text}]({link})"),
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


@bot.on_callback_query(filters.regex("bmeme"))
async def memess(_, query: CallbackQuery):
    res = requests.get("https://api.princexd.tech/meme").json()
    url = res["image"]
    text = res["title"]
    link = res["postLink"]
    await query.edit_message_media(
        InputMediaPhoto(url, caption=f"[{text}]({link})"),
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


@bot.on_callback_query(filters.regex("cmeme"))
async def hmeme(_, query: CallbackQuery):
    res = requests.get("https://meme-api.herokuapp.com/gimme/hentaimemes").json()
    url = res["url"]
    text = res["title"]
    link = res["postLink"]
    await query.edit_message_media(
        InputMediaPhoto(url, caption=f"[{text}]({link})"),
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
