# coding=utf-8

from skybluetech_scripts.tooldelta.plugins.ui_sync import S2CSync, S2C_SERVER, S2C_CLIENT, notifySyncToSingleClient
from skybluetech_scripts.tooldelta.no_runtime_typing import TYPE_CHECKING

# TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Self
    from ...machinery.basic.base_machine import BaseMachine
    from ...machinery.basic.multi_fluid_container import MultiFluidContainer
# TYPE_CHECKING END


class MachineUISync(S2CSync):
    @classmethod
    def NewServer(cls, m):
        # type: (BaseMachine) -> Self
        return cls(S2C_SERVER, "%s_%d_%d_%d_%d" % (cls.__name__, m.dim, m.x, m.y, m.z))

    @classmethod
    def NewClient(cls, dim, x, y, z):
        # type: (int, int, int, int) -> Self
        return cls(S2C_CLIENT, "%s_%d_%d_%d_%d" % (cls.__name__, dim, x, y, z))

    def FastSync(self, player_id):
        # type: (str) -> None
        notifySyncToSingleClient(player_id, {self.sync_id})



class FluidSlotSync:
    def __init__(self, fluid_id, fluid_volume, max_volume):
        # type: (str | None, float, float) -> None
        self.fluid_id = fluid_id
        self.volume = fluid_volume
        self.max_volume = max_volume

    @staticmethod
    def ListFromMachine(m):
        # type: (MultiFluidContainer) -> list[FluidSlotSync]
        return [FluidSlotSync(fluid.fluid_id, fluid.volume, fluid.max_volume) for fluid in m.fluids]

    @staticmethod
    def MarshalList(ls):
        # type: (list[FluidSlotSync]) -> list[list]
        return [[fluid.fluid_id, fluid.volume, fluid.max_volume] for fluid in ls]

    @staticmethod
    def UnmarshalList(orig_list, data):
        # type: (list[FluidSlotSync], list[list]) -> None
        orig_list[:] = [FluidSlotSync(fid, fvol, mvol) for fid, fvol, mvol in data]
