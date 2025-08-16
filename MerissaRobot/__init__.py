import asyncio
import os
import sys
import time
from logging import (
    INFO,
    ERROR,
    StreamHandler,
    basicConfig,
    getLogger,
    handlers,
)

import spamwatch
from aiohttp import ClientSession
from pyrogram import Client
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, PeerIdInvalid
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pyrogram.types import Message
from pyromod import listen  # ignore
from pytgcalls import PyTgCalls
from telethon import TelegramClient
from telethon.sessions import MemorySession

from telegram.ext import Application

from config import *

# ───────────────────────────────
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

# ───────────────────────────────
# PTB v22 Application
# ───────────────────────────────
application = (
    Application.builder()
    .token(TOKEN)
    .concurrent_updates(True)  # multi update processing
    .build()
)

BOT = application.bot  # bot instance after build()

BOT_ID = None
BOT_USERNAME = None
BOT_NAME = None
BOT_MENTION = "https://t.me/MerissaRobot"

async def init_bot():
    global BOT_ID, BOT_USERNAME, BOT_NAME
    me = await application.bot.get_me()
    BOT_ID = me.id
    BOT_USERNAME = me.username
    BOT_NAME = me.first_name

ASS_ID = "5249696122"
ASS_NAME = "Merissa Assistant"
ASS_USERNAME = "MerissaAssistant"
ASS_MENTION = "https://t.me/merissaassistant"

# ───────────────────────────────
# Pyrogram + Telethon
# ───────────────────────────────
pbot = Client(
    "MerissaRobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    workers=100,
)

user = Client(
    "MerissaMusic",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=str(STRING_SESSION),
)
pytgcalls = PyTgCalls(user)

telethn = TelegramClient(MemorySession(), API_ID, API_HASH)

# ───────────────────────────────
DEV_USERS.add(OWNER_ID)
sw = None


def dirr():
    for file in os.listdir():
        if file.endswith((".jpg", ".jpeg")):
            os.remove(file)
    if "downloads" not in os.listdir():
        os.mkdir("downloads")
    LOGGER.info("Directories Updated.")


DRAGONS = list(DRAGONS) + list(DEV_USERS)
DEV_USERS = list(DEV_USERS)
WOLVES = list(WOLVES)
DEMONS = list(DEMONS)
TIGERS = list(TIGERS)

# ───────────────────────────────
# Custom Handlers - PTB v22 Compatible
# ───────────────────────────────
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext
)
from telegram import Update
from typing import List, Optional, Union
import re

class CustomCommandHandler(CommandHandler):
    """Custom Command Handler compatible with PTB v22"""
    
    def __init__(
        self,
        command: Union[str, List[str]],
        callback,
        filters=None,
        block: bool = True,
        has_args: Optional[int] = None,
        **kwargs
    ):
        # Convert old filter system to new filters
        if filters is None:
            filters = ~filters.UpdateType.EDITED_MESSAGE
        
        super().__init__(
            command=command,
            callback=callback,
            filters=filters,
            block=block,
            **kwargs
        )
        self.has_args = has_args

    def check_update(self, update: object) -> Optional[bool]:
        """Override check_update for custom logic"""
        if not super().check_update(update):
            return None
            
        if self.has_args is not None:
            message = update.effective_message
            if message and message.text:
                args = message.text.split()[1:]  # Remove command
                if len(args) < self.has_args:
                    return None
                    
        return True


class CustomMessageHandler(MessageHandler):
    """Custom Message Handler compatible with PTB v22"""
    
    def __init__(
        self,
        filters,
        callback,
        block: bool = True,
        **kwargs
    ):
        # Ensure filters is properly converted
        if filters is None:
            filters = filters.ALL
            
        super().__init__(
            filters=filters,
            callback=callback,
            block=block,
            **kwargs
        )


class CustomRegexHandler(MessageHandler):
    """Custom Regex Handler compatible with PTB v22"""
    
    def __init__(
        self,
        pattern: Union[str, re.Pattern],
        callback,
        block: bool = True,
        **kwargs
    ):
        # Use filters.Regex for pattern matching in PTB v22
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
            
        super().__init__(
            filters=filters.Regex(pattern),
            callback=callback,
            block=block,
            **kwargs
        )


# ───────────────────────────────
# Application startup function
# ───────────────────────────────
async def start_bot():
    """Initialize and start the bot"""
    try:
        # Initialize bot info
        await init_bot()
        
        # Start pyrogram clients
        await pbot.start()
        await user.start()
        
        # Start pytgcalls
        await pytgcalls.start()
        
        # Start telethon
        await telethn.start(bot_token=TOKEN)
        
        # Clean directories
        dirr()
        
        LOGGER.info("Bot started successfully!")
        
        # Start PTB application
        await application.initialize()
        await application.start()
        await application.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
        # Keep running
        await application.updater.idle()
        
    except Exception as e:
        LOGGER.error(f"Error starting bot: {e}")
        raise
    finally:
        # Cleanup
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        
        await pbot.stop()
        await user.stop()
        await pytgcalls.stop()
        await telethn.disconnect()


if __name__ == "__main__":
    # Run the bot
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped by user")
    except Exception as e:
        LOGGER.error(f"Fatal error: {e}")
        sys.exit(1)
