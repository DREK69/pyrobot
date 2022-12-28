import requests
from pyrogram import filters
from pyrogram.enums import ChatAction

from MerissaRobot import pbot


@pbot.on_message(filters.command("write"))
async def handwriting(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Gɪᴠᴇ Sᴏᴍᴇ Tᴇxᴛ Tᴏ Wʀɪᴛᴇ Iᴛ Oɴ Mʏ Cᴏᴩʏ...")
    m = await message.reply_text("Wᴀɪᴛ A Sᴇᴄ, Lᴇᴛ Mᴇ Wʀɪᴛᴇ Tʜᴀᴛ Tᴇxᴛ...")
    name = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    merissa = requests.get(f"https://api.prince-xd.ml/write?text={name}").json()["url"]
    await m.edit("Uᴩʟᴏᴀᴅɪɴɢ...")
    await pbot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
    await message.reply_photo(
        merissa, caption="Wʀɪᴛᴛᴇɴ Wɪᴛʜ 🖊 Bʏ [Merissa](t.me/MerissaRobot)"
    )
