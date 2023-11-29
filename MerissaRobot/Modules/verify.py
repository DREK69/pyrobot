from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MerissaRobot import LOGGER, pbot


@pbot.on_message(filters.command("verify") & ~filters.private)
async def verifylink(bot, update):
    chat = update.chat
    uid = update.from_user.id
    if len(update.command) < 2:
        try:
            channel_id = (await bot.get_chat(int(chat.id))).linked_chat.id
        except Exception:
            print(str(Exception))
            return await update.reply_text(
                "You didn't have connected Channel so try /verify channelid"
            )
    else:
        channel_id = int(update.text.split(None, 1)[1])
    m = await update.reply("Processing")
    try:
        user = await pbot.get_chat_member(chat_id=int(channel_id), user_id=uid)
        if user.privileges.can_post_messages != True:
            await update.reply_text(text="You can't do that")
            return
    except Exception as e:
        return LOGGER.critical(e)
    link = f"https://t.me/MerissaRobot?start=verify_{chat.id}"
    button = [
        [
            InlineKeyboardButton(text="VERIFY", url=link),
        ],
    ]
    await pbot.send_message(
        int(channel_id),
        text=f"{chat.title} is being protected by @MerissaRobot\n\nClick below to verify you're human",
        reply_markup=InlineKeyboardMarkup(button),
    )
    await m.edit("Done ✅")


@pbot.on_callback_query(filters.regex("^verify"))
async def howtoaap_cb(bot, query):
    await query.answer(
        "Verifying You are Human 🗣️",
        show_alert=True,
    )
    chat_id = query.data.split(None, 1)[1]
    link = (await bot.create_chat_invite_link(int(chat_id), member_limit=1)).invite_link
    button = [
        [
            InlineKeyboardButton(text="Join Link", url=link),
        ],
    ]
    await query.edit_message_caption(
        f"☑️ Verified with fast-pass as a trusted user, join below with the temporary link\n\n{link}\n\nThis link is a one time use and will expire",
        reply_markup=InlineKeyboardMarkup(button),
    )
