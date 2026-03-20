# coding=utf-8
from ...internal import InClientEnv


def GetItemTags(item_id, aux_value):
    # type: (str, int) -> set[str]
    if InClientEnv():
        from ..client import GetItemTags as ClientGetItemTags

        return ClientGetItemTags(item_id, aux_value)
    else:
        from ..server import GetItemTags as ServerGetItemTags

        return ServerGetItemTags(item_id, aux_value)
