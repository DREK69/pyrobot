import random

import bs4
import requests
from pykeyboard import InlineKeyboard
from pyrogram import *
from pyrogram.errors import *
from pyrogram.types import *
from RandomWordGenerator import RandomWord

from MerissaRobot import pbot as app

# ********************************************************************************

API1 = "https://www.1secmail.com/api/v1/?action=getDomainList"
API2 = "https://www.1secmail.com/api/v1/?action=getMessages&login="
API3 = "https://www.1secmail.com/api/v1/?action=readMessage&login="

# ********************************************************************************


@app.on_message(filters.command("genmail"))
async def fakemailgen(_, message: Message):
    name = message.from_user.id
    rp = RandomWord(max_word_size=8, include_digits=True)
    email = rp.generate()
    xx = requests.get(API1).json()
    domain = random.choice(xx)
    # print(email)
    mes = await app.send_message(
        name,
        text=f"""
**📬 Done,Your Email Address Created!**
📧 **Email** : `{email}@{domain}`
📨 **Mail BOX** : `empty`
♨️ **Powered by** : @MerissaRobot """,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔁 Refresh", callback_data=f"mailbox |{email}|{domain}"
                    ),
                    InlineKeyboardButton("🗑️ Delete", callback_data="cb_close"),
                ]
            ]
        ),
    )
    pi = await mes.pin(disable_notification=True, both_sides=True)
    await pi.delete()


@app.on_message(filters.command("set"))
async def setmailgen(_, message: Message):
    name = message.from_user.id
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some text to make Tempmail\n\nEx. /set Merissarobot"
        )
    email = message.text.split(None, 1)[1]
    xx = requests.get(API1).json()
    domain = random.choice(xx)
    # print(email)
    mes = await app.send_message(
        name,
        text=f"""
**📬 Done,Your Email Address Created!**
📧 **Email** : `{email}@{domain}`
📨 **Mail BOX** : `empty`
♨️ **Powered by** : @MerissaRobot """,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔁 Refresh", callback_data=f"mailbox |{email}|{domain}"
                    ),
                    InlineKeyboardButton("🗑️ Delete", callback_data="cb_close"),
                ]
            ]
        ),
    )
    pi = await mes.pin(disable_notification=True, both_sides=True)
    await pi.delete()


async def gen_keyboard(mails, email, domain):
    num = 0
    i_kbd = InlineKeyboard(row_width=1)
    data = []
    for mail in mails:
        id = mail["id"]
        data.append(
            InlineKeyboardButton(f"{mail['subject']}", f"mail |{email}|{domain}|{id}")
        )
        num += 1
    data.append(InlineKeyboardButton("🔁 Refresh", f"mailbox |{email}|{domain}"))
    i_kbd.add(*data)
    return i_kbd


# ********************************************************************************


@app.on_callback_query(filters.regex("mailbox"))
async def mail_box(_, query: CallbackQuery):
    Data = query.data
    callback_request = Data.split(None, 1)[1]
    m, email, domain = callback_request.split("|")
    mails = requests.get(f"{API2}{email}&domain={domain}").json()
    if mails == []:
        await query.answer("🤷‍♂️ No Mails found!")
    else:
        try:
            smail = f"{email}@{domain}"
            mbutton = await gen_keyboard(mails, email, domain)
            await query.message.edit(
                f""" 
**📬 Done,Your Email Address Created!**
📧 **Email** : `{smail}`
📨 **Mail BOX** : ✅
**♨️ Powered by** : @MerissaRobot""",
                reply_markup=mbutton,
            )
        except bad_request_400.MessageNotModified as e:
            await query.answer("🤷‍♂️ No New Mails found!")


# ********************************************************************************


@app.on_callback_query(filters.regex("mail"))
async def mail_box(_, query: CallbackQuery):
    Data = query.data
    callback_request = Data.split(None, 1)[1]
    m, email, domain, id = callback_request.split("|")
    mail = requests.get(f"{API3}{email}&domain={domain}&id={id}").json()
    froms = mail["from"]
    subject = mail["subject"]
    date = mail["date"]
    if mail["textBody"] == "":
        kk = mail["htmlBody"]
        body = bs4.BeautifulSoup(kk, "lxml")
        txt = body.get_text()
        text = " ".join(txt.split())
        url_part = body.find("a")
        link = url_part["href"]
        mbutton = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔗 Open Link", url=link)],
                [InlineKeyboardButton("🔙 Back", f"mailbox |{email}|{domain}")],
            ]
        )
        await query.message.edit(
            f""" 
**From:** `{froms}`
**Subject:** `{subject}`   
**Date**: `{date}`
{text}
""",
            reply_markup=mbutton,
            disable_web_page_preview=True,
        )
    else:
        body = mail["textBody"]
        mbutton = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", f"mailbox |{email}|{domain}")]]
        )
        await query.message.edit(
            f""" 
**From:** `{froms}`
**Subject:** `{subject}`   
**Date**: `{date}`
{body}
""",
            reply_markup=mbutton,
            disable_web_page_preview=True,
        )


# ********************************************************************************


@app.on_message(filters.command("domains"))
async def fakemailgen(_, message: Message):
    name = message.from_user.id
    x = requests.get(f"https://www.1secmail.com/api/v1/?action=getDomainList").json()
    xx = str(",".join(x))
    email = xx.replace(",", "\n")
    await app.send_message(
        name,
        text=f"""
**{email}**
""",
    )

__help__ = """
You can generate Temp-Mail from MerissaRobot 
 ❍ /genmail : To get Random Temp-Mail.
 ❍ /set <email-name> : To get Tempmail of Your Name
"""

__mod_name__ = "TempMail 📩"
