import asyncio
from datetime import datetime

from telethon.errors.rpcerrorlist import YouBlockedUserError

from MerissaRobot import telethn as tbot
from MerissaRobot import ubot
from MerissaRobot.events import register


@register(pattern="^/insta ?(.*)")
async def insta(event):
    chat = "@instaDlerBot"
    link = event.pattern_match.group(1)
    xx = await event.reply("`Finding Video...`")
    if event.fwd_from:
        return
    if "instagram.com" not in link:
        await xx.edit("` I need a Instagram link to download it's Video...`(*_*)")
    else:
        start = datetime.now()
        catevent = await xx.edit("```Downloading Video...```")
    async with ubot.conversation(chat) as conv:
        try:
            msg_start = await conv.send_message("/start")
            r_start = await conv.get_response()
            msg = await conv.send_message(link)
            response = await conv.get_response()
            video = await conv.get_response()
            pantek = await ubot.download_media(video)
            await ubot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await catevent.edit(
                "**Error:** Contact @MerissaxSupport For InstaGram Download Video.`"
            )
            return
        await catevent.delete()
        cat = await tbot.send_file(
            event.chat.id, caption="Powered By @MerissaRobot", file=pantek
        )
        end = datetime.now()
        ms = (end - start).seconds
        await cat.edit(
            f"<b>📤 Uploaded in {ms} seconds from Instagram.</b>\n\n<b>© Powered by @MerissaRobot</b>",
            parse_mode="html",
        )
    await ubot.delete_messages(
        conv.chat_id,
        [msg_start.id, r_start.id, msg.id, response.id, video.id],
    )


@register(pattern="^/tiktok ?(.*)")
async def insta(event):
    chat = "@TIKTOKDOWNLOADROBOT"
    link = event.pattern_match.group(1)
    xx = await event.reply("`Finding Video...`")
    if event.fwd_from:
        return
    if "tiktok.com" not in link:
        await xx.edit("` I need a Tiktok link to download it's Video...`(*_*)")
    else:
        start = datetime.now()
        catevent = await xx.edit("```Downloading Video...```")
    async with ubot.conversation(chat) as conv:
        try:
            msg_start = await conv.send_message("/start")
            r_start = await conv.get_response()
            msg = await conv.send_message(link)
            video = await conv.get_response()
            pantek = await ubot.download_media(video)
            await ubot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await catevent.edit(
                "**Error:** Contact @MerissaxSupport For Titok Download Video.`"
            )
            return
        await catevent.delete()
        cat = await tbot.send_file(
            event.chat.id, caption="Uploaded By @MerissaRobot", file=pantek
        )
        end = datetime.now()
        ms = (end - start).seconds
        await cat.edit(
            f"<b>📤 Uploaded in {ms} seconds From Tiktok.</b>\n\n<b>© Powered by @MerissaRobot</b>",
            parse_mode="html",
        )
    await ubot.delete_messages(
        conv.chat_id,
        [msg_start.id, r_start.id, msg.id, video.id],
    )


@register(pattern="^/truecaller ?(.*)")
async def insta(event):
    chat = "@XTZ_TruecallerBot"
    link = event.pattern_match.group(1)
    xx = await event.reply("`Fetching Details.....`")
    if event.fwd_from:
        return
    x = await xx.edit("```Done Please Wait...```")
    async with ubot.conversation(chat) as conv:
        try:
            msg_start = await conv.send_message("/start")
            r_start = await conv.get_response()
            msg = await conv.send_message(link)
            await asyncio.sleep(3)
            response = await conv.get_response()
            await ubot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await catevent.edit(
                "**Error:** Contact @MerissaxSupport For Fetching Details.`"
            )
            return
        await x.delete()
        cat = await tbot.send_message(
            event.chat.id,
            message=response,
        )
    await ubot.delete_messages(
        conv.chat_id,
        [msg_start.id, r_start.id, msg.id, response.id],
    )


@register(pattern="^/stt ?(.*)")
async def insta(event):
    chat = "@voicybot"
    link = await event.get_reply_audio()
    xx = await event.reply("`Downloading Audio.....`")
    if event.fwd_from:
        return
    x = await xx.edit("```Fetching Text From Audio...```")
    async with ubot.conversation(chat) as conv:
        try:
            msg_start = await conv.send_message("/start")
            r_start = await conv.get_response()
            msg = await conv.send_message(link)
            await asyncio.sleep(2)
            response = await conv.get_response()
            await ubot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await catevent.edit(
                "**Error:** Contact @MerissaxSupport For Fetching Details.`"
            )
            return
        await x.delete()
        cat = await tbot.send_message(
            event.chat.id,
            message=response,
        )
    await ubot.delete_messages(
        conv.chat_id,
        [msg_start.id, r_start.id, msg.id, response.id],
    )
