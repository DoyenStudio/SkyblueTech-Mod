# coding=utf-8
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.api.server.block import GetBlockName
from ....common.define.id_enum.fluids import DEEPSLATE_LAVA
from ....common.machinery_def.bedrock_lava_drill import (
    STRUCTURE_PATTERN,
    STRUCTURE_PATTERN_MAPPING,
    STRUCTURE_REQUIRE_BLOCKS,
)
from ..basic import (
    BaseMachine,
    MultiBlockStructure,
    UpgradeControl,
    RegisterMachine,
)
from ..basic.multi_block_structure import GenerateSimpleStructureTemplate
from ..interfaces import FluidOutputInterface
from .lava_storage import pump_lava, pos_to_chunk

K_POSOK = "pos_ok"


@RegisterMachine
class BedrockLavaDrill(MultiBlockStructure, UpgradeControl):
    block_name = "skybluetech:bedrock_lava_drill"
    store_rf_max = 16000
    pump_speed = 200
    origin_process_ticks = 5
    running_power = 800
    structure_palette = GenerateSimpleStructureTemplate(
        STRUCTURE_PATTERN_MAPPING,
        STRUCTURE_PATTERN,
        require_blocks_count=STRUCTURE_REQUIRE_BLOCKS,
    )

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)

    def OnUnload(self):
        MultiBlockStructure.OnUnload(self)
        UpgradeControl.OnUnload(self)

    def OnPlaced(self, _):
        self.pos_ok = self.detect_block()

    def OnTicking(self):
        while self.IsActive():
            if self.ProcessOnce():
                self.pump_once()

    def detect_block(self):
        if self.y > -50:
            return False
        down_block = GetBlockName(self.dim, (self.x, self.y, self.z))
        if down_block != "minecraft:bedrock":
            return False
        return True

    def pump_once(self):
        fluid_output = self.get_fluid_output_io()
        space = int(fluid_output.max_fluid_volume - fluid_output.fluid_volume)
        cx, cy = pos_to_chunk(self.x, self.z)
        vol = pump_lava(cx, cy, min(space, self.pump_speed))
        fluid_output.AddFluid(DEEPSLATE_LAVA, vol)

    def get_fluid_output_io(self):
        return self.GetMachine(FluidOutputInterface)
