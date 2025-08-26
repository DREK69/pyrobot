import asyncio
from io import BytesIO
from time import sleep

from telegram import Update
from telegram.error import TelegramError
from telegram.error import BadRequest, Unauthorized
from telegram.ext import ContextTypes, CommandHandler, filters, MessageHandler

import MerissaRobot.Database.sql.users_sql as sql
from MerissaRobot import DEV_USERS, LOGGER, OWNER_ID, application
from MerissaRobot.Database.sql.users_sql import get_all_users
from MerissaRobot.Handler.ptb.chat_status import dev_plus, sudo_plus

USERS_GROUP = 4
CHAT_GROUP = 5
DEV_AND_MORE = DEV_USERS.copy()
DEV_AND_MORE.append(int(OWNER_ID))


async def get_user_id(username):
    # ensure valid userid
    if len(username) <= 5:
        return None

    if username.startswith("@"):
        username = username[1:]

    users = sql.get_userid_by_name(username)

    if not users:
        return None

    if len(users) == 1:
        return users[0].user_id
    
    for user_obj in users:
        try:
            userdat = await application.bot.get_chat(user_obj.user_id)
            if userdat.username == username:
                return userdat.id

        except BadRequest as excp:
            if excp.message == "Chat not found":
                pass
            else:
                LOGGER.exception("Error extracting user ID")

    return None


@dev_plus
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    to_send = update.effective_message.text.split(None, 1)

    if len(to_send) >= 2:
        to_group = False
        to_user = False
        if to_send[0] == "/promogroups":
            to_group = True
        elif to_send[0] == "/promousers":
            to_user = True
        else:
            to_group = to_user = True
            
        chats = sql.get_all_chats() or []
        users = get_all_users()
        failed = 0
        failed_user = 0
        
        if to_group:
            for chat in chats:
                try:
                    await context.bot.send_message(
                        int(chat.chat_id),
                        to_send[1],
                        parse_mode="MARKDOWN",
                        disable_web_page_preview=True,
                    )
                    await asyncio.sleep(0.1)
                except TelegramError:
                    failed += 1
                    
        if to_user:
            for user in users:
                try:
                    await context.bot.send_message(
                        int(user.user_id),
                        to_send[1],
                        parse_mode="MARKDOWN",
                        disable_web_page_preview=True,
                    )
                    await asyncio.sleep(0.1)
                except TelegramError:
                    failed_user += 1
                    
        await update.effective_message.reply_text(
            f"Broadcast complete.\nGroups failed: {failed}.\nUsers failed: {failed_user}.",
        )


async def log_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.effective_message

    sql.update_user(msg.from_user.id, msg.from_user.username, chat.id, chat.title)

    if msg.reply_to_message:
        sql.update_user(
            msg.reply_to_message.from_user.id,
            msg.reply_to_message.from_user.username,
            chat.id,
            chat.title,
        )

    if msg.forward_from:
        sql.update_user(msg.forward_from.id, msg.forward_from.username)


@sudo_plus
async def chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_chats = sql.get_all_chats() or []
    chatfile = "List of chats.\n0. Chat name | Chat ID | Members count\n"
    P = 1
    
    for chat in all_chats:
        try:
            curr_chat = await context.bot.get_chat(chat.chat_id)
            await curr_chat.get_member(context.bot.id)
            chat_members = await curr_chat.get_member_count()
            chatfile += "{}. {} | {} | {}\n".format(
                P,
                chat.chat_name,
                chat.chat_id,
                chat_members,
            )
            P = P + 1
        except Exception:
            pass

    with BytesIO(str.encode(chatfile)) as output:
        output.name = "groups_list.txt"
        await update.effective_message.reply_document(
            document=output,
            filename="groups_list.txt",
            caption="Here be the list of groups in my database.",
        )


async def chat_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    try:
        bot_member = await update.effective_message.chat.get_member(bot.id)
        if hasattr(bot_member, 'can_send_messages') and bot_member.can_send_messages is False:
            await bot.leave_chat(update.effective_message.chat.id)
    except Unauthorized:
        pass
    except Exception:
        pass


async def __user_info__(user_id):
    if user_id in [777000, 1087968824]:
        return """╘═━「 Groups count: <code>???</code> 」"""
    if user_id == application.bot.id:
        return """╘═━「 Groups count: <code>???</code> 」"""
    num_chats = sql.get_user_num_chats(user_id)
    return f"""╘═━「 Groups count: <code>{num_chats}</code> 」"""


def __stats__():
    return f"× {sql.num_users()} users, across {sql.num_chats()} chats"


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


# Additional utility functions for better user management
@sudo_plus
async def users_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get total users and chats count"""
    users = sql.num_users()
    chats = sql.num_chats()
    
    await update.effective_message.reply_text(
        f"📊 **Bot Statistics:**\n"
        f"👥 Total Users: `{users}`\n"
        f"💬 Total Chats: `{chats}`",
        parse_mode="MARKDOWN"
    )


@sudo_plus  
async def user_info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get info about a specific user"""
    args = context.args
    if not args:
        await update.effective_message.reply_text("Please provide a username or user ID!")
        return
        
    user_id = None
    if args[0].isdigit():
        user_id = int(args[0])
    else:
        user_id = await get_user_id(args[0])
        
    if not user_id:
        await update.effective_message.reply_text("User not found!")
        return
        
    user_info = await __user_info__(user_id)
    try:
        user_obj = await context.bot.get_chat(user_id)
        name = user_obj.first_name
        username = f"@{user_obj.username}" if user_obj.username else "No username"
        
        await update.effective_message.reply_text(
            f"📋 **User Information:**\n"
            f"🆔 ID: `{user_id}`\n"
            f"👤 Name: {name}\n"
            f"🔗 Username: {username}\n"
            f"{user_info}",
            parse_mode="MARKDOWN"
        )
    except Exception as e:
        await update.effective_message.reply_text(f"Error getting user info: {str(e)}")


__help__ = """
*User Management Commands:*

*For Sudo Users:*
❂ `/groups` - Get list of all groups bot is in
❂ `/stats` - Get user and chat statistics  
❂ `/userinfo <user_id/@username>` - Get info about a user

*For Developers:*
❂ `/promoall <message>` - Broadcast to all users and groups
❂ `/promousers <message>` - Broadcast to all users only
❂ `/promogroups <message>` - Broadcast to all groups only

*Note:* Bot automatically logs users and checks for permissions in groups.
"""

BROADCAST_HANDLER = CommandHandler(
    ["promoall", "promousers", "promogroups"],
    broadcast,
)
USER_HANDLER = MessageHandler(
    filters.ALL & filters.ChatType.GROUPS, log_user
)
CHAT_CHECKER_HANDLER = MessageHandler(
    filters.ALL & filters.ChatType.GROUPS, chat_checker
)
CHATLIST_HANDLER = CommandHandler("groups", chats)
STATS_HANDLER = CommandHandler("stats", users_count)
USER_INFO_HANDLER = CommandHandler("userinfo", user_info_cmd)

application.add_handler(USER_HANDLER, USERS_GROUP)
application.add_handler(BROADCAST_HANDLER)
application.add_handler(CHATLIST_HANDLER)
application.add_handler(STATS_HANDLER)
application.add_handler(USER_INFO_HANDLER)
application.add_handler(CHAT_CHECKER_HANDLER, CHAT_GROUP)

__mod_name__ = "Users"
__handlers__ = [
    (USER_HANDLER, USERS_GROUP), 
    BROADCAST_HANDLER, 
    CHATLIST_HANDLER,
    STATS_HANDLER,
    USER_INFO_HANDLER,
    (CHAT_CHECKER_HANDLER, CHAT_GROUP)
]
