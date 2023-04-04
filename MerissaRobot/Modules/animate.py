import base64
import json
import random
import string

import requests
import telebot
from pyrogram import filters
from pyrogram.types import *

from MerissaRobot import TOKEN
from MerissaRobot import pbot as app

bot = telebot.TeleBot(TOKEN)

y = {}


def get_ai_image(base64_image_string):
    headers = {
        "Connection": "keep-alive",
        "phone_gid": "2862114434",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; SM-G955N Build/NRD90M.G955NKSU1AQDC; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 com.meitu.myxj/11270(android7.1.2)/lang:ru/isDeviceSupport64Bit:false MTWebView/4.8.5",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://titan-h5.meitu.com",
        "X-Requested-With": "com.meitu.meiyancamera",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://titan-h5.meitu.com/",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    params = {
        "api_key": "237d6363213c4751ba1775aba648517d",
        "api_secret": "b7b1c5865a83461ea5865da3ecc7c03d",
    }

    json_data = {
        "parameter": {
            "rsp_media_type": "url",
            "strength": 0.45,
            "guidance_scale": 7.5,
            "prng_seed": "-1",
            "num_inference_steps": "50",
            "extra_prompt": "",
            "extra_negative_prompt": "",
            "random_generation": "False",
            "type": "1",
            "type_generation": "True",
            "sensitive_words": "white_kimono",
        },
        "extra": {},
        "media_info_list": [
            {
                "media_data": base64_image_string,
                "media_profiles": {
                    "media_data_type": "jpg",
                },
            },
        ],
    }

    response = requests.post(
        "https://openapi.mtlab.meitu.com/v1/stable_diffusion_anime",
        params=params,
        headers=headers,
        json=json_data,
    )

    return json.loads(response.content)


@app.on_message(filters.command("animate"))
def animats(client, message):
    if not message.reply_to_message:
        if not message.photo:
            message.reply_text("Reply To Image")
            return
    file_id = message.reply_to_message.photo.file_id
    filepath = bot.get_file(file_id).file_path
    x = message.reply_text("Creating your Anime Avtar... Please Wait!")
    r = requests.get("https://api.telegram.org/file/bot" + TOKEN + "/" + filepath)
    base64_image_string = base64.b64encode(r.content).decode("utf-8")
    ran_hash = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    y[ran_hash] = base64_image_string
    ai_image = get_ai_image(base64_image_string)["media_info_list"][0]["media_data"]
    message.reply_photo(
        photo=ai_image,
        caption="Powered By @MerissaRobot",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data=f"animate_{ran_hash}",
                    ),
                ],
            ],
        ),
    )
    x.delete()


@app.on_message(filters.photo & filters.private)
def mangadown(client, message):
    if not message.reply_to_message:
        if not message.photo:
            message.reply_text("Reply To Image")
            return
    file_id = message.photo.file_id
    filepath = bot.get_file(file_id).file_path
    x = message.reply_text("Creating your Anime Avtar... Please Wait!")
    r = requests.get("https://api.telegram.org/file/bot" + TOKEN + "/" + filepath)
    base64_image_string = base64.b64encode(r.content).decode("utf-8")
    ran_hash = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    y[ran_hash] = base64_image_string
    ai_image = get_ai_image(base64_image_string)["media_info_list"][0]["media_data"]
    message.reply_photo(
        photo=ai_image,
        caption="Powered By @MerissaRobot",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data=f"animate_{ran_hash}",
                    ),
                ],
            ],
        ),
    )
    x.delete()


@app.on_callback_query(filters.regex(pattern=r"animate"))
async def hmeme(_, query: CallbackQuery):
    await query.answer("Generating your Anime Avatar\nPlease Wait....", show_alert=True)
    callback_data = query.data.strip()
    ran_hash = callback_data.split("_")[1]
    base64_image_string = y.get(ran_hash)
    ai_image = get_ai_image(base64_image_string)["media_info_list"][0]["media_data"]
    await query.edit_message_media(
        InputMediaPhoto(ai_image, caption="Powered by @MerissaRobot"),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Change 🔂",
                        callback_data=f"animate_{ran_hash}",
                    ),
                ],
            ],
        ),
    )
