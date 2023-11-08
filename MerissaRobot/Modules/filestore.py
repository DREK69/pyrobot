import asyncio

from pyrogram import filters
from pyrogram.errors import ListenerCanceled
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from youtubesearchpython.__future__ import VideosSearch

from MerissaRobot import BOT_NAME, pbot
from MerissaRobot.helpers import postreq, subscribe

TRACK_CHANNEL = int("-1001900195958")
media_group_id = 0
BATCH = []


@pbot.on_message(filters.command("start") & filters.private)
async def _startfile(bot, update):
    if len(update.command) != 2:
        return
    code = update.command[1]
    if "info" in code:
        m = await update.reply_text("🔎 Fetching Info!")
        videoid = code.split("_")[1]
        query = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(query, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration = result["duration"]
            views = result["viewCount"]["short"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            channellink = result["channel"]["link"]
            channel = result["channel"]["name"]
            link = result["link"]
            published = result["publishedTime"]
        searched_text = f"""
🔍__**Video Track Information**__

❇️**Title:** {title}

⏳**Duration:** {duration} Mins
👀**Views:** `{views}`
⏰**Published Time:** {published}
🎥**Channel Name:** {channel}
📎**Channel Link:** [Visit From Here]({channellink})
🔗**Video Link:** [Link]({link})

⚡️ __Searched Powered By {BOT_NAME}__"""
        key = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="🎥 Watch ", url=f"{link}"),
                    InlineKeyboardButton(text="📥 Download ", url=f"ytdown {videoid}"),
                ],
                [
                    InlineKeyboardButton(text="🔄 Close", callback_data="close"),
                ],
            ]
        )
        await m.delete()
        await update.reply_photo(
            photo=thumbnail,
            caption=searched_text,
            reply_markup=key,
        )
    elif "store" in code:
        ok = await update.reply_text("Uploading Media...")
        cmd, unique_id, msg_id = code.split("_")

        if not msg_id.isdigit():
            return
        try:  # If message not belong to media group raise exception
            check_media_group = await bot.get_media_group(TRACK_CHANNEL, int(msg_id))
            check = check_media_group[0]  # Because func return`s list obj
        except Exception:
            check = await bot.get_messages(TRACK_CHANNEL, int(msg_id))

        if check.empty:
            await update.reply_text(
                "Error: [Message does not exist]\n/help for more details..."
            )
            return
        if check.video:
            unique_idx = check.video.file_unique_id
        elif check.photo:
            unique_idx = check.photo.file_unique_id
        elif check.audio:
            unique_idx = check.audio.file_unique_id
        elif check.document:
            unique_idx = check.document.file_unique_id
        elif check.sticker:
            unique_idx = check.sticker.file_unique_id
        elif check.animation:
            unique_idx = check.animation.file_unique_id
        elif check.voice:
            unique_idx = check.voice.file_unique_id
        elif check.video_note:
            unique_idx = check.video_note.file_unique_id
        if unique_id != unique_idx.lower():
            return
        try:  # If message not belong to media group raise exception
            await bot.copy_media_group(update.from_user.id, TRACK_CHANNEL, int(msg_id))
            await ok.delete()
        except Exception:
            await check.copy(update.from_user.id)
            await ok.delete()

    elif "batch_" in code:
        send_msg = await update.reply_text("Uploading Media...")
        cmd, chat_id, message = code.split("_")
        string = await bot.get_messages(TRACK_CHANNEL, int(message))
        message_ids = string.text.split("-")
        for msg_id in message_ids:
            msg = await bot.get_messages(TRACK_CHANNEL, int(msg_id))
            if msg.empty:
                return await update.reply_text(
                    "Sorry, Your file was deleted by File Owner or Bot Owner\n\nFor more help Contact File Owner/Bot owner"
                )

            await msg.copy(update.from_user.id)
        return await asyncio.sleep(1)

        chat_id, msg_id = code.split("_")
        msg = await bot.get_messages(TRACK_CHANNEL, int(msg_id))

        if msg.empty:
            return await send_msg.edit(
                "Sorry, Your file was deleted by File Owner or Bot Owner\n\nFor more help Contact File Owner/Bot owner."
            )
        caption = f"{msg.caption.markdown}\n\n\n" if msg.caption else ""
        await msg.copy(update.from_user.id, caption=caption)
        await send_msg.delete()

    elif "verify" in code:
        chat_id = code.split("_")[1]
        button = [
            [
                InlineKeyboardButton(text="VERIFY", callback_data=f"verify {chat_id}"),
            ],
        ]
        await update.reply_photo(
            photo="https://te.legra.ph/file/90b1aa10cf8b77d5b781b.jpg",
            caption=f"Hello Dear,\n\nClick 'VERIFY' Button to Verify you're human.",
            reply_markup=InlineKeyboardMarkup(button),
        )

    else:
        return


async def __reply(update, copied):
    ok = await update.reply_text("Downloading Media...")
    msg_id = copied.id
    if copied.video:
        unique_idx = copied.video.file_unique_id
    elif copied.photo:
        unique_idx = copied.photo.file_unique_id
    elif copied.audio:
        unique_idx = copied.audio.file_unique_id
    elif copied.document:
        unique_idx = copied.document.file_unique_id
    elif copied.sticker:
        unique_idx = copied.sticker.file_unique_id
    elif copied.animation:
        unique_idx = copied.animation.file_unique_id
    elif copied.voice:
        unique_idx = copied.voice.file_unique_id
    elif copied.video_note:
        unique_idx = copied.video_note.file_unique_id
    else:
        await copied.delete()
        return

    botlink = f"https://telegram.me/MerissaRobot?start=store_{unique_idx.lower()}_{str(msg_id)}"

    data = {"url": botlink}
    x = await postreq("https://drive.merissabot.me/shorten", data)

    await ok.edit_text(
        "Link Generated Successfully, Link Is Permanent and will not Expired\n\nShare Link with Your Friends:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Bot Url",
                        url=f"https://t.me/share/url?url={botlink}",
                    ),
                    InlineKeyboardButton(
                        "Short Url",
                        url=f"https://t.me/share/url?url=https://drive.merissabot.me/{x['hash']}",
                    ),
                ]
            ]
        ),
    )
    await asyncio.sleep(0.5)  # Wait do to avoid 5 sec flood ban


@pbot.on_message(~filters.media & filters.private & filters.media_group)
async def _main_grop(bot, update):
    global media_group_id

    if int(media_group_id) != int(update.media_group_id):
        media_group_id = update.media_group_id
        copied = (
            await bot.copy_media_group(
                TRACK_CHANNEL, update.from_user.id, update.message_id
            )
        )[0]
        await __reply(update, copied)

    else:
        # This handler catch EVERY message with [update.media_group_id] param
        # So we should ignore next >1_media_group_id messages
        return


@pbot.on_message(filters.command("batch") & filters.private & filters.incoming)
async def batch(c, m):
    BATCH.append(m.from_user.id)
    files = []
    i = 1

    while m.from_user.id in BATCH:
        if i == 1:
            media = await c.ask(
                chat_id=m.from_user.id,
                text="Send me some files or ᴠideo or photo or text or audio. if you want to cancel the process send /cancel",
            )
            if media.text == "/cancel":
                return await m.reply_text("Cᴀɴᴄᴇʟʟᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ ✌")
            files.append(media)
        else:
            try:
                reply_markup = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Done ✅", callback_data="fsdn")]]
                )
                media = await c.ask(
                    chat_id=m.from_user.id,
                    text="Ok. Now send me some more files or press done to get sharable link. If you want to cancel the process send /cancel",
                    reply_markup=reply_markup,
                )
                if media.text == "/cancel":
                    return await m.reply_text("Cancelled Successfully ✌")
                files.append(media)
            except ListenerCanceled:
                pass
            except Exception as e:
                print(e)
                await m.reply_text(
                    text="Something went wrong report here @MerissaxSupport."
                )
        i += 1

    ok = await m.reply_text("Generating Shareable link 🔗")
    string = ""
    for file in files:
        copy_message = await file.copy(TRACK_CHANNEL)
        string += f"{copy_message.id}-"
        await asyncio.sleep(1)

    string_base64 = string[:-1]
    send = await c.send_message(TRACK_CHANNEL, string_base64)
    base64_string = f"batch_{m.chat.id}_{send.id}"
    url = f"https://telegram.me/MerissaRobot?start={base64_string}"
    data = {"url": url}
    x = await postreq("https://drive.merissabot.me/shorten", data)

    await ok.edit_text(
        "Link Generated Successfully, Link Is Permanent and will not Expired\n\nShare Link with Your Friends:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Bot Url",
                        url=f"https://t.me/share/url?url={url}",
                    ),
                    InlineKeyboardButton(
                        "Short Url",
                        url=f"https://t.me/share/url?url=https://drive.merissabot.me/{x['hash']}",
                    ),
                ]
            ]
        ),
    )


@pbot.on_callback_query(filters.regex("^fsdn"))
async def done_cb(c, m):
    BATCH.remove(m.from_user.id)
    c.cancel_listener(m.from_user.id)
    await m.message.delete()


@pbot.on_message(filters.command("store"))
@subscribe
async def _main(bot, update):
    copied = await update.reply_to_message.copy(TRACK_CHANNEL)
    await __reply(update, copied)
