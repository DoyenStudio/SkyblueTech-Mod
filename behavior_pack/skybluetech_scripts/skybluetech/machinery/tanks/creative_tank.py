# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from ..basic import RegisterMachine
from .base_tank import BasicTank, FluidContainer, RegisterTank

INFINITY = float("inf")


@RegisterMachine
@RegisterTank
class CreativeTank(BasicTank):
    block_name = "skybluetech:creative_tank"
    max_fluid_volume = INFINITY

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BasicTank.__init__(self, dim, x, y, z, block_entity_data)

    def AddFluid(self, fluid_id, fluid_volume, depth=0):
        # type: (str, float, int) -> tuple[bool, float]
        if self.fluid_id is None:
            return True, 0
        else:
            return False, fluid_volume

    def ifPlayerInteractWithBucket(self, player_id, test=False):
        # type: (str, bool) -> bool
        res = FluidContainer.ifPlayerInteractWithBucket(self, player_id, test)
        if self.fluid_id is not None:
            self.fluid_volume = INFINITY
        self.OnSync()
        return res

