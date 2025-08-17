import html
import json
import os
from typing import Optional

from telegram import TelegramError, Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode
from telegram.helpers import mention_html

from MerissaRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    OWNER_ID,
    TIGERS,
    WOLVES,
    application,
)
from MerissaRobot.Handler.ptb.chat_status import dev_plus, sudo_plus, whitelist_plus
from MerissaRobot.Handler.ptb.extraction import extract_user
from MerissaRobot.Modules.log_channel import gloggable

ELEVATED_USERS_FILE = os.path.join(os.getcwd(), "MerissaRobot.Handler.pyro/users.json")


async def check_user_id(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    bot = context.bot
    if not user_id:
        reply = "❌ That...is a chat! baka ka omae?"

    elif user_id == bot.id:
        reply = "❌ This does not work that way."

    else:
        reply = None
    return reply


@dev_plus
@gloggable
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = await bot.get_chat(user_id)
    rt = ""

    reply = await check_user_id(user_id, context)
    if reply:
        await message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        await message.reply_text("👑 This member is already an **Emperor**!")
        return ""

    if user_id in DEMONS:
        rt += "✅ Successfully raised **Captain** to **Emperor**.\n"
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "✅ Successfully raised **Soldier** to **Emperor**.\n"
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    if user_id in TIGERS:
        rt += "✅ Successfully raised **Trader** to **Emperor**.\n"
        data["tigers"].remove(user_id)
        TIGERS.remove(user_id)

    data["sudos"].append(user_id)
    DRAGONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    await update.effective_message.reply_text(
        f"{rt}🎉 **Successfully raised {user_member.first_name} to Emperor!**",
        parse_mode=ParseMode.MARKDOWN
    )

    log_message = (
        f"#SUDO\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@sudo_plus
@gloggable
async def addsupport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = await bot.get_chat(user_id)
    rt = ""

    reply = await check_user_id(user_id, context)
    if reply:
        await message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "⬇️ Demoting this **Emperor** to **Captain**.\n"
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        await message.reply_text("🧞 This user is already a **Captain**!")
        return ""

    if user_id in WOLVES:
        rt += "✅ Successfully raised **Soldier** to **Captain**.\n"
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    if user_id in TIGERS:
        rt += "✅ Successfully raised **Trader** to **Captain**.\n"
        data["tigers"].remove(user_id)
        TIGERS.remove(user_id)

    data["supports"].append(user_id)
    DEMONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    await update.effective_message.reply_text(
        f"{rt}🎉 **{user_member.first_name} was added as a Captain!**",
        parse_mode=ParseMode.MARKDOWN
    )

    log_message = (
        f"#SUPPORT\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@sudo_plus
@gloggable
async def addwhitelist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = await bot.get_chat(user_id)
    rt = ""

    reply = await check_user_id(user_id, context)
    if reply:
        await message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "⬇️ This member is an **Emperor**, demoting to **Soldier**.\n"
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "⬇️ This user is a **Captain**, demoting to **Soldier**.\n"
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        await message.reply_text("🧜‍♂️ This user is already a **Soldier**!")
        return ""

    if user_id in TIGERS:
        rt += "✅ Successfully raised **Trader** to **Soldier**.\n"
        data["tigers"].remove(user_id)
        TIGERS.remove(user_id)

    data["whitelists"].append(user_id)
    WOLVES.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    await update.effective_message.reply_text(
        f"{rt}🎉 **Successfully raised {user_member.first_name} to be a Soldier!**",
        parse_mode=ParseMode.MARKDOWN
    )

    log_message = (
        f"#WHITELIST\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))} \n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@sudo_plus
@gloggable
async def addtiger(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = await bot.get_chat(user_id)
    rt = ""

    reply = await check_user_id(user_id, context)
    if reply:
        await message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "⬇️ This member is an **Emperor**, demoting to **Trader**.\n"
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "⬇️ This user is a **Captain**, demoting to **Trader**.\n"
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "⬇️ This user is a **Soldier**, demoting to **Trader**.\n"
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    if user_id in TIGERS:
        await message.reply_text("🧜 This user is already a **Trader**!")
        return ""

    data["tigers"].append(user_id)
    TIGERS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    await update.effective_message.reply_text(
        f"{rt}🎉 **Successfully made {user_member.first_name} a Trader!**",
        parse_mode=ParseMode.MARKDOWN
    )

    log_message = (
        f"#TIGER\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))} \n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message

@dev_plus
@gloggable
async def removesudo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = await bot.get_chat(user_id)

    reply = await check_user_id(user_id, context)
    if reply:
        await message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        await message.reply_text("⬇️ **Requested to demote this Emperor to Civilian**")
        DRAGONS.remove(user_id)
        data["sudos"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNSUDO\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = "<b>{}:</b>\n".format(html.escape(chat.title)) + log_message

        return log_message
    
    await message.reply_text("❌ This user is not an **Emperor**!")
    return ""


@sudo_plus
@gloggable
async def removesupport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = await bot.get_chat(user_id)

    reply = await check_user_id(user_id, context)
    if reply:
        await message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DEMONS:
        await message.reply_text("⬇️ **Demoting this Captain to Civilian**")
        DEMONS.remove(user_id)
        data["supports"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNSUPPORT\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    
    await message.reply_text("❌ This user is not a **Captain**!")
    return ""


@sudo_plus
@gloggable
async def removewhitelist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = await bot.get_chat(user_id)

    reply = await check_user_id(user_id, context)
    if reply:
        await message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in WOLVES:
        await message.reply_text("⬇️ **Demoting Soldier to normal user**")
        WOLVES.remove(user_id)
        data["whitelists"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNWHITELIST\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    
    await message.reply_text("❌ This user is not a **Soldier**!")
    return ""


@sudo_plus
@gloggable
async def removetiger(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = await bot.get_chat(user_id)

    reply = await check_user_id(user_id, context)
    if reply:
        await message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in TIGERS:
        await message.reply_text("⬇️ **Demoting Trader to normal user**")
        TIGERS.remove(user_id)
        data["tigers"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNTIGER\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    
    await message.reply_text("❌ This user is not a **Trader**!")
    return ""


# List Commands
@whitelist_plus
async def whitelistlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = "<b>🧜‍♂️ Known Soldiers:</b>\n"
    m = await update.effective_message.reply_text(
        "<code>📊 Gathering intel...</code>",
        parse_mode=ParseMode.HTML,
    )
    bot = context.bot
    for each_user in WOLVES:
        user_id = int(each_user)
        try:
            user = await bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    await m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
async def tigerlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = "<b>🧜 Known Traders:</b>\n"
    m = await update.effective_message.reply_text(
        "<code>📊 Gathering intel...</code>",
        parse_mode=ParseMode.HTML,
    )
    bot = context.bot
    for each_user in TIGERS:
        user_id = int(each_user)
        try:
            user = await bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    await m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
async def supportlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    m = await update.effective_message.reply_text(
        "<code>📊 Gathering intel...</code>",
        parse_mode=ParseMode.HTML,
    )
    reply = "<b>🧞 Known Captains:</b>\n"
    for each_user in DEMONS:
        user_id = int(each_user)
        try:
            user = await bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    await m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
async def sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    m = await update.effective_message.reply_text(
        "<code>📊 Gathering intel...</code>",
        parse_mode=ParseMode.HTML,
    )
    true_sudo = list(set(DRAGONS) - set(DEV_USERS))
    reply = "<b>🧞‍♀️ Known Emperors:</b>\n"
    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = await bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    await m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
async def devlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    m = await update.effective_message.reply_text(
        "<code>📊 Gathering intel...</code>",
        parse_mode=ParseMode.HTML,
    )
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply = "<b>🤴 Members of the Royal Family:</b>\n"
    for each_user in true_dev:
        user_id = int(each_user)
        try:
            user = await bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    await m.edit_text(reply, parse_mode=ParseMode.HTML)


# Handler Registration
SUDO_HANDLER = CommandHandler(("addsudo", "addemperor"), addsudo)
SUPPORT_HANDLER = CommandHandler(("addsupport", "addcaptain"), addsupport)
TIGER_HANDLER = CommandHandler("addsoldier", addtiger)
WHITELIST_HANDLER = CommandHandler(("addwhitelist", "addtrader"), addwhitelist)
UNSUDO_HANDLER = CommandHandler(("removesudo", "removeemperor"), removesudo)
UNSUPPORT_HANDLER = CommandHandler(("removesupport", "removecaptain"), removesupport)
UNTIGER_HANDLER = CommandHandler("removetiger", removetiger)
UNWHITELIST_HANDLER = CommandHandler(("removewhitelist", "removetrader"), removewhitelist)

WHITELISTLIST_HANDLER = CommandHandler(["whitelistlist", "soldiers"], whitelistlist)
TIGERLIST_HANDLER = CommandHandler(["tigerlist", "traders"], tigerlist)
SUPPORTLIST_HANDLER = CommandHandler(["supportlist", "captains"], supportlist)
SUDOLIST_HANDLER = CommandHandler(["sudolist", "emperors"], sudolist)
DEVLIST_HANDLER = CommandHandler(["devlist", "royals"], devlist)

application.add_handler(SUDO_HANDLER)
application.add_handler(SUPPORT_HANDLER)
application.add_handler(TIGER_HANDLER)
application.add_handler(WHITELIST_HANDLER)
application.add_handler(UNSUDO_HANDLER)
application.add_handler(UNSUPPORT_HANDLER)
application.add_handler(UNTIGER_HANDLER)
application.add_handler(UNWHITELIST_HANDLER)

application.add_handler(WHITELISTLIST_HANDLER)
application.add_handler(TIGERLIST_HANDLER)
application.add_handler(SUPPORTLIST_HANDLER)
application.add_handler(SUDOLIST_HANDLER)
application.add_handler(DEVLIST_HANDLER)

__mod_name__ = "Disasters"
__help__ = """
*User Management System - Disaster Control*

**Hierarchy System:**
👑 **Emperor** (Sudo) - Highest level access
🧞 **Captain** (Support) - Support level access  
🧜‍♂️ **Soldier** (Whitelist) - Whitelisted users
🧜 **Trader** (Tiger) - Basic elevated access

**Add Users (Dev/Sudo Only):**
❂ `/addsudo` or `/addemperor` - Promote to Emperor
❂ `/addsupport` or `/addcaptain` - Promote to Captain
❂ `/addwhitelist` or `/addtrader` - Add to Soldiers
❂ `/addsoldier` - Add to Traders

**Remove Users (Dev/Sudo Only):**
❂ `/removesudo` or `/removeemperor` - Demote Emperor
❂ `/removesupport` or `/removecaptain` - Demote Captain
❂ `/removewhitelist` or `/removetrader` - Remove Soldier
❂ `/removetiger` - Remove Trader

**List Users (Whitelist+ Access):**
❂ `/sudolist` or `/emperors` - List all Emperors
❂ `/supportlist` or `/captains` - List all Captains
❂ `/whitelistlist` or `/soldiers` - List all Soldiers
❂ `/tigerlist` or `/traders` - List all Traders
❂ `/devlist` or `/royals` - List Royal Family

**Features:**
• Automatic rank adjustment when promoting/demoting
• Persistent storage in JSON file
• Comprehensive logging system
• Permission-based access control
• User-friendly status messages with emojis

*Note:* Only users with appropriate permissions can manage the hierarchy.
"""

__handlers__ = [
    SUDO_HANDLER,
    SUPPORT_HANDLER,
    TIGER_HANDLER,
    WHITELIST_HANDLER,
    UNSUDO_HANDLER,
    UNSUPPORT_HANDLER,
    UNTIGER_HANDLER,
    UNWHITELIST_HANDLER,
    WHITELISTLIST_HANDLER,
    TIGERLIST_HANDLER,
    SUPPORTLIST_HANDLER,
    SUDOLIST_HANDLER,
    DEVLIST_HANDLER,
        ]
