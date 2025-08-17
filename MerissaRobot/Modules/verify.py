from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from MerissaRobot import LOGGER, pbot


@pbot.on_message(filters.command("verify") & ~filters.private, group=7)
async def verifylink(bot, message):
    chat = message.chat
    uid = message.from_user.id

    # Get channel id
    if len(message.command) < 2:
        try:
            channel_id = (await bot.get_chat(chat.id)).linked_chat.id
        except Exception:
            return await message.reply_text(
                "⚠️ This group is not linked to a channel.\n\nUsage:\n`/verify <channel_id>`"
            )
    else:
        try:
            channel_id = int(message.text.split(None, 1)[1])
        except ValueError:
            return await message.reply_text("❌ Invalid channel ID.")

    m = await message.reply("⏳ Processing verification...")

    try:
        user = await bot.get_chat_member(channel_id, uid)
        # Check if user is an admin
        if not getattr(user, "privileges", None):
            return await message.reply_text("❌ You must be an **admin** in the channel.")
    except Exception as e:
        LOGGER.error(f"Verify failed: {e}")
        return await m.edit("❌ Could not check your channel privileges.")

    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?start=verify_{chat.id}"

    button = [[InlineKeyboardButton(text="✅ VERIFY", url=link)]]

    try:
        await bot.send_message(
            channel_id,
            text=(
                f"🔒 **{chat.title}** is protected by @{bot_username}\n\n"
                "Click below to verify you're human 👇"
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
        await m.edit("✅ Verification request sent to channel.")
    except Exception as e:
        LOGGER.error(f"Send failed: {e}")
        await m.edit("❌ Failed to send verification link to the channel.")


@pbot.on_callback_query(filters.regex(r"^verify_"))
async def verify_cb(bot, query):
    await query.answer("🧾 Verifying you as human...", show_alert=True)

    try:
        chat_id = int(query.data.split("_", 1)[1])
        link = (await bot.create_chat_invite_link(chat_id, member_limit=1)).invite_link
    except Exception as e:
        LOGGER.error(f"Invite creation failed: {e}")
        return await query.edit_message_text("❌ Could not generate invite link.")

    button = [[InlineKeyboardButton(text="👉 Join Chat", url=link)]]

    await query.edit_message_text(
        (
            f"☑️ Verified successfully!\n\n"
            f"🔗 Use the one-time invite link below:\n\n{link}\n\n"
            "⚠️ This link is single-use and will expire after one join."
        ),
        reply_markup=InlineKeyboardMarkup(button),
    )
