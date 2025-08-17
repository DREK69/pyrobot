import html
import random
import re
import time
from functools import partial
from io import BytesIO

from telegram import (
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler,
    filters,
    MessageHandler,
)
from telegram.helpers import escape_markdown, mention_html, mention_markdown

import MerissaRobot.Database.sql.welcome_sql as sql
from MerissaRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    JOIN_LOGGER,
    LOGGER,
    OWNER_ID,
    WOLVES,
    application,
    sw,
)
from MerissaRobot.Database.sql.global_bans_sql import is_user_gbanned
from MerissaRobot.Handler.ptb.chat_status import is_user_ban_protected, user_admin
from MerissaRobot.Handler.ptb.handlers import MessageHandlerChecker
from MerissaRobot.Handler.ptb.misc import build_keyboard, revert_buttons
from MerissaRobot.Handler.ptb.msg_types import get_welcome_type
from MerissaRobot.Handler.ptb.string_handling import (
    escape_invalid_curly_brackets,
    markdown_parser,
)
from MerissaRobot.Modules.log_channel import loggable

VALID_WELCOME_FORMATTERS = [
    "first",
    "last",
    "fullname",
    "username",
    "id",
    "count",
    "chatname",
    "mention",
]

ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: application.bot.send_message,
    sql.Types.BUTTON_TEXT.value: application.bot.send_message,
    sql.Types.STICKER.value: application.bot.send_sticker,
    sql.Types.DOCUMENT.value: application.bot.send_document,
    sql.Types.PHOTO.value: application.bot.send_photo,
    sql.Types.AUDIO.value: application.bot.send_audio,
    sql.Types.VOICE.value: application.bot.send_voice,
    sql.Types.VIDEO.value: application.bot.send_video,
}

VERIFIED_USER_WAITLIST = {}
CAPTCHA_ANS_DICT = {}

from multicolorcaptcha import CaptchaGenerator


# do not async - utility function
async def send(update, message, keyboard, backup_message):
    chat = update.effective_chat
    cleanserv = sql.clean_service(chat.id)
    reply = None
    # Clean service welcome
    if cleanserv:
        try:
            await application.bot.delete_message(chat.id, update.message.message_id)
        except BadRequest:
            pass
        reply = False
    
    try:
        msg = await update.effective_message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
            reply_to_message_id=reply,
        )
    except BadRequest as excp:
        if excp.message == "Button_url_invalid":
            msg = await update.effective_chat.send_message(
                markdown_parser(
                    (
                        backup_message
                        + "\nNote: the current message has an invalid url in one of its buttons. Please update."
                    )
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )

        elif excp.message == "Have no rights to send a message":
            return
        elif excp.message == "Replied message not found":
            msg = await update.effective_message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
                reply_to_message_id=None,
            )

        elif excp.message == "Unsupported url protocol":
            msg = await update.effective_chat.send_message(
                markdown_parser(
                    (
                        backup_message
                        + "\nNote: the current message has buttons which use url protocols that are unsupported by telegram. Please update."
                    )
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )

        elif excp.message == "Wrong url host":
            msg = await update.effective_chat.send_message(
                markdown_parser(
                    (
                        backup_message
                        + "\nNote: the current message has some bad urls. Please update."
                    )
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )

            LOGGER.warning(message)
            LOGGER.warning(keyboard)
            LOGGER.exception("Could not parse! got invalid url host errors")
        else:
            msg = await update.effective_chat.send_message(
                markdown_parser(
                    (
                        backup_message
                        + "\nNote: An error occured when sending the custom message. Please update."
                    )
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )

            LOGGER.exception("Nothing")
    return msg


async def check_not_bot(member, chat_id, message_id, context):
    bot = context.bot
    member_dict = VERIFIED_USER_WAITLIST.pop((chat_id, member.id))
    member_status = member_dict.get("status")
    if not member_status:
        try:
            await bot.unban_chat_member(chat_id, member.id)
        except:
            pass

        try:
            await bot.edit_message_text(
                "*kicks user*\nThey can always rejoin and try.",
                chat_id=chat_id,
                message_id=message_id,
            )
        except:
            pass

@loggable
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):  # sourcery no-metrics
    bot, job_queue = context.bot, context.job_queue
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    should_welc, cust_welcome, cust_content, welc_type = sql.get_welc_pref(chat.id)
    welc_mutes = sql.welcome_mutes(chat.id)
    human_checks = sql.get_human_checks(user.id, chat.id)

    new_members = update.effective_message.new_chat_members

    for new_mem in new_members:
        welcome_log = None
        res = None
        sent = None
        should_mute = True
        welcome_bool = True
        media_wel = False

        if sw is not None:
            sw_ban = sw.get_ban(new_mem.id)
            if sw_ban:
                return

        reply = update.message.message_id
        cleanserv = sql.clean_service(chat.id)
        # Clean service welcome
        if cleanserv:
            try:
                await application.bot.delete_message(chat.id, update.message.message_id)
            except BadRequest:
                pass
            reply = False

        if should_welc:
            # Give the owner a special welcome
            if new_mem.id == OWNER_ID:
                await update.effective_message.reply_text(
                    f"👑 **Welcome to {html.escape(chat.title)} my king.**",
                    reply_to_message_id=reply,
                    parse_mode=ParseMode.MARKDOWN,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"My King just joined the chat"
                )
                continue

            # Welcome Devs
            if new_mem.id in DEV_USERS:
                await update.effective_message.reply_text(
                    "🤴 **Whoa! The Prince just joined!**",
                    reply_to_message_id=reply,
                    parse_mode=ParseMode.MARKDOWN,
                )
                continue

            # Welcome Sudos
            if new_mem.id in DRAGONS:
                await update.effective_message.reply_text(
                    "👑 **Huh! Emperor just joined! Stay Alert!**",
                    reply_to_message_id=reply,
                    parse_mode=ParseMode.MARKDOWN,
                )
                continue

            # Welcome Support
            if new_mem.id in DEMONS:
                await update.effective_message.reply_text(
                    "🧞 **Huh! Someone with Captain just joined!**",
                    reply_to_message_id=reply,
                    parse_mode=ParseMode.MARKDOWN,
                )
                continue

            # Welcome WOLVES
            if new_mem.id in WOLVES:
                await update.effective_message.reply_text(
                    "🧜‍♂️ **Oof! A Soldier Users just joined!**", 
                    reply_to_message_id=reply,
                    parse_mode=ParseMode.MARKDOWN,
                )
                continue

            # Welcome bot itself
            elif new_mem.id == bot.id:
                creator = None
                chat_admins = await bot.get_chat_administrators(update.effective_chat.id)
                for x in chat_admins:
                    if x.status == "creator":
                        creator = x.user
                        break
                        
                if creator:
                    await bot.send_message(
                        JOIN_LOGGER,
                        f"""
                        \\#NEWGROUP \
                        \nGroup Name:   **\\{chat.title}** \
                        \nID:   `\\{chat.id}` \
                        \nCreator ID:   `\\{creator.id}` \
                        \nCreator Username:   \@{creator.username or "None"} \
                        """,
                        parse_mode=ParseMode.MARKDOWN_V2,
                    )
                else:
                    await bot.send_message(
                        JOIN_LOGGER,
                        "#NEW_GROUP\n<b>Group name:</b> {}\n<b>ID:</b> <code>{}</code>".format(
                            html.escape(chat.title),
                            chat.id,
                        ),
                        parse_mode=ParseMode.HTML,
                    )

            buttons = sql.get_welc_buttons(chat.id)
            keyb = build_keyboard(buttons)

            if welc_type not in (sql.Types.TEXT, sql.Types.BUTTON_TEXT):
                media_wel = True

            first_name = (
                new_mem.first_name or "PersonWithNoName"
            )  # edge case of empty name - occurs for some bugs.

            if MessageHandlerChecker.check_user(update.effective_user.id):
                return

            if cust_welcome:
                if "%%%" in cust_welcome:
                    split = cust_welcome.split("%%%")
                    text = random.choice(split) if all(split) else cust_welcome
                else:
                    text = cust_welcome

                if cust_welcome == sql.DEFAULT_WELCOME_MESSAGES:
                    cust_welcome = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                        first=escape_markdown(first_name)
                    )

                if new_mem.last_name:
                    fullname = escape_markdown(f"{first_name} {new_mem.last_name}")
                else:
                    fullname = escape_markdown(first_name)
                    
                count = await chat.get_member_count()
                mention = mention_markdown(new_mem.id, escape_markdown(first_name))
                if new_mem.username:
                    username = "@" + escape_markdown(new_mem.username)
                else:
                    username = mention

                valid_format = escape_invalid_curly_brackets(
                    text, VALID_WELCOME_FORMATTERS
                )
                res = valid_format.format(
                    first=escape_markdown(first_name),
                    last=escape_markdown(new_mem.last_name or first_name),
                    fullname=escape_markdown(fullname),
                    username=username,
                    mention=mention,
                    count=count,
                    chatname=escape_markdown(chat.title),
                    id=new_mem.id,
                )

            else:
                res = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                    first=escape_markdown(first_name)
                )
                keyb = []

            backup_message = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                first=escape_markdown(first_name)
            )
            keyboard = InlineKeyboardMarkup(keyb)

        else:
            welcome_bool = False
            res = None
            keyboard = None
            backup_message = None
            reply = None

        # User exceptions from welcomemutes
        if (
            is_user_ban_protected(chat, new_mem.id, await chat.get_member(new_mem.id))
            or human_checks
        ):
            should_mute = False
        # Join welcome: soft mute
        if new_mem.is_bot:
            should_mute = False

        if user.id == new_mem.id and should_mute:
            if welc_mutes == "soft":
                await bot.restrict_chat_member(
                    chat.id,
                    new_mem.id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                        can_invite_users=False,
                        can_pin_messages=False,
                        can_send_polls=False,
                        can_change_info=False,
                        can_add_web_page_previews=False,
                    ),
                    until_date=(int(time.time() + 24 * 60 * 60)),
                )
                
            if welc_mutes == "strong":
                welcome_bool = False
                if not media_wel:
                    VERIFIED_USER_WAITLIST.update(
                        {
                            (chat.id, new_mem.id): {
                                "should_welc": should_welc,
                                "media_wel": False,
                                "status": False,
                                "update": update,
                                "res": res,
                                "keyboard": keyboard,
                                "backup_message": backup_message,
                            }
                        }
                    )
                else:
                    VERIFIED_USER_WAITLIST.update(
                        {
                            (chat.id, new_mem.id): {
                                "should_welc": should_welc,
                                "chat_id": chat.id,
                                "status": False,
                                "media_wel": True,
                                "cust_content": cust_content,
                                "welc_type": welc_type,
                                "res": res,
                                "keyboard": keyboard,
                            }
                        }
                    )
                    
                new_join_mem = (
                    f"[{escape_markdown(new_mem.first_name)}](tg://user?id={user.id})"
                )
                message = await msg.reply_text(
                    f"{new_join_mem}, click the button below to prove you're human.\nYou have 120 seconds.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Yes, I'm human.",
                                    callback_data=f"user_join_({new_mem.id})",
                                )
                            ]
                        ]
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=reply,
                )
                await bot.restrict_chat_member(
                    chat.id,
                    new_mem.id,
                    permissions=ChatPermissions(
                        can_send_messages=False,
                        can_invite_users=False,
                        can_pin_messages=False,
                        can_send_polls=False,
                        can_change_info=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False,
                    ),
                )
                job_queue.run_once(
                    partial(check_not_bot, new_mem, chat.id, message.message_id),
                    120,
                    name="welcomemute",
                )
                
            if welc_mutes == "captcha":
                btn = []
                # Captcha image size number (2 -> 640x360)
                CAPCTHA_SIZE_NUM = 2
                # Create Captcha Generator object of specified size
                generator = CaptchaGenerator(CAPCTHA_SIZE_NUM)

                # Generate a captcha image
                captcha = generator.gen_captcha_image(difficult_level=3)
                # Get information
                image = captcha["image"]
                characters = captcha["characters"]
                # print(characters)
                fileobj = BytesIO()
                fileobj.name = f"captcha_{new_mem.id}.png"
                image.save(fp=fileobj)
                fileobj.seek(0)
                CAPTCHA_ANS_DICT[(chat.id, new_mem.id)] = int(characters)
                welcome_bool = False
                
                if not media_wel:
                    VERIFIED_USER_WAITLIST.update(
                        {
                            (chat.id, new_mem.id): {
                                "should_welc": should_welc,
                                "media_wel": False,
                                "status": False,
                                "update": update,
                                "res": res,
                                "keyboard": keyboard,
                                "backup_message": backup_message,
                                "captcha_correct": characters,
                            }
                        }
                    )
                else:
                    VERIFIED_USER_WAITLIST.update(
                        {
                            (chat.id, new_mem.id): {
                                "should_welc": should_welc,
                                "chat_id": chat.id,
                                "status": False,
                                "media_wel": True,
                                "cust_content": cust_content,
                                "welc_type": welc_type,
                                "res": res,
                                "keyboard": keyboard,
                                "captcha_correct": characters,
                            }
                        }
                    )

                nums = [random.randint(1000, 9999) for _ in range(7)]
                nums.append(characters)
                random.shuffle(nums)
                to_append = []
                # print(nums)
                for a in nums:
                    to_append.append(
                        InlineKeyboardButton(
                            text=str(a),
                            callback_data=f"user_captchajoin_({chat.id},{new_mem.id})_({a})",
                        )
                    )
                    if len(to_append) > 2:
                        btn.append(to_append)
                        to_append = []
                if to_append:
                    btn.append(to_append)

                message = await msg.reply_photo(
                    fileobj,
                    caption=f"Welcome [{escape_markdown(new_mem.first_name)}](tg://user?id={user.id}). Click the correct button to get unmuted!",
                    reply_markup=InlineKeyboardMarkup(btn),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=reply,
                )
                await bot.restrict_chat_member(
                    chat.id,
                    new_mem.id,
                    permissions=ChatPermissions(
                        can_send_messages=False,
                        can_invite_users=False,
                        can_pin_messages=False,
                        can_send_polls=False,
                        can_change_info=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False,
                    ),
                )

        if welcome_bool:
            if media_wel:
                if ENUM_FUNC_MAP[welc_type] == application.bot.send_sticker:
                    sent = await ENUM_FUNC_MAP[welc_type](
                        chat.id,
                        cust_content,
                        reply_markup=keyboard,
                        reply_to_message_id=reply,
                    )
                else:
                    sent = await ENUM_FUNC_MAP[welc_type](
                        chat.id,
                        cust_content,
                        caption=res,
                        reply_markup=keyboard,
                        reply_to_message_id=reply,
                        parse_mode="markdown",
                    )
            else:
                sent = await send(update, res, keyboard, backup_message)
                
            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    await bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

        if welcome_log:
            return welcome_log

        if user.id == new_mem.id:
            welcome_log = (
                f"{html.escape(chat.title)}\n"
                f"#USER_JOINED\n"
                f"<b>User</b>: {mention_html(user.id, user.first_name)}\n"
                f"<b>ID</b>: <code>{user.id}</code>"
            )
        elif new_mem.is_bot:
            welcome_log = (
                f"{html.escape(chat.title)}\n"
                f"#BOT_ADDED\n"
                f"<b>Bot</b>: {mention_html(new_mem.id, new_mem.first_name)}\n"
                f"<b>ID</b>: <code>{new_mem.id}</code>"
            )
        else:
            welcome_log = (
                f"{html.escape(chat.title)}\n"
                f"#USER_ADDED\n"
                f"<b>User</b>: {mention_html(new_mem.id, new_mem.first_name)}\n"
                f"<b>ID</b>: <code>{new_mem.id}</code>"
            )
        return welcome_log

async def left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):  # sourcery no-metrics
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    should_goodbye, cust_goodbye, goodbye_type = sql.get_gdbye_pref(chat.id)

    if user.id == bot.id:
        return

    reply = update.message.message_id
    cleanserv = sql.clean_service(chat.id)
    # Clean service welcome
    if cleanserv:
        try:
            await application.bot.delete_message(chat.id, update.message.message_id)
        except BadRequest:
            pass
        reply = False

    if should_goodbye:
        left_mem = update.effective_message.left_chat_member
        if left_mem:
            # Thingy for spamwatched users
            if sw is not None:
                sw_ban = sw.get_ban(left_mem.id)
                if sw_ban:
                    return

            # Dont say goodbyes to gbanned users
            if is_user_gbanned(left_mem.id):
                return

            # Ignore bot being kicked
            if left_mem.id == bot.id:
                return

            # Give the owner a special goodbye
            if left_mem.id == OWNER_ID:
                await update.effective_message.reply_text(
            f"✅ **This chat has its goodbye setting set to:** `{pref}`\n"
            f"📝 **The goodbye message (not filling the {{}}) is:**",
            parse_mode=ParseMode.MARKDOWN,
        )

        if goodbye_type == sql.Types.BUTTON_TEXT:
            buttons = sql.get_gdbye_buttons(chat.id)
            if noformat:
                goodbye_m += revert_buttons(buttons)
                await update.effective_message.reply_text(goodbye_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                await send(
                    update,
                    goodbye_m,
                    keyboard,
                    random.choice(sql.DEFAULT_GOODBYE_MESSAGES),
                )

        elif noformat:
            await ENUM_FUNC_MAP[goodbye_type](chat.id, goodbye_m)

        else:
            await ENUM_FUNC_MAP[goodbye_type](
                chat.id, goodbye_m, parse_mode=ParseMode.MARKDOWN
            )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_gdbye_preference(str(chat.id), True)
            await update.effective_message.reply_text("✅ **Ok!**")

        elif args[0].lower() in ("off", "no"):
            sql.set_gdbye_preference(str(chat.id), False)
            await update.effective_message.reply_text("❌ **Ok!**")

        else:
            # idek what you're writing, say yes or no
            await update.effective_message.reply_text(
                "❓ **I understand 'on/yes' or 'off/no' only!**"
            )


@user_admin
@loggable
async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        await msg.reply_text("❌ **You didn't specify what to reply with!**")
        return ""

    sql.set_custom_welcome(chat.id, content, text, data_type, buttons)
    await msg.reply_text("✅ **Successfully set custom welcome message!**")

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#SET_WELCOME\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Set the welcome message."
    )


@user_admin
@loggable
async def reset_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_welcome(
        chat.id, None, random.choice(sql.DEFAULT_WELCOME_MESSAGES), sql.Types.TEXT
    )
    await update.effective_message.reply_text(
        "✅ **Successfully reset welcome message to default!**"
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RESET_WELCOME\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Reset the welcome message to default."
    )


@user_admin
@loggable
async def set_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        await msg.reply_text("❌ **You didn't specify what to reply with!**")
        return ""

    sql.set_custom_gdbye(chat.id, content or text, data_type, buttons)
    await msg.reply_text("✅ **Successfully set custom goodbye message!**")
    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#SET_GOODBYE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Set the goodbye message."
    )


@user_admin
@loggable
async def reset_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_gdbye(
        chat.id, random.choice(sql.DEFAULT_GOODBYE_MESSAGES), sql.Types.TEXT
    )
    await update.effective_message.reply_text(
        "✅ **Successfully reset goodbye message to default!**"
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RESET_GOODBYE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Reset the goodbye message."
    )        "👑 **Sorry to see you leave :(**", 
                    reply_to_message_id=reply,
                    parse_mode=ParseMode.MARKDOWN,
                )
                return

            # Give the devs a special goodbye
            if left_mem.id in DEV_USERS:
                await update.effective_message.reply_text(
                    "🤴 **See you later at the Eagle Union!**",
                    reply_to_message_id=reply,
                    parse_mode=ParseMode.MARKDOWN,
                )
                return

            # if media goodbye, use appropriate function for it
            if goodbye_type not in [sql.Types.TEXT, sql.Types.BUTTON_TEXT]:
                await ENUM_FUNC_MAP[goodbye_type](chat.id, cust_goodbye)
                return

            first_name = (
                left_mem.first_name or "PersonWithNoName"
            )  # edge case of empty name - occurs for some bugs.
            
            if cust_goodbye:
                if cust_goodbye == sql.DEFAULT_GOODBYE_MESSAGES:
                    cust_goodbye = random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(
                        first=escape_markdown(first_name)
                    )
                if left_mem.last_name:
                    fullname = escape_markdown(f"{first_name} {left_mem.last_name}")
                else:
                    fullname = escape_markdown(first_name)
                    
                count = await chat.get_member_count()
                mention = mention_markdown(left_mem.id, first_name)
                if left_mem.username:
                    username = "@" + escape_markdown(left_mem.username)
                else:
                    username = mention

                valid_format = escape_invalid_curly_brackets(
                    cust_goodbye, VALID_WELCOME_FORMATTERS
                )
                res = valid_format.format(
                    first=escape_markdown(first_name),
                    last=escape_markdown(left_mem.last_name or first_name),
                    fullname=escape_markdown(fullname),
                    username=username,
                    mention=mention,
                    count=count,
                    chatname=escape_markdown(chat.title),
                    id=left_mem.id,
                )
                buttons = sql.get_gdbye_buttons(chat.id)
                keyb = build_keyboard(buttons)

            else:
                res = random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(
                    first=first_name
                )
                keyb = []

            keyboard = InlineKeyboardMarkup(keyb)

            await send(
                update,
                res,
                keyboard,
                random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(first=first_name),
            )


@user_admin
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    chat = update.effective_chat
    # if no args, show current replies.
    if not args or args[0].lower() == "noformat":
        noformat = True
        pref, welcome_m, cust_content, welcome_type = sql.get_welc_pref(chat.id)
        await update.effective_message.reply_text(
            f"✅ **This chat has its welcome setting set to:** `{pref}`\n"
            f"📝 **The welcome message (not filling the {{}}) is:**",
            parse_mode=ParseMode.MARKDOWN,
        )

        if welcome_type in [sql.Types.BUTTON_TEXT, sql.Types.TEXT]:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                await update.effective_message.reply_text(welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                await send(
                    update,
                    welcome_m,
                    keyboard,
                    random.choice(sql.DEFAULT_WELCOME_MESSAGES),
                )
        else:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                await ENUM_FUNC_MAP[welcome_type](chat.id, cust_content, caption=welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)
                await ENUM_FUNC_MAP[welcome_type](
                    chat.id,
                    cust_content,
                    caption=welcome_m,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_welc_preference(str(chat.id), True)
            await update.effective_message.reply_text(
                "✅ **Okay! I'll greet members when they join.**"
            )

        elif args[0].lower() in ("off", "no"):
            sql.set_welc_preference(str(chat.id), False)
            await update.effective_message.reply_text(
                "❌ **I'll go loaf around and not welcome anyone then.**"
            )

        else:
            await update.effective_message.reply_text(
                "❓ **I understand 'on/yes' or 'off/no' only!**"
            )


@user_admin
async def goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    chat = update.effective_chat

    if not args or args[0] == "noformat":
        noformat = True
        pref, goodbye_m, goodbye_type = sql.get_gdbye_pref(chat.id)
        await update.effective_message.reply_text(
            f"✅ **This chat has its goodbye setting set to:** `{pref}`\n"
            f"📝 **The goodbye message (not filling the {{}}) is:**",
            parse_mode=ParseMode.MARKDOWN,
        )

        if goodbye_type == sql.Types.BUTTON_TEXT:
            buttons = sql.get_gdbye_buttons(chat.id)
            if noformat:
                goodbye_m += revert_buttons(buttons)
                await update.effective_message.reply_text(goodbye_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                await send(
                    update,
                    goodbye_m,
                    keyboard,
                    random.choice(sql.DEFAULT_GOODBYE_MESSAGES),
                )

        elif noformat:
            await ENUM_FUNC_MAP[goodbye_type](chat.id, goodbye_m)

        else:
            await ENUM_FUNC_MAP[goodbye_type](
                chat.id, goodbye_m, parse_mode=ParseMode.MARKDOWN
            )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_gdbye_preference(str(chat.id), True)
            await update.effective_message.reply_text("✅ **Ok!**")

        elif args[0].lower() in ("off", "no"):
            sql.set_gdbye_preference(str(chat.id), False)
            await update.effective_message.reply_text("❌ **Ok!**")

        else:
            # idek what you're writing, say yes or no
            await update.effective_message.reply_text(
                "❓ **I understand 'on/yes' or 'off/no' only!**"
            )


@user_admin
@loggable
async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        await msg.reply_text("❌ **You didn't specify what to reply with!**")
        return ""

    sql.set_custom_welcome(chat.id, content, text, data_type, buttons)
    await msg.reply_text("✅ **Successfully set custom welcome message!**")

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#SET_WELCOME\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Set the welcome message."
    )


@user_admin
@loggable
async def reset_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_welcome(
        chat.id, None, random.choice(sql.DEFAULT_WELCOME_MESSAGES), sql.Types.TEXT
    )
    await update.effective_message.reply_text(
        "✅ **Successfully reset welcome message to default!**"
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RESET_WELCOME\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Reset the welcome message to default."
    )


@user_admin
@loggable
async def set_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        await msg.reply_text("❌ **You didn't specify what to reply with!**")
        return ""

    sql.set_custom_gdbye(chat.id, content or text, data_type, buttons)
    await msg.reply_text("✅ **Successfully set custom goodbye message!**")
    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#SET_GOODBYE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Set the goodbye message."
    )


@user_admin
@loggable
async def reset_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_gdbye(
        chat.id, random.choice(sql.DEFAULT_GOODBYE_MESSAGES), sql.Types.TEXT
    )
    await update.effective_message.reply_text(
        "✅ **Successfully reset goodbye message to default!**"
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RESET_GOODBYE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Reset the goodbye message."
    )


@user_admin
@loggable
async def welcomemute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if len(args) >= 1:
        if args[0].lower() in ("off", "no"):
            sql.set_welcome_mutes(chat.id, False)
            await msg.reply_text("✅ **I will no longer mute people on joining!**")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>• Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has toggled welcome mute to <b>OFF</b>."
            )
        if args[0].lower() in ["soft"]:
            sql.set_welcome_mutes(chat.id, "soft")
            await msg.reply_text(
                "🔇 **I will restrict users' permission to send media for 24 hours.**"
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>• Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has toggled welcome mute to <b>SOFT</b>."
            )
        if args[0].lower() in ["strong"]:
            sql.set_welcome_mutes(chat.id, "strong")
            await msg.reply_text(
                "🔒 **I will now mute people when they join until they prove they're not a bot.**\n**They will have 120 seconds before they get kicked.**"
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>• Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has toggled welcome mute to <b>STRONG</b>."
            )
        if args[0].lower() in ["captcha"]:
            sql.set_welcome_mutes(chat.id, "captcha")
            await msg.reply_text(
                "🧩 **I will now mute people when they join until they prove they're not a bot.**\n**They have to solve a captcha to get unmuted.**"
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>• Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Has toggled welcome mute to <b>CAPTCHA</b>."
            )
        await msg.reply_text(
            "❓ **Please enter** `off`/`no`/`soft`/`strong`/`captcha`**!**",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    
    curr_setting = sql.welcome_mutes(chat.id)
    reply = (
        f"\n❓ **Give me a setting!**\n📋 **Choose one out of:** `off`/`no` or `soft`, `strong` or `captcha` only! \n"
        f"⚙️ **Current setting:** `{curr_setting}`"
    )
    await msg.reply_text(reply, parse_mode=ParseMode.MARKDOWN)
    return ""


@user_admin
@loggable
async def clean_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user

    if not args:
        clean_pref = sql.get_clean_pref(chat.id)
        if clean_pref:
            await update.effective_message.reply_text(
                "🧹 **I should be deleting welcome messages up to two days old.**"
            )
        else:
            await update.effective_message.reply_text(
                "❌ **I'm currently not deleting old welcome messages!**"
            )
        return ""

    if args[0].lower() in ("on", "yes"):
        sql.set_clean_welcome(str(chat.id), True)
        await update.effective_message.reply_text("✅ **I'll try to delete old welcome messages!**")
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#CLEAN_WELCOME\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"Has toggled clean welcomes to <code>ON</code>."
        )
    if args[0].lower() in ("off", "no"):
        sql.set_clean_welcome(str(chat.id), False)
        await update.effective_message.reply_text("❌ **I won't delete old welcome messages.**")
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#CLEAN_WELCOME\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"Has toggled clean welcomes to <code>OFF</code>."
        )
    await update.effective_message.reply_text("❓ **I understand 'on/yes' or 'off/no' only!**")
    return ""


@user_admin
async def cleanservice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat = update.effective_chat
    
    if chat.type == chat.PRIVATE:
        curr = sql.clean_service(chat.id)
        if curr:
            await update.effective_message.reply_text(
                "🧹 **Welcome clean service is:** `on`", parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.effective_message.reply_text(
                "❌ **Welcome clean service is:** `off`", parse_mode=ParseMode.MARKDOWN
            )

    elif len(args) >= 1:
        var = args[0]
        if var in ("no", "off"):
            sql.set_clean_service(chat.id, False)
            await update.effective_message.reply_text("❌ **Welcome clean service is:** `off`")
        elif var in ("yes", "on"):
            sql.set_clean_service(chat.id, True)
            await update.effective_message.reply_text("✅ **Welcome clean service is:** `on`")
        else:
            await update.effective_message.reply_text(
                "❌ **Invalid option**", parse_mode=ParseMode.MARKDOWN
            )
    else:
        await update.effective_message.reply_text(
            "❓ **Usage is** `on/yes` **or** `off/no`", parse_mode=ParseMode.MARKDOWN
        )

async def user_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    query = update.callback_query
    bot = context.bot
    match = re.match(r"user_join_\((.+?)\)", query.data)
    message = update.effective_message
    join_user = int(match.group(1))

    if join_user == user.id:
        sql.set_human_checks(user.id, chat.id)
        member_dict = VERIFIED_USER_WAITLIST[(chat.id, user.id)]
        member_dict["status"] = True
        await query.answer(text="✅ Yeet! You're a human, unmuted!")
        await bot.restrict_chat_member(
            chat.id,
            user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        try:
            await bot.delete_message(chat.id, message.message_id)
        except:
            pass
        if member_dict["should_welc"]:
            if member_dict["media_wel"]:
                sent = await ENUM_FUNC_MAP[member_dict["welc_type"]](
                    member_dict["chat_id"],
                    member_dict["cust_content"],
                    caption=member_dict["res"],
                    reply_markup=member_dict["keyboard"],
                    parse_mode="markdown",
                )
            else:
                sent = await send(
                    member_dict["update"],
                    member_dict["res"],
                    member_dict["keyboard"],
                    member_dict["backup_message"],
                )

            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    await bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

    else:
        await query.answer(text="❌ You're not allowed to do this!")


async def user_captcha_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # sourcery no-metrics
    chat = update.effective_chat
    user = update.effective_user
    query = update.callback_query
    bot = context.bot
    # print(query.data)
    match = re.match(r"user_captchajoin_\(([\d\-]+),(\d+)\)_\((\d{4})\)", query.data)
    message = update.effective_message
    join_chat = int(match.group(1))
    join_user = int(match.group(2))
    captcha_ans = int(match.group(3))
    join_usr_data = await bot.get_chat(join_user)

    if join_user == user.id:
        c_captcha_ans = CAPTCHA_ANS_DICT.pop((join_chat, join_user))
        if c_captcha_ans == captcha_ans:
            sql.set_human_checks(user.id, chat.id)
            member_dict = VERIFIED_USER_WAITLIST[(chat.id, user.id)]
            member_dict["status"] = True
            await query.answer(text="✅ Yeet! You're a human, unmuted!")
            await bot.restrict_chat_member(
                chat.id,
                user.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                    can_send_polls=True,
                    can_change_info=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )
            try:
                await bot.delete_message(chat.id, message.message_id)
            except:
                pass
            if member_dict["should_welc"]:
                if member_dict["media_wel"]:
                    sent = await ENUM_FUNC_MAP[member_dict["welc_type"]](
                        member_dict["chat_id"],
                        member_dict["cust_content"],
                        caption=member_dict["res"],
                        reply_markup=member_dict["keyboard"],
                        parse_mode="markdown",
                    )
                else:
                    sent = await send(
                        member_dict["update"],
                        member_dict["res"],
                        member_dict["keyboard"],
                        member_dict["backup_message"],
                    )

                prev_welc = sql.get_clean_pref(chat.id)
                if prev_welc:
                    try:
                        await bot.delete_message(chat.id, prev_welc)
                    except BadRequest:
                        pass

                    if sent:
                        sql.set_clean_welcome(chat.id, sent.message_id)
        else:
            try:
                await bot.delete_message(chat.id, message.message_id)
            except:
                pass
            kicked_msg = f"""
            ❌ [{escape_markdown(join_usr_data.first_name)}](tg://user?id={join_user}) failed the captcha and was kicked.
            """
            await query.answer(text="❌ Wrong answer")
            res = await chat.unban_member(join_user)
            if res:
                await bot.send_message(
                    chat_id=chat.id, text=kicked_msg, parse_mode=ParseMode.MARKDOWN
                )

    else:
        await query.answer(text="❌ You're not allowed to do this!")


WELC_HELP_TXT = (
    "Your group's welcome/goodbye messages can be personalised in multiple ways. If you want the messages"
    " to be individually generated, like the default welcome message is, you can use *these* variables:\n"
    "  • `{first}`*:* this represents the user's *first* name\n"
    "  • `{last}`*:* this represents the user's *last* name. Defaults to *first name* if user has no "
    "last name.\n"
    "  • `{fullname}`*:* this represents the user's *full* name. Defaults to *first name* if user has no "
    "last name.\n"
    "  • `{username}`*:* this represents the user's *username*. Defaults to a *mention* of the user's "
    "first name if has no username.\n"
    "  • `{mention}`*:* this simply *mentions* a user - tagging them with their first name.\n"
    "  • `{id}`*:* this represents the user's *id*\n"
    "  • `{count}`*:* this represents the user's *member number*.\n"
    "  • `{chatname}`*:* this represents the *current chat name*.\n"
    "\nEach variable MUST be surrounded by `{}` to be replaced.\n"
    "Welcome messages also support markdown, so you can make any elements bold/italic/code/links. "
    "Buttons are also supported, so you can make your welcomes look awesome with some nice intro "
    "buttons.\n"
    f"To create a button linking to your rules, use this: `[Rules](buttonurl://t.me/{application.bot.username}?start=group_id)`. "
    "Simply replace `group_id` with your group's id, which can be obtained via /id, and you're good to "
    "go. Note that group ids are usually preceded by a `-` sign; this is required, so please don't "
    "remove it.\n"
    "You can even set images/gifs/videos/voice messages as the welcome message by "
    "replying to the desired media, and calling `/setwelcome`."
)

WELC_MUTE_HELP_TXT = (
    "You can get the bot to mute new people who join your group and hence prevent spambots from flooding your group. "
    "The following options are possible:\n"
    "  • `/welcomemute soft`*:* restricts new members from sending media for 24 hours.\n"
    "  • `/welcomemute strong`*:* mutes new members till they tap on a button thereby verifying they're human.\n"
    "  • `/welcomemute captcha`*:*  mutes new members till they solve a button captcha thereby verifying they're human.\n"
    "  • `/welcomemute off`*:* turns off welcomemute.\n"
    "*Note:* Strong mode kicks a user from the chat if they dont verify in 120seconds. They can always rejoin though"
)


@user_admin
async def welcome_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(WELC_HELP_TXT, parse_mode=ParseMode.MARKDOWN)


@user_admin
async def welcome_mute_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        WELC_MUTE_HELP_TXT, parse_mode=ParseMode.MARKDOWN
    )


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, _):
    welcome_pref = sql.get_welc_pref(chat_id)[0]
    goodbye_pref = sql.get_gdbye_pref(chat_id)[0]
    return (
        "This chat has it's welcome preference set to `{}`.\n"
        "It's goodbye preference is `{}`.".format(welcome_pref, goodbye_pref)
    )


__help__ = """
*Welcome & Goodbye System*

**Admin Commands:**
❂ `/welcome <on/off>` - Enable/disable welcome messages
❂ `/welcome` - Show current welcome settings
❂ `/welcome noformat` - Show current welcome settings without formatting
❂ `/goodbye` - Same usage and args as `/welcome`
❂ `/setwelcome <text>` - Set a custom welcome message (reply to media to use media)
❂ `/setgoodbye <text>` - Set a custom goodbye message (reply to media to use media)
❂ `/resetwelcome` - Reset to the default welcome message
❂ `/resetgoodbye` - Reset to the default goodbye message
❂ `/cleanwelcome <on/off>` - Delete previous welcome message to avoid spam
❂ `/welcomemute <soft/strong/captcha/off>` - Mute new members until verification
❂ `/cleanservice <on/off>` - Delete telegram's service messages
❂ `/welcomehelp` - View formatting information for welcome/goodbye messages
❂ `/welcomemutehelp` - Get information about welcome mutes

**Welcome Mute Options:**
• `soft` - Restrict media for 24 hours
• `strong` - Mute until button verification (120s timeout)
• `captcha` - Mute until captcha solved
• `off` - Disable welcome mute

**Variables for Messages:**
• `{first}` - First name
• `{last}` - Last name  
• `{fullname}` - Full name
• `{username}` - Username or mention
• `{mention}` - Mention user
• `{id}` - User ID
• `{count}` - Member count
• `{chatname}` - Chat name

**Features:**
• Support for media welcomes (photos, videos, stickers, etc.)
• Button support for interactive welcomes
• Anti-spam protection with captcha/verification
• Clean service messages
• Customizable for each chat
"""

__helpbtns__ = [
    [
        InlineKeyboardButton("Captcha", callback_data="cb_captcha"),
        InlineKeyboardButton("Formatting", callback_data="cb_format"),
    ],
    [
        InlineKeyboardButton("🔙 Back", callback_data="help_back"),
    ],
]

NEW_MEM_HANDLER = MessageHandler(
    filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member
)
LEFT_MEM_HANDLER = MessageHandler(
    filters.StatusUpdate.LEFT_CHAT_MEMBER, left_member
)
WELC_PREF_HANDLER = CommandHandler(
    "welcome", welcome, filters=filters.ChatType.GROUPS
)
GOODBYE_PREF_HANDLER = CommandHandler(
    "goodbye", goodbye, filters=filters.ChatType.GROUPS
)
SET_WELCOME = CommandHandler(
    "setwelcome", set_welcome, filters=filters.ChatType.GROUPS
)
SET_GOODBYE = CommandHandler(
    "setgoodbye", set_goodbye, filters=filters.ChatType.GROUPS
)
RESET_WELCOME = CommandHandler(
    "resetwelcome", reset_welcome, filters=filters.ChatType.GROUPS
)
RESET_GOODBYE = CommandHandler(
    "resetgoodbye", reset_goodbye, filters=filters.ChatType.GROUPS
)
WELCOMEMUTE_HANDLER = CommandHandler(
    "welcomemute", welcomemute, filters=filters.ChatType.GROUPS
)
CLEAN_SERVICE_HANDLER = CommandHandler(
    "cleanservice", cleanservice, filters=filters.ChatType.GROUPS
)
CLEAN_WELCOME = CommandHandler(
    "cleanwelcome", clean_welcome, filters=filters.ChatType.GROUPS
)
WELCOME_HELP = CommandHandler("welcomehelp", welcome_help)
WELCOME_MUTE_HELP = CommandHandler("welcomemutehelp", welcome_mute_help)
BUTTON_VERIFY_HANDLER = CallbackQueryHandler(
    user_button, pattern=r"user_join_"
)
CAPTCHA_BUTTON_VERIFY_HANDLER = CallbackQueryHandler(
    user_captcha_button,
    pattern=r"user_captchajoin_\([\d\-]+,\d+\)_\(\d{4}\)",
)

application.add_handler(NEW_MEM_HANDLER)
application.add_handler(LEFT_MEM_HANDLER)
application.add_handler(WELC_PREF_HANDLER)
application.add_handler(GOODBYE_PREF_HANDLER)
application.add_handler(SET_WELCOME)
application.add_handler(SET_GOODBYE)
application.add_handler(RESET_WELCOME)
application.add_handler(RESET_GOODBYE)
application.add_handler(CLEAN_WELCOME)
application.add_handler(WELCOME_HELP)
application.add_handler(WELCOMEMUTE_HANDLER)
application.add_handler(CLEAN_SERVICE_HANDLER)
application.add_handler(BUTTON_VERIFY_HANDLER)
application.add_handler(WELCOME_MUTE_HELP)
application.add_handler(CAPTCHA_BUTTON_VERIFY_HANDLER)

__mod_name__ = "Welcome 🤗"
__command_list__ = []
__handlers__ = [
    NEW_MEM_HANDLER,
    LEFT_MEM_HANDLER,
    WELC_PREF_HANDLER,
    GOODBYE_PREF_HANDLER,
    SET_WELCOME,
    SET_GOODBYE,
    RESET_WELCOME,
    RESET_GOODBYE,
    CLEAN_WELCOME,
    WELCOME_HELP,
    WELCOMEMUTE_HANDLER,
    CLEAN_SERVICE_HANDLER,
    BUTTON_VERIFY_HANDLER,
    CAPTCHA_BUTTON_VERIFY_HANDLER,
    WELCOME_MUTE_HELP,
]
