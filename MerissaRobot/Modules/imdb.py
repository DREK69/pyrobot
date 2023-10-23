from pyrogram import filters
from pyrogram.types import *

from MerissaRobot import pbot
from MerissaRobot.helpers import getreq


@pbot.on_message(filters.command(["imdb", "tmdb"]))
async def imdb(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Give me some Movie Name\n\nEx. /imdb Kgf")
    query = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    resp = await getreq(
        f"https://api.themoviedb.org/3/search/movie?query={query}&api_key=6f77cb8794e999fed44476c8b3303723"
    )
    url = resp["results"][0]
    poster = f"https://image.tmdb.org/t/p/original/{url['poster_path']}"
    await message.reply_photo(
        photo=poster,
        caption=f"""**IMDB Movie Details :**

**Title :** {url["title"]}
**Description :** {url["overview"]}
**Release-Date :** {url["release_date"]}
**Popularity :** {url["popularity"]}
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Next Result ➡",
                        callback_data=f"imnext|{query}|1",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"Stream {url['title']}",
                        url=f"https://movie.princexd.tech/movie/{url['id']}/watch",
                    ),
                    InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                ],
            ],
        ),
    )


@pbot.on_callback_query(filters.regex("^imnext"))
async def ymnext_query(client, callbackquery):
    callback_data = callbackquery.data.strip()
    callback = callback_data.split("|")
    query = callback[1]
    page = int(callback[2])
    resp = await getreq(
        f"https://api.themoviedb.org/3/search/movie?query={query}&api_key=6f77cb8794e999fed44476c8b3303723"
    )
    url = search["results"][page]
    poster = f"https://image.tmdb.org/t/p/original/{url['poster_path']}"
    tpage = len(search["results"]) - 1
    if page == 0:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                poster,
                caption=f"""**IMDB Movie Details :**

**Title :** {url["title"]}
**Description :** {url["overview"]}
**Release-Date :** {url["release_date"]}
**Popularity :** {url["popularity"]}
""",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Next Track ➡", callback_data=f"imnext|{query}|1"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=f"Stream {url['title']}",
                            url=f"https://movie.princexd.tech/movie/{url['id']}/watch",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
    elif page == tpage:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                poster,
                caption=f"""**IMDB Movie Details :**

**Title :** {url["title"]}
**Description :** {url["overview"]}
**Release-Date :** {url["release_date"]}
**Popularity :** {url["popularity"]}
""",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Prev Track", callback_data=f"imnext|{query}|{page-1}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Stream",
                            url=f"https://movie.princexd.tech/movie/{url['id']}/watch",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
    else:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                poster,
                caption=f"""**IMDB Movie Details :**

**Title :** {url["title"]}
**Description :** {url["overview"]}
**Release-Date :** {url["release_date"]}
**Popularity :** {url["popularity"]}
""",
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️", callback_data=f"imnext|{query}|{page-1}"
                        ),
                        InlineKeyboardButton(
                            "➡", callback_data=f"imnext|{query}|{page+1}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=f"Stream {url['title']}",
                            url=f"https://movie.princexd.tech/movie/{url['id']}/watch",
                        ),
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
