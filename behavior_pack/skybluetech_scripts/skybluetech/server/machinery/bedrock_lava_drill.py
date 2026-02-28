# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.api.server.block import GetBlockName
from .basic import BaseMachine, FluidContainer, MultiBlockStructure, RegisterMachine
from .basic.multi_block_structure import StructureBlockPalette

K_POSOK = "pos_ok"


@RegisterMachine
class BedrockLavaDrill(FluidContainer, MultiBlockStructure):
    block_name = "skybluetech:bedrock_lava_drill"
    store_rf_max = 16000
    structure_palette = StructureBlockPalette()

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        FluidContainer.__init__(self, dim, x, y, z, block_entity_data)

    def OnLoad(self):
        BaseMachine.OnLoad(self)
        self.pos_ok = self.bdata[K_POSOK] or False

    def OnUnload(self):
        MultiBlockStructure.OnUnload(self)
        BaseMachine.OnUnload(self)

    def OnPlaced(self, _):
        self.pos_ok = self.detectBlock()

    def Dump(self):
        # type: () -> None
        BaseMachine.Dump(self)
        FluidContainer.Dump(self)
        self.bdata[K_POSOK] = self.pos_ok

    def OnTicking(self):
        while self.IsActive():
            pass

    def detectBlock(self):
        if self.y > -50:
            return False
        down_block = GetBlockName(self.dim, (self.x, self.y, self.z))
        if down_block != "minecraft:bedrock":
            return False
        return True



