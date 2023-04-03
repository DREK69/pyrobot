import base64
import hashlib
import json
import os
import random
import uuid

import requests
from pyrogram import filters

from MerissaRobot import pbot


def signV1(obj):
    s = json.dumps(obj)
    return hashlib.md5(
        b"https://h5.tu.qq.com" + str(len(s)).encode() + b"HQ31X02e"
    ).hexdigest()


def qq_request(img_buffer):
    str(uuid.uuid4())
    images = base64.b64encode(img_buffer).decode()

    data_report = {
        "parent_trace_id": "4c689320-71ba-1909-ab57-13c0804d4cc6",
        "root_channel": "",
        "level": 0,
    }

    obj = {
        "busiId": "different_dimension_me_img_entry",  #'ai_painting_anime_entry',
        "images": [
            images,
        ],
        "extra": json.dumps(
            {
                "face_rects": [],
                "version": 2,
                "platform": "web",
                "data_report": data_report,
            }
        ),
    }
    sign = signV1(obj)
    url = "https://ai.tu.qq.com/overseas/trpc.shadow_cv.ai_processor_cgi.AIProcessorCgi/Process"
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://h5.tu.qq.com",
        "Referer": "https://h5.tu.qq.com/web/ai-2d/cartoon/index?jump_qq_for_play=true",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "x-sign-value": sign,
        "x-sign-version": "v1",
    }

    timeout = 30000
    r = requests.get(
        "https://api.proxynova.com/proxy/find?url=https%3A%2F%2Fwww.proxynova.com%2Fproxy-server-list%2Fcountry-cn%2F"
    )
    x = [f"https://{ii['ip']}:{ii['port']}" for ii in r.json()["proxies"]]
    proxy = random.choice(x)
    proxies = {
        "http": proxy,
    }
    response = requests.post(
        url, json=obj, headers=headers, proxies=proxies, timeout=timeout
    )
    data = response.json()
    return data


@pbot.on_message(filters.command("animate") & filters.private)
async def movie(client, message):
    reply = message.reply_to_message
    if reply:
        logo = await message.reply_text("Creating your anime avtar...wait!")
        download_location = await client.download_media(
            message=reply,
            file_name="root/downloads/",
        )
        with open(download_location, "rb") as f:
            img_buffer = f.read()
            x = qq_request(img_buffer)
            await logo.edit_text(x)
            os.remove(download_location)
    else:
        await message.reply_text("Reply to your photo to convert anime avtar")
