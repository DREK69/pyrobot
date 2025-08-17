from asyncio import sleep
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError
from pyrogram.types import Message

from MerissaRobot import SUPPORT_CHAT, pbot
from MerissaRobot.Handler.pyro.permissions import adminsOnly


async def _purge(c: pbot, m: Message, secure: bool = False):
    if m.chat.type != ChatType.SUPERGROUP:
        return await m.reply_text("❌ Purge only works in supergroups.")

    if not m.reply_to_message:
        return await m.reply_text("⚡ Reply to a message to start purging!")

    # Collect all messages from replied msg to command msg
    message_ids = list(range(m.reply_to_message.id, m.id + 1))

    # Split into chunks of 100 (API limit)
    def chunks(seq, size=100):
        for i in range(0, len(seq), size):
            yield seq[i : i + size]

    try:
        for part in chunks(message_ids):
            await c.delete_messages(m.chat.id, part, revoke=True)

        if not secure:  # /purge sends a confirmation
            z = await m.reply_text(f"✅ Deleted <i>{len(message_ids)}</i> messages")
            await sleep(5)
            await z.delete()

    except MessageDeleteForbidden:
        return await m.reply_text(
            "⚠️ Cannot delete all messages. They might be too old, "
            "I might not have delete rights, or this chat is not a supergroup."
        )
    except RPCError as e:
        return await m.reply_text(
            f"⚠️ Error occurred, please report to @{SUPPORT_CHAT}\n\n"
            f"<b>Error:</b> <code>{e}</code>"
        )


@pbot.on_message(filters.command("purge"))
async def purge(c: pbot, m: Message):
    await _purge(c, m, secure=False)


@pbot.on_message(filters.command("spurge"))
@adminsOnly("can_delete_messages")
async def spurge(c: pbot, m: Message):
    await _purge(c, m, secure=True)


@pbot.on_message(filters.command("del") & ~filters.private)
async def del_msg(c: pbot, m: Message):
    if m.chat.type != ChatType.SUPERGROUP:
        return

    if not m.reply_to_message:
        return await m.reply_text("❓ What do you want me to delete?")

    try:
        await m.delete()
        await c.delete_messages(m.chat.id, m.reply_to_message.id)
    except MessageDeleteForbidden:
        await m.reply_text("⚠️ Cannot delete that message (maybe too old or no rights).")
