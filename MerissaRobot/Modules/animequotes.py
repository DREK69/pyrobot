import json
import random
from typing import Tuple, Optional

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler

from MerissaRobot import application
from MerissaRobot.Modules.disable import DisableAbleCommandHandler


async def anime_quote() -> Tuple[str, str, str]:
    """
    Fetch a random anime quote from AnimeChan API.
    
    Returns:
        Tuple of (quote, character, anime) or fallback values if API fails
    """
    url = "https://animechan.vercel.app/api/random"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        dic = response.json()  # Use .json() instead of json.loads(response.text)
        quote = dic.get("quote", "Life is not a game of luck. If you wanna win, work hard.")
        character = dic.get("character", "Sora")
        anime = dic.get("anime", "No Game No Life")
        
        return quote, character, anime
        
    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        # Fallback quote if API fails
        return (
            "Life is not a game of luck. If you wanna win, work hard.",
            "Sora",
            "No Game No Life"
        )


async def quotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a random anime quote with a refresh button"""
    message = update.effective_message
    quote, character, anime = await anime_quote()
    
    msg = f"<i>❝{quote}❞</i>\n\n<b>{character} from {anime}</b>"
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Change🔁", callback_data="change_quote")]]
    )
    
    await message.reply_text(
        msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


async def change_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback query to change the quote"""
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    
    # Answer the callback query to remove loading state
    await query.answer()
    
    quote, character, anime = await anime_quote()
    msg = f"<i>❝{quote}❞</i>\n\n<b>{character} from {anime}</b>"
    
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Change🔁", callback_data="change_quote")]]
    )
    
    try:
        await message.edit_text(
            msg, 
            reply_markup=keyboard, 
            parse_mode=ParseMode.HTML
        )
    except Exception:
        # If editing fails, send a new message
        await message.reply_text(
            msg,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )


async def animequotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a random anime quote image"""
    message = update.effective_message
    
    # Get user name for mention (though not used in current implementation)
    user_name = (
        message.reply_to_message.from_user.first_name
        if message.reply_to_message
        else message.from_user.first_name
    )
    
    try:
        # Send a random anime quote image
        await message.reply_photo(
            photo=random.choice(QUOTES_IMG),
            caption=f"Here's an anime quote for you, {user_name}! 🌸"
        )
    except Exception as e:
        # If sending photo fails, send a text message instead
        await message.reply_text(
            "Sorry, I couldn't send the anime quote image right now. Please try again later!"
        )


# Collection of anime quote images
QUOTES_IMG = (
    "https://i.imgur.com/Iub4RYj.jpg",
    "https://i.imgur.com/uvNMdIl.jpg",
    "https://i.imgur.com/YOBOntg.jpg",
    "https://i.imgur.com/fFpO2ZQ.jpg",
    "https://i.imgur.com/f0xZceK.jpg",
    "https://i.imgur.com/RlVcCip.jpg",
    "https://i.imgur.com/CjpqLRF.jpg",
    "https://i.imgur.com/8BHZDk6.jpg",
    "https://i.imgur.com/8bHeMgy.jpg",
    "https://i.imgur.com/5K3lMvr.jpg",
    "https://i.imgur.com/NTzw4RN.jpg",
    "https://i.imgur.com/wJxryAn.jpg",
    "https://i.imgur.com/9L0DWzC.jpg",
    "https://i.imgur.com/sBe8TTs.jpg",
    "https://i.imgur.com/1Au8gdf.jpg",
    "https://i.imgur.com/28hFQeU.jpg",
    "https://i.imgur.com/Qvc03JY.jpg",
    "https://i.imgur.com/gSX6Xlf.jpg",
    "https://i.imgur.com/iP26Hwa.jpg",
    "https://i.imgur.com/uSsJoX8.jpg",
    "https://i.imgur.com/OvX3oHB.jpg",
    "https://i.imgur.com/JMWuksm.jpg",
    "https://i.imgur.com/lhM3fib.jpg",
    "https://i.imgur.com/64IYKkw.jpg",
    "https://i.imgur.com/nMbyA3J.jpg",
    "https://i.imgur.com/7KFQhY3.jpg",
    "https://i.imgur.com/mlKb7zt.jpg",
    "https://i.imgur.com/JCQGJVw.jpg",
    "https://i.imgur.com/hSFYDEz.jpg",
    "https://i.imgur.com/PQRjAgl.jpg",
    "https://i.imgur.com/ot9624U.jpg",
    "https://i.imgur.com/iXmqN9y.jpg",
    "https://i.imgur.com/RhNBeGr.jpg",
    "https://i.imgur.com/tcMVNa8.jpg",
    "https://i.imgur.com/LrVg810.jpg",
    "https://i.imgur.com/TcWfQlz.jpg",
    "https://i.imgur.com/muAUdvJ.jpg",
    "https://i.imgur.com/AtC7ZRV.jpg",
    "https://i.imgur.com/sCObQCQ.jpg",
    "https://i.imgur.com/AJFDI1r.jpg",
    "https://i.imgur.com/TCgmRrH.jpg",
    "https://i.imgur.com/LMdmhJU.jpg",
    "https://i.imgur.com/eyyax0N.jpg",
    "https://i.imgur.com/YtYxV66.jpg",
    "https://i.imgur.com/292w4ye.jpg",
    "https://i.imgur.com/6Fm1vdw.jpg",
    "https://i.imgur.com/2vnBOZd.jpg",
    "https://i.imgur.com/j5hI9Eb.jpg",
    "https://i.imgur.com/cAv7pJB.jpg",
    "https://i.imgur.com/jvI7Vil.jpg",
    "https://i.imgur.com/fANpjsg.jpg",
    "https://i.imgur.com/5o1SJyo.jpg",
    "https://i.imgur.com/dSVxmh8.jpg",
    "https://i.imgur.com/02dXlAD.jpg",
    "https://i.imgur.com/htvIoGY.jpg",
    "https://i.imgur.com/hy6BXOj.jpg",
    "https://i.imgur.com/OuwzNYu.jpg",
    "https://i.imgur.com/L8vwvc2.jpg",
    "https://i.imgur.com/3VMVF9y.jpg",
    "https://i.imgur.com/yzjq2n2.jpg",
    "https://i.imgur.com/0qK7TAN.jpg",
    "https://i.imgur.com/zvcxSOX.jpg",
    "https://i.imgur.com/FO7bApW.jpg",
    "https://i.imgur.com/KK06gwg.jpg",
    "https://i.imgur.com/6lG4tsO.jpg",
)

# Handler definitions for PTB v22
ANIMEQUOTES_HANDLER = DisableAbleCommandHandler("animequotes", animequotes)
QUOTES_HANDLER = DisableAbleCommandHandler("quote", quotes)

# Callback query handlers with updated patterns
CHANGE_QUOTE = CallbackQueryHandler(change_quote, pattern=r"change_.*")
QUOTE_CHANGE = CallbackQueryHandler(change_quote, pattern=r"quote_.*")

# Add handlers to application
application.add_handler(CHANGE_QUOTE)
application.add_handler(QUOTE_CHANGE)
application.add_handler(ANIMEQUOTES_HANDLER)
application.add_handler(QUOTES_HANDLER)

__command_list__ = [
    "animequotes",
    "quote",
]

__handlers__ = [
    ANIMEQUOTES_HANDLER,
    QUOTES_HANDLER,
    CHANGE_QUOTE,
    QUOTE_CHANGE,
]
