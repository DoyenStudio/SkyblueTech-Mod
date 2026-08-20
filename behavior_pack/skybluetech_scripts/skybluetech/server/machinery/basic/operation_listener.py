# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import GetPlayerDimensionId
from skybluetech_scripts.tooldelta.events.event_bus import GetMCServerEventBus
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from ....common.events.machinery.basic import MachineryOperationC2S
from ..pool import GetMachineStrict
from .multi_block_structure import MultiBlockStructure

if 0 > 1:
    import typing

    EventT = typing.TypeVar("EventT", bound=MachineryOperationC2S)


class OperationListener(object):
    """
    表示一个需要接受玩家端设置的机器。

    机器类继承此基类后, 可使用 @Machinery.ForOperation(MachineryOperationC2S)
    来监听玩家端对机器的操作, 做进一步处理。
    """
    __metaclass__ = SuperExecutorMeta

    def __init__(self, dim, x, y, z, block_entity_data):
        pass

    @classmethod
    def ForOperation(
        cls,
        event,  # type: type[EventT]
        priority=0,
    ):
        def decorator(
            fun,  # type: typing.Callable[[EventT, typing.Self], None]
        ):
            def get_listener():
                def listener(event):
                    # type: (EventT) -> None
                    machine = GetMachineStrict(
                        GetPlayerDimensionId(event.player_id), event.x, event.y, event.z
                    )
                    if not isinstance(machine, cls):
                        return
                    if isinstance(machine, MultiBlockStructure) and not machine.StructureFinished():
                        return
                    fun(event, machine)
                return listener

            GetMCServerEventBus().AddEventListener(event, get_listener(), priority, static=True)

        return decorator


# def _safe_get_machine(x, y, z, player_id):
#     # type: (int, int, int, str) -> BaseMachine | None
#     if not all(abs(a - b) < 10 for a, b in zip(GetPos(player_id), (x, y, z))):
#         return None
#     m = GetMachineStrict(GetPlayerDimensionId(player_id), x, y, z)
#     if not isinstance(m, GUIControl) or not m.ui_sync.PlayerInSync(player_id):
#         return None
#     return m
