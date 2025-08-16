import html
import os
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden
from telegram.ext import ContextTypes, CommandHandler, filters
from telegram.helpers import mention_html

from MerissaRobot import DRAGONS, SUPPORT_CHAT, application
from MerissaRobot.Handler.ptb.admin_rights import user_can_changeinfo
from MerissaRobot.Handler.ptb.alternate import send_message
from MerissaRobot.Handler.ptb.chat_status import (
    ADMIN_CACHE,
    bot_admin,
    can_pin,
    can_promote,
    connection_status,
    user_admin,
)
from MerissaRobot.Handler.ptb.extraction import extract_user, extract_user_and_text
from MerissaRobot.Modules.disable import DisableAbleCommandHandler
from MerissaRobot.Modules.log_channel import loggable


@bot_admin
@user_admin
async def set_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set chat sticker set"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not await user_can_changeinfo(chat, user, context.bot.id):
        await msg.reply_text("You're missing rights to change chat info!")
        return

    if msg.reply_to_message:
        if not msg.reply_to_message.sticker:
            await msg.reply_text(
                "You need to reply to some sticker to set chat sticker set!"
            )
            return
        
        stkr = msg.reply_to_message.sticker.set_name
        try:
            await context.bot.set_chat_sticker_set(chat.id, stkr)
            await msg.reply_text(f"Successfully set new group stickers in {chat.title}!")
        except BadRequest as excp:
            if excp.message == "Participants_too_few":
                await msg.reply_text(
                    "Sorry, due to telegram restrictions chat needs to have minimum 100 members before they can have group stickers!"
                )
                return
            await msg.reply_text(f"Error! {excp.message}.")
    else:
        await msg.reply_text("You need to reply to some sticker to set chat sticker set!")


@bot_admin
@user_admin
async def setchatpic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set chat profile picture"""
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if not await user_can_changeinfo(chat, user, context.bot.id):
        await msg.reply_text("You are missing right to change group info!")
        return

    if msg.reply_to_message:
        if msg.reply_to_message.photo:
            pic_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            pic_id = msg.reply_to_message.document.file_id
        else:
            await msg.reply_text("You can only set some photo as chat pic!")
            return
        
        dlmsg = await msg.reply_text("Just a sec...")
        try:
            # Get file and download
            tpic = await context.bot.get_file(pic_id)
            await tpic.download_to_drive("gpic.png")
            
            # Set chat photo
            with open("gpic.png", "rb") as chatp:
                await context.bot.set_chat_photo(int(chat.id), photo=chatp)
                await msg.reply_text("Successfully set new chatpic!")
                
        except BadRequest as excp:
            await msg.reply_text(f"Error! {excp.message}")
        finally:
            await dlmsg.delete()
            if os.path.isfile("gpic.png"):
                os.remove("gpic.png")
    else:
        await msg.reply_text("Reply to some photo or file to set new chat pic!")


@bot_admin
@user_admin
async def rmchatpic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove chat profile picture"""
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if not await user_can_changeinfo(chat, user, context.bot.id):
        await msg.reply_text("You don't have enough rights to delete group photo")
        return
    
    try:
        await context.bot.delete_chat_photo(int(chat.id))
        await msg.reply_text("Successfully deleted chat's profile photo!")
    except BadRequest as excp:
        await msg.reply_text(f"Error! {excp.message}.")


@bot_admin
@user_admin
async def set_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set chat description"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not await user_can_changeinfo(chat, user, context.bot.id):
        await msg.reply_text("You're missing rights to change chat info!")
        return

    tesc = msg.text.split(None, 1)
    if len(tesc) >= 2:
        desc = tesc[1]
    else:
        await msg.reply_text("Setting empty description won't do anything!")
        return
    
    try:
        if len(desc) > 255:
            await msg.reply_text("Description must needs to be under 255 characters!")
            return
        await context.bot.set_chat_description(chat.id, desc)
        await msg.reply_text(f"Successfully updated chat description in {chat.title}!")
    except BadRequest as excp:
        await msg.reply_text(f"Error! {excp.message}.")


@bot_admin
@user_admin
async def setchat_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set chat title"""
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    args = context.args

    if not await user_can_changeinfo(chat, user, context.bot.id):
        await msg.reply_text("You don't have enough rights to change chat info!")
        return

    title = " ".join(args)
    if not title:
        await msg.reply_text("Enter some text to set new title in your chat!")
        return

    try:
        await context.bot.set_chat_title(int(chat.id), str(title))
        await msg.reply_text(
            f"Successfully set <b>{title}</b> as new chat title!",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        await msg.reply_text(f"Error! {excp.message}.")


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Promote a user to admin"""
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = await chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        await message.reply_text("You don't have the necessary rights to do that!")
        return ""

    user_id = extract_user(message, args)

    if not user_id:
        await message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return ""

    try:
        user_member = await chat.get_member(user_id)
    except Exception:
        return ""

    if user_member.status in ("administrator", "creator"):
        await message.reply_text("How am I meant to promote someone that's already an admin?")
        return ""

    if user_id == bot.id:
        await message.reply_text("I can't promote myself! Get an admin to do it for me.")
        return ""

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = await chat.get_member(bot.id)

    try:
        await bot.promote_chat_member(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_manage_video_chats=getattr(bot_member, 'can_manage_video_chats', False),
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            await message.reply_text("I can't promote someone who isn't in the group.")
        else:
            await message.reply_text("An error occurred while promoting.")
        return ""

    await bot.send_message(
        chat.id,
        f"Promoting a user in <b>{chat.title}</b>\n\nUser: {mention_html(user_member.user.id, user_member.user.first_name)}\nAdmin: {mention_html(user.id, user.first_name)}",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#PROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
async def lowpromote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Low promote a user with limited permissions"""
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = await chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        await message.reply_text("You don't have the necessary rights to do that!")
        return ""

    user_id = extract_user(message, args)

    if not user_id:
        await message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return ""

    try:
        user_member = await chat.get_member(user_id)
    except Exception:
        return ""

    if user_member.status in ("administrator", "creator"):
        await message.reply_text("How am I meant to promote someone that's already an admin?")
        return ""

    if user_id == bot.id:
        await message.reply_text("I can't promote myself! Get an admin to do it for me.")
        return ""

    # set limited perms for low promote
    bot_member = await chat.get_member(bot.id)

    try:
        await bot.promote_chat_member(
            chat.id,
            user_id,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            await message.reply_text("I can't promote someone who isn't in the group.")
        else:
            await message.reply_text("An error occurred while promoting.")
        return ""

    await bot.send_message(
        chat.id,
        f"Lowpromoting a user in <b>{chat.title}</b>\n\nUser: {mention_html(user_member.user.id, user_member.user.first_name)}\nAdmin: {mention_html(user.id, user.first_name)}",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#LOWPROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message

@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
async def fullpromote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Full promote a user with all permissions"""
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = await chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        await message.reply_text("You don't have the necessary rights to do that!")
        return ""

    user_id = extract_user(message, args)

    if not user_id:
        await message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return ""

    try:
        user_member = await chat.get_member(user_id)
    except Exception:
        return ""

    if user_member.status in ("administrator", "creator"):
        await message.reply_text("How am I meant to promote someone that's already an admin?")
        return ""

    if user_id == bot.id:
        await message.reply_text("I can't promote myself! Get an admin to do it for me.")
        return ""

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = await chat.get_member(bot.id)

    try:
        await bot.promote_chat_member(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_video_chats=getattr(bot_member, 'can_manage_video_chats', False),
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            await message.reply_text("I can't promote someone who isn't in the group.")
        else:
            await message.reply_text("An error occurred while promoting.")
        return ""

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Demote", callback_data="demote_({})".format(user_member.user.id)
                )
            ]
        ]
    )

    await bot.send_message(
        chat.id,
        f"Fullpromoting a user in <b>{chat.title}</b>\n\n<b>User: {mention_html(user_member.user.id, user_member.user.first_name)}</b>\n<b>Promoter: {mention_html(user.id, user.first_name)}</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#FULLPROMOTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Demote an admin"""
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    if not user_id:
        await message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return ""

    try:
        user_member = await chat.get_member(user_id)
    except Exception:
        return ""

    if user_member.status == "creator":
        await message.reply_text("This person CREATED the chat, how would I demote them?")
        return ""

    if not user_member.status == "administrator":
        await message.reply_text("Can't demote what wasn't promoted!")
        return ""

    if user_id == bot.id:
        await message.reply_text("I can't demote myself! Get an admin to do it for me.")
        return ""

    try:
        await bot.promote_chat_member(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_video_chats=False,
        )

        await bot.send_message(
            chat.id,
            f"Successfully demoted an admin in <b>{chat.title}</b>\n\nAdmin: <b>{mention_html(user_member.user.id, user_member.user.first_name)}</b>\nDemoter: {mention_html(user.id, user.first_name)}",
            parse_mode=ParseMode.HTML,
        )

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#DEMOTED\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        await message.reply_text(
            "Could not demote. I might not be admin, or the admin status was appointed by another"
            " user, so I can't act upon them!",
        )
        return ""


@user_admin
async def refresh_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Refresh admin cache"""
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    await update.effective_message.reply_text("✅ Admins cache refreshed!")


@connection_status
@bot_admin
@can_promote
@user_admin
async def set_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set custom title for an admin"""
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = await chat.get_member(user_id)
    except Exception:
        return

    if not user_id:
        await message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return

    if user_member.status == "creator":
        await message.reply_text(
            "This person CREATED the chat, how can I set custom title for him?",
        )
        return

    if user_member.status != "administrator":
        await message.reply_text(
            "Can't set title for non-admins!\nPromote them first to set custom title!",
        )
        return

    if user_id == bot.id:
        await message.reply_text(
            "I can't set my own title myself! Get the one who made me admin to do it for me.",
        )
        return

    if not title:
        await message.reply_text("Setting blank title doesn't do anything!")
        return

    if len(title) > 16:
        await message.reply_text(
            "The title length is longer than 16 characters.\nTruncating it to 16 characters.",
        )

    try:
        await bot.set_chat_administrator_custom_title(chat.id, user_id, title)
    except BadRequest:
        await message.reply_text(
            "Either they aren't promoted by me or you set a title text that is impossible to set."
        )
        return

    await bot.send_message(
        chat.id,
        f"Successfully set title for <code>{user_member.user.first_name or user_id}</code> "
        f"to <code>{html.escape(title[:16])}</code>!",
        parse_mode=ParseMode.HTML,
    )


@bot_admin
@can_pin
@user_admin
@loggable
async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Pin a message"""
    bot, args = context.bot, context.args
    user = update.effective_user
    chat = update.effective_chat
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id
    unpinner = await chat.get_member(user.id)

    if (
        not (unpinner.can_pin_messages or unpinner.status == "creator")
        and user.id not in DRAGONS
    ):
        await msg.reply_text("» You Don't Have Permission To Pin/Unpin Message In This Chat.")
        return ""

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message is None:
        await msg.reply_text("» Reply To A Message To Pin It 📌")
        return ""

    is_silent = True
    if len(args) >= 1:
        is_silent = (
            args[0].lower() != "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            await bot.pin_chat_message(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
            await msg.reply_text(
                f"» Successfully Pinned That Message. 📌\nClick On The Button Below To See The Message.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Message", url=f"{message_link}")]]
                ),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"Pinned A Message\n"
            f"<b>Pinned By :</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message
    return ""


@bot_admin
@can_pin
@user_admin
@loggable
async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unpin a message"""
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id
    unpinner = await chat.get_member(user.id)

    if (
        not (unpinner.can_pin_messages or unpinner.status == "creator")
        and user.id not in DRAGONS
    ):
        await msg.reply_text("» You Don't Have Permission To Pin/Unpin Message In This Chat.")
        return

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message and is_group:
        try:
            await context.bot.unpin_chat_message(chat.id, prev_message.message_id)
            await msg.reply_text(
                f"» Successfully Unpinned <a href='{message_link}'> This Pinned Message</a>.",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

    if not prev_message and is_group:
        try:
            await context.bot.unpin_chat_message(chat.id)
            await msg.reply_text("» Successfully Unpinned That Last Pinned Message.")
        except BadRequest as excp:
            if excp.message == "Message to unpin not found":
                await msg.reply_text(
                    "» I Can't Unpin That Message, Maybe That Message Is Too Old Or Maybe Someone Already Unpinned It."
                )
            else:
                raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"Unpinned A Message\n"
        f"<b>Unpinned By :</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log_message

@bot_admin
async def pinned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Show pinned message"""
    bot = context.bot
    msg = update.effective_message
    msg_id = (
        update.effective_message.reply_to_message.message_id
        if update.effective_message.reply_to_message
        else update.effective_message.message_id
    )

    chat = await bot.get_chat(chat_id=msg.chat.id)
    if chat.pinned_message:
        pinned_id = chat.pinned_message.message_id
        if msg.chat.username:
            link_chat_id = msg.chat.username
            message_link = f"https://t.me/{link_chat_id}/{pinned_id}"
        elif (str(msg.chat.id)).startswith("-100"):
            link_chat_id = (str(msg.chat.id)).replace("-100", "")
            message_link = f"https://t.me/c/{link_chat_id}/{pinned_id}"

        await msg.reply_text(
            f"Pinned on {html.escape(chat.title)}.",
            reply_to_message_id=msg_id,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Pinned Message",
                            url=message_link,
                        )
                    ]
                ]
            ),
        )

    else:
        await msg.reply_text(
            f"There is no pinned message in <b>{html.escape(chat.title)}!</b>",
            parse_mode=ParseMode.HTML,
        )


@bot_admin
@user_admin
@connection_status
async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get chat invite link"""
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        await update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type in [chat.SUPERGROUP, chat.CHANNEL]:
        bot_member = await chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = await bot.export_chat_invite_link(chat.id)
            await update.effective_message.reply_text(invitelink)
        else:
            await update.effective_message.reply_text(
                "I don't have access to the invite link, try changing my permissions!",
            )
    else:
        await update.effective_message.reply_text(
            "I can only give you invite links for supergroups and channels, sorry!",
        )


@connection_status
async def adminlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all admins in the chat"""
    chat = update.effective_chat
    user = update.effective_user
    args = context.args
    bot = context.bot

    if update.effective_message.chat.type == "private":
        await send_message(update.effective_message, "This command only works in Groups.")
        return

    chat_id = update.effective_chat.id
    chat_name = update.effective_message.chat.title

    try:
        msg = await update.effective_message.reply_text(
            "Fetching group admins...",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest:
        msg = await update.effective_message.reply_text(
            "Fetching group admins...",
            parse_mode=ParseMode.HTML,
        )

    administrators = await bot.get_chat_administrators(chat_id)
    text = "Admins in <b>{}</b>:".format(html.escape(update.effective_chat.title))

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ Deleted Account"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " + (user.last_name or "")),
                ),
            )

        if user.is_bot:
            administrators.remove(admin)
            continue

        if status == "creator":
            text += "\n 🌏 Creator:"
            text += "\n<code> • </code>{}\n".format(name)

            if custom_title:
                text += f"<code> ┗━ {html.escape(custom_title)}</code>\n"

    text += "\n🌟 Admins:"

    custom_admin_list = {}
    normal_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ Deleted Account"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " + (user.last_name or "")),
                ),
            )

        if status == "administrator":
            if custom_title:
                try:
                    custom_admin_list[custom_title].append(name)
                except KeyError:
                    custom_admin_list.update({custom_title: [name]})
            else:
                normal_admin_list.append(name)

    for admin in normal_admin_list:
        text += "\n<code> • </code>{}".format(admin)

    for admin_group in custom_admin_list.copy():
        if len(custom_admin_list[admin_group]) == 1:
            text += "\n<code> • </code>{} | <code>{}</code>".format(
                custom_admin_list[admin_group][0],
                html.escape(admin_group),
            )
            custom_admin_list.pop(admin_group)

    text += "\n"
    for admin_group, value in custom_admin_list.items():
        text += "\n🚨 <code>{}</code>".format(admin_group)
        for admin in value:
            text += "\n<code> • </code>{}".format(admin)
        text += "\n"

    try:
        await msg.edit_text(text, parse_mode=ParseMode.HTML)
    except BadRequest:  # if original message is deleted
        return


@bot_admin
@can_promote
@user_admin
@loggable
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle callback buttons"""
    from telegram import CallbackQuery, User, Bot, Chat
    import re
    
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    bot: Optional[Bot] = context.bot
    match = re.match(r"demote_\((.+?)\)", query.data)
    
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        member = await chat.get_member(user_id)
        bot_member = await chat.get_member(bot.id)
        
        demoted = await bot.promote_chat_member(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_video_chats=False,
        )
        
        if demoted:
            await update.effective_message.edit_text(
                f"Admin {mention_html(user.id, user.first_name)} Demoted {mention_html(member.user.id, member.user.first_name)}!",
                parse_mode=ParseMode.HTML,
            )
            await query.answer("Demoted!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#DEMOTE\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
            )
    else:
        await update.effective_message.edit_text(
            "This user is not promoted or has left the group!"
        )
        return ""


@connection_status
async def bug_reporting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Report bugs to support chat"""
    from MerissaRobot import LOGGER
    
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    bot = context.bot
    
    try:
        invitelink = await bot.export_chat_invite_link(chat.id)
    except Exception:
        invitelink = "Private Group"
        
    puki = msg.text.split(None, 1)
    if len(puki) >= 2:
        bugnya = puki[1]
    else:
        await msg.reply_text(
            "❌ <b>You must specify the bug to report.</b>\n • example: <code>/bug Music not working.</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        if len(bugnya) > 100:
            await msg.reply_text("Bug must needs to be under 100 characters!")
            return
            
        await msg.reply_text(
            f"✅ Your Bug was submitted to <b>Bot Admins</b>. Thanks for reporting the bug.",
            parse_mode=ParseMode.HTML,
        )
        
        if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
            try:
                await bot.send_message(
                    f"@{SUPPORT_CHAT}",
                    f"📣 <b>New bug reported.</b>\n\n<b>Chat:</b> <a href='{invitelink}'>{chat.title}</a>\n<b>Name:</b> <a href='tg://user?id={msg.from_user.id}'>{mention_html(msg.from_user.id, msg.from_user.first_name)}</a>\n<b>User ID:</b> <code>{msg.from_user.id}</code>\n<b>Chat id:</b> <code>{chat.id}</code>\n\nContent of the report:\n{bugnya}",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Go To Message", url=f"{msg.link}")]]
                    ),
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except Forbidden:
                LOGGER.warning(
                    "Bot isn't able to send message to support_chat, go and check!"
                )
            except BadRequest as e:
                LOGGER.warning(e.message)
    except BadRequest:
        pass


__help__ = """
We promise to keep you latest up-date with the latest technology on telegram. 
We Upgrade Merissa Robot everyday to simplify use of telegram and give a better experience to users.
Click on below buttons and check amazing Admin commands for Users.
"""

# Handler registrations for PTB v22
SET_DESC_HANDLER = CommandHandler(
    "setdesc", set_desc, filters=filters.ChatType.GROUPS
)
SET_STICKER_HANDLER = CommandHandler(
    "setsticker", set_sticker, filters=filters.ChatType.GROUPS
)
SETCHATPIC_HANDLER = CommandHandler(
    "setgpic", setchatpic, filters=filters.ChatType.GROUPS
)
RMCHATPIC_HANDLER = CommandHandler(
    "delgpic", rmchatpic, filters=filters.ChatType.GROUPS
)
SETCHAT_TITLE_HANDLER = CommandHandler(
    "setgtitle", setchat_title, filters=filters.ChatType.GROUPS
)

ADMINLIST_HANDLER = DisableAbleCommandHandler("admins", adminlist)
BUG_HANDLER = DisableAbleCommandHandler("bug", bug_reporting)

PIN_HANDLER = CommandHandler(
    "pin", pin, filters=filters.ChatType.GROUPS
)
UNPIN_HANDLER = CommandHandler(
    "unpin", unpin, filters=filters.ChatType.GROUPS
)
PINNED_HANDLER = CommandHandler(
    "pinned", pinned, filters=filters.ChatType.GROUPS
)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote)
FULLPROMOTE_HANDLER = DisableAbleCommandHandler("fullpromote", fullpromote)
LOW_PROMOTE_HANDLER = DisableAbleCommandHandler("lowpromote", lowpromote)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote)

SET_TITLE_HANDLER = CommandHandler("title", set_title)
ADMIN_REFRESH_HANDLER = CommandHandler(
    "admincache", refresh_admin, filters=filters.ChatType.GROUPS
)

# Add handlers to application
application.add_handler(SET_DESC_HANDLER)
application.add_handler(SET_STICKER_HANDLER)
application.add_handler(SETCHATPIC_HANDLER)
application.add_handler(RMCHATPIC_HANDLER)
application.add_handler(SETCHAT_TITLE_HANDLER)
application.add_handler(ADMINLIST_HANDLER)
application.add_handler(PIN_HANDLER)
application.add_handler(UNPIN_HANDLER)
application.add_handler(BUG_HANDLER)
application.add_handler(PINNED_HANDLER)
application.add_handler(INVITE_HANDLER)
application.add_handler(PROMOTE_HANDLER)
application.add_handler(FULLPROMOTE_HANDLER)
application.add_handler(LOW_PROMOTE_HANDLER)
application.add_handler(DEMOTE_HANDLER)
application.add_handler(SET_TITLE_HANDLER)
application.add_handler(ADMIN_REFRESH_HANDLER)

__mod_name__ = "Admins 👮‍♀"
__command_list__ = [
    "setdesc", "setsticker", "setgpic", "delgpic", "setgtitle", "adminlist",
    "admins", "invitelink", "promote", "fullpromote", "lowpromote", "demote", "admincache",
]
__handlers__ = [
    SET_DESC_HANDLER, SET_STICKER_HANDLER, SETCHATPIC_HANDLER, RMCHATPIC_HANDLER,
    SETCHAT_TITLE_HANDLER, ADMINLIST_HANDLER, PIN_HANDLER, UNPIN_HANDLER,
    PINNED_HANDLER, INVITE_HANDLER, PROMOTE_HANDLER, FULLPROMOTE_HANDLER,
    LOW_PROMOTE_HANDLER, DEMOTE_HANDLER, SET_TITLE_HANDLER, ADMIN_REFRESH_HANDLER,
]

__helpbtns__ = [
    [
        InlineKeyboardButton("Approve", callback_data="cb_approve"),
        InlineKeyboardButton("Disable", callback_data="cb_disable"),
        InlineKeyboardButton("Group", callback_data="cb_group"),
    ],
    [
        InlineKeyboardButton("F-Sub", callback_data="cb_fsub"),
        InlineKeyboardButton("Feds", callback_data="cb_fed"),
        InlineKeyboardButton("Lock", callback_data="cb_lock"),
    ],
    [
        InlineKeyboardButton("🔙 Back", callback_data="help_back"),
        InlineKeyboardButton("Next ➡️", callback_data="cb_adminb"),
    ],
]
