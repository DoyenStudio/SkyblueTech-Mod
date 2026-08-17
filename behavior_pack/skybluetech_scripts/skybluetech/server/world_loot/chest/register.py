# coding=utf-8
import random
from mod.server.extraServerApi import GetLevelId
from skybluetech_scripts.tooldelta.api.server import GetExtraData, SetExtraData
from skybluetech_scripts.tooldelta.events.server import (
    OnContainerFillLoottableServerEvent,
)

if 0>1:
    import typing  # noqa: F401
    from skybluetech_scripts.tooldelta.define import Item  # noqa: F401


_handlers = {}


class PlayerLootHistoryManager(object):
    _instance = None
    _data_key_prefix = "skybluetech:world_loot_chest_player_history"

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _make_data_key(
        self,
        player_id,  # type: str
    ):
        # type: (...) -> str
        return self._data_key_prefix + "#" + str(player_id)

    def _get_history(
        self,
        player_id,  # type: str
    ):
        # type: (...) -> dict
        data = GetExtraData(GetLevelId(), self._make_data_key(player_id), {})
        if not isinstance(data, dict):
            return {}
        return data

    def _make_key(
        self,
        item_id,  # type: str
        extra_id=None,
    ):
        # type: (...) -> str
        if extra_id is None:
            extra_id = ""
        return str(item_id) + "#" + str(extra_id)

    def has(
        self,
        player_id,  # type: str
        item_id,  # type: str
        extra_id=None,
    ):
        # type: (...) -> bool
        history = self._get_history(player_id)
        return bool(history.get(self._make_key(item_id, extra_id), False))

    def record(
        self,
        player_id,  # type: str
        item_id,  # type: str
        extra_id=None,
    ):
        # type: (...) -> None
        history = self._get_history(player_id)
        history[self._make_key(item_id, extra_id)] = True
        SetExtraData(
            GetLevelId(),
            self._make_data_key(player_id),
            history,
            auto_save=True,
        )


def Register(
    loottable,  # type: str
    handler,  # type: typing.Callable[[str], list[Item]]
):
    _handlers[loottable] = handler


def LootHandler(
    loottable,  # type: str
):
    def decorator(
        func,  # type: typing.Callable[[str], list[Item]]
    ):
        Register(loottable, func)
        return func

    return decorator


def DoRand(value):
    # type: (float) -> bool
    return random.random() < value


@OnContainerFillLoottableServerEvent.Listen()
def onContainerLoot(
    event,  # type: OnContainerFillLoottableServerEvent
):
    hdl = _handlers.get(event.loottable)
    if hdl:
        itemList = hdl(event.playerId)
        if itemList:
            event.itemList.extend([item.marshal() for item in itemList])
            event.SetDirty()
