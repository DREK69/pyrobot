from secrets import token_urlsafe as uls

from pyrogram import filters

from MerissaRobot import ERROR_LOG
from MerissaRobot import pbot as app
from MerissaRobot.Database.mongo import leveldb
from MerissaRobot.helpers import subscribe


@app.on_message(
    filters.command("token", prefixes=["/", ".", "?", "-"]) & filters.private
)
@subscribe
async def token(client, message):
    m = await message.reply_text("Processing")
    toggle = leveldb["myFirstDatabase"]["jsons"]
    user = leveldb["MerissaApi"]["user"]
    word = f"{message.from_user.id}:{uls(round(2030709195/69696969))}"
    is_user = user.find_one({"user_id": message.from_user.id})
    if not is_user:
        toggle.insert_one({"ID": word, "data": word})
        user.insert_one({"user_id": message.from_user.id, "API": word})
        await m.edit_text(
            f"Your Merissa Token: `{word}`.\n\nDo not give this token to anyone else!\nKnow More - @MerissaChatbotApi"
        )
        await app.send_message(
            ERROR_LOG,
            f"#New Merissa Token Generated\n\nUser- [{message.from_user.first_name}](tg://user?id={message.from_user.id})\nToken- `{word}`\n\n©️ MerissaRobot",
        )
    else:
        MerissaAPI = is_user["API"]
        await m.edit_text(
            f"Your Merissa Token: `{MerissaAPI}` Do not give this token to anyone else!\n Join @MerissaxSupport"
        )


@app.on_message(
    filters.command("revoke", prefixes=["/", ".", "?", "-"]) & filters.private
)
@subscribe
async def revoke(client, message):
    toggle = leveldb["myFirstDatabase"]["jsons"]
    user = leveldb["MerissaApi"]["user"]
    is_user = user.find_one({"user_id": message.from_user.id})
    MerissaAPI = is_user["API"]
    if is_user:
        toggle.delete_one({"ID": MerissaAPI, "data": MerissaAPI})
        user.delete_one({"user_id": message.from_user.id, "API": MerissaAPI})
        await message.reply_text(
            f"Your Merissa Token: `{MerissaAPI}` Your Merissa Api Token Revoked Successfully.\n\nYou can Generate again using /token."
        )
    else:
        await message.reply_text("You don't have any token. Type /token to generate")
