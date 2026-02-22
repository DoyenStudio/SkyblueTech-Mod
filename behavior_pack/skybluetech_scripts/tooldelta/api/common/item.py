# coding=utf-8
from ...internal import InClientEnv
from ..client import GetItemTags as ClientGetItemTags
from ..server import GetItemTags as ServerGetItemTags


def GetItemTags(item_id, aux_value):
    # type: (str, int) -> set[str]
    if InClientEnv():
        return ClientGetItemTags(item_id, aux_value)
    else:
        return ServerGetItemTags(item_id, aux_value)
