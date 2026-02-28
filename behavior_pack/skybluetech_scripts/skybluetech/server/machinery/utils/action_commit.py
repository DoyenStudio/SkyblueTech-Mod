# coding=utf-8

from skybluetech_scripts.tooldelta.api.server import GetPos, GetPlayerDimensionId
from ..basic import BaseMachine, GUIControl
from ..pool import GetMachineStrict


def SafeGetMachine(x, y, z, player_id):
    # type: (int, int, int, str) -> BaseMachine | None
    if not all(abs(a - b) < 10 for a, b in zip(GetPos(player_id), (x, y, z))):
        return None
    m = GetMachineStrict(GetPlayerDimensionId(player_id), x, y, z)
    if not isinstance(m, GUIControl) or not m.sync.PlayerInSync(player_id):
        return None
    return m
