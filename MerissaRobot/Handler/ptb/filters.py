from telegram import Message
from telegram.ext import filters

from MerissaRobot import DEMONS, DEV_USERS, DRAGONS


class CustomFilters:
    """Custom filters for MerissaRobot - PTB v22 Compatible"""
    
    @staticmethod
    def support_filter(message: Message) -> bool:
        """Filter for support users (DEMONS)"""
        return bool(message.from_user and message.from_user.id in DEMONS)

    @staticmethod
    def sudo_filter(message: Message) -> bool:
        """Filter for sudo users (DRAGONS)"""
        return bool(message.from_user and message.from_user.id in DRAGONS)

    @staticmethod
    def dev_filter(message: Message) -> bool:
        """Filter for developer users (DEV_USERS)"""
        return bool(message.from_user and message.from_user.id in DEV_USERS)

    @staticmethod
    def mime_type(mimetype: str):
        """Filter for specific document MIME types"""
        def _filter(message: Message) -> bool:
            return bool(
                message.document and message.document.mime_type == mimetype
            )
        return _filter

    @staticmethod
    def has_text(message: Message) -> bool:
        """Filter for messages that have some form of content"""
        return bool(
            message.text
            or message.sticker
            or message.photo
            or message.document
            or message.video
        )


# Create filter instances using PTB v22 syntax
class MerissaFilters:
    """PTB v22 compatible filter instances"""
    
    # User permission filters
    support_filter = filters.User(user_id=list(DEMONS))
    sudo_filter = filters.User(user_id=list(DRAGONS)) 
    dev_filter = filters.User(user_id=list(DEV_USERS))
    
    # Combined permission filters
    sudo_plus = filters.User(user_id=list(DRAGONS) + list(DEV_USERS))
    support_plus = filters.User(user_id=list(DEMONS) + list(DRAGONS) + list(DEV_USERS))
    
    # Content filters
    has_text = filters.TEXT | filters.PHOTO | filters.Document.ALL | filters.VIDEO | filters.Sticker.ALL
    
    # Custom mime type filter factory
    @staticmethod
    def mime_type(mimetype: str):
        """Create a filter for specific MIME type"""
        return filters.Document.MimeType(mimetype)
    
    # Media filters
    image_filter = filters.PHOTO
    document_filter = filters.Document.ALL
    video_filter = filters.VIDEO
    audio_filter = filters.AUDIO
    sticker_filter = filters.Sticker.ALL
    animation_filter = filters.ANIMATION
    voice_filter = filters.VOICE
    video_note_filter = filters.VIDEO_NOTE
    
    # Chat type filters
    private_filter = filters.ChatType.PRIVATE
    group_filter = filters.ChatType.GROUPS
    supergroup_filter = filters.ChatType.SUPERGROUP
    channel_filter = filters.ChatType.CHANNEL
    
    # Message type filters
    command_filter = filters.COMMAND
    reply_filter = filters.REPLY
    forwarded_filter = filters.FORWARDED
    edited_filter = filters.UpdateType.EDITED_MESSAGE
    
    # Status update filters
    new_chat_members = filters.StatusUpdate.NEW_CHAT_MEMBERS
    left_chat_member = filters.StatusUpdate.LEFT_CHAT_MEMBER
    new_chat_title = filters.StatusUpdate.NEW_CHAT_TITLE
    new_chat_photo = filters.StatusUpdate.NEW_CHAT_PHOTO
    delete_chat_photo = filters.StatusUpdate.DELETE_CHAT_PHOTO
    chat_migration = filters.StatusUpdate.MIGRATE
    pinned_message = filters.StatusUpdate.PINNED_MESSAGE
    
    # Admin only filter (for groups)
    admin_filter = filters.ChatType.GROUPS & filters.User.ADMIN


# Backward compatibility with old CustomFilters class
support_filter = CustomFilters.support_filter
sudo_filter = CustomFilters.sudo_filter  
dev_filter = CustomFilters.dev_filter
mime_type = CustomFilters.mime_type
has_text = CustomFilters.has_text
