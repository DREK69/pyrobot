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
# Startup notification function
# ───────────────────────────────
async def send_startup_notification():
    """Send startup notification to owner"""
    try:
        if OWNER_ID:
            await application.bot.send_message(
                chat_id=OWNER_ID,
                text=f"🚀 {BOT_NAME} has started successfully!\n"
                     f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                     f"🤖 Bot: @{BOT_USERNAME}"
            )
            LOGGER.info("Startup notification sent successfully")
    except Exception as e:
        LOGGER.error(f"Failed to send startup notification: {e}")


# ───────────────────────────────
# Application startup function
# ───────────────────────────────
async def start_clients():
    """Start all clients"""
    try:
        LOGGER.info("Starting Pyrogram bot client...")
        await pbot.start()
        LOGGER.info("Pyrogram bot client started")
        
        if STRING_SESSION:
            LOGGER.info("Starting Pyrogram user client...")
            await user.start()
            LOGGER.info("Pyrogram user client started")
            
            LOGGER.info("Starting PyTgCalls...")
            await pytgcalls.start()
            LOGGER.info("PyTgCalls started")
        else:
            LOGGER.warning("STRING_SESSION not provided, skipping user client and PyTgCalls")
        
        LOGGER.info("Starting Telethon client...")
        await telethn.start(bot_token=TOKEN)
        LOGGER.info("Telethon client started")
        
    except Exception as e:
        LOGGER.error(f"Error starting clients: {e}")
        raise


async def stop_clients():
    """Stop all clients"""
    try:
        LOGGER.info("Stopping clients...")
        
        if pbot.is_connected:
            await pbot.stop()
            LOGGER.info("Pyrogram bot client stopped")
            
        if user.is_connected:
            await user.stop()
            LOGGER.info("Pyrogram user client stopped")
            
        if pytgcalls:
            await pytgcalls.stop()
            LOGGER.info("PyTgCalls stopped")
            
        if telethn.is_connected():
            await telethn.disconnect()
            LOGGER.info("Telethon client stopped")
            
    except Exception as e:
        LOGGER.error(f"Error stopping clients: {e}")


async def main():
    """Main function to run the bot"""
    try:
        # Clean directories first
        dirr()
        
        # Initialize PTB application
        LOGGER.info("Initializing PTB application...")
        await application.initialize()
        
        # Initialize bot info
        await init_bot()
        LOGGER.info("PTB Started Successfully")
        
        # Start other clients
        await start_clients()
        
        # Send startup notification
        await send_startup_notification()
        
        LOGGER.info("MerissaRobot Started Successfully")
        
        # Start the PTB application
        await application.start()
        
        # Start polling for updates
        LOGGER.info("Starting polling...")
        await application.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
        # Keep the bot running
        LOGGER.info("Bot is running... Press Ctrl+C to stop")
        
        # Create a task for the updater idle and wait for it
        import signal
        
        # Handle shutdown signals
        def signal_handler(signum, frame):
            LOGGER.info(f"Received signal {signum}, shutting down...")
            raise KeyboardInterrupt
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Keep running until interrupted
        try:
            # This replaces updater.idle() which doesn't exist in PTB v22
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            LOGGER.info("Shutdown signal received")
        
    except Exception as e:
        LOGGER.error(f"Error in main: {e}")
        raise
    finally:
        # Cleanup
        LOGGER.info("Starting cleanup...")
        try:
            if application.updater.running:
                await application.updater.stop()
                LOGGER.info("Updater stopped")
            
            await application.stop()
            LOGGER.info("Application stopped")
            
            await application.shutdown()
            LOGGER.info("Application shutdown complete")
            
            await stop_clients()
            LOGGER.info("All clients stopped")
            
        except Exception as e:
            LOGGER.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    # Set event loop policy for better compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the bot
    try:
        LOGGER.info("Starting MerissaRobot...")
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped by user")
    except Exception as e:
        LOGGER.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        LOGGER.info("Bot shutdown complete")
