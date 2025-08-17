import re
import aiohttp
from pyrogram import filters
from MerissaRobot import pbot


API_KEY = "f9eb715d62213c45c33fc2f8b563846cae8a0711"  # move to config for safety


async def get_shortlink(link: str) -> str:
    url = "https://gplinks.in/api"
    params = {"api": API_KEY, "url": link}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                raise Exception(f"API error: {response.status}")
            data = await response.json()

            if "shortenedUrl" not in data:
                raise Exception(data.get("message", "Unknown API error"))

            return data["shortenedUrl"]


@pbot.on_message(filters.command("shorturl") & filters.private & filters.incoming)
async def link_handler(bot, message):
    if len(message.command) < 2:
        return await message.reply("❌ Please provide a link to shorten.", quote=True)

    text = message.text.split(None, 1)[1]

    # Better regex for URLs
    link_pattern = re.compile(r"https?://[^\s]+", re.IGNORECASE)
    links = re.findall(link_pattern, text)

    if not links:
        return await message.reply("⚠️ No valid links found in your text.", quote=True)

    results = []
    for link in links:
        try:
            short_link = await get_shortlink(link)
            results.append(f"🔗 **Original:** {link}\n➡️ **Shortened:** `{short_link}`")
        except Exception as e:
            results.append(f"❌ **Failed to shorten:** {link}\nError: `{e}`")

    reply_text = "**Here are your shortened links:**\n\n" + "\n\n".join(results)
    await message.reply(reply_text, disable_web_page_preview=True, quote=True)
