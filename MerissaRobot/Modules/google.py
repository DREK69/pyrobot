import glob
import io
import os
import re
import urllib
import urllib.request

import bs4
import requests
from bing_image_downloader import downloader
from bs4 import BeautifulSoup
from PIL import Image
from pyrogram import filters

import json

from MerissaRobot import pbot as app
from MerissaRobot import telethn as tbot
from MerissaRobot.events import register
from MerissaRobot.helpers import getreq

import requests
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto, Message


@app.on_message(filters.command("google"))
async def google(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Give me some query to search on google\n\nex: /google who is merissarobot?"
        )
    webevent = await message.reply_text("Searching...")
    query = message.text.split(None, 1)[1]
    gresults = await getreq(f"https://api.princexd.tech/google?query={query}&limit=5")
    msg = ""
    for i in gresults["results"]:
        title = i["title"]
        link = i["link"]
        desc = i["description"]
        msg += f"❍[{title}]({link})\n**{desc}**\n\n"
    await webevent.edit_text(
        "**Search Query:**\n`" + query + "`\n\n**Results:**\n" + msg,
        disable_web_page_preview=True,
    )


@app.on_message(filters.command("bingimg"))
def bingimg_search(client: Client, message: Message):
    try:
        text = message.text.split(None, 1)[1] 
    except IndexError:
        return await message.reply_text(
            "Provide me a query to search!"
        ) 

    search_message = await message.reply_text(
        "Searching image using Bing search 🔎"
    )  

    url = "https://sugoi-api.vercel.app/bingimg?keyword=" + text
    images = await getreq(url)
    media = []
    count = 0
    for img in images:
        if count == 7:
            break

        media.append(InputMediaPhoto(media=img))
        count += 1

    await message.reply_media_group(media=media)
    await search_message.delete()


@app.on_message(filters.command("googleimg"))
def googleimg_search(client: Client, message: Message):
    try:
        text = message.text.split(None, 1)[1]  
    except IndexError:
        return await message.reply_text(
            "Provide me a query to search!"
        )  

    search_message = await message.reply_text(
        "Searching image using Google search 🔎"
    )
    
    url = "https://sugoi-api.vercel.app/googleimg?keyword=" + text
    images = await getreq(url)
    media = []
    count = 0
    for img in images:
        if count == 7:
            break

        media.append(InputMediaPhoto(media=img))
        count += 1

    await message.reply_media_group(media=media)
    await search_message.delete()
