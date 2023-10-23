import os

from PeakPxApi import PeakPx
from pyrogram import filters
from pyrogram.types import *

from MerissaRobot import pbot
from MerissaRobot.helpers import save_file

px = PeakPx()


@pbot.on_message(filters.command("wallpaper"))
async def wallpaper(bot, message):
    if len(message.command) < 2:
        return await message.reply_text("Give me some text to search for wallpaper")
    m = await message.reply_text("🔄 Processing Query... Please Wait!")
    search = message.text.split(None, 1)[1]
    wallsearch = px.search_wallpapers(search)
    wallpaper = wallsearch[0]["url"]
    try:
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
    except:
        await save_file(wallpaper, "wall.png")
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
                            callback_data=f"walld",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
    await m.delete()
    os.remove("wall.png")


@pbot.on_callback_query(filters.regex("^wnext"))
async def wnext_query(client, callbackquery):
    callback_data = callbackquery.data.strip()
    callback = callback_data.split("|")
    search = callback[1]
    page = int(callback[2])
    wallsearch = px.search_wallpapers(query=search)
    wallpaper = wallsearch[page]["url"]
    tpage = len(wallsearch) - 1
    try:
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
                                callback_data=f"dlwall",
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
                                callback_data=f"wnext|{search}|{page-1}",
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                "📥 Download",
                                callback_data=f"dlwall",
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
                                callback_data=f"dlwall",
                            ),
                            InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                        ],
                    ]
                ),
            )
    except:
        wall = await save_file(wallpaper, "wall.png")
        if page == 0:
            await callbackquery.edit_message_media(
                InputMediaPhoto(
                    wall,
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
                                callback_data=f"dlwall",
                            ),
                            InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                        ],
                    ]
                ),
            )
        elif page == tpage:
            await callbackquery.edit_message_media(
                InputMediaPhoto(
                    wall,
                    caption="Powered By @MerissaRobot",
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "⬅️ Prev Wallpaper",
                                callback_data=f"wnext|{search}|{page-1}",
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                "📥 Download",
                                callback_data=f"dlwall",
                            ),
                            InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                        ],
                    ]
                ),
            )
        else:
            await callbackquery.edit_message_media(
                InputMediaPhoto(
                    wall,
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
                                callback_data=f"dlwall",
                            ),
                            InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                        ],
                    ]
                ),
            )
        os.remove(wall)


@pbot.on_callback_query(filters.regex("^dlwall"))
async def wall_down(client, callbackquery):
    await callbackquery.answer(
        "Please Wait Downloading Wallpaper for You", show_alert=True
    )
    wall = await callbackquery.message.download()
    await callbackquery.message.reply_document(wall)
    os.remove(wall)
