import re
from pyrate_limiter import (
    BucketFullException,
    Duration,
    Limiter,
    Rate,
)
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import MerissaRobot.Database.sql.blacklistusers_sql as sql
from MerissaRobot import ALLOW_EXCL, DEMONS, DEV_USERS, DRAGONS, TIGERS, WOLVES


# ────────────────────────────────
# Command starters
# ────────────────────────────────
if ALLOW_EXCL:
    CMD_STARTERS = ("/", "!", "~", ".")
else:
    CMD_STARTERS = ("/", "!", "~", ".")


# ────────────────────────────────
# AntiSpam (Updated for pyrate-limiter 3.9.0 + PTB v22)
# ────────────────────────────────
class AntiSpam:
    def __init__(self):
        self.whitelist = (
            (DEV_USERS or [])
            + (DRAGONS or [])
            + (WOLVES or [])
            + (DEMONS or [])
            + (TIGERS or [])
        )
        # Create rate limits using available classes
        self.sec_limit = Rate(6, 15)                # 6 per 15 seconds
        self.min_limit = Rate(20, Duration.MINUTE)  # 20 per minute
        self.hour_limit = Rate(100, Duration.HOUR)  # 100 per hour
        self.daily_limit = Rate(1000, Duration.DAY) # 1000 per day

        # New Limiter syntax (no bucket_class needed)
        self.limiter = Limiter(
            self.sec_limit,
            self.min_limit,
            self.hour_limit,
            self.daily_limit,
        )

    def check_user(self, user_id: int) -> bool:
        """Return True if user is to be ignored else False"""
        if user_id in self.whitelist:
            return False
        try:
            self.limiter.try_acquire(user_id)
            return False
        except BucketFullException:
            return True


SpamChecker = AntiSpam()
MessageHandlerChecker = AntiSpam()


# ────────────────────────────────
# Custom Filter for Blacklisted Users
# ────────────────────────────────
class BlacklistFilter:
    """Custom filter to check if user is blacklisted"""

    def __call__(self, update: Update) -> bool:
        if update.effective_user:
            return not sql.is_user_blacklisted(update.effective_user.id)
        return True

    def __bool__(self):
        return True


# ────────────────────────────────
# Custom Filter for Anti-Spam
# ────────────────────────────────
class AntiSpamFilter:
    """Custom filter to check spam limits"""

    def __call__(self, update: Update) -> bool:
        if update.effective_user:
            # Handle anonymous admin case
            user_id = update.effective_user.id
            if user_id == 1087968824:  # anonymous admin
                user_id = update.effective_chat.id if update.effective_chat else user_id

            return not SpamChecker.check_user(user_id)
        return True

    def __bool__(self):
        return True


# ────────────────────────────────
# Custom Filter for Command Starters
# ────────────────────────────────
class CustomCommandFilter:
    """Filter for custom command prefixes"""

    def __init__(self, commands, bot_username=None):
        if isinstance(commands, str):
            commands = [commands]
        self.commands = [cmd.lower() for cmd in commands]
        self.bot_username = bot_username

    def __call__(self, update: Update) -> bool:
        if not update.effective_message or not update.effective_message.text:
            return False

        message = update.effective_message
        if len(message.text) <= 1:
            return False

        fst_word = message.text.split(None, 1)[0]

        # Check if starts with any command starter
        if not any(fst_word.startswith(start) for start in CMD_STARTERS):
            return False

        # Extract command
        command = fst_word[1:].split("@")
        if len(command) == 1:
            return command[0].lower() in self.commands
        elif len(command) == 2:
            bot_username = self.bot_username or (
                update.get_bot().username if hasattr(update, "get_bot") else None
            )
            return (
                command[0].lower() in self.commands
                and command[1].lower() == (bot_username.lower() if bot_username else "")
            )

        return False

    def __bool__(self):
        return True


# ────────────────────────────────
# Custom CommandHandler (PTB v22 Compatible)
# ────────────────────────────────
class CustomCommandHandler(CommandHandler):
    def __init__(self, command, callback, admin_ok=False, allow_edit=False, **kwargs):
        # Create combined filters
        base_filters = filters.TEXT & BlacklistFilter() & AntiSpamFilter()

        if not allow_edit:
            base_filters &= ~filters.UpdateType.EDITED_MESSAGE

        # Add custom command filter
        if "filters" in kwargs:
            combined_filters = base_filters & kwargs["filters"]
        else:
            combined_filters = base_filters

        # Initialize with custom filter that handles command parsing
        super().__init__(command, callback, filters=combined_filters, **kwargs)

    def check_update(self, update: object) -> bool:
        """Override check_update for PTB v22"""
        if not super().check_update(update):
            return False

        if isinstance(update, Update) and update.effective_message:
            message = update.effective_message
            user_id = update.effective_user.id if update.effective_user else None

            if user_id and sql.is_user_blacklisted(user_id):
                return False

            if message.text and len(message.text) > 1:
                fst_word = message.text.split(None, 1)[0]

                if len(fst_word) > 1 and any(
                    fst_word.startswith(start) for start in CMD_STARTERS
                ):
                    command = fst_word[1:].split("@")

                    if len(command) == 2:
                        try:
                            from MerissaRobot import application
                            bot_username = (
                                application.bot.username
                                if hasattr(application, "bot")
                                else None
                            )
                            if bot_username and command[1].lower() != bot_username.lower():
                                return False
                        except ImportError:
                            pass

                    if command[0].lower() not in [cmd.lower() for cmd in self.commands]:
                        return False

                    if user_id == 1087968824:
                        user_id = (
                            update.effective_chat.id if update.effective_chat else user_id
                        )

                    if SpamChecker.check_user(user_id):
                        return False

                    return True

        return False


# ────────────────────────────────
# Custom MessageHandler (PTB v22 Compatible)
# ────────────────────────────────
class CustomMessageHandler(MessageHandler):
    def __init__(self, filters_, callback, allow_edit=False, **kwargs):
        combined_filters = filters_ & BlacklistFilter() & AntiSpamFilter()

        if not allow_edit:
            combined_filters &= ~filters.UpdateType.EDITED_MESSAGE

        super().__init__(combined_filters, callback, **kwargs)

    def check_update(self, update: object) -> bool:
        if not super().check_update(update):
            return False

        if isinstance(update, Update) and update.effective_user:
            user_id = update.effective_user.id

            if user_id == 1087968824:
                user_id = update.effective_chat.id if update.effective_chat else user_id

            if MessageHandlerChecker.check_user(user_id):
                return False

        return True


# ────────────────────────────────
# Custom RegexHandler (PTB v22 Compatible)
# ────────────────────────────────
class CustomRegexHandler(MessageHandler):
    def __init__(self, pattern, callback, allow_edit=False, **kwargs):
        regex_filter = filters.Regex(re.compile(pattern))
        combined_filters = regex_filter & BlacklistFilter() & AntiSpamFilter()

        if not allow_edit:
            combined_filters &= ~filters.UpdateType.EDITED_MESSAGE

        super().__init__(combined_filters, callback, **kwargs)

    def check_update(self, update: object) -> bool:
        if not super().check_update(update):
            return False

        if isinstance(update, Update) and update.effective_user:
            user_id = update.effective_user.id

            if user_id == 1087968824:
                user_id = update.effective_chat.id if update.effective_chat else user_id

            if MessageHandlerChecker.check_user(user_id):
                return False

        return True


# ────────────────────────────────
# Convenience Functions
# ────────────────────────────────
def command_handler(commands, callback, **kwargs):
    return CustomCommandHandler(commands, callback, **kwargs)


def message_handler(filters_, callback, **kwargs):
    return CustomMessageHandler(filters_, callback, **kwargs)


def regex_handler(pattern, callback, **kwargs):
    return CustomRegexHandler(pattern, callback, **kwargs)
