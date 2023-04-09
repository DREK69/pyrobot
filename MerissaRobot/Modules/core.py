import os

from MerissaRobot import OWNER_ID
from MerissaRobot import pbot

@pbot.on_message(filters.command("module"))
def animats(client, message):
    if message.from_user.id == OWNER_ID
        pass
    else:
        return
    input_str = message.text.split(None, 1)[1]
    the_plugin_file = "./MerissaRobot/Modules/{}.py".format(input_str)
    if os.path.exists(the_plugin_file):
        message.reply_document(the_plugin_file)
    else:
        await message.reply_text("No File Found")
