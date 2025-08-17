import asyncio
import os
from datetime import datetime
from inspect import getfullargspec

from aiohttp import BasicAuth, ClientSession
from gtts import gTTS
from pyrogram import enums, filters
from pyrogram.types import Message

from MerissaRobot import IBM_WATSON_CRED_PASSWORD, IBM_WATSON_CRED_URL, pbot

# Default language for TTS
LANG = "en"


async def edit_or_reply(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})


@pbot.on_message(filters.command("tts"))
async def voice(client, message):
    global LANG
    cmd = message.command
    if len(cmd) > 1:
        v_text = " ".join(cmd[1:])
    elif message.reply_to_message and message.reply_to_message.text:
        v_text = message.reply_to_message.text
    else:
        return await edit_or_reply(message, text="Usage: `/tts text` or reply to a message.")

    await client.send_chat_action(message.chat.id, enums.ChatAction.RECORD_VOICE)

    try:
        tts = gTTS(v_text, lang=LANG)
        tts.save("voice.mp3")

        if message.reply_to_message:
            await client.send_voice(
                message.chat.id,
                voice="voice.mp3",
                reply_to_message_id=message.reply_to_message.message_id,
            )
        else:
            await client.send_voice(message.chat.id, voice="voice.mp3")

    except Exception as e:
        await edit_or_reply(message, text=f"❌ TTS Error: `{e}`")

    finally:
        if os.path.exists("voice.mp3"):
            os.remove("voice.mp3")
        await client.send_chat_action(message.chat.id, enums.ChatAction.CANCEL)


@pbot.on_message(filters.command("voicelang"))
async def voicelang(_, message):
    global LANG
    if len(message.command) < 2:
        return await edit_or_reply(message, text="Usage: `/voicelang en`")
    new_lang = message.command[1]
    try:
        gTTS("test", lang=new_lang)  # validate language
        LANG = new_lang
        await edit_or_reply(message, text=f"✅ Language set to `{LANG}`")
    except Exception as e:
        await edit_or_reply(message, text=f"❌ Invalid language code: `{e}`")


@pbot.on_message(filters.command("stt"))
async def speech_to_text(client, message):
    if not message.reply_to_message:
        return await edit_or_reply(message, text="Reply to a voice/audio message with `/stt`")

    media = message.reply_to_message.voice or message.reply_to_message.audio or message.reply_to_message.video_note
    if not media:
        return await edit_or_reply(message, text="❌ Supported formats: voice, audio, video_note")

    file_path = await message.reply_to_message.download()
    if not IBM_WATSON_CRED_URL or not IBM_WATSON_CRED_PASSWORD:
        os.remove(file_path)
        return await edit_or_reply(message, text="❌ No IBM Watson credentials provided.")

    start = datetime.now()
    headers = {"Content-Type": media.mime_type}

    try:
        async with ClientSession(headers=headers) as ses:
            async with ses.post(
                IBM_WATSON_CRED_URL + "/v1/recognize",
                data=open(file_path, "rb"),
                auth=BasicAuth("apikey", IBM_WATSON_CRED_PASSWORD),
            ) as resp:
                r = await resp.json()

        if "results" in r:
            results = r["results"]
            transcript = " ".join(alt["alternatives"][0]["transcript"] for alt in results)
            confidence = " ".join(str(alt["alternatives"][0]["confidence"]) for alt in results)
            ms = (datetime.now() - start).seconds

            text = f"""
**📝 Transcript:**
`{transcript.strip()}`

**⏱ Time Taken:** `{ms} sec`
**✅ Confidence:** `{confidence}`
"""
        else:
            text = f"❌ Error: {r.get('error', 'No results found')}"

        await edit_or_reply(message, text=text)

    except Exception as e:
        await edit_or_reply(message, text=f"❌ STT Error: `{e}`")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
