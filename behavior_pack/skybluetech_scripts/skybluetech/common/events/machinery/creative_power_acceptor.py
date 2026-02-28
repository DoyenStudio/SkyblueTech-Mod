# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent
from skybluetech_scripts.tooldelta.internal import ClientComp, ClientLevelId
from skybluetech_scripts.tooldelta.general import ClientInitCallback, ServerInitCallback
from skybluetech_scripts.tooldelta.api.common import AsTimerFunc
from skybluetech_scripts.tooldelta.events.client.block import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)


class CreativePowerAcceptorPowerUpdateRequest(CustomC2SEvent):
    name = "st:CPAPUpdateRequest"

    def __init__(self, dim, x, y, z, player_id=""):
        # type: (int, int, int, int, str) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.player_id = player_id

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            dim=data["dim"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            player_id=data["__id__"],
        )


class CreativePowerAcceptorPowerUpdate(CustomS2CEvent):
    name = "st:CPAPUpdate"

    def __init__(self, datas=None):
        # type: (list[list[int]] | None) -> None
        self.datas = datas or []

    def marshal(self):
        return self.datas

    @classmethod
    def unmarshal(
        cls,
        data,  # type: list[list[int]]
    ):
        return cls(data)
