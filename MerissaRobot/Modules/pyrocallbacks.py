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
