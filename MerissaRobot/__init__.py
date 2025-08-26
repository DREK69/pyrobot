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
# Pyrogram + Telethon - Fixed Event Loop Issue
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
# FIXED Main Function to Match Your __main__.py
# ───────────────────────────────
async def main():
    """Main function to start the bot - Fixed to work with your existing __main__.py structure"""
    try:
        # Clean directories first
        dirr()
        
        # Load modules dynamically (from your __main__.py)
        from MerissaRobot.Modules import ALL_MODULES
        LOGGER.info("Successfully loaded Modules: " + str(ALL_MODULES))

        # Initialize all clients (using your existing function structure)
        await initiate_clients()

        # Setup handlers (using your existing function structure)
        await setup_handlers()

        # Initialize PTB application
        await application.initialize()
        
        # Initialize bot info
        await init_bot()
        
        # Start PTB application
        await application.start()

        LOGGER.info("PTB Started Successfully")
        LOGGER.info("MerissaRobot Started Successfully")

        # Send startup notification (using your existing notification)
        try:
            await application.bot.send_message(2030709195, "Merissa Started")
        except Exception as e:
            LOGGER.error(f"Failed to send startup notification: {e}")

        # CRITICAL FIX: Use run_polling instead of updater
        await application.run_polling(
            stop_signals=None,  # let asyncio handle signals
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )

    except Exception as e:
        LOGGER.error(f"Error in main: {e}")
        raise
    finally:
        # Cleanup - Fixed to match PTB v22
        try:
            if hasattr(application, 'running') and application.running:
                await application.stop()
            if hasattr(application, 'shutdown'):
                await application.shutdown()

            # Stop other clients
            if hasattr(pbot, 'is_connected') and pbot.is_connected:
                await pbot.stop()
            if hasattr(user, 'is_connected') and user.is_connected:
                await user.stop()
            if hasattr(pytgcalls, 'stop'):
                await pytgcalls.stop()
            if hasattr(telethn, 'is_connected') and telethn.is_connected():
                await telethn.disconnect()

            LOGGER.info("Bot stopped successfully")
        except Exception as e:
            LOGGER.error(f"Error during cleanup: {e}")


# ───────────────────────────────
# Client Functions - Fixed for Event Loop Compatibility
# ───────────────────────────────
async def initiate_clients():
    """Initialize all clients - Fixed for event loop compatibility"""
    from pyrogram.errors.exceptions.flood_420 import FloodWait
    from telethon.errors.rpcerrorlist import FloodWaitError
    
    try:
        # Start pyrogram clients
        await pbot.start()
        LOGGER.info("Pyrogram Started")
        
        if STRING_SESSION:
            await user.start()
            LOGGER.info("Userbot Started")
            
            await pytgcalls.start()
            LOGGER.info("Pytgcalls Started")
        else:
            LOGGER.warning("STRING_SESSION not provided, skipping user client")
        
        # Start telethon
        await telethn.start(bot_token=TOKEN)
        LOGGER.info("Telethon Started")
        
        # Send startup messages
        try:
            if hasattr(pbot, 'send_message') and pbot.is_connected:
                await pbot.send_message(-1001446814207, "Bot Started")
            if hasattr(user, 'send_message') and user.is_connected and STRING_SESSION:
                await user.send_message(-1001446814207, "Assistant Started")
        except Exception as e:
            LOGGER.error(f"Failed to send startup messages: {e}")
            
    except FloodWait as e:
        LOGGER.info(f"FloodWait: Have to wait {e.value} seconds")
        await asyncio.sleep(e.value)
        await initiate_clients()
    except FloodWaitError as e:
        LOGGER.info(f"Telethon FloodWait: Have to wait {e.seconds} seconds")
        await asyncio.sleep(e.seconds)
        await initiate_clients()
    except Exception as e:
        LOGGER.error(f"Error starting clients: {e}")
        raise


async def setup_handlers():
    """Setup all handlers - Includes handlers from your __main__.py"""
    # Import and setup handlers from your __main__.py structure
    from MerissaRobot.__main__ import (
        start, test, get_help, get_settings, error_handler,
        help_button, ghelp_button, settings_button, 
        merissa_about_callback, Source_about_callback, migrate_chats
    )
    
    # Command handlers
    application.add_handler(CommandHandler("test", test))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", get_help))
    application.add_handler(CommandHandler("settings", get_settings))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(help_button, pattern=r"help_.*"))
    application.add_handler(CallbackQueryHandler(ghelp_button, pattern=r"ghelp_.*"))
    application.add_handler(CallbackQueryHandler(settings_button, pattern=r"stngs_"))
    application.add_handler(CallbackQueryHandler(merissa_about_callback, pattern=r"merissa_"))
    application.add_handler(CallbackQueryHandler(Source_about_callback, pattern=r"source_"))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.StatusUpdate.MIGRATE, migrate_chats))
    
    # Error handlers
    application.add_error_handler(error_handler)
    
    LOGGER.info("All handlers setup completed")


if __name__ == "__main__":
    # CRITICAL: Fixed event loop management
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    else:
        # For Linux/Unix - better event loop handling
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass
    
    # Run the bot with proper event loop management
    try:
        LOGGER.info("Starting MerissaRobot...")
        
        # Create new event loop to avoid conflicts
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run main function
        loop.run_until_complete(main())
        
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped by user")
    except Exception as e:
        LOGGER.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Clean up event loop
        try:
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                loop.close()
        except:
            pass
        LOGGER.info("Bot shutdown complete")
