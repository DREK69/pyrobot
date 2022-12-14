from telegram import ParseMode
from telethon import Button

from MerissaRobot import OWNER_ID, SUPPORT_CHAT
from MerissaRobot import telethn as tbot
from MerissaRobot.events import register


@register(pattern="/bug ?(.*)")
async def feedback(e):
    quew = e.pattern_match.group(1)
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    BUTTON = [[Button.url("Support Group", f"https://t.me/{SUPPORT_CHAT}")]]
    TEXT = "Thanks For Reporting Us, I Hope You Happy With Our Service"
    GIVE = "No bug Reports Right Now ✔️"
    logger_text = f"""
**New Bug Report**

**From User:** {mention}
**Username:** @{e.sender.username}
**User ID:** `{e.sender.id}`
**Bug Report:** `{e.text}`

**Powered By MerissaRobot**
"""
    if e.sender_id != OWNER_ID and not quew:
        await e.reply(
            GIVE,
            parse_mode=ParseMode.MARKDOWN,
            buttons=BUTTON,
        ),
        return

    await tbot.send_message(
        SUPPORT_CHAT,
        f"{logger_text}",
        link_preview=False,
    )
    await e.reply(TEXT, buttons=BUTTON)
