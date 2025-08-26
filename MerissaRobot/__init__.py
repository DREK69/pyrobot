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

# CRITICAL: Only import what we absolutely need to avoid conflicts
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
# SIMPLIFIED: Only PTB for main bot operations
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
# LAZY LOADING: Initialize other clients only when needed
# ───────────────────────────────
_pbot = None
_user = None
_pytgcalls = None
_telethn = None

async def get_pbot():
    """Get Pyrogram bot client (lazy loaded)"""
    global _pbot
    if _pbot is None:
        from pyrogram import Client
        _pbot = Client(
            "MerissaRobot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=TOKEN,
            workers=10,
            in_memory=True,
        )
        if not _pbot.is_connected:
            await _pbot.start()
    return _pbot

async def get_user():
    """Get Pyrogram user client (lazy loaded)"""
    global _user
    if _user is None and STRING_SESSION and STRING_SESSION.strip():
        from pyrogram import Client
        _user = Client(
            "MerissaMusic",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=str(STRING_SESSION),
            in_memory=True,
        )
        if not _user.is_connected:
            await _user.start()
    return _user

async def get_pytgcalls():
    """Get PyTgCalls client (lazy loaded)"""
    global _pytgcalls
    if _pytgcalls is None:
        user_client = await get_user()
        if user_client:
            from pytgcalls import PyTgCalls
            _pytgcalls = PyTgCalls(user_client)
            if not _pytgcalls.is_connected:
                await _pytgcalls.start()
    return _pytgcalls

async def get_telethn():
    """Get Telethon client (lazy loaded)"""
    global _telethn
    if _telethn is None:
        from telethon import TelegramClient
        from telethon.sessions import MemorySession
        _telethn = TelegramClient(MemorySession(), API_ID, API_HASH)
        if not _telethn.is_connected():
            await _telethn.start(bot_token=TOKEN)
    return _telethn

# Compatibility aliases - these will return the lazy-loaded clients
pbot = property(lambda self: asyncio.create_task(get_pbot()))
user = property(lambda self: asyncio.create_task(get_user()))
pytgcalls = property(lambda self: asyncio.create_task(get_pytgcalls()))
telethn = property(lambda self: asyncio.create_task(get_telethn()))

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
# SIMPLIFIED Client Management
# ───────────────────────────────
async def initiate_clients():
    """Initialize only PTB - others are lazy loaded"""
    try:
        # Initialize PTB application
        await application.initialize()
        await init_bot()
        LOGGER.info("PTB Application initialized")
        
        # Send startup message using PTB
        try:
            await application.bot.send_message(2030709195, "Merissa Started (PTB Mode)")
        except Exception as e:
            LOGGER.warning(f"Failed to send startup message: {e}")
            
    except Exception as e:
        LOGGER.error(f"Error initializing clients: {e}")
        raise

async def stop_clients():
    """Stop all clients gracefully"""
    try:
        # Stop lazy-loaded clients if they exist
        if _pytgcalls:
            try:
                await _pytgcalls.stop()
                LOGGER.info("PyTgCalls stopped")
            except:
                pass
                
        if _user and _user.is_connected:
            try:
                await _user.stop()
                LOGGER.info("Pyrogram User stopped")
            except:
                pass
                
        if _pbot and _pbot.is_connected:
            try:
                await _pbot.stop()
                LOGGER.info("Pyrogram Bot stopped")
            except:
                pass
                
        if _telethn and _telethn.is_connected():
            try:
                await _telethn.disconnect()
                LOGGER.info("Telethon disconnected")
            except:
                pass
                
    except Exception as e:
        LOGGER.warning(f"Error stopping clients: {e}")

async def graceful_shutdown():
    """Gracefully shutdown all components"""
    try:
        # Stop PTB application
        if hasattr(application, 'running') and application.running:
            await application.stop()
            LOGGER.info("PTB Application stopped")
            
        if hasattr(application, 'shutdown'):
            await application.shutdown()
            LOGGER.info("PTB Application shutdown")
        
        # Stop other clients
        await stop_clients()
        
    except Exception as e:
        LOGGER.error(f"Error during graceful shutdown: {e}")

# ───────────────────────────────
# Module Loading
# ───────────────────────────────
def load_all_modules():
    """Load all modules"""
    try:
        from MerissaRobot.Modules import ALL_MODULES
        LOGGER.info("Successfully loaded Modules: " + str(ALL_MODULES))
        return ALL_MODULES
    except Exception as e:
        LOGGER.error(f"Failed to load modules: {e}")
        return []
