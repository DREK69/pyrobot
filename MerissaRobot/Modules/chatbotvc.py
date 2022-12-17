import os

import aiofiles
import aiohttp
from pyrogram import filters

from MerissaRobot import pbot as LYCIA


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            try:
                data = await resp.json()
            except:
                data = await resp.text()
    return data


async def ai_lycia(url):
    ai_name = "Merissa.mp3"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(ai_name, mode="wb")
                await f.write(await resp.read())
                await f.close()
    return ai_name


@LYCIA.on_message(filters.command("merissa"))
async def Lycia(_, message):
    if len(message.command) < 2:
        await message.reply_text("Merissa AI Voice Chatbot")
        return
    text = message.text.split(None, 1)[1]
    lycia = text.replace(" ", "%20")
    m = await message.reply_text("Merissa Is Best...")
    try:
        L = await fetch(
            f"https://merissachatbot.vercel.app/chatbot/Merissa/Prince/message={m}"
        )
        chatbot = L["reply"]
        VoiceAi = f"https://serverless-tts.vercel.app/api/demo?voice=en-US_LisaExpressive&text={chatbot}"
        name = "Merissa"
    except Exception as e:
        await m.edit(str(e))
        return
    await m.edit("Powered By @MerissaRobot...")
    LyciaVoice = await ai_lycia(VoiceAi)
    await m.edit("Replying...")
    await message.reply_audio(audio=LyciaVoice, title=chatbot, performer=name)
    os.remove(LyciaVoice)
    await m.delete()
