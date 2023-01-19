"""
Module `log` contains the logger adapter for add context information on each call.

see more: https://docs.python.org/3/library/logging.html#loggeradapter-objects
see more: https://docs.python.org/3/library/contextvars.html
"""

import contextvars
import datetime
import logging
import typing

# ---- typing
ContextT = contextvars.ContextVar[typing.Mapping[str, typing.Any]]
ExtraT = typing.Mapping[str, typing.Any]
KwargsT = typing.MutableMapping[str, typing.Any]
GT = typing.TypeVar('GT')

if typing.TYPE_CHECKING:
    LoggerAdapter = logging.LoggerAdapter[logging.Logger]
else:
    LoggerAdapter = logging.LoggerAdapter


class Tracer(LoggerAdapter):
    def __init__(
        self,
        logger: logging.Logger,
        context_var: ContextT | None = None,
        extra: ExtraT | None = None,
    ):
        """
        Adapter for any `logger` to be compliant with context information.

        :param logger: any logger
        :param context_var: context variable for share contexts, must be key-value
        :param extra: any optional additional information for logging
        """
        super().__init__(logger, extra=extra)
        self.context_var = context_var or contextvars.ContextVar(logger.name)

    def process(self, msg: GT, kwargs: KwargsT) -> tuple[GT, KwargsT]:
        """:raises LookupError: when empty context are given"""
        extra = kwargs.setdefault('extra', {})
        extra.update(self.extra or {})
        extra.update(self.context_var.get())
        extra['timestamp'] = datetime.datetime.utcnow()
        return msg, kwargs
