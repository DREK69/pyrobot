import random
import string
from random import sample

import httpx
from pyrogram import enums, filters
from pyrogram.types import InputMediaPhoto

from MerissaRobot import pbot
from MerissaRobot.helpers import getreq


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


@pbot.on_message(filters.command(["gpt", "ask", "chatgpt"]))
async def chatgpt(c, message):
    if len(message.command) == 1:
        return await message.reply_msg(
            "Give me some questions to ask Chatgpt AI. Example- /ask question"
        )
    query = message.text.split(None, 1)[1]
    msg = await message.reply_text(
        "Wait a moment looking for your answer..", quote=True
    )
    try:
        await c.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        x = await getreq(f"https://vihangayt.me/tools/chatgpt?q={query}")
        response = x["data"]
    except:
        response = "Something Went Wrong"
    await msg.edit_text(response)
    await c.send_chat_action(message.chat.id, enums.ChatAction.CANCEL)


@pbot.on_message(filters.command(["bard", "googleai"]))
async def bard_chatbot(c, message):
    if len(message.command) == 1:
        return await message.reply_text(
            "Give me some questions to ask Bard AI. Example- /bard question"
        )
    query = message.text.split(None, 1)[1]
    msg = await message.reply_text(
        "Wait a moment looking for your answer..", quote=True
    )
    try:
        await c.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        x = await getreq(f"https://vihangayt.me/tools/bard?q={query}")
        response = x["data"]
    except:
        response = "Something went wrong"
    await msg.edit_text(response)
    await c.send_chat_action(message.chat.id, enums.ChatAction.CANCEL)


@pbot.on_message(filters.command("lexica"))
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


@pbot.on_message(filters.command(["generate", "dream", "prompt"]))
async def ai_img_search(c, m):
    try:
        query = m.text.split(None, 1)[1]
    except IndexError:
        await m.reply_text(
            "`What should i imagine??\nGive some prompt along with the command`"
        )
        return
    x = await m.reply_text("`Processing...`")
    try:
        await c.send_chat_action(m.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        response = await getreq(f"https://vihangayt.me/tools/photoleap?q={query}")
        image = f"https://vihangayt.me/tools/enhance?url={response['data']}"
        await m.reply_photo(image, caption="Genereted by @MerissaRobot")
    except:
        await m.reply_text("Something went wrong")
    await x.delete()
