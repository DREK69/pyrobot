import os

import requests as re
import wget
from pyrogram import *
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MerissaRobot import pbot as app

buttons = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("📧 Generate Email", callback_data="generate")],
        [
            InlineKeyboardButton("🔁 Refresh", callback_data="refresh"),
            InlineKeyboardButton("🗑️ Close", callback_data="cb_close"),
        ],
    ]
)

msg_buttons = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("📫 View message", callback_data="view_msg")],
        [InlineKeyboardButton("🗑️ Close", callback_data="cb_close")],
    ]
)

email = ""


@app.on_message(filters.command("genmail"))
async def start_msg(client, message):
    await message.reply(
        "Hello Welcome to Merissa Temp Mail Generator", reply_markup=buttons
    )


@app.on_callback_query()
async def mailbox(client, message):
    response = message.data
    if response == "generate":
        global email
        email = re.get(
            "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1"
        ).json()[0]
        await message.edit_message_text(
            "__**Your Temporary E-mail: **__`" + str(email) + "`", reply_markup=buttons
        )
        print(email)
    elif response == "refresh":
        print(email)
        try:
            if email == "":
                await message.edit_message_text(
                    "Genaerate a email", reply_markup=buttons
                )
            else:
                getmsg_endp = (
                    "https://www.1secmail.com/api/v1/?action=getMessages&login="
                    + email[: email.find("@")]
                    + "&domain="
                    + email[email.find("@") + 1 :]
                )
                print(getmsg_endp)
                ref_response = re.get(getmsg_endp).json()
                global idnum
                idnum = str(ref_response[0]["id"])
                from_msg = ref_response[0]["from"]
                subject = ref_response[0]["subject"]
                refreshrply = (
                    "You a message from " + from_msg + "\n\nSubject : " + subject
                )
                await message.edit_message_text(refreshrply, reply_markup=msg_buttons)
        except:
            await message.answer(
                "No messages were received..\nin your Mailbox " + email
            )
    elif response == "view_msg":
        msg = re.get(
            "https://www.1secmail.com/api/v1/?action=readMessage&login="
            + email[: email.find("@")]
            + "&domain="
            + email[email.find("@") + 1 :]
            + "&id="
            + idnum
        ).json()
        print(msg)
        from_mail = msg["from"]
        date = msg["date"]
        subjectt = msg["subject"]
        attachments = msg["attachments"][0]
        body = msg["body"]
        mailbox_view = (
            "ID No : "
            + idnum
            + "\nFrom : "
            + from_mail
            + "\nDate : "
            + date
            + "\nSubject : "
            + subjectt
            + "\n\n"
            + body
        )
        await message.edit_message_text(mailbox_view, reply_markup=buttons)
        print(attachments)
        mailbox_view = (
            "ID No : "
            + idnum
            + "\nFrom : "
            + from_mail
            + "\nDate : "
            + date
            + "\nSubject : "
            + subjectt
            + "\n\n"
            + body
        )
        if attachments == "[]":
            await message.edit_message_text(mailbox_view, reply_markup=buttons)
            await message.answer("No Messages Were Recieved..", show_alert=True)
        else:
            dlattach = attachments["filename"]
            attc = (
                "https://www.1secmail.com/api/v1/?action=download&login="
                + email[: email.find("@")]
                + "&domain="
                + email[email.find("@") + 1 :]
                + "&id="
                + idnum
                + "&file="
                + dlattach
            )
            print(attc)
            mailbox_vieww = (
                "ID No : "
                + idnum
                + "\nFrom : "
                + from_mail
                + "\nDate : "
                + date
                + "\nSubject : "
                + subjectt
                + "\n\n"
                + body
                + "\n\n"
                + "[Download]("
                + attc
                + ") Attachments"
            )
            wget.download(attc)
            await message.edit_message_text(mailbox_vieww, reply_markup=buttons)
            os.remove(dlattach)
