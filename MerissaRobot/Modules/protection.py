from telegram import InlineKeyboardButton

__help__ = """
Anti-Function:

- /nsfwscan : Reply to an image/document/sticker/animation to scan it
- /spamscan - Get Spam predictions of replied message.

Group's Anti-Function is also an very essential fact to consider in group management
Anti-Function is the inbuilt toolkit in Rose for avoid spammers, and to improve Anti-Function of your group"""

__mod_name__ = "Protection 🔒"

__helpbtns__ = [
    [
        InlineKeyboardButton("Anti-Service", callback_data="cb_service"),
        InlineKeyboardButton("Anti-Language", callback_data="cb_antilang"),
    ],
    [
        InlineKeyboardButton("Anti-Spam", callback_data="cb_flood"),
        InlineKeyboardButton("Anti-Channel", callback_data="cb_antichannel"),
    ],
    [InlineKeyboardButton("🔙 Back", callback_data="help_back")],
]
