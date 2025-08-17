import os
from pyrogram import filters
from pyrogram.types import Message

from MerissaRobot import OWNER_ID, pbot


@pbot.on_message(filters.command("module"))
async def sendmodule(client, message: Message):
    # Only OWNER can use
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ You are not authorized to use this command.")

    # Check if module name is given
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: `/module <modulename>`", quote=True)

    module_name = message.command[1]  # the input after /module
    the_plugin_file = os.path.join("MerissaRobot", "Modules", f"{module_name}.py")

    # Check if file exists
    if os.path.exists(the_plugin_file):
        await message.reply_document(
            document=the_plugin_file,
            caption=f"📂 Module: `{module_name}.py`",
        )
    else:
        await message.reply_text("❌ No such module found.", quote=True)
