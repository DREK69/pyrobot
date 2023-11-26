from random import randint

import requests as r
from telegram import (
    ChatAction,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.ext import CallbackContext, CommandHandler, Filters

from MerissaRobot import WALL_API, dispatcher
from MerissaRobot.Handler.ptb.alternate import send_action
from MerissaRobot.Handler.ptb.chat_status import user_admin
from MerissaRobot.Modules.disable import DisableAbleCommandHandler

MARKDOWN_HELP = """
Markdown is a very powerful formatting tool supported by telegram. Merissa has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.

❂ <code>_italic_</code>: wrapping text with '_' will produce italic text
❂ <code>*bold*</code>: wrapping text with '*' will produce bold text
❂ <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
❂ <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
and tapping on it will open the page at <code>someURL</code>.
<b>Example:</b><code>[test](example.com)</code>

❂ <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \
will be the url which is opened.
<b>Example:</b> <code>[This is a button](buttonurl:example.com)</code>

If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
This will create two buttons on a single line, instead of one button per line.

Keep in mind that your message <b>MUST</b> contain some text other than just a button!
"""


@user_admin
def echo(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1], parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    else:
        message.reply_text(
            args[1], quote=False, parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    message.delete()


def markdown_help_sender(update: Update):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Try forwarding the following message to me, and you'll see, and Use #test!"
    )
    update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, *bold*, code, "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)"
    )


def markdown_help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        update.effective_message.reply_text(
            "Contact me in pm",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Markdown help",
                            url=f"t.me/{context.bot.username}?start=markdownhelp",
                        )
                    ]
                ]
            ),
        )
        return
    markdown_help_sender(update)


@send_action(ChatAction.UPLOAD_PHOTO)
def wall(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    msg = update.effective_message
    msg_id = update.effective_message.message_id
    args = context.args
    query = " ".join(args)
    if not query:
        msg.reply_text("Please enter a query!")
        return
    caption = query
    term = query.replace(" ", "%20")
    json_rep = r.get(
        f"https://wall.alphacoders.com/api2.0/get.php?auth={WALL_API}&method=search&term={term}"
    ).json()
    if not json_rep.get("success"):
        msg.reply_text("An error occurred!")

    else:
        wallpapers = json_rep.get("wallpapers")
        if not wallpapers:
            msg.reply_text("No results found! Refine your search.")
            return
        index = randint(0, len(wallpapers) - 1)  # Choose random index
        wallpaper = wallpapers[index]
        wallpaper = wallpaper.get("url_image")
        wallpaper = wallpaper.replace("\\", "")
        context.bot.send_photo(
            chat_id,
            photo=wallpaper,
            caption="Preview",
            reply_to_message_id=msg_id,
            timeout=60,
        )
        context.bot.send_document(
            chat_id,
            document=wallpaper,
            filename="wallpaper",
            caption=caption,
            reply_to_message_id=msg_id,
            timeout=60,
        )


__help__ = """
*Available commands:*
❂ /markdownhelp*:* quick summary of how markdown works in telegram - can only be called in private chats
❂ /paste*:* Saves replied content to `nekobin.com` and replies with a url
❂ /react*:* Reacts with a random reaction 
❂ /ud <word>*:* Type the word or expression you want to search use
❂ /reverse*:* Does a reverse image search of the media which it was replied to.
❂ /wiki <query>*:* wikipedia your query
❂ /wall <query>*:* get a wallpaper from wall.alphacoders.com
❂ /cash*:* currency converter
 Example:
 `/cash 1 USD INR`  
      _OR_
 `/cash 1 usd inr`
 Output: `1.0 USD = 75.505 INR`
"""

__mod_name__ = "Extras 🥴"

ECHO_HANDLER = DisableAbleCommandHandler(
    "echo", echo, filters=Filters.chat_type.groups, run_async=True
)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, run_async=True)
WALLPAPER_HANDLER = DisableAbleCommandHandler("wall", wall, run_async=True)

dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(WALLPAPER_HANDLER)

__command_list__ = ["id", "echo", "wall"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
    WALLPAPER_HANDLER,
]
