import os
from datetime import datetime

from PIL import Image
from telegraph import Telegraph, exceptions, upload_file

from MerissaRobot import pbot

TMP_DOWNLOAD_DIRECTORY = "./"
telegraph = Telegraph()
r = telegraph.create_account(short_name="MerissaRobot")
auth_url = r["auth_url"]


@pbot.on_message(filters.command('tgm'))
async def get_link_group(client, message):
    try:
        text = await message.reply("Processing...")
        async def progress(current, total):
            await text.edit_text(f"📥 Downloading media... {current * 100 / total:.1f}%")
        try:
            location = f"./media/group/"
            local_path = await message.reply_to_message.download(location, progress=progress)
            await text.edit_text("📤 Uploading to Telegraph...")
            upload_path = upload_file(local_path) 
            await text.edit_text(f"**🌐 | Telegraph Link**:\n\n<code>https://telegra.ph{upload_path[0]}</code>")     
            os.remove(local_path) 
        except Exception as e:
            await text.edit_text(f"**❌ | File upload failed**\n\n<i>**Reason**: {e}</i>")
            os.remove(local_path) 
            return         
    except Exception:
        pass 

@pbot.on_message(filters.command('tgt'))
async def get_link_group(client, message):
    optional_title = message.text.split(None, 1)[1]
    m = await message.reply_text("Processing")
    async def progress(current, total):
        await m.edit_text(f"📥 Downloading media... {current * 100 / total:.1f}%")
    title_of_page = message.from_user.first_name
    if optional_title:
        title_of_page = optional_title
    page_content = message.reply_to_message
    if r_message.media:
        if page_content != "":
            title_of_page = page_content
        location = f"./media/group/"
        downloaded_file_name = await message.reply_to_message.download(location, progress=progress)
        m_list = None
        with open(downloaded_file_name, "rb") as fd:
            m_list = fd.readlines()
            for m in m_list:
                page_content += m.decode("UTF-8") + "\n"
            os.remove(downloaded_file_name)
        page_content = page_content.replace("\n", "<br>")
        response = telegraph.create_page(title_of_page, html_content=page_content)
        end = datetime.now()
        ms = (end - start).seconds
        await m.edit_text(
        "Pasted to https://te.legra.ph/{} in {} seconds.".format(
                response["path"], ms
            ))
    else:
        await message.reply("Reply to a message to get a permanent telegra.ph link.")


def resize_image(image):
    im = Image.open(image)
    im.save(image, "PNG")


__help__ = """
I can upload files to Telegraph
 ❍ /tgm :Get Telegraph Link Of Replied Media
 ❍ /tgt :Get Telegraph Link of Replied Text
"""

__mod_name__ = "Telegraph 📋"
