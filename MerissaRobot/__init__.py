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
from telegram import Update

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
# CRITICAL: Set event loop policy BEFORE creating any clients
# ───────────────────────────────
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
else:
    # For Linux/Unix - use uvloop if available for better performance
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

# Create a single event loop for all components
try:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# ───────────────────────────────
# PTB v22 Application - Created AFTER event loop setup
# ───────────────────────────────
application = (
    Application.builder()
    .token(TOKEN)
    .concurrent_updates(True)
    .build()
)

BOT = application.bot

BOT_ID = None
BOT_USERNAME = None
BOT_NAME = None
BOT_MENTION = "https://t.me/MerissaRobot"

async def init_bot():
    global BOT_ID, BOT_USERNAME, BOT_NAME
    try:
        me = await application.bot.get_me()
        BOT_ID = me.id
        BOT_USERNAME = me.username
        BOT_NAME = me.first_name
        LOGGER.info(f"Bot initialized: {BOT_NAME} (@{BOT_USERNAME})")
    except Exception as e:
        LOGGER.error(f"Failed to initialize bot: {e}")
        raise

ASS_ID = "5249696122"
ASS_NAME = "Merissa Assistant"
ASS_USERNAME = "MerissaAssistant"
ASS_MENTION = "https://t.me/merissaassistant"

# ───────────────────────────────
# Pyrogram + Telethon - FIXED for Single Event Loop
# ───────────────────────────────

# CRITICAL: Create clients with no_updates=True to prevent event loop conflicts
pbot = Client(
    "MerissaRobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    workers=50,  # Reduced workers to prevent conflicts
    no_updates=True,  # CRITICAL: Prevents automatic update handling
)

user = None
pytgcalls = None

# Only create user client if STRING_SESSION is provided
if STRING_SESSION and STRING_SESSION.strip():
    user = Client(
        "MerissaMusic",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=str(STRING_SESSION),
        no_updates=True,  # CRITICAL: Prevents automatic update handling
    )
    pytgcalls = PyTgCalls(user)

# Telethon with MemorySession to prevent file conflicts
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)

# ───────────────────────────────
# Initialize global lists
# ───────────────────────────────
DEV_USERS.add(OWNER_ID)
sw = None

def dirr():
    """Clean up directory and create necessary folders"""
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
    CallbackQueryHandler,
    filters,
    ContextTypes,
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
        if not super().check_update(update):
            return None
            
        if self.has_args is not None:
            message = update.effective_message
            if message and message.text:
                args = message.text.split()[1:]
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
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
            
        super().__init__(
            filters=filters.Regex(pattern),
            callback=callback,
            block=block,
            **kwargs
        )

# ───────────────────────────────
# Client Management Functions - FIXED
# ───────────────────────────────
async def initiate_clients():
    """Initialize all clients with proper error handling"""
    try:
        # Start pyrogram bot client
        if not pbot.is_connected:
            await pbot.start()
            LOGGER.info("Pyrogram Bot Started")
        
        # Start user client if available
        if user and not user.is_connected:
            await user.start()
            LOGGER.info("Pyrogram User Started")
            
            # Start PyTgCalls only if user client is available
            if pytgcalls and not pytgcalls.is_connected:
                await pytgcalls.start()
                LOGGER.info("PyTgCalls Started")
        
        # Start Telethon
        if not telethn.is_connected():
            await telethn.start(bot_token=TOKEN)
            LOGGER.info("Telethon Started")
        
        # Send startup messages
        try:
            if pbot.is_connected:
                await pbot.send_message(-1001446814207, "Bot Started")
            if user and user.is_connected:
                await user.send_message(-1001446814207, "Assistant Started")
        except Exception as e:
            LOGGER.warning(f"Failed to send startup messages: {e}")
            
    except FloodWait as e:
        LOGGER.info(f"FloodWait: Have to wait {e.value} seconds")
        await asyncio.sleep(e.value)
        await initiate_clients()
    except Exception as e:
        LOGGER.error(f"Error starting clients: {e}")
        # Don't raise - let the bot continue with available clients

async def stop_clients():
    """Properly stop all clients"""
    try:
        if pytgcalls and hasattr(pytgcalls, 'stop'):
            try:
                await pytgcalls.stop()
                LOGGER.info("PyTgCalls stopped")
            except:
                pass
                
        if user and user.is_connected:
            try:
                await user.stop()
                LOGGER.info("Pyrogram User stopped")
            except:
                pass
                
        if pbot.is_connected:
            try:
                await pbot.stop()
                LOGGER.info("Pyrogram Bot stopped")
            except:
                pass
                
        if telethn.is_connected():
            try:
                await telethn.disconnect()
                LOGGER.info("Telethon disconnected")
            except:
                pass
                
    except Exception as e:
        LOGGER.error(f"Error stopping clients: {e}")

# ───────────────────────────────
# FIXED: Import after client initialization to prevent circular imports
# ───────────────────────────────
def load_all_modules():
    """Load all modules after clients are initialized"""
    try:
        # Import ALL_MODULES after clients are ready
        from MerissaRobot.Modules import ALL_MODULES
        LOGGER.info("Successfully loaded Modules: " + str(ALL_MODULES))
        return ALL_MODULES
    except Exception as e:
        LOGGER.error(f"Failed to load modules: {e}")
        return []
