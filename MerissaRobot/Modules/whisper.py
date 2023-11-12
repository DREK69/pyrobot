import ast
import json
from pyrogram import Client
from pyrogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChosenInlineResult
)

from pyrogram.errors import UsernameInvalid, UsernameNotOccupied, PeerIdInvalid
from MerissaRobot import pbot as Client 
from MerissaRobot.Database.sql.whisper_sql import Whispers, Users
from MerissaRobot.Database.sql import SESSION

async def check_for_users(user_ids):
    if isinstance(user_ids, int):
        user_ids = [user_ids]
    elif isinstance(user_ids, list):
        pass
    for user_id in user_ids:
        q = SESSION.query(Users).get(user_id)
        if not q:
            SESSION.add(Users(user_id))
            SESSION.commit()
        else:
            SESSION.close()

@Client.on_callback_query(filters.regex("^wspr"))
async def _callbacks(bot, callback_query: CallbackQuery):
    cb_data = callback_query.data.strip()
    cbdata = cb_data.split("_")[1]
    data_list = ast.literal_eval(str(cbdata))
    if callback_query.from_user.id in data_list:
        specific = callback_query.inline_message_id
        q = SESSION.query(Whispers).get(specific)
        if q:
	          await callback_query.answer(q.message, show_alert=True)
	      else:
	          await callback_query.answer("Message Not Found", show_alert=True)
	          SESSION.commit()
    else:
	      await callback_query.answer("Sorry, you cannot see this whisper as it is not meant for you!", show_alert=True)
        await check_for_users(data_list)


async def previous_target(sender):
    q = SESSION.query(Users).get(sender)
    if q and q.target_user is not None:
        target_user = q.target_user
        target_user = json.loads(target_user)
        receiver = target_user["id"]
        data_list = [sender, receiver]
        first_name = target_user["first_name"]
        try:
            last_name = target_user["last_name"]
            name = first_name + last_name
        except KeyError:
            name = first_name
        text1 = f"A whisper message to {name}"
        text2 = "Only he/she can open it."
        mention = f"[{name}](tg://user?id={receiver})"
        results = [
              InlineQueryResultArticle(
                  title=text1,
                  input_message_content=InputTextMessageContent(
                      f"A whisper message to {mention}" + " " + text2),
                  url="https://t.me/StarkBots",
                  description=text2,
                  thumb_url="https://telegra.ph/file/33af12f457b16532e1383.jpg",
                  reply_markup=InlineKeyboardMarkup(
                      [
                          [
                              InlineKeyboardButton(
                                  "🔐 Show Message 🔐",
                                  callback_data=f"wspr_{str(data_list)}",
                              )
                          ]
                      ]
                  ),
              ),
              main[0]
        ]
    else:
        results = main
    return results
