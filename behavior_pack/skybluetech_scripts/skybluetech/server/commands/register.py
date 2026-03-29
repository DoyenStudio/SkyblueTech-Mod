# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import GetBlockName
from skybluetech_scripts.tooldelta.events.server import CustomCommandTriggerServerEvent
from .utils import generate_simple_arg_mapping

if 0:
    import typing

    T = typing.TypeVar(
        "T", bound=typing.Callable[["CustomCommandTriggerServerEvent"], None]
    )

cbs = {}  # type: dict[str, typing.Callable[[CustomCommandTriggerServerEvent], None]]


@CustomCommandTriggerServerEvent.Listen()
def onCustomCommandTrigger(event):
    # type: (CustomCommandTriggerServerEvent) -> None
    cb = cbs.get(event.command)
    if cb:
        cb(event)


def RegisterCommand(
    command,  # type: str
):
    def decorator(func):
        # type: (T) -> T
        cbs[command] = func
        return func

    return decorator
