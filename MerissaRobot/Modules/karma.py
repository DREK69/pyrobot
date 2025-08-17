import asyncio
import re
from pyrogram import filters
from pyrogram.types import Message

from MerissaRobot import OWNER_ID, pbot
from MerissaRobot.Database.mongo.karma_mongo import (
    alpha_to_int,
    get_karma,
    get_karmas,
    int_to_alpha,
    is_karma_on,
    karma_off,
    karma_on,
    update_karma,
)
from MerissaRobot.Handler.pyro.errors import capture_err
from MerissaRobot.Handler.pyro.filter_groups import (
    karma_negative_group,
    karma_positive_group,
)
from MerissaRobot.Handler.pyro.permissions import adminsOnly


# Regex patterns compiled once
REGEX_UPVOTE = re.compile(
    r"^(\+|\+\+|\+1|\+69|thx|thanx|thanks|🖤|❣️|💝|💖|💕|❤|💘|cool|good|👍|baby|thankyou|love|pro)$",
    re.IGNORECASE,
)
REGEX_DOWNVOTE = re.compile(
    r"^(\-|\-\-|\-1|👎|💔|noob|weak|fuck off|nub|gey|kid|shit|mf)$",
    re.IGNORECASE,
)


# -------------------- UPVOTE -------------------- #
@pbot.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(REGEX_UPVOTE)
    & ~filters.via_bot
    & ~filters.bot,
    group=karma_positive_group,
)
@capture_err
async def upvote(_, message: Message):
    if not await is_karma_on(message.chat.id):
        return
    if not message.reply_to_message.from_user or not message.from_user:
        return
    if message.reply_to_message.from_user.id == OWNER_ID:
        return await message.reply_text("👑 He’s the boss, always pro!")
    if message.reply_to_message.from_user.id == message.from_user.id:
        return  # no self karma farming

    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention

    current = await get_karma(chat_id, await int_to_alpha(user_id))
    karma = (current["karma"] if current else 0) + 1

    await update_karma(chat_id, await int_to_alpha(user_id), {"karma": karma})
    await message.reply_text(f"✨ Karma +1 for {mention}\n**Total Points:** {karma}")


# -------------------- DOWNVOTE -------------------- #
@pbot.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(REGEX_DOWNVOTE)
    & ~filters.via_bot
    & ~filters.bot,
    group=karma_negative_group,
)
@capture_err
async def downvote(_, message: Message):
    if not await is_karma_on(message.chat.id):
        return
    if not message.reply_to_message.from_user or not message.from_user:
        return
    if message.reply_to_message.from_user.id == OWNER_ID:
        return await message.reply_text("🙅 I won’t decrease the Owner’s karma.")
    if message.reply_to_message.from_user.id == message.from_user.id:
        return  # no self -karma

    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention

    current = await get_karma(message.chat.id, await int_to_alpha(user_id))
    karma = (current["karma"] if current else 0) - 1

    await update_karma(message.chat.id, await int_to_alpha(user_id), {"karma": karma})
    await message.reply_text(f"⚡ Karma -1 for {mention}\n**Total Points:** {karma}")


# -------------------- KARMA STATS -------------------- #
@pbot.on_message(filters.command("karmastat") & filters.group)
@capture_err
async def karma(_, message: Message):
    if not message.reply_to_message:
        m = await message.reply_text("📊 Analyzing Karma... Please wait.")
        all_karma = await get_karmas(message.chat.id)

        if not all_karma:
            return await m.edit_text("No karma data found in this chat.")

        # Build dict of user_id: karma
        karma_dicc = {
            str(await alpha_to_int(uid)): data["karma"] for uid, data in all_karma.items()
        }
        # Sort by karma value
        sorted_karma = dict(
            sorted(karma_dicc.items(), key=lambda item: item[1], reverse=True)
        )

        msg = f"**🏆 Karma list of {message.chat.title}:**\n\n"
        limit = 0

        for uid, points in sorted_karma.items():
            if limit >= 10:
                break
            try:
                user = await pbot.get_users(int(uid))
                await asyncio.sleep(0.8)  # avoid flood
            except Exception:
                continue

            if not user.first_name:
                continue
            name = (user.first_name[:12] + "...") if len(user.first_name) > 12 else user.first_name
            msg += f"`{points}`  {name}\n"
            limit += 1

        return await m.edit_text(msg)

    else:
        user_id = message.reply_to_message.from_user.id
        karma = await get_karma(message.chat.id, await int_to_alpha(user_id))
        karma = karma["karma"] if karma else 0
        return await message.reply_text(f"⭐ **Total Points:** {karma}")


# -------------------- KARMA SETTINGS -------------------- #
@pbot.on_message(filters.command("karma") & ~filters.private)
@adminsOnly("can_change_info")
async def karma_state(_, message: Message):
    usage = "**Usage:**\n/karma [ON|OFF]"
    if len(message.command) != 2:
        return await message.reply_text(usage)

    state = message.text.split(None, 1)[1].strip().lower()

    if state == "on":
        await karma_on(message.chat.id)
        await message.reply_text("✅ Karma system enabled.")
    elif state == "off":
        await karma_off(message.chat.id)
        await message.reply_text("🚫 Karma system disabled.")
    else:
        await message.reply_text(usage)
