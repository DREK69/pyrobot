import json
import os
import time
from io import BytesIO

from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes
from telegram.constants import ParseMode, ChatAction
from telegram import Update

import MerissaRobot.Database.sql.blacklist_sql as blacklistsql
import MerissaRobot.Database.sql.locks_sql as locksql
import MerissaRobot.Database.sql.notes_sql as sql
import MerissaRobot.Database.sql.rules_sql as rulessql
from MerissaRobot import JOIN_LOGGER, LOGGER, OWNER_ID, SUPPORT_CHAT, application
from MerissaRobot.__main__ import DATA_IMPORT
from MerissaRobot.Database.sql import disable_sql as disabledsql
from MerissaRobot.Handler.ptb.alternate import typing_action
from MerissaRobot.Handler.ptb.chat_status import user_admin
from MerissaRobot.Modules.connection import connected


@user_admin
@typing_action
async def import_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    
    conn = await connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat_obj = await context.bot.get_chat(conn)
        chat = chat_obj
        chat_name = chat_obj.title
    else:
        if update.effective_message.chat.type == "private":
            await update.effective_message.reply_text("This is a group only command!")
            return ""

        chat = update.effective_chat
        chat_name = update.effective_message.chat.title

    if msg.reply_to_message and msg.reply_to_message.document:
        try:
            file_info = await context.bot.get_file(msg.reply_to_message.document.file_id)
        except BadRequest:
            await msg.reply_text(
                "Try downloading and uploading the file yourself again, This one seem broken to me!",
            )
            return

        with BytesIO() as file:
            await file_info.download_to_memory(file)
            file.seek(0)
            data = json.load(file)

        # only import one group
        if len(data) > 1 and str(chat.id) not in data:
            await msg.reply_text(
                "There are more than one group in this file and the chat.id is not same! How am i supposed to import it?",
            )
            return

        # Check if backup is this chat
        try:
            if data.get(str(chat.id)) is None:
                if conn:
                    text = f"Backup comes from another chat, I can't return another chat to chat *{chat_name}*"
                else:
                    text = "Backup comes from another chat, I can't return another chat to this chat"
                return await msg.reply_text(text, parse_mode="markdown")
        except Exception:
            return await msg.reply_text("There was a problem while importing the data!")
            
        # Check if backup is from self
        try:
            if str(context.bot.id) != str(data[str(chat.id)]["bot"]):
                return await msg.reply_text(
                    "Backup from another bot that is not suggested might cause the problem, documents, photos, videos, audios, records might not work as it should be.",
                )
        except Exception:
            pass
            
        # Select data source
        if str(chat.id) in data:
            data = data[str(chat.id)]["hashes"]
        else:
            data = data[list(data.keys())[0]]["hashes"]

        try:
            for mod in DATA_IMPORT:
                mod.__import_data__(str(chat.id), data)
        except Exception:
            await msg.reply_text(
                f"An error occurred while recovering your data. The process failed. If you experience a problem with this, please take it to @{SUPPORT_CHAT}",
            )

            LOGGER.exception(
                "Import for the chat %s with the name %s failed.",
                str(chat.id),
                str(chat.title),
            )
            return

        if conn:
            text = f"Backup fully restored on *{chat_name}*."
        else:
            text = "Backup fully restored"
        await msg.reply_text(text, parse_mode="markdown")


@user_admin
async def export_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    msg = update.effective_message
    user = update.effective_user
    chat_id = update.effective_chat.id
    chat = update.effective_chat
    current_chat_id = update.effective_chat.id
    
    conn = await connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat_obj = await context.bot.get_chat(conn)
        chat = chat_obj
        chat_id = conn
    else:
        if update.effective_message.chat.type == "private":
            await update.effective_message.reply_text("This is a group only command!")
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id

    jam = time.time()
    new_jam = jam + 10800
    checkchat = get_chat(chat_id, chat_data)
    
    if checkchat.get("status"):
        if jam <= int(checkchat.get("value")):
            timeformatt = time.strftime(
                "%H:%M:%S %d/%m/%Y",
                time.localtime(checkchat.get("value")),
            )
            await update.effective_message.reply_text(
                f"You can only backup once a day!\nYou can backup again in about `{timeformatt}`",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        if user.id != OWNER_ID:
            put_chat(chat_id, new_jam, chat_data)
    else:
        if user.id != OWNER_ID:
            put_chat(chat_id, new_jam, chat_data)

    note_list = sql.get_all_chat_notes(chat_id)
    backup = {}
    buttonlist = []
    namacat = ""
    isicat = ""
    rules = ""
    count = 0
    countbtn = 0
    
    # Notes
    for note in note_list:
        count += 1
        namacat += f"{note.name}<###splitter###>"
        if note.msgtype == 1:
            tombol = sql.get_buttons(chat_id, note.name)
            for btn in tombol:
                countbtn += 1
                if btn.same_line:
                    buttonlist.append(
                        (f"{btn.name}", f"{btn.url}", True),
                    )
                else:
                    buttonlist.append(
                        (f"{btn.name}", f"{btn.url}", False),
                    )
            isicat += f"###button###: {note.value}<###button###>{str(buttonlist)}<###splitter###>"
            buttonlist.clear()
        elif note.msgtype == 2:
            isicat += f"###sticker###:{note.file}<###splitter###>"
        elif note.msgtype == 3:
            isicat += f"###file###:{note.file}<###TYPESPLIT###>{note.value}<###splitter###>"
        elif note.msgtype == 4:
            isicat += f"###photo###:{note.file}<###TYPESPLIT###>{note.value}<###splitter###>"
        elif note.msgtype == 5:
            isicat += f"###audio###:{note.file}<###TYPESPLIT###>{note.value}<###splitter###>"
        elif note.msgtype == 6:
            isicat += f"###voice###:{note.file}<###TYPESPLIT###>{note.value}<###splitter###>"
        elif note.msgtype == 7:
            isicat += f"###video###:{note.file}<###TYPESPLIT###>{note.value}<###splitter###>"
        elif note.msgtype == 8:
            isicat += f"###video_note###:{note.file}<###TYPESPLIT###>{note.value}<###splitter###>"
        else:
            isicat += f"{note.value}<###splitter###>"
            
    notes = {
        f"#{namacat.split('<###splitter###>')[x]}": f"{isicat.split('<###splitter###>')[x]}"
        for x in range(count)
    }
    
    # Rules
    rules = rulessql.get_rules(chat_id)
    
    # Blacklist
    bl = list(blacklistsql.get_chat_blacklist(chat_id))
    
    # Disabled command
    disabledcmd = list(disabledsql.get_all_disabled(chat_id))
    
    # Locked
    curr_locks = locksql.get_locks(chat_id)
    curr_restr = locksql.get_restr(chat_id)

    if curr_locks:
        locked_lock = {
            "sticker": curr_locks.sticker,
            "audio": curr_locks.audio,
            "voice": curr_locks.voice,
            "document": curr_locks.document,
            "video": curr_locks.video,
            "contact": curr_locks.contact,
            "photo": curr_locks.photo,
            "gif": curr_locks.gif,
            "url": curr_locks.url,
            "bots": curr_locks.bots,
            "forward": curr_locks.forward,
            "game": curr_locks.game,
            "location": curr_locks.location,
            "rtl": curr_locks.rtl,
        }
    else:
        locked_lock = {}

    if curr_restr:
        locked_restr = {
            "messages": curr_restr.messages,
            "media": curr_restr.media,
            "other": curr_restr.other,
            "previews": curr_restr.preview,
            "all": all(
                [
                    curr_restr.messages,
                    curr_restr.media,
                    curr_restr.other,
                    curr_restr.preview,
                ],
            ),
        }
    else:
        locked_restr = {}

    locks = {"locks": locked_lock, "restrict": locked_restr}
    
    # Backing up
    backup[chat_id] = {
        "bot": context.bot.id,
        "hashes": {
            "info": {"rules": rules},
            "extra": notes,
            "blacklist": bl,
            "disabled": disabledcmd,
            "locks": locks,
        },
    }
    
    baccinfo = json.dumps(backup, indent=4)
    with open(f"MerissaRobot{chat_id}.txt", "w") as f:
        f.write(str(baccinfo))
        
    await context.bot.send_chat_action(current_chat_id, ChatAction.UPLOAD_DOCUMENT)
    tgl = time.strftime("%H:%M:%S - %d/%m/%Y", time.localtime(time.time()))
    
    try:
        await context.bot.send_message(
            JOIN_LOGGER,
            f"*Successfully exported backup:*\nChat: `{chat.title}`\nChat ID: `{chat_id}`\nOn: `{tgl}`",
            parse_mode=ParseMode.MARKDOWN,
        )
    except BadRequest:
        pass
        
    with open(f"MerissaRobot{chat_id}.txt", "rb") as doc:
        await context.bot.send_document(
            current_chat_id,
            document=doc,
            caption=f"*Successfully Exported backup:*\nChat: `{chat.title}`\nChat ID: `{chat_id}`\nOn: `{tgl}`\n\nNote: This `MerissaRobot-Backup` was specially made for notes.",
            reply_to_message_id=msg.message_id,
            parse_mode=ParseMode.MARKDOWN,
        )
    os.remove(f"MerissaRobot{chat_id}.txt")  # Cleaning file


# Temporary data
def put_chat(chat_id, value, chat_data):
    status = value is not False
    chat_data[chat_id] = {"backups": {"status": status, "value": value}}


def get_chat(chat_id, chat_data):
    try:
        return chat_data[chat_id]["backups"]
    except KeyError:
        return {"status": False, "value": False}


__mod_name__ = "Backups"

IMPORT_HANDLER = CommandHandler("import", import_data)
EXPORT_HANDLER = CommandHandler("export", export_data)

application.add_handler(IMPORT_HANDLER)
application.add_handler(EXPORT_HANDLER)

__command_list__ = ["import", "export"]
__handlers__ = [IMPORT_HANDLER, EXPORT_HANDLER]
