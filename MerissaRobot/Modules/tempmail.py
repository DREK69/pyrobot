import os

import requests as re
from pyrogram import *
import os
import asyncio
import requests
import random
import bs4

from pykeyboard import InlineKeyboard
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid, bad_request_400
from RandomWordGenerator import RandomWord
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MerissaRobot import pbot as app


#********************************************************************************

API1='https://www.1secmail.com/api/v1/?action=getDomainList'
API2='https://www.1secmail.com/api/v1/?action=getMessages&login='
API3='https://www.1secmail.com/api/v1/?action=readMessage&login='

#********************************************************************************

create = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Groupdcbots ⚡", url="https://t.me/NotReallyPrince")]])

#*******************************************************************************

@app.on_message(filters.command("genmail"))
async def fakemailgen(_, message: Message):
    name = message.from_user.id
    m =  await app.send_message(name,text=f"📧 Creating  temp email....",reply_markup = create)
    rp = RandomWord(max_word_size=8, include_digits=True)
    email = rp.generate()
    xx = requests.get(API1).json()
    domain = random.choice(xx)
    #print(email)
    mes = await app.send_message(
    name, 
    text = f"""
**📬 Done,Your Email Address Created!**
📧 **Email** : `{email}@{domain}`
📨 **Mail BOX** : `empty`
♨️ **Powered by** : @groupdcbots """,
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("♻️ Update Mail BOX ♻️", callback_data = f"mailbox |{email}|{domain}")]]))
    pi = await mes.pin(disable_notification=True, both_sides=True)
    await m.delete()
    await pi.delete()

async def gen_keyboard(mails, email, domain):
    num = 0
    i_kbd = InlineKeyboard(row_width=1)
    data = []
    for mail in mails:
        id = mail['id']
        data.append(
            InlineKeyboardButton(f"{mail['subject']}", f"mail |{email}|{domain}|{id}")
        )
        num += 1
    data.append(
        InlineKeyboardButton(f"Update Mail BOX ♻️", f"mailbox |{email}|{domain}")
    )
    i_kbd.add(*data)
    return i_kbd
 
#********************************************************************************

@app.on_callback_query(filters.regex("mailbox"))
async def mail_box(_, query : CallbackQuery):
    Data = query.data
    callback_request = Data.split(None, 1)[1]
    m, email , domain = callback_request.split("|")
    mails = requests.get(f'{API2}{email}&domain={domain}').json()
    if mails == []:
            await query.answer("🤷‍♂️ No Mails found! 🤷‍♂️")
    else:
        try:
            smail = f"{email}@{domain}"
            mbutton = await gen_keyboard(mails,email, domain)
            await query.message.edit(f""" 
**📬 Done,Your Email Address Created!**
📧 **Email** : `{smail}`
📨 **Mail BOX** : ✅
**♨️ Powered by** : @Groupdcbots""",
reply_markup = mbutton
)   
        except bad_request_400.MessageNotModified as e:
            await query.answer("🤷‍♂️ No New Mails found! 🤷‍♂️")

#********************************************************************************

@app.on_callback_query(filters.regex("mail"))
async def mail_box(_, query : CallbackQuery):
    Data = query.data
    callback_request = Data.split(None, 1)[1]
    m, email , domain, id = callback_request.split("|")
    mail = requests.get(f'{API3}{email}&domain={domain}&id={id}').json()
    froms = mail['from']
    subject = mail['subject']
    date = mail['date']
    if mail['textBody'] == "":
        kk = mail['htmlBody']
        body = bs4.BeautifulSoup(kk, 'lxml')
        txt = body.get_text()
        text = " ".join(txt.split())
        url_part = body.find('a')
        link = url_part['href']
        mbutton = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔗 Open Link", url=link)
                ],
                [
                    InlineKeyboardButton("Back", f"mailbox |{email}|{domain}")
                ]
            ]
        )
        await query.message.edit(f""" 
**From:** `{froms}`
**Subject:** `{subject}`   
**Date**: `{date}`
{text}
""",
reply_markup = mbutton
)
    else:
        body = mail['textBody']
        mbutton = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Back", f"mailbox |{email}|{domain}")
                ]
            ]
        )
        await query.message.edit(f""" 
**From:** `{froms}`
**Subject:** `{subject}`   
**Date**: `{date}`
{body}
""",
reply_markup = mbutton
)
#********************************************************************************

@app.on_message(filters.command("domains"))
async def fakemailgen(_, message: Message):
    name = message.from_user.id
    x = requests.get(f'https://www.1secmail.com/api/v1/?action=getDomainList').json()
    xx = str(",".join(x))
    email = xx.replace(",", "\n")
    await app.send_message(
    name, 
    text = f"""
**{email}**
""",
    reply_markup = create)
