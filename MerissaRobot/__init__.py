#!/usr/bin/env python3
# __main__.py - fixed main startup for MerissaRobot
import asyncio
import os
import sys
import time
import re
from logging import (
    INFO,
    ERROR,
    StreamHandler,
    basicConfig,
    getLogger,
    handlers,
)

# Third-party
from pyrogram import Client
from pytgcalls import PyTgCalls
from telethon import TelegramClient
from telethon.sessions import MemorySession

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Local config - must provide these in config.py
from config import (
    TOKEN,
    API_ID,
    API_HASH,
    STRING_SESSION,
    OWNER_ID,
    # any other config you already use (DEV_USERS, DRAGONS, etc.)
)

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

# reduce spammy logs
getLogger("pyrogram").setLevel(ERROR)
getLogger("telethon").setLevel(ERROR)
getLogger("telegram").setLevel(ERROR)

# ───────────────────────────────
# PTB Application (v20+/v22+)
# ───────────────────────────────
application = Application.builder().token(TOKEN).concurrent_updates(True).build()

# convenience reference to bot (exists after build)
BOT = application.bot

# ───────────────────────────────
# Pyrogram (bot + user), PyTgCalls, Telethon
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
    session_string=str(STRING_SESSION) if STRING_SESSION else None,
)

pytgcalls = PyTgCalls(user)
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)

# ───────────────────────────────
# Helper functions
# ───────────────────────────────
def dirr():
    """clean unwanted images and ensure downloads dir exists"""
    for file in os.listdir():
        if file.endswith((".jpg", ".jpeg")):
            try:
                os.remove(file)
            except Exception:
                pass
    if "downloads" not in os.listdir():
        os.mkdir("downloads")
    LOGGER.info("Directories Updated.")


async def init_bot_info():
    """Fetch bot details and store if needed"""
    try:
        me = await application.bot.get_me()
        LOGGER.info(f"Bot: {me.id} @{me.username} ({me.first_name})")
        return me
    except Exception as e:
        LOGGER.error(f"Failed to fetch bot info: {e}")
        return None


# ───────────────────────────────
# Optional: custom handler classes (kept from your previous code)
# ───────────────────────────────
class CustomCommandHandler(CommandHandler):
    """Custom Command Handler compatible with PTB v22"""

    def __init__(
        self,
        command,
        callback,
        filters=None,
        block: bool = True,
        has_args: int | None = None,
        **kwargs
    ):
        if filters is None:
            # default to ignore edited messages
            filters = ~filters.UpdateType.EDITED_MESSAGE

        super().__init__(command=command, callback=callback, filters=filters, block=block, **kwargs)
        self.has_args = has_args

    def check_update(self, update: object) -> bool | None:
        if not super().check_update(update):
            return None
        if self.has_args is not None:
            message = getattr(update, "effective_message", None)
            if message and getattr(message, "text", None):
                args = message.text.split()[1:]
                if len(args) < self.has_args:
                    return None
        return True


class CustomMessageHandler(MessageHandler):
    def __init__(self, filters, callback, block: bool = True, **kwargs):
        if filters is None:
            filters = filters.ALL
        super().__init__(filters=filters, callback=callback, block=block, **kwargs)


class CustomRegexHandler(MessageHandler):
    def __init__(self, pattern, callback, block: bool = True, **kwargs):
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        super().__init__(filters=filters.Regex(pattern), callback=callback, block=block, **kwargs)


# ───────────────────────────────
# Register any handlers here (example)
# ───────────────────────────────
def setup_handlers():
    """
    Register simple handlers as example.
    Replace/add your module handlers here (import modules as needed).
    """
    # Example start command - adapt to your existing command code
    async def _start(update: Update, context):
        await update.message.reply_text("MerissaRobot is online ✅")

    application.add_handler(CommandHandler("start", _start))
    # Add other handlers / module initializations here


# ───────────────────────────────
# Main startup coroutine - unified single asyncio loop
# ───────────────────────────────
async def start_all():
    """
    Start Pyrogram (bot + user), PyTgCalls, Telethon, then start PTB polling.
    Everything runs in the same asyncio event loop to avoid 'different loop' errors.
    """
    try:
        LOGGER.info("Starting MerissaRobot...")

        # clean directories first
        dirr()

        # Start Pyrogram bot & user clients
        LOGGER.info("Starting Pyrogram bot client (pbot)...")
        await pbot.start()
        LOGGER.info("Pyrogram bot started.")

        LOGGER.info("Starting Pyrogram user client (user)...")
        await user.start()
        LOGGER.info("Pyrogram user started.")

        # Start PyTgCalls (needs the user client)
        LOGGER.info("Starting PyTgCalls...")
        await pytgcalls.start()
        LOGGER.info("PyTgCalls started.")

        # Start Telethon (use same process loop)
        LOGGER.info("Starting Telethon...")
        # Telethon's `start` accepts bot_token for bot sessions; use it to log in as bot
        await telethn.start(bot_token=TOKEN)
        LOGGER.info("Telethon started.")

        # Optional: set up your PTB handlers before starting PTB loop
        setup_handlers()

        # Initialize PTB application but do NOT call updater.* (removed in PTB v20+)
        # `run_polling` will take care of start/stop, but we call initialize() here to allow get_me/send_message before blocking,
        # it's safe because we're in same loop.
        LOGGER.info("Initializing PTB application...")
        await application.initialize()
        # After initialize we can fetch bot info and send startup notification
        me = await init_bot_info()

        # Try to send startup notification to owner (if OWNER_ID present)
        if OWNER_ID:
            try:
                await application.bot.send_message(int(OWNER_ID), "MerissaRobot started ✅")
                LOGGER.info("Startup notification sent to owner.")
            except Exception as e:
                LOGGER.error(f"Failed to send startup notification: {e}")

        LOGGER.info("Starting PTB polling (this will block until stopped)...")
        # This will start dispatcher and block until the app is stopped (ctrl-c or signal)
        await application.run_polling(
            stop_signals=None,
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
        )

    except Exception as e:
        LOGGER.error(f"Fatal error in start_all: {e}")
        raise
    finally:
        LOGGER.info("Shutting down all clients...")

        # PTB cleanup
        try:
            if application.running:
                await application.stop()
            # ensure shutdown called
            await application.shutdown()
        except Exception as e:
            LOGGER.error(f"Error stopping PTB application: {e}")

        # Pyrogram/Telethon/PyTgCalls cleanup
        try:
            if getattr(pytgcalls, "is_connected", lambda: False)():
                await pytgcalls.stop()
        except Exception as e:
            # pytgcalls stop sometimes raises if not started
            LOGGER.error(f"Error stopping pytgcalls: {e}")

        try:
            if getattr(user, "is_connected", False):
                # For Pyrogram client, property is .is_connected (callable or attribute)
                if callable(user.is_connected):
                    if await user.is_connected():
                        await user.stop()
                elif user.is_connected:
                    await user.stop()
        except Exception as e:
            LOGGER.error(f"Error stopping Pyrogram user client: {e}")

        try:
            if getattr(pbot, "is_connected", False):
                if callable(pbot.is_connected):
                    if await pbot.is_connected():
                        await pbot.stop()
                elif pbot.is_connected:
                    await pbot.stop()
        except Exception as e:
            LOGGER.error(f"Error stopping Pyrogram bot client: {e}")

        try:
            # Telethon disconnect
            if telethn and getattr(telethn, "is_connected", None):
                if callable(telethn.is_connected):
                    if await telethn.is_connected():
                        await telethn.disconnect()
                elif telethn.is_connected:
                    await telethn.disconnect()
        except Exception as e:
            LOGGER.error(f"Error disconnecting Telethon: {e}")

        LOGGER.info("All clients shut down. Exiting.")


# ───────────────────────────────
# Entrypoint
# ───────────────────────────────
if __name__ == "__main__":
    try:
        asyncio.run(start_all())
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped by user (KeyboardInterrupt)")
        try:
            # best-effort graceful shutdown
            asyncio.run(start_all())  # attempt to ensure cleanup; safe-guard (optional)
        except Exception:
            pass
    except Exception as e:
        LOGGER.error(f"Fatal error: {e}")
        sys.exit(1)
