from typing import List, Optional, Union
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    InlineQueryHandler,
    MessageHandler,
    filters,
)

from MerissaRobot import LOGGER, application  # use application, not dispatcher
from MerissaRobot.Modules.disable import (
    DisableAbleCommandHandler,
    DisableAbleMessageHandler,
)


class MerissaHandler:
    def __init__(self, app: Application):
        self._application = app

    def command(
        self,
        command: Union[str, List[str]],
        filters: Optional[filters.BaseFilter] = None,
        admin_ok: bool = False,
        can_disable: bool = True,
        group: Optional[int] = 40,
    ):
        def _command(func):
            handler_cls = DisableAbleCommandHandler if can_disable else CommandHandler
            self._application.add_handler(
                handler_cls(command, func, filters=filters),
                group=group,
            )
            LOGGER.debug(
                f"[MERISSACMD] Loaded handler {command} for function {func.__name__} in group {group}"
            )
            return func

        return _command

    def message(
        self,
        pattern: Optional[filters.BaseFilter] = None,
        can_disable: bool = True,
        group: Optional[int] = 60,
        friendly=None,
    ):
        def _message(func):
            handler_cls = DisableAbleMessageHandler if can_disable else MessageHandler
            
            try:
                # Try with group parameter first
                if can_disable:
                    self._application.add_handler(
                        handler_cls(pattern, func, friendly=friendly),
                        group=group,
                    )
                else:
                    self._application.add_handler(
                        MessageHandler(pattern, func),
                        group=group,
                    )
                LOGGER.debug(
                    f"[MERISSAMSG] Loaded filter pattern {pattern} for function {func.__name__} in group {group}"
                )
            except TypeError:
                # Fallback without group parameter
                if can_disable:
                    self._application.add_handler(
                        handler_cls(pattern, func, friendly=friendly)
                    )
                else:
                    self._application.add_handler(
                        MessageHandler(pattern, func)
                    )
                LOGGER.debug(
                    f"[MERISSAMSG] Loaded filter pattern {pattern} for function {func.__name__}"
                )

            return func

        return _message

    def callbackquery(self, pattern: str = None):
        def _callbackquery(func):
            self._application.add_handler(
                CallbackQueryHandler(pattern=pattern, callback=func)
            )
            LOGGER.debug(
                f"[MERISSACALLBACK] Loaded callbackquery handler with pattern {pattern} for function {func.__name__}"
            )
            return func

        return _callbackquery

    def inlinequery(
        self,
        pattern: Optional[str] = None,
        chat_types: List[str] = None,
    ):
        def _inlinequery(func):
            self._application.add_handler(
                InlineQueryHandler(pattern=pattern, callback=func, chat_types=chat_types)
            )
            LOGGER.debug(
                f"[MERISSAINLINE] Loaded inlinequery handler with pattern {pattern} for function {func.__name__} | CHAT TYPES: {chat_types}"
            )
            return func

        return _inlinequery


# Create handler instances
merissacmd = MerissaHandler(application).command
merissamsg = MerissaHandler(application).message
merissacallback = MerissaHandler(application).callbackquery
merissainline = MerissaHandler(application).inlinequery
