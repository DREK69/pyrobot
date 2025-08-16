import asyncio
from time import sleep

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest, Unauthorized
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler

import MerissaRobot.Database.sql.global_bans_sql as gban_sql
import MerissaRobot.Database.sql.users_sql as user_sql
from MerissaRobot import DEV_USERS, OWNER_ID, application
from MerissaRobot.Handler.ptb.chat_status import dev_plus


async def get_invalid_chats(update: Update, context: ContextTypes.DEFAULT_TYPE, remove: bool = False):
    bot = context.bot
    chat_id = update.effective_chat.id
    chats = user_sql.get_all_chats()
    kicked_chats, progress = 0, 0
    chat_list = []
    progress_message = None

    for chat in chats:
        if ((100 * chats.index(chat)) / len(chats)) > progress:
            progress_bar = f"{progress}% completed in getting invalid chats."
            if progress_message:
                try:
                    await bot.edit_message_text(
                        progress_bar,
                        chat_id,
                        progress_message.message_id,
                    )
                except:
                    pass
            else:
                progress_message = await bot.send_message(chat_id, progress_bar)
            progress += 5

        cid = chat.chat_id
        await asyncio.sleep(0.1)  # Use asyncio.sleep instead of sleep
        try:
            await bot.get_chat(cid, read_timeout=60, write_timeout=60)
        except (BadRequest, Unauthorized):
            kicked_chats += 1
            chat_list.append(cid)
        except Exception:
            pass

    try:
        await progress_message.delete()
    except:
        pass

    if not remove:
        return kicked_chats
    
    for muted_chat in chat_list:
        await asyncio.sleep(0.1)
        user_sql.rem_chat(muted_chat)
    return kicked_chats


async def get_invalid_gban(update: Update, context: ContextTypes.DEFAULT_TYPE, remove: bool = False):
    bot = context.bot
    banned = gban_sql.get_gban_list()
    ungbanned_users = 0
    ungban_list = []

    for user in banned:
        user_id = user["user_id"]
        await asyncio.sleep(0.1)
        try:
            await bot.get_chat(user_id)
        except BadRequest:
            ungbanned_users += 1
            ungban_list.append(user_id)
        except Exception:
            pass

    if not remove:
        return ungbanned_users
    
    for user_id in ungban_list:
        await asyncio.sleep(0.1)
        gban_sql.ungban_user(user_id)
    return ungbanned_users


async def get_muted_chats(update: Update, context: ContextTypes.DEFAULT_TYPE, remove: bool = False):
    """Get chats where bot was muted/restricted"""
    bot = context.bot
    chat_id = update.effective_chat.id
    chats = user_sql.get_all_chats()
    muted_chats, progress = 0, 0
    chat_list = []
    progress_message = None

    for chat in chats:
        if ((100 * chats.index(chat)) / len(chats)) > progress:
            progress_bar = f"{progress}% completed in checking muted chats."
            if progress_message:
                try:
                    await bot.edit_message_text(
                        progress_bar,
                        chat_id,
                        progress_message.message_id,
                    )
                except:
                    pass
            else:
                progress_message = await bot.send_message(chat_id, progress_bar)
            progress += 5

        cid = chat.chat_id
        await asyncio.sleep(0.1)
        try:
            chat_obj = await bot.get_chat(cid)
            if chat_obj.type in ['group', 'supergroup']:
                bot_member = await bot.get_chat_member(cid, bot.id)
                if bot_member.status == 'restricted' and not bot_member.can_send_messages:
                    muted_chats += 1
                    chat_list.append(cid)
        except (BadRequest, Unauthorized):
            # If we can't access the chat, we should leave it
            muted_chats += 1
            chat_list.append(cid)
        except Exception:
            pass

    try:
        await progress_message.delete()
    except:
        pass

    if not remove:
        return muted_chats
    
    for muted_chat in chat_list:
        await asyncio.sleep(0.1)
        try:
            await bot.leave_chat(muted_chat)
            user_sql.rem_chat(muted_chat)
        except Exception:
            pass
    return muted_chats


@dev_plus
async def dbcleanup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message

    await msg.reply_text("Getting invalid chat count ...")
    invalid_chat_count = await get_invalid_chats(update, context)

    await msg.reply_text("Getting invalid gbanned count ...")
    invalid_gban_count = await get_invalid_gban(update, context)

    reply = f"Total invalid chats - {invalid_chat_count}\n"
    reply += f"Total invalid gbanned users - {invalid_gban_count}"

    buttons = [[InlineKeyboardButton("Cleanup DB", callback_data="db_cleanup")]]

    await update.effective_message.reply_text(
        reply,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@dev_plus
async def leave_muted_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to leave chats where bot is muted"""
    msg = update.effective_message

    await msg.reply_text("Getting muted chat count ...")
    muted_chat_count = await get_muted_chats(update, context)

    reply = f"Total muted chats - {muted_chat_count}"
    buttons = [[InlineKeyboardButton("Leave Muted Chats", callback_data="db_leave_chat")]]

    await update.effective_message.reply_text(
        reply,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def callback_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    message = query.message
    chat_id = update.effective_chat.id
    query_type = query.data

    admin_list = [OWNER_ID] + DEV_USERS

    await bot.answer_callback_query(query.id)

    if query_type == "db_leave_chat":
        if query.from_user.id in admin_list:
            await bot.edit_message_text("Leaving muted chats ...", chat_id, message.message_id)
            chat_count = await get_muted_chats(update, context, True)
            await bot.send_message(chat_id, f"Left {chat_count} muted chats.")
        else:
            await query.answer("You are not allowed to use this.")
    elif query_type == "db_cleanup":
        if query.from_user.id in admin_list:
            await bot.edit_message_text("Cleaning up DB ...", chat_id, message.message_id)
            invalid_chat_count = await get_invalid_chats(update, context, True)
            invalid_gban_count = await get_invalid_gban(update, context, True)
            reply = "Cleaned up {} chats and {} gbanned users from db.".format(
                invalid_chat_count,
                invalid_gban_count,
            )
            await bot.send_message(chat_id, reply)
        else:
            await query.answer("You are not allowed to use this.")


DB_CLEANUP_HANDLER = CommandHandler("dbcleanup", dbcleanup)
LEAVE_MUTED_HANDLER = CommandHandler("leavemuted", leave_muted_chats)
BUTTON_HANDLER = CallbackQueryHandler(callback_button, pattern="db_.*")

application.add_handler(DB_CLEANUP_HANDLER)
application.add_handler(LEAVE_MUTED_HANDLER)
application.add_handler(BUTTON_HANDLER)

__mod_name__ = "DB Cleanup"
__handlers__ = [DB_CLEANUP_HANDLER, LEAVE_MUTED_HANDLER, BUTTON_HANDLER]
