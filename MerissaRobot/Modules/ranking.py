from datetime import date
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from MerissaRobot import pbot as app
from MerissaRobot.Database.mongo.chatdb_mongo import chatdb, get_name, increase_count


@app.on_message(
    ~filters.bot
    & ~filters.forwarded
    & filters.group
    & ~filters.via_bot
    & ~filters.service
)
async def inc_user(_, message: Message):
    if message.text:
        if message.text.strip() in ["/top", "/top@MerissaRobot"]:
            return await show_top_today(_, message)

    try:
        chat = message.chat.id
        user = message.from_user.id
        increase_count(chat, user)  # if async → await increase_count(chat, user)
    except Exception:
        pass


async def show_top_today(_, message: Message):
    chat = chatdb.find_one({"chat": message.chat.id})
    today = str(date.today())

    if not chat or not chat.get(today):
        return await message.reply_text(
            "⚠️ No messages logged for today!",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📊 Overall Ranking", callback_data="overall")]]
            ),
        )

    t = "🔰 **Today's Top Users :**\n\n"
    pos = 1

    for i, k in sorted(chat[today].items(), key=lambda x: x[1], reverse=True)[:10]:
        i = await get_name(app, i)
        t += f"**{pos}.** {i} — `{k}` messages\n"
        pos += 1

    total = sum(chat[today].values())
    t += f"\n✉️ **Total messages today:** `{total}`"

    await message.reply_text(
        t,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📊 Overall Ranking", callback_data="overall")]]
        ),
    )


@app.on_callback_query(filters.regex("^overall"))
async def show_top_overall_callback(_, query: CallbackQuery):
    chat = chatdb.find_one({"chat": query.message.chat.id})

    if not chat:
        return await query.answer("⚠️ No messages logged yet!", show_alert=True)

    await query.answer("Processing... Please wait")

    t = "🔰 **Overall Top Users :**\n\n"
    overall_dict = {}
    total = 0

    for i, k in chat.items():
        if i in ["chat", "_id"]:
            continue
        for j, l in k.items():
            overall_dict[j] = overall_dict.get(j, 0) + l
        total += sum(k.values())

    pos = 1
    for i, k in sorted(overall_dict.items(), key=lambda x: x[1], reverse=True)[:10]:
        i = await get_name(app, i)
        t += f"**{pos}.** {i} — `{k}` messages\n"
        pos += 1

    t += f"\n✉️ **Total messages overall:** `{total}`"

    await query.message.edit_text(
        t,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📅 Today's Ranking", callback_data="today")]]
        ),
    )


@app.on_callback_query(filters.regex("^today"))
async def show_top_today_callback(_, query: CallbackQuery):
    chat = chatdb.find_one({"chat": query.message.chat.id})
    today = str(date.today())

    if not chat or not chat.get(today):
        return await query.answer("⚠️ No messages logged for today!", show_alert=True)

    await query.answer("Processing... Please wait")

    t = "🔰 **Today's Top Users :**\n\n"
    pos = 1

    for i, k in sorted(chat[today].items(), key=lambda x: x[1], reverse=True)[:10]:
        i = await get_name(app, i)
        t += f"**{pos}.** {i} — `{k}` messages\n"
        pos += 1

    total = sum(chat[today].values())
    t += f"\n✉️ **Total messages today:** `{total}`"

    await query.message.edit_text(
        t,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📊 Overall Ranking", callback_data="overall")]]
        ),
    )
