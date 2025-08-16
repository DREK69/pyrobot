from math import ceil
from typing import Dict, List
from uuid import uuid4
import asyncio

import cv2
import ffmpeg
from telegram import (
    Bot, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    constants
)
from telegram.error import TelegramError
from telegram.constants import ParseMode

from MerissaRobot import NO_LOAD

# Use the new constants system in PTB v22
MAX_MESSAGE_LENGTH = constants.MessageLimit.MAX_TEXT_LENGTH


class EqInlineKeyboardButton(InlineKeyboardButton):
    """Custom InlineKeyboardButton with comparison methods"""
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def split_message(msg: str) -> List[str]:
    """Split a message into multiple parts if it exceeds the maximum length"""
    if len(msg) < MAX_MESSAGE_LENGTH:
        return [msg]

    lines = msg.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < MAX_MESSAGE_LENGTH:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line
    else:
        # Else statement at the end of the for loop, so append the leftover string.
        result.append(small_msg)

    return result


def paginate_modules(page_n: int, module_dict: Dict, prefix, chat=None) -> List:
    """Create paginated inline keyboard for modules"""
    if not chat:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({})".format(
                        prefix, x.__mod_name__.lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )
    else:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({},{})".format(
                        prefix, chat, x.__mod_name__.lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )

    pairs = [modules[i * 2 : (i + 1) * 2] for i in range((len(modules) + 2 - 1) // 2)]

    round_num = len(modules) / 2
    calc = len(modules) - round(round_num)
    if calc in [1, 2]:
        pairs.append((modules[-1],))

    max_num_pages = ceil(len(pairs) / 6)
    modulo_page = page_n % max_num_pages

    # can only have a certain amount of buttons side by side
    if len(pairs) > 6:
        pairs = pairs[modulo_page * 6 : 6 * (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton(
                    "⬅️ Previous",
                    callback_data="{}_prev({})".format(prefix, modulo_page),
                ),
                EqInlineKeyboardButton(
                    "Next ➡️", callback_data="{}_next({})".format(prefix, modulo_page)
                ),
            ),
            (EqInlineKeyboardButton("Return Home 🏠", callback_data="merissa_back"),),
        ]

    else:
        pairs += [[EqInlineKeyboardButton("Back", callback_data="merissa_back")]]

    return pairs


def gpaginate_modules(page_n: int, module_dict: Dict, prefix, chat=None) -> List:
    """Create paginated inline keyboard for modules (group version)"""
    if not chat:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({})".format(
                        prefix, x.__mod_name__.lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )
    else:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({},{})".format(
                        prefix, chat, x.__mod_name__.lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )

    pairs = [modules[i * 2 : (i + 1) * 2] for i in range((len(modules) + 2 - 1) // 2)]

    round_num = len(modules) / 2
    calc = len(modules) - round(round_num)
    if calc in [1, 2]:
        pairs.append((modules[-1],))

    max_num_pages = ceil(len(pairs) / 6)
    modulo_page = page_n % max_num_pages

    # can only have a certain amount of buttons side by side
    if len(pairs) > 6:
        pairs = pairs[modulo_page * 6 : 6 * (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton(
                    "⬅️ Previous",
                    callback_data="{}_prev({})".format(prefix, modulo_page),
                ),
                EqInlineKeyboardButton(
                    "Next ➡️", callback_data="{}_next({})".format(prefix, modulo_page)
                ),
            ),
            (
                EqInlineKeyboardButton(
                    "Return Home 🏠", callback_data="merissa_setting"
                ),
            ),
        ]

    else:
        pairs += [[EqInlineKeyboardButton("Back", callback_data="merissa_back")]]

    return pairs


async def send_to_list(
    bot: Bot, send_to: list, message: str, markdown=False, html=False
) -> None:
    """Send message to a list of users - Updated for PTB v22 async"""
    if html and markdown:
        raise Exception("Can only send with either markdown or HTML!")
    
    for user_id in set(send_to):
        try:
            if markdown:
                await bot.send_message(user_id, message, parse_mode=ParseMode.MARKDOWN)
            elif html:
                await bot.send_message(user_id, message, parse_mode=ParseMode.HTML)
            else:
                await bot.send_message(user_id, message)
        except TelegramError:
            pass  # ignore users who fail


def build_keyboard(buttons):
    """Build inline keyboard from button objects"""
    keyb = []
    for btn in buttons:
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def article(
    title: str = "",
    description: str = "",
    message_text: str = "",
    thumb_url: str = None,
    reply_markup: InlineKeyboardMarkup = None,
    disable_web_page_preview: bool = False,
) -> InlineQueryResultArticle:
    """Create an inline query result article"""
    return InlineQueryResultArticle(
        id=str(uuid4()),  # Convert UUID to string for PTB v22
        title=title,
        description=description,
        thumbnail_url=thumb_url,  # Updated from thumb_url to thumbnail_url in PTB v22
        input_message_content=InputTextMessageContent(
            message_text=message_text,
            disable_web_page_preview=disable_web_page_preview,
        ),
        reply_markup=reply_markup,
    )


def revert_buttons(buttons):
    """Convert button objects back to text format"""
    res = ""
    for btn in buttons:
        if btn.same_line:
            res += "\n[{}](buttonurl://{}:same)".format(btn.name, btn.url)
        else:
            res += "\n[{}](buttonurl://{})".format(btn.name, btn.url)

    return res


def build_keyboard_parser(bot, chat_id, buttons):
    """Build keyboard with special parsing for rules buttons"""
    keyb = []
    for btn in buttons:
        if btn.url == "{rules}":
            btn.url = "http://t.me/{}?start={}".format(bot.username, chat_id)
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def is_module_loaded(name):
    """Check if a module is loaded"""
    return name not in NO_LOAD


def convert_gif(input_file):
    """Function to convert mp4 to webm(vp9) - Updated for PTB v22"""
    
    vid = cv2.VideoCapture(input_file)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    
    # Release video capture object
    vid.release()

    # check height and width to scale
    if width > height:
        width = 512
        height = -1
    elif height > width:
        height = 512
        width = -1
    elif width == height:
        width = 512
        height = 512

    converted_name = "kangsticker.webm"

    try:
        (
            ffmpeg.input(input_file)
            .filter("fps", fps=30, round="up")
            .filter("scale", width=width, height=height)
            .trim(start="00:00:00", end="00:00:03", duration="3")
            .output(
                converted_name,
                vcodec="libvpx-vp9",
                **{
                    "crf": "30"
                }
            )
            .overwrite_output()
            .run(quiet=True)  # Added quiet=True to suppress ffmpeg output
        )
    except ffmpeg.Error as e:
        print(f"Error converting video: {e}")
        return None

    return converted_name


# ────────────────────────────────
# Additional utility functions for PTB v22
# ────────────────────────────────

async def send_to_list_safe(
    bot: Bot, send_to: list, message: str, 
    parse_mode: ParseMode = None, **kwargs
) -> int:
    """
    Send message to list with better error handling and success counting
    Returns number of successful sends
    """
    success_count = 0
    for user_id in set(send_to):
        try:
            await bot.send_message(
                user_id, message, parse_mode=parse_mode, **kwargs
            )
            success_count += 1
        except TelegramError as e:
            print(f"Failed to send message to {user_id}: {e}")
            continue
    
    return success_count


def create_deep_link(bot_username: str, payload: str) -> str:
    """Create a deep link for the bot"""
    return f"https://t.me/{bot_username}?start={payload}"


def escape_markdown_v2(text: str) -> str:
    """Escape markdown v2 characters"""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text


def mention_html(user_id: int, name: str) -> str:
    """Create HTML mention"""
    return f'<a href="tg://user?id={user_id}">{name}</a>'


def mention_markdown(user_id: int, name: str) -> str:
    """Create Markdown mention"""
    return f'[{name}](tg://user?id={user_id})'


# ────────────────────────────────
# Async wrapper for synchronous functions
# ────────────────────────────────

async def async_convert_gif(input_file):
    """Async wrapper for convert_gif function"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, convert_gif, input_file)
    
