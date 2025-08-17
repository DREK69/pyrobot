from random import randint

import requests as r
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes, CommandHandler, filters

from MerissaRobot import WALL_API, application
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
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        await message.reply_to_message.reply_text(
            args[1], parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    else:
        await message.reply_text(
            args[1], quote=False, parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    await message.delete()


async def markdown_help_sender(update: Update):
    await update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    await update.effective_message.reply_text(
        "Try forwarding the following message to me, and you'll see, and Use #test!"
    )
    await update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, *bold*, code, "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)"
    )


async def markdown_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.effective_message.reply_text(
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
    await markdown_help_sender(update)


@send_action(ChatAction.UPLOAD_PHOTO)
async def wall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = update.effective_message
    msg_id = update.effective_message.message_id
    args = context.args
    query = " ".join(args)
    if not query:
        await msg.reply_text("Please enter a query!")
        return
    caption = query
    term = query.replace(" ", "%20")
    
    try:
        json_rep = r.get(
            f"https://wall.alphacoders.com/api2.0/get.php?auth={WALL_API}&method=search&term={term}"
        ).json()
    except Exception as e:
        await msg.reply_text("Failed to fetch wallpapers. Please try again later.")
        return
        
    if not json_rep.get("success"):
        await msg.reply_text("An error occurred!")
        return

    wallpapers = json_rep.get("wallpapers")
    if not wallpapers:
        await msg.reply_text("No results found! Refine your search.")
        return
        
    index = randint(0, len(wallpapers) - 1)  # Choose random index
    wallpaper = wallpapers[index]
    wallpaper = wallpaper.get("url_image")
    wallpaper = wallpaper.replace("\\", "")
    
    try:
        await context.bot.send_photo(
            chat_id,
            photo=wallpaper,
            caption="Preview",
            reply_to_message_id=msg_id,
            read_timeout=60,
            write_timeout=60,
        )
        await context.bot.send_document(
            chat_id,
            document=wallpaper,
            filename="wallpaper",
            caption=caption,
            reply_to_message_id=msg_id,
            read_timeout=60,
            write_timeout=60,
        )
    except Exception as e:
        await msg.reply_text("Failed to send wallpaper. Please try again later.")


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
    "echo", echo, filters=filters.ChatType.GROUPS, block=False
)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, block=False)
WALLPAPER_HANDLER = DisableAbleCommandHandler("wall", wall, block=False)

application.add_handler(ECHO_HANDLER)
application.add_handler(MD_HELP_HANDLER)
application.add_handler(WALLPAPER_HANDLER)

__command_list__ = ["id", "echo", "wall"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
    WALLPAPER_HANDLER,
]
