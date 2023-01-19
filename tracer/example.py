import asyncio
import contextvars
import typing
from logging import config, getLogger

from tracer import log

# step 1: add pythonjsonlogger formatter
config.dictConfig(
    {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(levelname)s %(message)s',  # noqa: WPS323
            },
        },
        'handlers': {
            'info': {
                'level': 'INFO',
                'formatter': 'json',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            '': {'level': 'INFO', 'handlers': ('info',)},
        },
    },
)

# step 2: setup tracer with the proper context
context: contextvars.ContextVar[
    typing.Mapping[str, typing.Any]
] = contextvars.ContextVar('trace')
tracer = log.Tracer(getLogger(__name__), context)


async def func_one() -> None:
    token = context.set({'requestID': 1})

    tracer.info('func_one start')

    await asyncio.sleep(2)

    context.reset(token)
    tracer.info('func_one finish')


async def func_two() -> None:
    tracer.info('func_two start')

    await asyncio.sleep(2)

    context.set({'requestID': 2})
    tracer.info('func_two finish')


async def func_context() -> None:
    context.set({'requestID': 3})


async def main() -> None:
    await func_context()
    await asyncio.gather(func_one(), func_two())


if __name__ == '__main__':
    asyncio.run(main())
