import random

from pyrogram import filters

from MerissaRobot import pbot as app
from MerissaRobot.Database.mongo import leveldb


@app.on_message(
    filters.command("token", prefixes=["/", ".", "?", "-"]) & filters.private
)
async def token(client, message):
    toggle = leveldb["myFirstDatabase"]["jsons"]
    user = leveldb["MerissaApi"]["user"]
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars1 = "1234564890"
    gen1 = random.choice(chars)
    gen2 = random.choice(chars)
    gen3 = random.choice(chars1)
    gen4 = random.choice(chars)
    gen5 = random.choice(chars)
    gen6 = random.choice(chars)
    gen7 = random.choice(chars1)
    gen8 = random.choice(chars)
    gen9 = random.choice(chars)
    gen10 = random.choice(chars1)
    word = f"{message.from_user.id}-MERISSA{gen1}{gen2}{gen3}{gen4}{gen5}{gen6}{gen7}{gen8}{gen9}{gen10}"
    is_user = user.find_one({"user_id": message.from_user.id})
    if not is_user:
        toggle.insert_one({"ID": word, "data": word})
        user.insert_one({"user_id": message.from_user.id, "API": word})
        await message.reply_text(
            f"Your Merissa Token: `{word}` Do not give this token to anyone else!\n Join @MerissaxSupport"
        )
    else:
        MerissaAPI = is_user["API"]
        await message.reply_text(
            f"Your Merissa Token: `{MerissaAPI}` Do not give this token to anyone else!\n Join @MerissaxSupport"
        )


@app.on_message(
    filters.command("revoke", prefixes=["/", ".", "?", "-"]) & filters.private
)
async def revoke(client, message):
    toggle = leveldb["myFirstDatabase"]["jsons"]
    user = leveldb["MerissaApi"]["user"]
    is_user = user.find_one({"user_id": message.from_user.id})
    MerissaAPI = is_user["API"]
    if is_user:
        toggle.delete_one({"ID": MerissaAPI, "data": MerissaAPI})
        user.delete_one({"user_id": message.from_user.id, "API": MerissaAPI})
        await message.reply_text(
            f"Your Merissa Token: `{MerissaAPI}` Your Merissa Api Token Revoked Successfully. You can Generate using /token."
        )
    else:
        await message.reply_text("Please First Press /token")
