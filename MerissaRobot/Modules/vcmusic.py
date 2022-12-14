from telegram import InlineKeyboardButton

__help__ = """
**A Telegram Streaming bot with some useful features.**

**Few Features Here**:
- Zero lagtime Video + Audio + live stream player.
- Working Queue and Interactive Queue Checker.
- Youtube Downloader Bar.
- Auth Users Function .
- Download Audios/Videos from Youtube.
- Multi Assistant Mode for High Number of Chats.
- Interactive UI, Fonts and Thumbnails.
- Channel player.

**Original work is done by** : @TheYukki
"""

__mod_name__ = "Music-Bot 🎧"

__helpbtns__ = [
    [
        InlineKeyboardButton("Setup MusicBot", callback_data="cb_setup"),
        InlineKeyboardButton("Commands", callback_data="settings_back_helper"),
    ],
    [InlineKeyboardButton("🔙 Back", callback_data="help_back")],
]
