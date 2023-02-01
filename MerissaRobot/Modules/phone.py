import json

import requests

from MerissaRobot import telethn as client
from MerissaRobot.events import register

# Copyright (C) 2021 CALL ME VP


# This file is part of MissVisa (Telegram Bot)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await client(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    elif isinstance(chat, types.InputPeerChat):
        ui = await client.get_peer_id(user)
        ps = (
            await client(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    else:
        return None


# Join Our Channel t.me/MissVisa_Updates


@register(pattern=r"^/phone (.*)")
async def phone(event):
    if event.is_group:
        if not (await is_register_admin(event.input_chat, event.message.sender_id)):
            await event.reply("😒 You are not admin 🚶‍♀️")
            return
    information = event.pattern_match.group(1)
    number = information
    output = requests.get(f"https://prince-api.tk/phone?number={number}")
    content = output.text
    obj = json.loads(content)
    country_code = obj["country_code"]
    country_name = obj["country_name"]
    location = obj["location"]
    carrier = obj["carrier"]
    line_type = obj["line_type"]
    validornot = obj["valid"]
    aa = "Valid: " + str(validornot)
    a = "Phone number: " + str(number)
    b = "Country: " + str(country_code)
    c = "Country Name: " + str(country_name)
    d = "Location: " + str(location)
    e = "Carrier: " + str(carrier)
    f = "Device: " + str(line_type)
    g = f"{aa}\n{a}\n{b}\n{c}\n{d}\n{e}\n{f}"
    await event.reply(g)
