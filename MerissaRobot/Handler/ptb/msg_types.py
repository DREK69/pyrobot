from enum import IntEnum, unique
from typing import Optional, Tuple, List, Any

from telegram import Message

from MerissaRobot.Handler.ptb.string_handling import button_markdown_parser


@unique
class Types(IntEnum):
    TEXT = 0
    BUTTON_TEXT = 1
    STICKER = 2
    DOCUMENT = 3
    PHOTO = 4
    AUDIO = 5
    VOICE = 6
    VIDEO = 7
    VIDEO_NOTE = 8  # Added missing VIDEO_NOTE type


def get_note_type(msg: Message) -> Tuple[Optional[str], str, Optional[Types], Optional[str], List]:
    """
    Extract note information from a message.
    
    :param msg: Telegram message object
    :return: Tuple of (note_name, text, data_type, content, buttons)
    """
    data_type = None
    content = None
    text = ""
    raw_text = msg.text or msg.caption
    
    if not raw_text:
        return None, "", None, None, []
    
    args = raw_text.split(None, 2)  # use python's maxsplit to separate cmd and args
    
    if len(args) < 2:
        return None, "", None, None, []
    
    note_name = args[1]
    buttons = []
    
    # determine what the contents of the filter are - text, image, sticker, etc
    if len(args) >= 3:
        offset = len(args[2]) - len(raw_text)  # set correct offset relative to command + notename
        
        # In PTB v22, parse_entities returns a tuple of MessageEntity objects
        entities_dict = {}
        if msg.entities:
            # Convert entities to the format expected by button_markdown_parser
            for entity in msg.entities:
                entity_text = raw_text[entity.offset:entity.offset + entity.length]
                entities_dict[entity] = entity_text
        elif msg.caption_entities:
            for entity in msg.caption_entities:
                entity_text = raw_text[entity.offset:entity.offset + entity.length]
                entities_dict[entity] = entity_text
        
        text, buttons = button_markdown_parser(
            args[2],
            entities=entities_dict,
            offset=offset,
        )
        
        if buttons:
            data_type = Types.BUTTON_TEXT
        else:
            data_type = Types.TEXT

    elif msg.reply_to_message:
        reply_msg = msg.reply_to_message
        entities_dict = {}
        msgtext = reply_msg.text or reply_msg.caption or ""
        
        # Handle entities from reply message
        if reply_msg.entities:
            for entity in reply_msg.entities:
                entity_text = msgtext[entity.offset:entity.offset + entity.length]
                entities_dict[entity] = entity_text
        elif reply_msg.caption_entities:
            for entity in reply_msg.caption_entities:
                entity_text = msgtext[entity.offset:entity.offset + entity.length]
                entities_dict[entity] = entity_text
        
        if len(args) >= 2 and reply_msg.text:  # not caption, text
            text, buttons = button_markdown_parser(msgtext, entities=entities_dict)
            if buttons:
                data_type = Types.BUTTON_TEXT
            else:
                data_type = Types.TEXT

        elif reply_msg.sticker:
            content = reply_msg.sticker.file_id
            data_type = Types.STICKER

        elif reply_msg.document:
            content = reply_msg.document.file_id
            text, buttons = button_markdown_parser(msgtext, entities=entities_dict)
            data_type = Types.DOCUMENT

        elif reply_msg.photo:
            content = reply_msg.photo[-1].file_id  # last elem = best quality
            text, buttons = button_markdown_parser(msgtext, entities=entities_dict)
            data_type = Types.PHOTO

        elif reply_msg.audio:
            content = reply_msg.audio.file_id
            text, buttons = button_markdown_parser(msgtext, entities=entities_dict)
            data_type = Types.AUDIO

        elif reply_msg.voice:
            content = reply_msg.voice.file_id
            text, buttons = button_markdown_parser(msgtext, entities=entities_dict)
            data_type = Types.VOICE

        elif reply_msg.video:
            content = reply_msg.video.file_id
            text, buttons = button_markdown_parser(msgtext, entities=entities_dict)
            data_type = Types.VIDEO

        elif reply_msg.video_note:
            content = reply_msg.video_note.file_id
            text, buttons = button_markdown_parser(msgtext, entities=entities_dict)
            data_type = Types.VIDEO_NOTE

    return note_name, text, data_type, content, buttons


def get_welcome_type(msg: Message) -> Tuple[Optional[str], Optional[Types], Optional[str], List]:
    """
    Extract welcome message information from a message.
    
    :param msg: Telegram message object
    :return: Tuple of (text, data_type, content, buttons)
    """
    data_type = None
    content = None
    text = ""
    buttons = []

    try:
        if msg.reply_to_message:
            if msg.reply_to_message.text:
                args = msg.reply_to_message.text
            else:
                args = msg.reply_to_message.caption or ""
        else:
            split_text = msg.text.split(None, 1) if msg.text else []
            args = split_text[1] if len(split_text) > 1 else ""
    except AttributeError:
        args = ""

    if msg.reply_to_message and msg.reply_to_message.sticker:
        content = msg.reply_to_message.sticker.file_id
        text = None
        data_type = Types.STICKER

    elif msg.reply_to_message and msg.reply_to_message.document:
        content = msg.reply_to_message.document.file_id
        text = msg.reply_to_message.caption
        data_type = Types.DOCUMENT

    elif msg.reply_to_message and msg.reply_to_message.photo:
        content = msg.reply_to_message.photo[-1].file_id  # last elem = best quality
        text = msg.reply_to_message.caption
        data_type = Types.PHOTO

    elif msg.reply_to_message and msg.reply_to_message.audio:
        content = msg.reply_to_message.audio.file_id
        text = msg.reply_to_message.caption
        data_type = Types.AUDIO

    elif msg.reply_to_message and msg.reply_to_message.voice:
        content = msg.reply_to_message.voice.file_id
        text = msg.reply_to_message.caption
        data_type = Types.VOICE

    elif msg.reply_to_message and msg.reply_to_message.video:
        content = msg.reply_to_message.video.file_id
        text = msg.reply_to_message.caption
        data_type = Types.VIDEO

    elif msg.reply_to_message and msg.reply_to_message.video_note:
        content = msg.reply_to_message.video_note.file_id
        text = None
        data_type = Types.VIDEO_NOTE

    # determine what the contents of the filter are - text, image, sticker, etc
    if args:
        entities_dict = {}
        
        if msg.reply_to_message:
            argumen = msg.reply_to_message.caption if msg.reply_to_message.caption else ""
            offset = 0  # offset is no need since target was in reply
            
            # Handle reply message entities
            if msg.reply_to_message.entities:
                for entity in msg.reply_to_message.entities:
                    entity_text = argumen[entity.offset:entity.offset + entity.length]
                    entities_dict[entity] = entity_text
            elif msg.reply_to_message.caption_entities:
                for entity in msg.reply_to_message.caption_entities:
                    entity_text = argumen[entity.offset:entity.offset + entity.length]
                    entities_dict[entity] = entity_text
        else:
            argumen = args
            offset = len(argumen) - len(msg.text) if msg.text else 0  # set correct offset relative to command + notename
            
            # Handle message entities
            if msg.entities:
                for entity in msg.entities:
                    entity_text = msg.text[entity.offset:entity.offset + entity.length] if msg.text else ""
                    entities_dict[entity] = entity_text
            elif msg.caption_entities:
                for entity in msg.caption_entities:
                    caption_text = msg.caption or ""
                    entity_text = caption_text[entity.offset:entity.offset + entity.length]
                    entities_dict[entity] = entity_text
        
        text, buttons = button_markdown_parser(
            argumen,
            entities=entities_dict,
            offset=offset,
        )

    if not data_type:
        if text and buttons:
            data_type = Types.BUTTON_TEXT
        elif text:
            data_type = Types.TEXT

    return text, data_type, content, buttons


def get_filter_type(msg: Message) -> Tuple[Optional[str], Optional[Types], Optional[str]]:
    """
    Extract filter information from a message.
    
    :param msg: Telegram message object
    :return: Tuple of (text, data_type, content)
    """
    if not msg.reply_to_message and msg.text and len(msg.text.split()) >= 3:
        content = None
        text = msg.text.split(None, 2)[2]
        data_type = Types.TEXT

    elif (
        msg.reply_to_message
        and msg.reply_to_message.text
        and msg.text
        and len(msg.text.split()) >= 2
    ):
        content = None
        text = msg.reply_to_message.text
        data_type = Types.TEXT

    elif msg.reply_to_message and msg.reply_to_message.sticker:
        content = msg.reply_to_message.sticker.file_id
        text = None
        data_type = Types.STICKER

    elif msg.reply_to_message and msg.reply_to_message.document:
        content = msg.reply_to_message.document.file_id
        text = msg.reply_to_message.caption
        data_type = Types.DOCUMENT

    elif msg.reply_to_message and msg.reply_to_message.photo:
        content = msg.reply_to_message.photo[-1].file_id  # last elem = best quality
        text = msg.reply_to_message.caption
        data_type = Types.PHOTO

    elif msg.reply_to_message and msg.reply_to_message.audio:
        content = msg.reply_to_message.audio.file_id
        text = msg.reply_to_message.caption
        data_type = Types.AUDIO

    elif msg.reply_to_message and msg.reply_to_message.voice:
        content = msg.reply_to_message.voice.file_id
        text = msg.reply_to_message.caption
        data_type = Types.VOICE

    elif msg.reply_to_message and msg.reply_to_message.video:
        content = msg.reply_to_message.video.file_id
        text = msg.reply_to_message.caption
        data_type = Types.VIDEO

    elif msg.reply_to_message and msg.reply_to_message.video_note:
        content = msg.reply_to_message.video_note.file_id
        text = None
        data_type = Types.VIDEO_NOTE

    else:
        text = None
        data_type = None
        content = None

    return text, data_type, content


# Helper functions for better type safety and error handling

def extract_entities_dict(msg: Message) -> dict:
    """
    Extract message entities as a dictionary for compatibility with button_markdown_parser.
    
    :param msg: Telegram message object
    :return: Dictionary mapping MessageEntity to entity text
    """
    entities_dict = {}
    text_content = msg.text or msg.caption or ""
    
    entities = msg.entities or msg.caption_entities
    if entities:
        for entity in entities:
            try:
                entity_text = text_content[entity.offset:entity.offset + entity.length]
                entities_dict[entity] = entity_text
            except IndexError:
                # Skip malformed entities
                continue
    
    return entities_dict


def safe_get_file_id(media_object) -> Optional[str]:
    """
    Safely get file_id from media objects.
    
    :param media_object: Media object from telegram message
    :return: File ID or None if not available
    """
    try:
        return media_object.file_id if media_object else None
    except AttributeError:
        return None


def get_message_content_type(msg: Message) -> Optional[Types]:
    """
    Determine the content type of a message.
    
    :param msg: Telegram message object
    :return: Types enum value or None
    """
    if msg.sticker:
        return Types.STICKER
    elif msg.document:
        return Types.DOCUMENT
    elif msg.photo:
        return Types.PHOTO
    elif msg.audio:
        return Types.AUDIO
    elif msg.voice:
        return Types.VOICE
    elif msg.video:
        return Types.VIDEO
    elif msg.video_note:
        return Types.VIDEO_NOTE
    elif msg.text:
        return Types.TEXT
    else:
        return None
