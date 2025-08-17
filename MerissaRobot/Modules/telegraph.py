import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

try:
    from telegraph import Telegraph, exceptions, upload_file
    TELEGRAPH_ENABLED = True
except ImportError:
    TELEGRAPH_ENABLED = False

from MerissaRobot import pbot

if TELEGRAPH_ENABLED:
    telegraph = Telegraph()
    r = telegraph.create_account(short_name="MerissaBot")
    auth_url = r["auth_url"]


@pbot.on_message(filters.command(["telegraph", "tgt", "tgm"]))
async def telegrapher(c, m):
    if not TELEGRAPH_ENABLED:
        return await m.reply_text("❌ Telegraph module not installed on this server.")

    tg = await m.reply_text("`Please wait...`")
    if not m.reply_to_message:
        await tg.edit("`This command needs a reply to work..`")
        return

    # Media Upload
    if m.reply_to_message.media:
        m_d = await m.reply_to_message.download()
        try:
            media_url = upload_file(m_d)
        except exceptions.TelegraphException as exc:
            await tg.edit(f"⚠️ Telegraph failed:\n`{exc}`")
            os.remove(m_d)
            return
        url = "https://graph.org" + media_url[0]
        button = InlineKeyboardButton(text="📎 Open Telegraph", url=url)
        await m.reply_text("✅ Uploaded to Telegraph", reply_markup=InlineKeyboardMarkup([[button]]))
        os.remove(m_d)
        await tg.delete()

    # Text Upload
    elif m.reply_to_message.text:
        try:
            page_title = m.text.split(None, 1)[1]
        except IndexError:
            page_title = m.from_user.first_name
        page_text = m.reply_to_message.text.replace("\n", "</br>")
        try:
            response = telegraph.create_page(page_title, html_content=page_text)
            button = InlineKeyboardButton(text="📎 Open Telegraph", url=response["url"])
            await m.reply_text("✅ Uploaded to Telegraph", reply_markup=InlineKeyboardMarkup([[button]]))
            await tg.delete()
        except exceptions.TelegraphException as exc:
            await tg.edit(f"⚠️ Telegraph failed:\n`{exc}`")
