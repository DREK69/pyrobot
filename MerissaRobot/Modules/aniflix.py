import requests
from pyrogram import filters
from pyrogram.types import *

from MerissaRobot import pbot

animeregex = r"https:\/\/anikatsu\.me\/anime\/"


@pbot.on_message(filters.command("aniflix"))
async def animedl(_, message):
    if len(message.command) < 2:
        return message.reply_text(
            "Give some Anime Movie/Series name to Find it on my Database\n\nEx. /aniflix suzume"
        )
    search_results = await message.reply_text("Processing...")
    animeinput = message.text.split(None, 1)[1]
    anime = requests.get(
        f"https://anime.princexd.tech/search?keyw={animeinput}&page=1"
    ).json()
    keyboards = []
    if anime:
        for result in anime:
            animeid = result["anime_id"]
            animeoutput = result["name"]
            keyboard = InlineKeyboardButton(
                animeoutput, callback_data=f"anix|{animeid}"
            )
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        await search_results.edit_text(
            f"Search Results For {animeinput}...", reply_markup=reply_markup
        )
    else:
        await search_results.edit_text(
            "Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Anime Name."
        )


@pbot.on_callback_query(filters.regex(pattern=r"asearch"))
async def anime_result(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    animeinput = callback_data.split(None, 1)[1]
    search_results = await CallbackQuery.message.reply_text("Processing...")
    await CallbackQuery.message.delete()
    anime = requests.get(
        f"https://anime.princexd.tech/search?keyw={animeinput}&page=1"
    ).json()
    keyboards = []
    if anime:
        for result in anime:
            animeid = result["anime_id"]
            animeoutput = result["name"]
            keyboard = InlineKeyboardButton(
                animeoutput, callback_data=f"anix|{animeid}"
            )
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        await search_results.edit_text(
            f"Search Results For {animeinput}...", reply_markup=reply_markup
        )
    else:
        await search_results.edit_text(
            "Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Anime Name."
        )


@pbot.on_message(filters.regex(animeregex))
async def animedl(_, message):
    id = message.text.split("/")[4]
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Stream/Download", callback_data=f"anixx|{id}"),
            ]
        ]
    )
    await message.reply_text(
        text="What would you like to do?",
        reply_markup=button,
    )


@pbot.on_callback_query(filters.regex(pattern=r"anix"))
async def movie_result(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    data = callback_data.split("|")
    id = data[1]
    m = await CallbackQuery.message.edit(
        text="Please Wait Movie/Series Details Fetching From Anikatsu",
        reply_markup=None,
    )
    search = requests.get(f"https://anime.princexd.tech/getAnime/{id}").json()
    name = search["name"]
    oname = search["othername"]
    animetype = search["type"]
    release = search["released"]
    image = search["imageUrl"]
    episodeid = search["episode_id"]
    text = ""
    for episodeId in episodeid:
        episodeid = episodeId["episodeId"]
        episodenum = episodeId["episodeNum"]
        link = f"https://anikatsu.me/watch/{episodeid}"
        text += f"Anime Episode {episodenum}: [Click Here]({link})<br>──────────────────────────────────<br>"
    if animetype == "Movie":
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Stream/Download", url=link)]]
        )
        await CallbackQuery.message.reply_photo(
            image,
            caption=f"Name: {name}\nOtherName: {oname}\nType: {animetype}\nReleased: {release}",
            reply_markup=button,
        )
    else:
        episodes = f"<center><h2>Anime Links of<br>{name}<br>By [@MerissaRobot](https://telegram.dog/MerissaRobot)</center></h2>──────────────────────────────────<br>{text}"
        data = {"content": episodes, "ext": "md"}
        response = requests.post("https://api.princexd.tech/nekobin", json=data).json()[
            "link"
        ]
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Stream/Download", url=response)]]
        )
        await CallbackQuery.message.reply_photo(
            image,
            caption=f"Name: {name}\nOtherName: {oname}\nType: {animetype}\nReleased: {release}",
            reply_markup=button,
        )
    await m.delete()
