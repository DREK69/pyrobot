from pyrate_limiter import (
    BucketFullException,
    Duration,
    Limiter,
    MemoryListBucket,
    RequestRate,
)
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
)
import re

import MerissaRobot.Database.sql.blacklistusers_sql as sql
from MerissaRobot import ALLOW_EXCL, DEMONS, DEV_USERS, DRAGONS, TIGERS, WOLVES

if ALLOW_EXCL:
    CMD_STARTERS = ("/", "!", "~")
else:
    CMD_STARTERS = ("/", "!", "~")


class AntiSpam:
    def __init__(self):
        self.whitelist = (
            (DEV_USERS or [])
            + (DRAGONS or [])
            + (WOLVES or [])
            + (DEMONS or [])
            + (TIGERS or [])
        )
        Duration.CUSTOM = 15  # 15 seconds
        self.sec_limit = RequestRate(6, Duration.CUSTOM)   # 6 per 15 sec
        self.min_limit = RequestRate(20, Duration.MINUTE)  # 20 per minute
        self.hour_limit = RequestRate(100, Duration.HOUR)  # 100 per hour
        self.daily_limit = RequestRate(1000, Duration.DAY) # 1000 per day
        self.limiter = Limiter(
            self.sec_limit,
            self.min_limit,
            self.hour_limit,
            self.daily_limit,
            bucket_class=MemoryListBucket,
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


class CustomCommandHandler(CommandHandler):
    def __init__(self, command, callback, admin_ok=False, allow_edit=False, **kwargs):
        super().__init__(command, callback, **kwargs)
        if not allow_edit:
            self.filters &= ~filters.UpdateType.EDITED

    async def check_update(self, update: Update, context):
        if update.effective_message:
            message = update.effective_message
            user_id = update.effective_user.id if update.effective_user else None

            if user_id and sql.is_user_blacklisted(user_id):
                return False

            if message.text and len(message.text) > 1:
                fst_word = message.text.split(None, 1)[0]
                if len(fst_word) > 1 and any(fst_word.startswith(start) for start in CMD_STARTERS):
                    args = message.text.split()[1:]
                    command = fst_word[1:].split("@")
                    command.append(context.bot.username)

                    if user_id == 1087968824:
                        user_id = update.effective_chat.id

                    if not (
                        command[0].lower() in self.commands
                        and command[1].lower() == context.bot.username.lower()
                    ):
                        return None

                    if SpamChecker.check_user(user_id):
                        return None

                    filter_result = self.filters(update)
                    if filter_result:
                        return args, filter_result
                    return False


class CustomRegexHandler(MessageHandler):
    def __init__(self, pattern, callback, **kwargs):
        regex_filter = filters.Regex(re.compile(pattern))
        super().__init__(regex_filter, callback, **kwargs)


class CustomMessageHandler(MessageHandler):
    def __init__(self, filters_, callback, allow_edit=False, **kwargs):
        if not allow_edit:
            filters_ &= ~filters.UpdateType.EDITED
        super().__init__(filters_, callback, **kwargs)
