import asyncio

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MerissaRobot import BOT_USERNAME as botun
from MerissaRobot import pbot
from MerissaRobot.helpers import postreq, subscribe

TRACK_CHANNEL = int("-1001900195958")
media_group_id = 0


@pbot.on_message(filters.command("start") & filters.private)
async def _startfile(bot, update):
    if len(update.command) != 2:
        return
    code = update.command[1]
    if "-" in code:
        ok = await update.reply_text("Uploading Media...")
        msg_id = code.split("-")[-1]
        # due to new type of file_unique_id, it can contain "-" sign like "agadyruaas-puuo"
        unique_id = "-".join(code.split("-")[0:-1])

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

    botlink = f"https://telegram.me/{botun}?start={unique_idx.lower()}-{str(msg_id)}"

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


@pbot.on_message(filters.command("batch"))
async def _main_grop(bot, update):
    global media_group_id

    if int(media_group_id) != int(update.reply_to_message.media_group_id):
        media_group_id = update.reply_to_message.media_group_id
        copied = await update.reply_to_message.copy(TRACK_CHANNEL)
        await __reply(update, copied)

    else:
        # This handler catch EVERY message with [update.media_group_id] param
        # So we should ignore next >1_media_group_id messages
        return


@pbot.on_message(filters.command("save"))
async def _main(bot, update):
    userid = update.from_user.id
    sub = await subscribe(bot, userid)
    if sub == False:
        return await update.reply_text("Please Join @MerissaxUpdates to Use Premium Features")
    copied = await update.reply_to_message.copy(TRACK_CHANNEL)
    await __reply(update, copied)
