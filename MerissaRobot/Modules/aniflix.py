import requests
from pyrogram import filters
from pyrogram.types import *

from MerissaRobot import pbot


@pbot.on_message(filters.command("aniflix"))
async def animedl(_, message):
    if len(message.command) < 2:
        return message.reply_text(
            "Give some Anime Movie/Series name to Find it on my Database\n\nEx. /aniflix suzume"
        )
    search_results = await message.reply_text("Processing...")
    animeinput = message.text.split(None, 1)[1]
    anime = requests.get(
        f"https://animeapi.princexd.vercel.app/search?keyw={animeinput}&page=1"
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
        f"https://animeapi.princexd.vercel.app/search?keyw={animeinput}&page=1"
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


@pbot.on_callback_query(filters.regex(pattern=r"anix"))
async def movie_result(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    data = callback_data.split("|")
    id = data[1]
    m = await CallbackQuery.message.edit(
        text="Please Wait Fetching Movie/Series Details",
        reply_markup=None,
    )
    search = requests.get(f"https://animeapi.princexd.vercel.app/getAnime/{id}").json()
    name = search["name"]
    oname = search["othername"]
    animetype = search["type"]
    release = search["released"]
    image = search["imageUrl"]
    episodeid = search["episode_id"]
    data = {"search": name}
    if animetype == "Movie":
        link = (
            f"https://api.princexd.vercel.app/anime/watch/{episodeid[0]['episodeId']}"
        )
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Stream/Download", url=link)]]
        )
        await CallbackQuery.message.reply_photo(
            image,
            caption=f"Name: {name}\nOtherName: {oname}\nType: {animetype}\nReleased: {release}",
            reply_markup=button,
        )
    else:
        text = ""
        for episodeId in episodeid:
            episodeid = episodeId["episodeId"]
            episodenum = episodeId["episodeNum"]
            link = f"https://api.princexd.vercel.app/anime/watch/{episodeid}"
            text += f"Anime Episode {episodenum}: [Click Here]({link})<br>──────────────────────────────────<br>"
        episodes = f"<center><h2>Anime Links of<br>{name}<br>By [@MerissaRobot](https://telegram.dog/MerissaRobot)</center></h2>──────────────────────────────────<br>{text}"
        data = {"content": episodes}
        key = requests.post("https://nekobin.com/api/documents", json=data).json()[
            "result"
        ]["key"]
        link = f"https://nekobin.com/{key}.md"
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Stream/Download", url=link)]]
        )
        await CallbackQuery.message.reply_photo(
            image,
            caption=f"Name: {name}\nOtherName: {oname}\nType: {animetype}\nReleased: {release}",
            reply_markup=button,
        )
    await m.delete()
