# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF


from ..basic import BaseMachine, GUIControl
from ..core.pool import GetLoadedMachine


def SafeGetLoadedMachine(x, y, z, player_id):
    # type: (int, int, int, str) -> BaseMachine | None
    if not all(abs(a - b) < 10 for a, b in zip(CF.CreatePos(player_id).GetPos(), (x, y, z))):
        return None
    m = GetLoadedMachine(CF.CreateDimension(player_id).GetEntityDimensionId(), x, y, z)
    if not isinstance(m, GUIControl) or not m.ui_sync.PlayerInSync(player_id):
        return None
    return m
