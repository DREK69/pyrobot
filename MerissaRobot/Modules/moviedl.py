import requests
from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MerissaRobot import pbot
from MerissaRobot.helpers import subscribe

url_list = {}


def search_movies(query):
    movies_list = []
    movies_details = {}
    website = BeautifulSoup(
        requests.get(f"https://mkvcinemas.rsvp/?s={query.replace(' ', '+')}").text,
        "html.parser",
    )
    movies = website.find_all("a", {"class": "ml-mask jt"})
    for movie in movies:
        if movie:
            movies_details["id"] = f"link{movies.index(movie)}"
            movies_details["title"] = movie.find("span", {"class": "mli-info"}).text
            url_list[movies_details["id"]] = movie["href"]
        movies_list.append(movies_details)
        movies_details = {}
    return movies_list


def get_movie(query):
    movie_details = {}
    if "https" in query:
        movie_page_link = BeautifulSoup(requests.get(query).text, "html.parser")
    else:
        movie_page_link = BeautifulSoup(
            requests.get(f"{url_list[query]}").text, "html.parser"
        )
    if movie_page_link:
        title = movie_page_link.find("div", {"class": "mvic-desc"}).h3.text
        movie_details["title"] = title
        img = movie_page_link.find("div", {"class": "mvic-thumb"})["data-bg"]
        movie_details["img"] = img
        links = movie_page_link.find_all(
            "a", {"rel": "noopener", "data-wpel-link": "internal"}
        )
        final_links = {}
        for i in links:
            url = i["href"]
            final_links[f"{i.text}"] = url
        movie_details["links"] = final_links
    return movie_details


@pbot.on_message(filters.command("moviedl"))
@subscribe
async def find_movie(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Give some Movie/Series name to Find it on my Database\n\nEx. /moviedl pathaan"
        )
    m = await message.reply_text("Processing...")
    query = message.text.split(None, 1)[1]
    movies_list = search_movies(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = InlineKeyboardButton(
                movie["title"], callback_data=f"moviedl {movie['id']}"
            )
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        await m.edit_text(f"Search Results For {query}...", reply_markup=reply_markup)
    else:
        await m.edit_text(
            "Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name."
        )


@pbot.on_callback_query(filters.regex(pattern=r"moviedl"))
async def movie_result(Client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    id = callback_data.split(None, 1)[1]
    m = await CallbackQuery.message.edit(
        text="Please Wait Movie/Series Details Fetching From MKVCinemas",
        reply_markup=None,
    )
    s = get_movie(id)
    link = ""
    links = s["links"]
    for i in links:
        link += (
            f"🎬{i}<br>         └ <a href={links[i]}>Click Here To Download</a><br><br>"
        )
    caption = f"📥 Download Links is Here:-<br><br>{link}Powered By <a href='https://telegram.dog/MerissaRobot'>@MerissaRobot</a>"
    data = {"content": caption, "ext": "md"}
    response = requests.post("https://nekobin.com/api/documents", json=data).json()[
        "link"
    ]
    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Download Links", url=response)]]
    )
    await m.edit_text(
        text="Your Movie/Series Downloading Link is in Button", reply_markup=button
    )


@pbot.on_message(filters.command("movie"))
@subscribe
async def find_streammovie(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Give some Movie/Series name to Find it on my Database\n\nEx. /moviedl pathaan"
        )
    search_results = await message.reply_text("Processing...")
    query = message.text.split(None, 1)[1]
    movies_list = requests.get(f"https://yasirapi.eu.org/lk21?q={query}").json()[
        "result"
    ]
    if movies_list:
        link = ""
        for movie in movies_list:
            link += f"🎬Movie: {movie['judul']}<br>└  <a href={movie['dl']}>Download</a>  |  <a href={movie['link']}>Stream</a><br><br>"
        caption = f"📥 Download/Stream Links is Here:-<br><br>{link}Powered By <a href='https://telegram.dog/MerissaRobot'>@MerissaRobot</a>"
        data = {"content": caption, "ext": "md"}
        response = requests.post("https://nekobin.com/api/documents", json=data).json()[
            "result"
        ]["key"]
        link = f"https://nekobin.com/{key}.md"
        button = InlineKeyboardMarkup([[InlineKeyboardButton(f"{query}", url=link)]])
        await search_results.edit_text(
            text="Your Movie Downloading/Streaming Link", reply_markup=button
        )
    else:
        await search_results.edit_text(
            "Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name."
        )


def search_anime(query):
    movies_list = []
    movies_details = {}
    website = BeautifulSoup(
        requests.get(f"https://ww1.mkvanime.site/?s={query.replace(' ', '+')}").text,
        "html.parser",
    )
    movies = website.find_all("a", {"class": "ml-mask jt"})
    for movie in movies:
        if movie:
            movies_details["id"] = f"link{movies.index(movie)}"
            movies_details["title"] = movie.find("span", {"class": "mli-info"}).text
            url_list[movies_details["id"]] = movie["href"]
        movies_list.append(movies_details)
        movies_details = {}
    return movies_list


def get_anime(query):
    movie_details = {}
    movie_page_link = BeautifulSoup(
        requests.get(f"{url_list[query]}").text, "html.parser"
    )
    if movie_page_link:
        title = movie_page_link.find("div", {"class": "mvic-desc"}).h3.text
        movie_details["title"] = title
        img = movie_page_link.find("div", {"class": "mvic-thumb"})["data-bg"]
        movie_details["img"] = img
        links = movie_page_link.find_all(
            "a", {"rel": "noopener", "data-wpel-link": "internal"}
        )
        final_links = {}
        for i in links:
            url = i["href"]
            final_links[f"{i.text}"] = url
        movie_details["links"] = final_links
    return movie_details


@pbot.on_message(filters.command("animedl"))
@subscribe
async def find_anime(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Give some Movie/Series name to Find it on my Database\n\nEx. /animedl naruto"
        )
    search_results = await message.reply_text("Processing...")
    query = message.text.split(None, 1)[1]
    movies_list = search_anime(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = InlineKeyboardButton(
                movie["title"], callback_data=f"animedl {movie['id']}"
            )
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        await search_results.edit_text(
            f"Search Results For {query}...", reply_markup=reply_markup
        )
    else:
        await search_results.edit_text(
            "Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name."
        )


@pbot.on_callback_query(filters.regex(pattern=r"animedl"))
async def anime_result(Client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    id = callback_data.split(None, 1)[1]
    m = await CallbackQuery.message.edit(
        text="Please Wait Movie Details Fetching From MKVCinemas", reply_markup=None
    )
    s = get_anime(id)
    link = ""
    links = s["links"]
    for i in links:
        link += (
            f"🎬{i}<br>         └ <a href={links[i]}>Click Here To Download</a><br><br>"
        )
    caption = f"📥 Download Links is Here:-<br><br>{link}Powered By <a href='https://telegram.dog/MerissaRobot'>@MerissaRobot</a>"
    data = {"content": caption, "ext": "md"}
    response = requests.post("https://nekobin.com/api/documents", json=data).json()[
        "result"
    ]["key"]
    link = f"https://nekobin.com/{key}.md"
    button = InlineKeyboardMarkup([[InlineKeyboardButton("Download Links", url=link)]])
    await m.edit_text(
        text="Your Movie/Series Downloading Link is in Button", reply_markup=button
    )
