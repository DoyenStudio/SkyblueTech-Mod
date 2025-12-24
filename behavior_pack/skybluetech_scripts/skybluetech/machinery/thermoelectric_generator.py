# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.events.server.block import (
    BlockNeighborChangedServerEvent,
    ServerPlaceBlockEntityEvent,
)
from skybluetech_scripts.tooldelta.api.server.block import GetBlockName
from ..machinery_def.thermoelectric_generator import COLD_BLOCKS, HOT_BLOCKS
from ..define.utils import NEIGHBOR_BLOCKS_ENUM
from ..ui_sync.machines.thermoelectric_generator import ThermoelectricGeneratorUISync
from ..ui.machines.thermoelectric_generator import ThermoelectricGeneratorUI
from .basic import BaseMachine, GUIControl, RegisterMachine


@RegisterMachine
class ThermoelectricGenerator(BaseMachine, GUIControl):
    block_name = "skybluetech:thermoelectric_generator"
    store_rf_max = 14400
    bound_ui = ThermoelectricGeneratorUI
    is_container = False
    energy_mode = (1, 1, 1, 1, 1, 1)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = ThermoelectricGeneratorUISync.NewServer().Activate()
        self.active = True

    def OnPlaced(self, event):
        # type: (ServerPlaceBlockEntityEvent) -> None
        BaseMachine.OnPlaced(self, event)

    def OnUnload(self):
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)
        self.sync.Deactivate()

    def OnTicking(self):
        update, _ = self.AddPower(self.power_output, True)
        if update:
            self.OnSync()
        else:
            self.active = False

    def OnTryActivate(self):
        # type: () -> None
        self.active = True

    # 温差发电机: 方块变化
    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        self.active = True
        BaseMachine.OnNeighborChanged(self, event)
        former_block = event.fromBlockName
        to_block = event.toBlockName
        self.cool_value -= COLD_BLOCKS.get(former_block, 0) - COLD_BLOCKS.get(to_block, 0)
        self.heat_value -= HOT_BLOCKS.get(former_block, 0) - HOT_BLOCKS.get(to_block, 0)
        self.update_power()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.heat_val = self.heat_value
        self.sync.cool_val = self.cool_value
        self.sync.rf_max = self.store_rf_max
        self.sync.power = self.power_output
        self.sync.MarkedAsChanged()

    def OnLoad(self):
        BaseMachine.OnLoad(self)
        data = self.bdata
        self.heat_value = data["heat_value"] or 0
        self.cool_value = data["cool_value"] or 0
        self.power_output = data["power_output"] or 0
        if data["heat_value"] is None:
            for offset_x, offset_y, offset_z in NEIGHBOR_BLOCKS_ENUM:
                block_name = GetBlockName(
                    self.dim,
                    (self.x + offset_x, self.y + offset_y, self.z + offset_z)
                )
                if block_name is None:
                    continue
                self.heat_value += HOT_BLOCKS.get(block_name, 0)
                self.cool_value += COLD_BLOCKS.get(block_name, 0)
            self.update_power()

    def Dump(self):
        BaseMachine.Dump(self)
        self.bdata["heat_value"] = self.heat_value
        self.bdata["cool_value"] = self.cool_value
        self.bdata["power_output"] = self.power_output
        self.OnSync()

    def update_power(self):
        if self.cool_value == 0 or self.heat_value == 0:
            self.power_output = 0
        else:
            self.power_output = (self.cool_value + self.heat_value) * 2
