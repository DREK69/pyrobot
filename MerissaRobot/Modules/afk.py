import random
from datetime import datetime
from typing import Optional

import humanize
from telegram import MessageEntity, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes, filters, MessageHandler

from MerissaRobot import application
from MerissaRobot.Database.sql import afk_sql as sql
from MerissaRobot.Modules.disable import DisableAbleCommandHandler
from MerissaRobot.Modules.users import get_user_id

AFK_GROUP = 7
AFK_REPLY_GROUP = 8


async def afk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set user as AFK with optional reason"""
    args = update.effective_message.text.split(None, 1)
    user = update.effective_user
    chat = update.effective_chat

    if not user:  # ignore channels
        return

    if user.id in [777000, 1087968824]:  # Telegram service accounts
        return

    notice = ""
    if len(args) >= 2:
        reason = args[1]
        if len(reason) > 100:
            reason = reason[:100]
            notice = "\nYour afk reason was shortened to 100 characters."
    else:
        reason = ""

    sql.set_afk(update.effective_user.id, reason)
    fname = update.effective_user.first_name
    
    try:
        await update.effective_message.reply_text(
            "{} is now away!{}".format(fname, notice)
        )
    except BadRequest:
        pass


async def no_longer_afk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove user from AFK status when they send a message"""
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat

    if not user:  # ignore channels
        return

    res = sql.rm_afk(user.id)
    if res:
        if message.new_chat_members:  # don't say message for new members
            return
        
        firstname = update.effective_user.first_name
        try:
            options = [
                "{} is here!",
                "{} is back!",
                "{} is now in the chat!",
                "{} is awake!",
                "{} is back online!",
                "{} is finally here!",
                "Welcome back! {}",
                "Where is {}?\nIn the chat!",
            ]
            chosen_option = random.choice(options)
            await update.effective_message.reply_text(
                chosen_option.format(firstname)
            )
        except Exception:
            return


async def reply_afk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply with AFK status when user is mentioned or replied to"""
    bot = context.bot
    message = update.effective_message
    userc = update.effective_user
    userc_id = userc.id
    
    # Check for mentions in the message
    if message.entities:
        # Filter entities to get mentions and text mentions
        mention_entities = [
            entity for entity in message.entities 
            if entity.type in [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
        ]
        
        if mention_entities:
            chk_users = []
            for ent in mention_entities:
                if ent.type == MessageEntity.TEXT_MENTION:
                    user_id = ent.user.id
                    fst_name = ent.user.first_name

                    if user_id in chk_users:
                        continue
                    chk_users.append(user_id)

                elif ent.type == MessageEntity.MENTION:
                    # Extract username from mention
                    username = message.text[ent.offset : ent.offset + ent.length]
                    user_id = get_user_id(username)
                    
                    if not user_id:
                        # Should never happen, since for a user to become AFK they must have spoken
                        continue

                    if user_id in chk_users:
                        continue
                    chk_users.append(user_id)

                    try:
                        chat = await bot.get_chat(user_id)
                        fst_name = chat.first_name
                    except BadRequest:
                        continue
                else:
                    continue

                await check_afk(update, context, user_id, fst_name, userc_id)

    # Check for reply to message
    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        fst_name = message.reply_to_message.from_user.first_name
        await check_afk(update, context, user_id, fst_name, userc_id)


async def check_afk(
    update: Update, 
    context: ContextTypes.DEFAULT_TYPE, 
    user_id: int, 
    fst_name: str, 
    userc_id: int
):
    """Check if user is AFK and send appropriate response"""
    chat = update.effective_chat
    
    if sql.is_afk(user_id):
        user = sql.check_afk_status(user_id)

        if int(userc_id) == int(user_id):
            return

        time = humanize.naturaldelta(datetime.now() - user.time)

        if not user.reason:
            res = f"{fst_name} is *afk*.\nLast seen: `{time} ago`"
        else:
            res = f"{fst_name} is *afk*.\nReason: `{user.reason}`\nLast seen: `{time} ago`"

        try:
            await update.effective_message.reply_text(
                res,
                parse_mode=ParseMode.MARKDOWN,
            )
        except BadRequest:
            pass


def __gdpr__(user_id):
    """GDPR compliance - remove user data"""
    sql.rm_afk(user_id)


# Handler definitions for PTB v22
AFK_HANDLER = DisableAbleCommandHandler("afk", afk)

NO_AFK_HANDLER = MessageHandler(
    filters.ALL & filters.ChatType.GROUPS, 
    no_longer_afk
)

AFK_REPLY_HANDLER = MessageHandler(
    filters.ALL & filters.ChatType.GROUPS, 
    reply_afk
)

# Add handlers to application with groups
application.add_handler(AFK_HANDLER, AFK_GROUP)
application.add_handler(NO_AFK_HANDLER, AFK_GROUP)
application.add_handler(AFK_REPLY_HANDLER, AFK_REPLY_GROUP)

__command_list__ = ["afk"]
__handlers__ = [
    (AFK_HANDLER, AFK_GROUP),
    (NO_AFK_HANDLER, AFK_GROUP),
    (AFK_REPLY_HANDLER, AFK_REPLY_GROUP),
]
