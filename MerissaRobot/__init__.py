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
# CRITICAL: Create a single shared event loop for ALL frameworks
# ───────────────────────────────
def setup_event_loop():
    """Setup single event loop for all frameworks"""
    try:
        # Try to get existing loop
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Loop is closed")
    except RuntimeError:
        # Create new loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Set policy for better compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    else:
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass
    
    return loop

# Setup event loop FIRST
EVENT_LOOP = setup_event_loop()

# ───────────────────────────────
# PTB v22 Application
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

ASS_ID = "7946751397"
ASS_NAME = "Merissa Assistant"
ASS_USERNAME = "Cjjdjdjjdj"
ASS_MENTION = "https://t.me/Cjjdjdjjdj"

# ───────────────────────────────
# FIXED: Create clients but don't start them immediately
# ───────────────────────────────

# Create clients without starting
pbot = Client(
    "MerissaRobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    workers=10,
    in_memory=True,
)

user = None
pytgcalls = None

if STRING_SESSION and STRING_SESSION.strip():
    user = Client(
        "MerissaMusic",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=str(STRING_SESSION),
        in_memory=True,
    )
    pytgcalls = PyTgCalls(user)

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
# CRITICAL FIX: Client Management with Controlled Startup
# ───────────────────────────────
_clients_started = False

async def initiate_clients():
    """Initialize all clients in controlled manner"""
    global _clients_started
    
    if _clients_started:
        return
        
    try:
        LOGGER.info("Starting clients initialization...")
        
        # Start Pyrogram clients FIRST (they create fewer conflicts)
        if not pbot.is_connected:
            await pbot.start()
            LOGGER.info("Pyrogram Bot started")
        
        if user and not user.is_connected:
            await user.start()
            LOGGER.info("Pyrogram User started")
            
            if pytgcalls and not pytgcalls.is_connected:
                await pytgcalls.start()
                LOGGER.info("PyTgCalls started")
        
        # Start Telethon LAST
        if not telethn.is_connected():
            await telethn.start(bot_token=TOKEN)
            LOGGER.info("Telethon started")
        
        _clients_started = True
        LOGGER.info("All clients initialized successfully")
        
        # Send startup messages
        try:
            await pbot.send_message(-1002846516370, "Bot Started")
            if user:
                await user.send_message(-1002846516370, "Assistant Started")
        except Exception as e:
            LOGGER.warning(f"Failed to send startup messages: {e}")
            
    except FloodWait as e:
        LOGGER.info(f"FloodWait: Have to wait {e.value} seconds")
        await asyncio.sleep(e.value)
        _clients_started = False  # Reset flag to retry
        await initiate_clients()
    except Exception as e:
        LOGGER.error(f"Error starting clients: {e}")
        raise

async def stop_clients():
    """Stop all clients in reverse order"""
    global _clients_started
    
    try:
        # Stop in reverse order
        if pytgcalls and hasattr(pytgcalls, 'stop'):
            try:
                await pytgcalls.stop()
                LOGGER.info("PyTgCalls stopped")
            except Exception as e:
                LOGGER.warning(f"Error stopping PyTgCalls: {e}")
                
        if user and user.is_connected:
            try:
                await user.stop()
                LOGGER.info("Pyrogram User stopped")
            except Exception as e:
                LOGGER.warning(f"Error stopping User client: {e}")
                
        if pbot.is_connected:
            try:
                await pbot.stop()
                LOGGER.info("Pyrogram Bot stopped")
            except Exception as e:
                LOGGER.warning(f"Error stopping Bot client: {e}")
                
        if telethn.is_connected():
            try:
                await telethn.disconnect()
                LOGGER.info("Telethon disconnected")
            except Exception as e:
                LOGGER.warning(f"Error disconnecting Telethon: {e}")
        
        _clients_started = False
        
        # Cancel pending tasks related to pyrogram
        try:
            current_task = asyncio.current_task()
            all_tasks = [t for t in asyncio.all_tasks() if t != current_task and not t.done()]
            
            # Filter pyrogram related tasks
            pyrogram_tasks = [
                t for t in all_tasks 
                if hasattr(t.get_coro(), 'cr_code') and 
                'pyrogram' in str(t.get_coro().cr_code.co_filename)
            ]
            
            if pyrogram_tasks:
                LOGGER.info(f"Cancelling {len(pyrogram_tasks)} pyrogram tasks...")
                for task in pyrogram_tasks:
                    task.cancel()
                
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*pyrogram_tasks, return_exceptions=True),
                        timeout=5.0
                    )
                    LOGGER.info("Pyrogram tasks cancelled successfully")
                except asyncio.TimeoutError:
                    LOGGER.warning("Some pyrogram tasks took too long to cancel")
                except Exception as e:
                    LOGGER.warning(f"Error cancelling pyrogram tasks: {e}")
                    
        except Exception as e:
            LOGGER.warning(f"Error during task cleanup: {e}")
                
    except Exception as e:
        LOGGER.error(f"Error stopping clients: {e}")

async def graceful_shutdown():
    """Gracefully shutdown all components"""
    try:
        # Stop clients first
        await stop_clients()
        
        # Then stop PTB
        if hasattr(application, 'running') and application.running:
            await application.stop()
            LOGGER.info("PTB Application stopped")
            
        if hasattr(application, 'shutdown'):
            await application.shutdown()
            LOGGER.info("PTB Application shutdown")
        
        # Small delay for cleanup
        await asyncio.sleep(0.5)
        
    except Exception as e:
        LOGGER.error(f"Error during graceful shutdown: {e}")

# ───────────────────────────────
# Module Loading
# ───────────────────────────────
def load_all_modules():
    """Load all modules after clients are ready"""
    try:
        from MerissaRobot.Modules import ALL_MODULES
        LOGGER.info("Successfully loaded Modules: " + str(ALL_MODULES))
        return ALL_MODULES
    except Exception as e:
        LOGGER.error(f"Failed to load modules: {e}")
        return []
