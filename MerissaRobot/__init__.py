import asyncio
import os
import sys
import time
from inspect import getfullargspec
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    StreamHandler,
    basicConfig,
    disable,
    getLogger,
    handlers,
)

import spamwatch
import telegram.ext as tg
from aiohttp import ClientSession
from pyrogram import Client, errors, idle
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, PeerIdInvalid
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pyrogram.types import Message
from pyromod import listen  # ignore
from pytgcalls import PyTgCalls
from telethon import TelegramClient
from telethon.sessions import MemorySession, StringSession

from config import *

StartTime = time.time()

LOGGER = getLogger("[MerissaRobot]")

basicConfig(
    level=INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s.%(funcName)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        handlers.RotatingFileHandler("log.txt", mode="w+", maxBytes=1000000),
        StreamHandler(),
    ],
)
getLogger("pyrogram").setLevel(INFO)
getLogger("telegram").setLevel(INFO)

updater = tg.Updater(TOKEN, workers=WORKERS, use_context=True)
dispatcher = updater.dispatcher

BOT_ID = dispatcher.bot.id
BOT_USERNAME = dispatcher.bot.username
BOT_NAME = dispatcher.bot.first_name
BOT_MENTION = "https://t.me/MerissaRobot"
ASS_ID = "5249696122"
ASS_NAME = "Merissa Assistant"
ASS_USERNAME = "MerissaAssistant"
ASS_MENTION = "https://t.me/merissaassistant"

pbot = Client(
    "MerissaRobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
)
user = Client(
    "MerissaMusic",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=str(STRING_SESSION),
)
pytgcalls = PyTgCalls(user)

DEV_USERS.add(OWNER_ID)
sw = None

DRAGONS = list(DRAGONS) + list(DEV_USERS)
DEV_USERS = list(DEV_USERS)
WOLVES = list(WOLVES)
DEMONS = list(DEMONS)
TIGERS = list(TIGERS)

# Load at end to ensure all prev variables have been set
from MerissaRobot.Handler.handlers import (
    CustomCommandHandler,
    CustomMessageHandler,
    CustomRegexHandler,
)

# make sure the regex handler can take extra kwargs
tg.RegexHandler = CustomRegexHandler
tg.CommandHandler = CustomCommandHandler
tg.MessageHandler = CustomMessageHandler
