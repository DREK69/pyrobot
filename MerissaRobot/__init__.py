import asyncio
import os
import sys
import time
from inspect import getfullargspec
from logging import (
    CRITICAL,
    ERROR,
    INFO,
    DEBUG,
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
from redis import StrictRedis
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
getLogger("telethon").setLevel(ERROR)
getLogger("telegram").setLevel(ERROR)
getLogger("sqlalchemy").setLevel(DEBUG)
disable(DEBUG)

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    quit(1)

    from config import *

    TOKEN = TOKEN
    OWNER_ID = OWNER_ID
    try:
        OWNER_ID = int(OWNER_ID)
    except ValueError:
        raise Exception("Your OWNER_ID variable is not a valid integer.")

    try:
        DRAGONS = {int(x) for x in os.environ.get("DRAGONS", "1218405248").split()}
        DEV_USERS = {int(x) for x in os.environ.get("DEV_USERS", "2030709195").split()}
    except ValueError:
        raise Exception("Your sudo or dev users list does not contain valid integers.")

    try:
        DEMONS = {int(x) for x in os.environ.get("DEMONS", "1218405248").split()}
    except ValueError:
        raise Exception("Your support users list does not contain valid integers.")

    try:
        WOLVES = {int(x) for x in os.environ.get("WOLVES", "1218405248").split()}
    except ValueError:
        raise Exception("Your whitelisted users list does not contain valid integers.")

    try:
        TIGERS = {int(x) for x in os.environ.get("TIGERS", "1218405248").split()}
    except ValueError:
        raise Exception("Your tiger users list does not contain valid integers.")

    try:
        BL_CHATS = {int(x) for x in os.environ.get("BL_CHATS", "").split()}
    except ValueError:
        raise Exception("Your blacklisted chats list does not contain valid integers.")

    JOIN_LOGGER = JOIN_LOGGER
    OWNER_USERNAME = OWNER_USERNAME
    ALLOW_CHATS = ALLOW_CHATS
    DRAGONS = {int(x) for x in os.environ.get("DRAGONS", "1218405248").split()}
    EVENT_LOGS = EVENT_LOGS
    ERROR_LOG = ERROR_LOG
    WEBHOOK = WEBHOOK
    URL = URL
    PORT = PORT
    CERT_PATH = CERT_PATH
    API_ID = API_ID
    API_HASH = API_HASH
    BOT_USERNAME = BOT_USERNAME
    DB_URI = SQLALCHEMY_DATABASE_URI
    MONGO_DB_URI = MONGO_DB_URI
    ARQ_API_KEY = ARQ_API_KEY
    ARQ_API_URL = ARQ_API_URL
    HEROKU_API_KEY = HEROKU_API_KEY
    HEROKU_APP_NAME = HEROKU_APP_NAME
    TEMP_DOWNLOAD_DIRECTORY = TEMP_DOWNLOAD_DIRECTORY
    OPENWEATHERMAP_ID = OPENWEATHERMAP_ID
    BOT_ID = BOT_ID
    API_ID = API_ID
    API_HASH = API_HASH
    STRING_SESSION = STRING_SESSION
    MERISSA_TOKEN = MERISSA_TOKEN
    STRICT_GMUTE = STRICT_GMUTE
    VIRUS_API_KEY = VIRUS_API_KEY
    DONATION_LINK = DONATION_LINK
    LOAD = LOAD
    NO_LOAD = NO_LOAD
    DEL_CMDS = DEL_CMDS
    STRICT_GBAN = STRICT_GBAN
    STRING_SESSION = STRING_SESSION
    WORKERS = WORKERS
    BAN_STICKER = AN_STICKER
    ALLOW_EXCL = ALLOW_EXCL
    CASH_API_KEY = CASH_API_KEY
    TIME_API_KEY = TIME_API_KEY
    AI_API_KEY = AI_API_KEY
    WALL_API = WALL_API
    SUPPORT_CHAT = SUPPORT_CHAT
    SPAMWATCH_SUPPORT_CHAT = SPAMWATCH_SUPPORT_CHAT
    IBM_WATSON_CRED_PASSWORD = IBM_WATSON_CRED_PASSWORD
    IBM_WATSON_CRED_URL = IBM_WATSON_CRED_URL
    SPAMWATCH_API = SPAMWATCH_API
    INFOPIC = INFOPIC

    try:
        BL_CHATS = set(int(x) for x in Config.BL_CHATS or [])
    except ValueError:
        raise Exception("Your blacklisted chats list does not contain valid integers.")

DEV_USERS.add(OWNER_ID)

sw = None

updater = tg.Updater(TOKEN, workers=WORKERS, use_context=True)
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)
dispatcher = updater.dispatcher
aiohttpsession = ClientSession()

pbot = Client(
    "MerissaRobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
)

BOT_ID = dispatcher.bot.id
BOT_USERNAME = dispatcher.bot.username
BOT_NAME = dispatcher.bot.first_name


async def eor(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})


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
