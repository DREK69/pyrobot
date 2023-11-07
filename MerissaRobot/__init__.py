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
from pyrogram import Client, errors
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, PeerIdInvalid
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
getLogger("pyrogram").setLevel(ERROR)
getLogger("apscheduler").setLevel(ERROR)
getLogger("telethon").setLevel(ERROR)
getLogger("telegram").setLevel(CRITICAL)
getLogger("sqlalchemy").setLevel(ERROR)


pbot = Client(
    "MerissaRobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    workers=min(32, os.cpu_count() + 4),
    sleep_threshold=60,
    in_memory=True,
)
user = Client(
    "MerissaMusic",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=str(STRING_SESSION),
)
pytgcalls = PyTgCalls(user)
updater = tg.Updater(TOKEN, workers=WORKERS, use_context=True)
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)
dispatcher = updater.dispatcher
aiohttpsession = ClientSession()
BOT_ID = dispatcher.bot.id
BOT_USERNAME = dispatcher.bot.username
BOT_NAME = dispatcher.bot.first_name
BOT_MENTION = ""
ASS_ID = ""
ASS_NAME = ""
ASS_USERNAME = ""
ASS_MENTION = ""


async def startpyro():
    global BOT_ID, BOT_NAME, BOT_USERNAME, BOT_MENTION
    global ASS_ID, ASS_NAME, ASS_USERNAME, ASS_MENTION
    try:
        await pbot.start()
        LOGGER.info("Pyrogram Started")
    except FloodWait as e:
        LOGGER.info(
            f"[Pyrogram: FloodWaitError] Have to wait {e.value} seconds due to FloodWait."
        )
        time.sleep(e.value)
        await pbot.start()
    getme = await pbot.get_me()
    BOT_ID = getme.id
    BOT_NAME = getme.first_name
    BOT_USERNAME = getme.username
    BOT_MENTION = getme.mention
    await user.start()
    getme2 = await user.get_me()
    ASS_ID = getme2.id
    ASS_NAME = getme2.first_name + " " + (getme2.last_name or "")
    ASS_USERNAME = getme2.username
    ASS_MENTION = getme2.mention
    LOGGER.info("Userbot Started")
    await pbot.send_message(-1001446814207, "Bot Started")
    await user.send_message(-1001446814207, "Assistant Started")
    await pytgcalls.start()
    LOGGER.info("Pytgcalls Started")


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
