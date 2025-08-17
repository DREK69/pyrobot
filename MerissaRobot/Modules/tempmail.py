import random
import aiohttp
import bs4
from pykeyboard import InlineKeyboard
from pyrogram import filters
from pyrogram.types import *
from RandomWordGenerator import RandomWord

from MerissaRobot import pbot as app
from MerissaRobot.helpers import subscribe

API1 = "https://www.1secmail.com/api/v1/?action=getDomainList"
API2 = "https://www.1secmail.com/api/v1/?action=getMessages&login="
API3 = "https://www.1secmail.com/api/v1/?action=readMessage&login="


async def fetch_json(url, params=None):
    """Helper to fetch JSON asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


@app.on_message(filters.command("genmail"))
@subscribe
async def fakemailgen(client, message: Message):
    user_id = message.from_user.id
    rp = RandomWord(max_word_size=8, include_digits=True)
    email = rp.generate()

    domains = await fetch_json(API1)
    domain = random.choice(domains)

    await app.send_message(
        user_id,
        text=f"""
**📬 Temp-Mail Created!**
📧 **Email** : `{email}@{domain}`
📨 **Mail BOX** : `empty`
♨️ Powered by : @MerissaRobot
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔁 Refresh", callback_data=f"mailbox|{email}|{domain}"),
                    InlineKeyboardButton("🗑️ Delete", callback_data="cb_close"),
                ]
            ]
        ),
    )


@app.on_message(filters.command("set"))
@subscribe
async def setmailgen(client, message: Message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: `/set username`")

    email = message.text.split(None, 1)[1]
    domains = await fetch_json(API1)
    domain = random.choice(domains)

    await app.send_message(
        user_id,
        text=f"""
**📬 Temp-Mail Created!**
📧 **Email** : `{email}@{domain}`
📨 **Mail BOX** : `empty`
♨️ Powered by : @MerissaRobot
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔁 Refresh", callback_data=f"mailbox|{email}|{domain}"),
                    InlineKeyboardButton("🗑️ Delete", callback_data="cb_close"),
                ]
            ]
        ),
    )


async def gen_keyboard(mails, email, domain):
    """Generate inline keyboard for available mails."""
    buttons = [
        [InlineKeyboardButton(f"{mail['subject'] or 'No Subject'}", callback_data=f"mail|{email}|{domain}|{mail['id']}")]
        for mail in mails
    ]
    buttons.append([InlineKeyboardButton("🔁 Refresh", callback_data=f"mailbox|{email}|{domain}")])
    return InlineKeyboardMarkup(buttons)


@app.on_callback_query(filters.regex("^mailbox"))
async def show_mailbox(_, query: CallbackQuery):
    _, email, domain = query.data.split("|")
    mails = await fetch_json(f"{API2}{email}&domain={domain}")

    if not mails:
        return await query.answer("📭 No new mails found!")

    keyboard = await gen_keyboard(mails, email, domain)
    await query.message.edit_text(
        f"""
📧 **Email**: `{email}@{domain}`
📨 **Mail BOX**: {len(mails)} message(s)
♨️ Powered by : @MerissaRobot
""",
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex("^mail"))
async def show_mail(_, query: CallbackQuery):
    _, email, domain, mail_id = query.data.split("|")
    mail = await fetch_json(f"{API3}{email}&domain={domain}&id={mail_id}")

    froms = mail.get("from", "Unknown")
    subject = mail.get("subject", "No Subject")
    date = mail.get("date", "Unknown")
    body = mail.get("textBody", "")

    if not body:
        # Parse HTML body
        html = mail.get("htmlBody", "")
        soup = bs4.BeautifulSoup(html, "lxml")
        text = " ".join(soup.get_text().split())
        links = soup.find_all("a")

        buttons = [[InlineKeyboardButton("🔙 Back", callback_data=f"mailbox|{email}|{domain}")]]
        if links:
            for i, link in enumerate(links[:3], start=1):  # show max 3 links
                buttons.insert(0, [InlineKeyboardButton(f"🔗 Link {i}", url=link.get("href"))])

        reply_markup = InlineKeyboardMarkup(buttons)
        body = text
    else:
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data=f"mailbox|{email}|{domain}")]]
        )

    await query.message.edit_text(
        f"""
**From:** `{froms}`
**Subject:** `{subject}`
**Date:** `{date}`

{body}
""",
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )


@app.on_message(filters.command("domains"))
async def list_domains(_, message: Message):
    domains = await fetch_json(API1)
    await message.reply_text("📋 Available Domains:\n\n" + "\n".join(domains))

__help__ = """
You can generate Temp-Mail from MerissaRobot 
 ❍ /genmail : To get Random Temp-Mail.
 ❍ /set <email-name> : To get Tempmail of Your Name
 ❍ /domains : To check Domains List
"""

__mod_name__ = "TempMail 📩"
