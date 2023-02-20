from asyncio import sleep

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError
from pyrogram.types import Message

from MerissaRobot import SUPPORT_CHAT, Abishnoi


@Abishnoi.on_message(filters.command("purge"))
async def purge(c: Abishnoi, m: Message):
    if m.chat.type != ChatType.SUPERGROUP:
        await m.reply_text(text="ᴄᴀɴɴᴏᴛ ᴘᴜʀɢᴇ ᴍᴇssᴀɢᴇs ɪɴ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ")
        return

    if m.reply_to_message:
        message_ids = list(range(m.reply_to_message.id, m.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        # Dielete messages in chunks of 100 messages
        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await c.delete_messages(
                    chat_id=m.chat.id,
                    message_ids=plist,
                    revoke=True,
                )
            await m.delete()
        except MessageDeleteForbidden:
            await m.reply_text(
                text="ᴄᴀɴɴᴏᴛ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴍᴇssᴀɢᴇs. ᴛʜᴇ ᴍᴇssᴀɢᴇs ᴍᴀʏ ʙᴇ ᴛᴏᴏ ᴏʟᴅ, I ᴍɪɢʜᴛ ɴᴏᴛ ʜᴀᴠᴇ ᴅᴇʟᴇᴛᴇ ʀɪɢʜᴛs, ᴏʀ ᴛʜɪs ᴍɪɢʜᴛ ɴᴏᴛ ʙᴇ ᴀ sᴜᴘᴇʀɢʀᴏᴜᴘ."
            )
            return
        except RPCError as ef:
            await m.reply_text(
                text=f"""sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ, ʀᴇᴘᴏʀᴛ ᴛᴏ @{SUPPORT_CHAT}

      <b>ᴇʀʀᴏʀ:</b> <code>{ef}</code>"""
            )

        count_del_msg = len(message_ids)

        z = await m.reply_text(text=f"ᴅᴇʟᴇᴛᴇᴅ <i>{count_del_msg}</i> messages")
        await sleep(3)
        await z.delete()
        return
    await m.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴛᴀʀᴛ ᴘᴜʀɢᴇ !")
    return


@Abishnoi.on_message(filters.command("spurge"))
@adminsOnly("can_delete_messages")
async def spurge(c: Abishnoi, m: Message):
    if m.chat.type != ChatType.SUPERGROUP:
        await m.reply_text(text="ᴄᴀɴɴᴏᴛ ᴘᴜʀɢᴇ ᴍᴇssᴀɢᴇs ɪɴ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ")
        return

    if m.reply_to_message:
        message_ids = list(range(m.reply_to_message.id, m.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        # Dielete messages in chunks of 100 messages
        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await c.delete_messages(
                    chat_id=m.chat.id,
                    message_ids=plist,
                    revoke=True,
                )
            await m.delete()
        except MessageDeleteForbidden:
            await m.reply_text(
                text="ᴄᴀɴɴᴏᴛ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴍᴇssᴀɢᴇs. ᴛʜᴇ ᴍᴇssᴀɢᴇs ᴍᴀʏ ʙᴇ ᴛᴏᴏ ᴏʟᴅ, I ᴍɪɢʜᴛ ɴᴏᴛ ʜᴀᴠᴇ ᴅᴇʟᴇᴛᴇ ʀɪɢʜᴛs, ᴏʀ ᴛʜɪs ᴍɪɢʜᴛ ɴᴏᴛ ʙᴇ ᴀ sᴜᴘᴇʀɢʀᴏᴜᴘ."
            )
            return
        except RPCError as ef:
            await m.reply_text(
                text=f"""sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ, ʀᴇᴘᴏʀᴛ ᴛᴏ @{SUPPORT_CHAT}

      <b>ᴇʀʀᴏʀ:</b> <code>{ef}</code>"""
            )
        return
    await m.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴛᴀʀᴛ sᴘᴜʀɢᴇ !")
    return


@Abishnoi.on_message(filters.command("del") & ~filters.private)
async def del_msg(c: Abishnoi, m: Message):
    if m.chat.type != ChatType.SUPERGROUP:
        return

    if m.reply_to_message:
        await m.delete()
        await c.delete_messages(
            chat_id=m.chat.id,
            message_ids=m.reply_to_message.id,
        )
    else:
        await m.reply_text(text="ᴡʜᴀᴛ ᴅᴏ ʏᴏᴜ ᴡᴀɴɴᴀ ᴅᴇʟᴇᴛᴇ?")
    return
