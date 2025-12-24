# coding=utf-8

from skybluetech_scripts.tooldelta.api.server import GetPos, GetPlayerDimensionId
from ..machinery.basic import BaseMachine
from ..machinery.pool import GetMachineStrict, cached_machines


def SafeGetMachine(x, y, z, player_id):
    # type: (int, int, int, str) -> BaseMachine | None
    if not all(
        abs(a - b) < 10
        for a, b in zip(GetPos(player_id), (x, y, z))
    ):
        return None
    return GetMachineStrict(GetPlayerDimensionId(player_id), x, y, z)
    