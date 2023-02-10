import pyshorteners
import requests
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackQueryHandler, CommandHandler

from MerissaRobot import dispatcher

url_list = {}


def search_movies(query):
    movies_list = []
    movies_details = {}
    website = BeautifulSoup(
        requests.get(f"https://185.53.88.104/?s={query.replace(' ', '+')}").text,
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
            s = pyshorteners.Shortener()
            url = s.tinyurl.short(i["href"])
            final_links[f"{i.text}"] = url
        movie_details["links"] = final_links
    return movie_details


def find_movie(update, context):
    search_results = update.message.reply_text("Processing...")
    query = update.message.text.split(None, 1)[1]
    movies_list = search_movies(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = InlineKeyboardButton(
                movie["title"], callback_data=f"m_{movie['id']}"
            )
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        search_results.edit_text(
            f"Search Results For {query}...", reply_markup=reply_markup
        )
    else:
        search_results.edit_text(
            "Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name."
        )


def movie_result(update, context) -> None:
    query = update.callback_query
    id = query.data.split("_")[1]
    query.message.edit_text(
        text="Please Wait Movie Details Fetching From MKVCinemas", reply_markup=None
    )
    s = get_movie(id)
    link = ""
    links = s["links"]
    for i in links:
        link += f"🎬{i}\n         └ [Click Here To Download]({links[i]})\n\n"
    caption = f"📥 Download Links is Here:-\n\n{link}Credits To MKVCinemas\nPowered By @MerissaRobot"
    if len(caption) > 4095:
        for x in range(0, len(caption), 4095):
            query.message.reply_text(
                text=caption[x : x + 4095],
                reply_markup=None,
                parse_mode=ParseMode.MARKDOWN,
            )
            query.message.delete()
    else:
        query.message.edit_text(
            text=caption, reply_markup=None, parse_mode=ParseMode.MARKDOWN
        )


def search_anime(query):
    movies_list = []
    movies_details = {}
    website = BeautifulSoup(
        requests.get(f"https://mkvanime.cfd/?s={query.replace(' ', '+')}").text,
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
            s = pyshorteners.Shortener()
            url = s.tinyurl.short(i["href"])
            final_links[f"{i.text}"] = url
        movie_details["links"] = final_links
    return movie_details


def find_anime(update, context):
    search_results = update.message.reply_text("Processing...")
    query = update.message.text.split(None, 1)[1]
    movies_list = search_anime(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = InlineKeyboardButton(
                movie["title"], callback_data=f"a_{movie['id']}"
            )
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        search_results.edit_text(
            f"Search Results For {query}...", reply_markup=reply_markup
        )
    else:
        search_results.edit_text(
            "Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name."
        )


def anime_result(update, context) -> None:
    query = update.callback_query
    id = query.data.split("_")[1]
    query.message.edit_text(
        text="Please Wait Movie Details Fetching From MKVCinemas", reply_markup=None
    )
    s = get_anime(id)
    link = ""
    links = s["links"]
    for i in links:
        link += f"🎬{i}\n         └ [Click Here To Download]({links[i]})\n\n"
    caption = f"📥 Download Links is Here:-\n\n{link}Credits To MKVCinemas\nPowered By @MerissaRobot"
    if len(caption) > 4095:
        for x in range(0, len(caption), 4095):
            query.message.reply_text(
                text=caption[x : x + 4095],
                reply_markup=None,
                parse_mode=ParseMode.MARKDOWN,
            )
            query.message.delete()
    else:
        query.message.edit_text(
            text=caption, reply_markup=None, parse_mode=ParseMode.MARKDOWN
        )


dispatcher.add_handler(CommandHandler("movie", find_movie))
dispatcher.add_handler(CallbackQueryHandler(movie_result, pattern=r"m_"))
dispatcher.add_handler(CommandHandler("anime", find_anime))
dispatcher.add_handler(CallbackQueryHandler(movie_result, pattern=r"a_"))
