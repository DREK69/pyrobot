from pyrogram import filters
from pyrogram.types import *

from MerissaRobot import getreq, pbot


@pbot.on_message(filters.command(["imdb", "tmdb"]))
async def imdb(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Give me some Movie Name\n\nEx. /imdb Kgf")
    query = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    url = await getreq(f"https://api.safone.me/tmdb?query={query}").json()["results"][0]
    await message.reply_photo(
        photo=url["poster"],
        caption=f"""**IMDB Movie Details :**

**Title :** {url["title"]}
**Description :** {url["overview"]}
**Rating :** {url["rating"]}
**Release-Date :** {url["releaseDate"]}
**Popularity :** {url["popularity"]}
**Runtime :** {url["runtime"]}
**Status :** {url["status"]}
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
                        text="Imdb",
                        url=url["imdbLink"],
                    ),
                    InlineKeyboardButton(
                        text="Stream",
                        url=f"https://api.princexd.tech/stream?imdbid={url['imdbId']}",
                    ),
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
    search = await getreq(f"https://api.safone.me/tmdb?query={query}").json()
    url = search["results"][page]
    tpage = len(search["results"]) - 1
    if page == 0:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                url["poster"],
                caption=f"""**IMDB Movie Details :**

**Title :** {url["title"]}
**Description :** {url["overview"]}
**Rating :** {url["rating"]}
**Release-Date :** {url["releaseDate"]}
**Popularity :** {url["popularity"]}
**Runtime :** {url["runtime"]}
**Status :** {url["status"]}
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
                            text="Imdb",
                            url=url["imdbLink"],
                        ),
                        InlineKeyboardButton(
                            text="Stream",
                            url=f"https://api.princexd.tech/stream?imdbid={url['imdbId']}",
                        ),
                    ],
                    [
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
    elif page == tpage:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                url["poster"],
                caption=f"""**IMDB Movie Details :**

**Title :** {url["title"]}
**Description :** {url["overview"]}
**Rating :** {url["rating"]}
**Release-Date :** {url["releaseDate"]}
**Popularity :** {url["popularity"]}
**Runtime :** {url["runtime"]}
**Status :** {url["status"]}
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
                            text="Imdb",
                            url=url["imdbLink"],
                        ),
                        InlineKeyboardButton(
                            text="Stream",
                            url=f"https://api.princexd.tech/stream?imdbid={url['imdbId']}",
                        ),
                    ],
                    [
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
    else:
        await callbackquery.edit_message_media(
            InputMediaPhoto(
                url["poster"],
                caption=f"""**IMDB Movie Details :**

**Title :** {url["title"]}
**Description :** {url["overview"]}
**Rating :** {url["rating"]}
**Release-Date :** {url["releaseDate"]}
**Popularity :** {url["popularity"]}
**Runtime :** {url["runtime"]}
**Status :** {url["status"]}
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
                            text="Imdb",
                            url=url["imdbLink"],
                        ),
                        InlineKeyboardButton(
                            text="Stream",
                            url=f"https://api.princexd.tech/stream?imdbid={url['imdbId']}",
                        ),
                    ],
                    [
                        InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
                    ],
                ]
            ),
        )
