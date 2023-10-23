import os

from PeakPxApi import PeakPx
from pyrogram import filters
from pyrogram.types import *

from MerissaRobot import pbot

px = PeakPx()


@pbot.on_message(filters.command("wallpaper"))
async def wallpaper(bot, message):
    if len(message.command) < 2:
        return await message.reply_text("Give me some text to search for wallpaper")
    m = await message.reply_text("🔄 Processing Query... Please Wait!")
    search = message.text.split(None, 1)[1]
    wallsearch = px.search_wallpapers(search)
    wallpaper = wallsearch[0]["url"]
    await message.reply_photo(
        wallpaper,
        caption="Powered by @MerissaRobot",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Next Wallpaper ➡", callback_data=f"wnext|{search}|1"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "📥 Download",
                        callback_data=f"wall|{search}|0",
                    ),
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ]
        ),
    )
    await m.delete()


@pbot.on_callback_query(filters.regex("^wnext"))
async def wnext_query(client, callbackquery):
    callback_data = callbackquery.data.strip()
    callback = callback_data.split("|")
    search = callback[1]
    page = int(callback[2])
    wallsearch = px.search_wallpapers(query=search)
    wallpaper = wallsearch[page]["url"]
    tpage = len(wallsearch) - 1
    if page == 0:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                wallpaper,
                caption="Powered By @MerissaRobot",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Next Wallpaper ➡", callback_data=f"wnext|{search}|1"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"wall|{search}|{page}",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
    elif page == tpage:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                wallpaper,
                caption="Powered By @MerissaRobot",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Prev Wallpaper",
                            callback_data=f"ymnext|{search}|{page-1}",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"wall|{search}|{page}",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
    else:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                wallpaper,
                caption="Powered By @MerissaRobot",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️", callback_data=f"wnext|{search}|{page-1}"
                        ),
                        InlineKeyboardButton(
                            "➡", callback_data=f"wnext|{search}|{page+1}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📥 Download",
                            callback_data=f"wall|{search}|{page}",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )


@pbot.on_callback_query(filters.regex("^wall"))
async def wall_down(client, callbackquery):
    wall = await callbackquery.message.download()
    await callbackquery.message.reply_document(wall)
    os.remove(wall)
