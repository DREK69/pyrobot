from telethon.tl.types import ChannelParticipantAdmin as admin
from telethon.tl.types import ChannelParticipantCreator as owner
from telethon.tl.types import UserStatusOffline as off
from telethon.tl.types import UserStatusOnline as onn
from telethon.tl.types import UserStatusRecently as rec
from telethon.utils import get_display_name

from MerissaRobot.events import register


@register(
    pattern="/tag(on|off|active|bots|rec|admins|owner)?(.*)",
    outgoing=True,
)
async def _(e):
    okk = e.text
    msg = e.pattern_match.group(2)
    users = 0
    o = 0
    nn = 0
    rece = 0
    if msg:
        mention = f"{msg}\n\n"
    else:
        mention = ""
    async for bb in e.client.iter_participants(e.chat_id, 99):
        users = users + 1
        x = bb.status
        y = bb.participant

        if isinstance(x, onn):
            o = o + 1
            if "on" in okk:
                mention += f"[{get_display_name(bb)}](tg://user?id={bb.id}) "

        if isinstance(x, off):
            nn = nn + 1
            if "off" in okk:
                if not (bb.bot or bb.deleted):
                    mention += f"[{get_display_name(bb)}](tg://user?id={bb.id}) "

        if isinstance(x, rec):
            rece = rece + 1
            if "rec" in okk:
                if not (bb.bot or bb.deleted):
                    mention += f"[{get_display_name(bb)}](tg://user?id={bb.id}) "

        if isinstance(y, owner):
            if "admin" or "owner" in okk:
                mention += f"✰ [{get_display_name(bb)}](tg://user?id={bb.id}) ✰ "

        if isinstance(y, admin):
            if "admin" in okk:
                if not bb.deleted:
                    mention += f"[{get_display_name(bb)}](tg://user?id={bb.id}) "

        if "all" in okk:
            if not (bb.bot or bb.deleted):
                mention += f"[{get_display_name(bb)}](tg://user?id={bb.id}) "

        if "bot" in okk:
            if bb.bot:
                mention += f"[{get_display_name(bb)}](tg://user?id={bb.id}) "
    await e.client.send_message(e.chat_id, mention)
    await e.delete()
