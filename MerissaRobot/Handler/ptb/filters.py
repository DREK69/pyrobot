from telegram import Message
from telegram.ext import filters

from MerissaRobot import DEMONS, DEV_USERS, DRAGONS

class CustomFilters:
    @staticmethod
    def support_filter(message: Message) -> bool:
        return bool(message.from_user and message.from_user.id in DEMONS)

    @staticmethod
    def sudo_filter(message: Message) -> bool:
        return bool(message.from_user and message.from_user.id in DRAGONS)

    @staticmethod
    def dev_filter(message: Message) -> bool:
        return bool(message.from_user and message.from_user.id in DEV_USERS)

    @staticmethod
    def mime_type(mimetype: str):
        def _filter(message: Message) -> bool:
            return bool(
                message.document and message.document.mime_type == mimetype
            )
        return _filter

    @staticmethod
    def has_text(message: Message) -> bool:
        return bool(
            message.text
            or message.sticker
            or message.photo
            or message.document
            or message.video
        )
