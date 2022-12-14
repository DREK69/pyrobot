from telegram import InlineKeyboardButton

__help__ = """
Merissa supports a large number of formatting options to make your messages more expressive. Take a look!"""

__mod_name__ = "Formatting 📑"

__helpbtns__ = [
    [
        InlineKeyboardButton("Markdown", callback_data="cb_markdown"),
        InlineKeyboardButton("Filling", callback_data="cb_filling"),
    ],
    [
        InlineKeyboardButton("🔙 Back", callback_data="help_back"),
    ],
]
