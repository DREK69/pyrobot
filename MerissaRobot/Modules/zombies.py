from asyncio import sleep
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from MerissaRobot import pbot
from MerissaRobot.Handler.pyro.permissions import adminsOnly


@pbot.on_message(filters.command(["zombies", "ghosts"]))
@adminsOnly("can_delete_messages")
async def ban_zombies(_, message: Message):
    args = message.text.split(None, 1)
    mode = args[1].lower() if len(args) > 1 else None

    # Case 1: Just scanning
    if mode != "clean":
        status = await message.reply_text("🔎 **Scanning for deleted accounts...**")
        deleted_count = 0

        async for member in pbot.get_chat_members(message.chat.id):
            if member.user.is_deleted:
                deleted_count += 1

        if deleted_count == 0:
            return await status.edit_text("✅ No deleted accounts found in this chat.")

        return await status.edit_text(
            f"⚠️ Found **{deleted_count}** deleted accounts in this chat.\n\n"
            "Press the button below to remove them.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🧹 Clean Zombies", callback_data=f"zombies_clean_{message.chat.id}")]]
            ),
        )

    # Case 2: /zombies clean (manual text command)
    await start_cleaning(message)


@pbot.on_callback_query(filters.regex(r"^zombies_clean_(\d+)$"))
async def zombies_clean_callback(client, callback_query):
    chat_id = int(callback_query.data.split("_")[2])
    msg = callback_query.message

    # Ensure only admins can press
    member = await client.get_chat_member(chat_id, callback_query.from_user.id)
    if not (member.can_delete_messages or member.status in ("administrator", "creator")):
        return await callback_query.answer("❌ You are not an admin!", show_alert=True)

    await msg.edit_text("🧹 **Cleaning deleted accounts...**")
    fake_message = Message(
        id=msg.id, 
        chat=msg.chat, 
        client=client
    )
    await start_cleaning(fake_message)


async def start_cleaning(message: Message):
    chat = message.chat
    cleaner = await message.reply_text("🧹 **Cleaning deleted accounts...**")

    banned = 0
    failed = 0

    async for member in pbot.get_chat_members(chat.id):
        if member.user.is_deleted:
            try:
                await chat.ban_member(member.user.id)
                banned += 1
                await sleep(0.5)  # prevent FloodWait
            except:
                failed += 1
                continue

    if banned == 0:
        return await cleaner.edit_text("✅ No deleted accounts found.")
    else:
        return await cleaner.edit_text(
            f"✅ Removed **{banned}** deleted accounts.\n"
            f"⚠️ Failed to remove **{failed}** (probably admins)."
        )


__help__ = """
*🧹 Remove Deleted Accounts (Zombies)*

❂ `/zombies` → Scan for deleted accounts.  
❂ `/zombies clean` → Remove all deleted accounts.  
❂ Inline button also available for cleaning.
"""

__mod_name__ = "Zombies ☠️"
