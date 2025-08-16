import html

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from telegram.helpers import mention_html

import MerissaRobot.Database.sql.approve_sql as sql
from MerissaRobot import DRAGONS, application
from MerissaRobot.Handler.ptb.chat_status import user_admin
from MerissaRobot.Handler.ptb.extraction import extract_user
from MerissaRobot.Modules.disable import DisableAbleCommandHandler
from MerissaRobot.Modules.log_channel import loggable


@loggable
@user_admin
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!",
        )
        return ""
    try:
        member = await chat.get_member(user_id)
    except BadRequest:
        return ""
        
    if member.status in ("administrator", "creator"):
        await message.reply_text(
            "User is already admin - locks, blocklists, and antiflood already don't apply to them.",
        )
        return ""
        
    if sql.is_approved(message.chat_id, user_id):
        await message.reply_text(
            f"[{member.user.first_name}](tg://user?id={member.user.id}) is already approved in {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
        
    sql.approve(message.chat_id, user_id)
    await message.reply_text(
        f"[{member.user.first_name}](tg://user?id={member.user.id}) has been approved in {chat_title}! They will now be ignored by automated admin actions like locks, blocklists, and antiflood.",
        parse_mode=ParseMode.MARKDOWN,
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#APPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@loggable
@user_admin
async def disapprove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!",
        )
        return ""
        
    try:
        member = await chat.get_member(user_id)
    except BadRequest:
        return ""
        
    if member.status in ("administrator", "creator"):
        await message.reply_text("This user is an admin, they can't be unapproved.")
        return ""
        
    if not sql.is_approved(message.chat_id, user_id):
        await message.reply_text(f"{member.user.first_name} isn't approved yet!")
        return ""
        
    sql.disapprove(message.chat_id, user_id)
    await message.reply_text(
        f"{member.user.first_name} is no longer approved in {chat_title}.",
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNAPPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@user_admin
async def approved(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "The following users are approved.\n"
    approved_users = sql.list_approved(message.chat_id)
    
    for i in approved_users:
        try:
            member = await chat.get_member(int(i.user_id))
            msg += f"- `{i.user_id}`: {member.user.first_name}\n"
        except BadRequest:
            continue
            
    if msg.endswith("approved.\n"):
        await message.reply_text(f"No users are approved in {chat_title}.")
        return ""
        
    await message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


@user_admin
async def approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    
    if not user_id:
        await message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!",
        )
        return ""
        
    try:
        member = await chat.get_member(int(user_id))
    except BadRequest:
        await message.reply_text("User not found in this chat.")
        return ""
        
    if sql.is_approved(message.chat_id, user_id):
        await message.reply_text(
            f"{member.user.first_name} is an approved user. Locks, antiflood, and blocklists won't apply to them.",
        )
    else:
        await message.reply_text(
            f"{member.user.first_name} is not an approved user. They are affected by normal commands.",
        )


async def unapproveall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)
    
    if member.status != "creator" and user.id not in DRAGONS:
        await update.effective_message.reply_text(
            "Only the chat owner can unapprove all users at once.",
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Unapprove all users",
                        callback_data="unapproveall_user",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Cancel",
                        callback_data="unapproveall_cancel",
                    ),
                ],
            ],
        )
        await update.effective_message.reply_text(
            f"Are you sure you would like to unapprove ALL users in {chat.title}? This action cannot be undone.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


async def unapproveall_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = await chat.get_member(query.from_user.id)
    
    if query.data == "unapproveall_user":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            approved_users = sql.list_approved(chat.id)
            users = [int(i.user_id) for i in approved_users]
            for user_id in users:
                sql.disapprove(chat.id, user_id)
            await message.edit_text("Successfully Unapproved all user in this Chat.")
            return

        if member.status == "administrator":
            await query.answer("Only owner of the chat can do this.")

        if member.status == "member":
            await query.answer("You need to be admin to do this.")
            
    elif query.data == "unapproveall_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            await message.edit_text("Removing of all approved users has been cancelled.")
            return ""
        if member.status == "administrator":
            await query.answer("Only owner of the chat can do this.")
        if member.status == "member":
            await query.answer("You need to be admin to do this.")


APPROVE = DisableAbleCommandHandler("approve", approve)
DISAPPROVE = DisableAbleCommandHandler("unapprove", disapprove)
APPROVED = DisableAbleCommandHandler("approved", approved)
APPROVAL = DisableAbleCommandHandler("approval", approval)
UNAPPROVEALL = DisableAbleCommandHandler("unapproveall", unapproveall)
UNAPPROVEALL_BTN = CallbackQueryHandler(
    unapproveall_btn, pattern=r"unapproveall_.*"
)

application.add_handler(APPROVE)
application.add_handler(DISAPPROVE)
application.add_handler(APPROVED)
application.add_handler(APPROVAL)
application.add_handler(UNAPPROVEALL)
application.add_handler(UNAPPROVEALL_BTN)

__command_list__ = ["approve", "unapprove", "approved", "approval"]
__handlers__ = [APPROVE, DISAPPROVE, APPROVED, APPROVAL, UNAPPROVEALL, UNAPPROVEALL_BTN]
