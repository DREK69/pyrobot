import requests
from pyrogram import filters
from pyrogram.types import *

from MerissaRobot import pbot as bot


@bot.on_message(filters.command(["ameme", "animememe"]))
async def animememes(_, m):
    res = requests.get("https://api.princexd.tech/reddit?query=Animememe").json()[
        "data"
    ]
    url = res["image_url"]
    text = res["title"]
    link = res["post_url"]
    await m.reply_photo(
        url,
        caption=f"[{text}]({link})",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="ameme",
                    ),
                ],
            ],
        ),
    )


@bot.on_callback_query(filters.regex("ameme"))
async def ameme(_, query: CallbackQuery):
    res = requests.get("https://api.princexd.tech/reddit?query=Animememe").json()[
        "data"
    ]
    url = res["image_url"]
    text = res["title"]
    link = res["post_url"]
    await query.edit_message_media(
        InputMediaPhoto(url, caption=f"[{text}]({link})"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="ameme",
                    ),
                ],
            ],
        ),
    )


@bot.on_message(filters.command("meme"))
async def memes(_, m):
    res = requests.get("https://api.princexd.tech/meme").json()
    url = res["image"]
    text = res["title"]
    link = res["postLink"]
    await m.reply_photo(
        url,
        caption=f"[{text}]({link})",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="bmeme",
                    ),
                ],
            ],
        ),
    )


@bot.on_callback_query(filters.regex("bmeme"))
async def memess(_, query: CallbackQuery):
    res = requests.get("https://api.princexd.tech/meme").json()
    url = res["image"]
    text = res["title"]
    link = res["postLink"]
    await query.edit_message_media(
        InputMediaPhoto(url, caption=f"[{text}]({link})"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="bmeme",
                    ),
                ],
            ],
        ),
    )


@bot.on_message(filters.command(["hmeme", "hentaimeme"]))
async def hetaimemes(_, m):
    res = requests.get("https://meme-api.herokuapp.com/gimme/hentaimemes").json()
    url = res["url"]
    text = res["title"]
    link = res["postLink"]
    await m.reply_photo(
        url,
        caption=f"[{text}]({link})",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="cmeme",
                    ),
                ],
            ],
        ),
    )


@bot.on_callback_query(filters.regex("cmeme"))
async def hmeme(_, query: CallbackQuery):
    res = requests.get("https://meme-api.herokuapp.com/gimme/hentaimemes").json()
    url = res["url"]
    text = res["title"]
    link = res["postLink"]
    await query.edit_message_media(
        InputMediaPhoto(url, caption=f"[{text}]({link})"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data="cmeme",
                    ),
                ],
            ],
        ),
    )


__mod_name__ = "Fun 👻"

__help__ = """
*Play Games Online*:
- /games : To get all Games

*Play Game With Emojis:*
/dice - Dice 🎲
/dart - Dart 🎯
/basket - Basket Ball 🏀
/bowling - Bowling Ball 🎳
/football - Football ⚽
/slot - Spin slot machine 🎰

- Fun Commands
❂ /runs*:* reply a random string from an array of replies
❂ /slap*:* slap a user, or get slapped if not a reply
❂ /shrug*:* get shrug XD
❂ /table*:* get flip/unflip :v
❂ /decide*:* Randomly answers yes/no/maybe
❂ /toss*:* Tosses A coin
❂ /bluetext*:* check urself :V
❂ /roll*:* Roll a dice
❂ /rlg*:* Join ears,nose,mouth and create an emo ;-;
❂ /shout <keyword>*:* write anything you want to give loud shout
❂ /weebify <text>*:* returns a weebified text
❂ /sanitize*:* always use this before /pat or any contact
❂ /pat*:* pats a user, or get patted
❂ /8ball*:* predicts using 8ball method

- Font Command 
- /font <text> - to Get Different types of fonts

- Animation
❂ /love 
❂ /hack 
❂ /bombs 

- Shippering
❂ /couples - get couples of today"""
