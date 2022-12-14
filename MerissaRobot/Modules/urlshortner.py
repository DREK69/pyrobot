import re

import aiohttp
from pyrogram import filters

from MerissaRobot import pbot


async def get_shortlink(link):
    url = "https://gplinks.in/api"
    params = {"api": "f9eb715d62213c45c33fc2f8b563846cae8a0711", "url": link}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, raise_for_status=True) as response:
            data = await response.json()
            return data["shortenedUrl"]


@pbot.on_message(filters.command("shorturl") & filters.private & filters.incoming)
async def link_handler(bot, message):
    link_pattern = re.compile(
        "https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,}",
        re.DOTALL,
    )
    links = re.findall(link_pattern, message.text.split(None, 1)[1])
    if len(message.command) < 2:
        await message.reply("No links Found in this text", quote=True)
        return
    for link in links:
        try:
            short_link = await get_shortlink(link)
            await message.reply(
                f"Here is Your Shortened Link\n\nOriginal Link: {link}\n\nShortened Link: `{short_link}`",
                quote=True,
                disable_web_page_preview=True,
            )
        except Exception as e:
            await message.reply(f"𝐄𝐫𝐫𝐨𝐫: `{e}`", quote=True)
