from telegram import InlineKeyboardButton

__mod_name__ = "Tools 🛠"

__help__ = """
**Here is the help for the tools module:
We promise to keep you latest up-date with the latest technology on telegram. 
We Upgrade Merissa RoBot everyday to simplifie use of telegram and give a better exprince to users.

Click on below buttons and check amazing tools for users.**"""

__helpbtns__ = [
    [
        InlineKeyboardButton("Afk", callback_data="cb_afk"),
        InlineKeyboardButton("Animation", callback_data="cb_animation"),
        InlineKeyboardButton("Anime", callback_data="cb_anime"),
    ],
    [
        InlineKeyboardButton("Convert", callback_data="cb_convert"),
        InlineKeyboardButton("Extra", callback_data="cb_extra"),
        InlineKeyboardButton("Fun", callback_data="cb_fun"),
    ],
    [
        InlineKeyboardButton("🔙 Back", callback_data="help_back"),
        InlineKeyboardButton("➡️", callback_data="cb_toolb"),
    ],
]
