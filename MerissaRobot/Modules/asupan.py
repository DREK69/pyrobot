import os

import wget
from pyrogram import filters
from pyrogram.types import *

from MerissaRobot import pbot as bot


@bot.on_message(filters.command("asupan"))
async def animememes(_, message):
    x = await message.reply_text("Please Wait Video Uploading...")
    res = wget.download("https://api.princexd.tech/asupan/tiktok", "asupan.mp4")
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Change 🔂", callback_data="asupan"),
            ],
        ]
    )
    await message.reply_video("asupan.mp4", reply_markup=button)
    await x.delete()
    os.remove("asupan.mp4")


@bot.on_callback_query(filters.regex(pattern=r"asupan"))
async def hmeme(_, query: CallbackQuery):
    await query.answer(
        "Generating another Asupan Video\nPlease Wait....", show_alert=True
    )
    res = wget.download("https://api.princexd.tech/asupan/tiktok", "asupan.mp4")
    await query.edit_message_media(
        InputMediaVideo("asupan.mp4", caption="Powered by @MerissaRobot"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="asupan",
                    ),
                ],
            ],
        ),
    )
    os.remove("asupan.mp4")
