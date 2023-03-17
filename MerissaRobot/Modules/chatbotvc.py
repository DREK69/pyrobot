import os

import aiofiles
import aiohttp
from pyrogram import filters

from MerissaRobot import pbot


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            try:
                data = await resp.json()
            except:
                data = await resp.text()
    return data


async def ai_merissa(url):
    ai_name = "Merissa.mp3"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(ai_name, mode="wb")
                await f.write(await resp.read())
                await f.close()
    return ai_name


@pbot.on_message(filters.command("merissa"))
async def merissa(_, message):
    if len(message.command) < 2:
        await message.reply_text("Merissa AI Voice Chatbot")
        return
    text = message.text.split(None, 1)[1]
    merissa = text.replace(" ", "%20")
    m = await message.reply_text("Replying...")
    try:
        L = await fetch(
            f"https://api.princexd.tech/ask?text={merissa}"
        )
        chatbot = L["answer"]
        VoiceAi = f"https://serverless-tts.vercel.app/api/demo?voice=en-US_LisaExpressive&text={chatbot}"
        name = "Merissa"
    except Exception as e:
        await m.edit(str(e))
        return
    await m.edit("Powered By @MerissaRobot...")
    MerissaVoice = await ai_merissa(VoiceAi)
    await message.reply_audio(audio=MerissaVoice, title=chatbot, performer=name)
    os.remove(MerissaVoice)
    await m.delete()
