import re

from telethon import custom, events

from MerissaRobot import telethn as bot
from MerissaRobot import telethn as tgbot
from MerissaRobot.events import register


@register(pattern="/myinfo")
async def proboyx(event):
    button = [[custom.Button.inline("Check", data="information")]]
    await bot.send_message(
        event.chat,
        "Your Information\n\nClick Below Button To Get Information",
        buttons=button,
    )


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"information")))
async def callback_query_handler(event):
    try:
        boy = event.sender_id
        PRO = await bot.get_entity(boy)
        text = "Your Details By MerissaRobot\n"
        text += f"Firstname : {PRO.first_name} \n"
        text += f"Lastname : {PRO.last_name}\n"
        text += f"You Bot : {PRO.bot} \n"
        text += f"Restricted : {PRO.restricted} \n"
        text += f"UserId : {boy}\n"
        text += f"Username : {PRO.username}\n"
        await event.answer(text, alert=True)
    except Exception as e:
        await event.reply(f"{e}")
