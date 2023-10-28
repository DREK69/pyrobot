from pyrogram import *
from pyrogram.types import *

from MerissaRobot import pbot
from MerissaRobot.helpers import subscribe


@pbot.on_message(filters.private & filters.reply & filters.command("post"))
@subscribe
async def post(bot, update):
    update.from_user.id
    if (update.text == "post") or (" " not in update.text):
        return

    if " " in update.text:
        chat_id = int(update.text.split()[1])

    try:
        user = await bot.get_chat_member(chat_id=chat_id, user_id=update.from_user.id)
        if user.can_post_messages != True:
            await update.reply_text(text="You can't do that")
            return
    except Exception:
        return

    try:
        post = await bot.copy_message(
            chat_id=chat_id,
            from_chat_id=update.reply_to_message.chat.id,
            message_id=update.reply_to_message.message_id,
            reply_markup=update.reply_to_message.reply_markup,
        )
        post_link = f"https://telegram.me/c/{post.chat.id}/{post.message_id}"
        await update.reply_text(
            text="Posted Successfully",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Post", url=post_link)]]
            ),
        )
    except Exception as error:
        print(error)
        await update.reply_text(error)


@pbot.on_message(filters.private & filters.reply & filters.command(["edit"]), group=2)
@subscribe
async def edit(bot, update):
    if update.text == "/edit":
        return

    if " " in update.text:
        command, link = update.text.split(" ", 1)
    else:
        return

    if "/" in link:
        ids = link.split("/")
        chat_id = -100 + int(ids[-2])
        message_id = int(ids[-1])
    else:
        return

    try:
        user = await bot.get_chat_member(chat_id=chat_id, user_id=update.from_user.id)
        if user.can_be_edited != True:
            await update.reply_text(
                text="You can't do that, User needed can_be_edited permission."
            )
            return
    except Exception as error:
        print(error)
        await update.reply_text(error)
        return

    if update.reply_to_message.text:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=update.reply_to_message.text,
                reply_markup=update.reply_to_message.reply_markup,
                disable_web_page_preview=True,
            )
        except Exception as error:
            await update.reply_text(error)
    else:
        await update.reply_text("I can edit text only")
