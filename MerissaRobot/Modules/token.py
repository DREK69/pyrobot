from secrets import token_urlsafe
from pyrogram import filters
from MerissaRobot import ERROR_LOG, pbot as app
from MerissaRobot.Database.mongo import leveldb
from MerissaRobot.helpers import subscribe


@app.on_message(filters.command("token", prefixes=["/", ".", "?", "-"]) & filters.private)
@subscribe
async def token(client, message):
    m = await message.reply_text("🔑 Generating your Merissa API Token...")
    toggle = leveldb["myFirstDatabase"]["jsons"]
    user = leveldb["MerissaApi"]["user"]

    # Check if user already has a token
    is_user = user.find_one({"user_id": message.from_user.id})

    if not is_user:
        # Generate a new secure token
        new_token = f"{message.from_user.id}:{token_urlsafe(32)}"

        # Store in both collections
        toggle.insert_one({"ID": new_token, "data": new_token})
        user.insert_one({"user_id": message.from_user.id, "API": new_token})

        await m.edit_text(
            f"✅ Your Merissa Token has been generated!\n\n`{new_token}`\n\n⚠️ Do **not** share this token with anyone!\nKnow More - @MerissaChatbotApi"
        )

        # Log for admins
        await app.send_message(
            ERROR_LOG,
            f"🆕 #NewToken\n\n👤 User: [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n🔑 Token: `{new_token}`",
        )

    else:
        existing_token = is_user["API"]
        await m.edit_text(
            f"🔑 You already have a token:\n\n`{existing_token}`\n\n⚠️ Do **not** share this token with anyone!\nKnow More - @MerissaChatbotApi"
        )


@app.on_message(filters.command("revoke", prefixes=["/", ".", "?", "-"]) & filters.private)
@subscribe
async def revoke(client, message):
    toggle = leveldb["myFirstDatabase"]["jsons"]
    user = leveldb["MerissaApi"]["user"]

    is_user = user.find_one({"user_id": message.from_user.id})

    if not is_user:
        return await message.reply_text("❌ You don’t have any token yet. Use `/token` to generate one.")

    MerissaAPI = is_user["API"]

    # Delete from both collections
    toggle.delete_one({"ID": MerissaAPI, "data": MerissaAPI})
    user.delete_one({"user_id": message.from_user.id})

    await message.reply_text(
        f"✅ Your Merissa Token `{MerissaAPI}` has been **revoked successfully**.\n\nUse `/token` to generate a new one."
    )
