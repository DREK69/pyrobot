import random
import string
from random import sample
from urllib.parse import quote

import httpx
from pyrogram import enums, filters
from pyrogram.types import InputMediaPhoto
from SafoneAPI import SafoneAPI

from MerissaRobot import pbot


class Lexica:
    def __init__(
        self,
        query,
        negativePrompt="",
        guidanceScale: int = 7,
        portrait: bool = True,
        cookie=None,
    ):
        self.query = query
        self.negativePrompt = negativePrompt
        self.guidanceScale = guidanceScale
        self.portrait = portrait
        self.cookie = cookie

    def images(self):
        response = httpx.post(
            "https://lexica.art/api/infinite-prompts",
            json={
                "text": self.query,
                "searchMode": "images",
                "source": "search",
                "model": "lexica-aperture-v2",
            },
        )

        prompts = [
            f"https://image.lexica.art/full_jpg/{ids['id']}"
            for ids in response.json()["images"]
        ]

        return prompts

    def _generate_random_string(self, length):
        chars = string.ascii_letters + string.digits
        result_str = "".join(random.choice(chars) for _ in range(length))

        return result_str


# Generate gpt response...


@pbot.on_message(filters.command(["gpt", "ask", "chatgpt"]))
async def chatgpt(c, m):
    try:
        query = m.text.split(None, 1)[1]
    except:
        await m.reply_text("`ɪ ᴅɪᴅɴ'ᴛ ɢᴇᴛ ᴛʜᴀᴛ`")
        return
    query = quote(query)
    await c.send_chat_action(m.chat.id, enums.ChatAction.TYPING)
    api = SafoneAPI()
    resp = await api.chatgpt(query)
    response = resp.message
    await c.send_message(m.chat.id, response, reply_to_message_id=m.id)
    await c.send_chat_action(m.chat.id, enums.ChatAction.CANCEL)


@pbot.on_message(filters.command(["img"]))
async def ai_img_search(c, m):
    try:
        prompt = m.text.split(None, 1)[1]
    except IndexError:
        await m.reply_text(
            "`What should i imagine??\nGive some prompt along with the command`"
        )
        return
    x = await m.reply_text("`Processing...`")
    try:
        lex = Lexica(query=prompt).images()
        k = sample(lex, 4)
        result = [InputMediaPhoto(image) for image in k]
        await c.send_media_group(
            chat_id=m.chat.id,
            media=result,
            reply_to_message_id=m.id,
        )
        await x.delete()
    except:
        await x.edit("`Failed to get images`")
