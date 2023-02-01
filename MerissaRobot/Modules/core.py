import os

from MerissaRobot import OWNER_ID
from MerissaRobot import telethn as tbot
from MerissaRobot.events import register

client = tbot

@register(pattern=r"^/send ?(.*)")
async def Prof(event):
    if event.sender_id == OWNER_ID:
        pass
    else:
        return    
    message_id = event.message.id
    input_str = event.pattern_match.group(1)
    the_plugin_file = "./MerissaRobot/Modules/{}.py".format(input_str)
    if os.path.exists(the_plugin_file):
        message_id = event.message.id
        await event.client.send_file(
            event.chat_id,
            the_plugin_file,
            force_document=True,
            allow_cache=False,           
            reply_to=message_id,
        )
    else:
        await event.reply("No File Found, Report It To Support!")
