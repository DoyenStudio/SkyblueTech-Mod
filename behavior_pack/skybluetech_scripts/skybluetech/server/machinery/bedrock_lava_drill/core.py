# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server.block import GetBlockName
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.define import flags
from ....common.define.id_enum.machinery import (
    BEDROCK_LAVA_DRILL_CONTROLLER as MACHINE_ID,
)
from ....common.define.id_enum.fluids import DEEPSLATE_LAVA
from ....common.machinery_def.bedrock_lava_drill import (
    STRUCTURE_PATTERN,
    STRUCTURE_PATTERN_MAPPING,
    STRUCTURE_REQUIRE_BLOCKS,
    IO_FLUID1,
    IO_ENERGY,
    DRILL_POWER,
    PUMP_POWER,
)
from ....common.ui_sync.machinery.bedrock_lava_drill import BedrockLavaDrillUISync
from ..basic import (
    GUIControl,
    MultiBlockStructure,
    UpgradeControl,
    RegisterMachine,
)
from ..basic.multi_block_structure import GenerateSimpleStructureTemplate
from ..interfaces import EnergyInputInterface, FluidOutputInterface
from .lava_storage import (
    pump_deepslate_lava,
    get_chunk_drill_time,
    get_available_lava_storage,
)

K_POS_OK = "st:pos_ok"
K_DRILL_TIMES = "st:drill_times"
K_DRILL_PROGRESS = "st:drill_progress"
K_VOLUME_LEFT = "st:volume_left"
K_TOTAL_PUMPED_VOLUME = "st:total_pumped_vol"
K_READY = "st:ready"

EnergyInputInterface.AddExtraMachineId(IO_ENERGY)
FluidOutputInterface.AddExtraMachineId(IO_FLUID1)


@RegisterMachine
class BedrockLavaDrill(GUIControl, MultiBlockStructure, UpgradeControl):
    block_name = MACHINE_ID
    store_rf_max = 16000
    pump_speed = 400
    origin_process_ticks = 10
    running_power = DRILL_POWER
    structure_palette = GenerateSimpleStructureTemplate(
        STRUCTURE_PATTERN_MAPPING,
        STRUCTURE_PATTERN,
        require_blocks_count=STRUCTURE_REQUIRE_BLOCKS,
    )
    functional_block_ids = set(STRUCTURE_REQUIRE_BLOCKS)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = BedrockLavaDrillUISync.NewServer(self).Activate()
        self._pos_ok = None
        self._current_drill_times = None
        self._total_drill_times = None
        self._rest_volume_predicted = None
        self._total_storage_volume = None
        self._power_changed = False

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    @SuperExecutorMeta.execute_super
    def OnPlaced(self, _):
        self.pos_ok = self.detect_block()
        self.total_drill_times = get_chunk_drill_time(self.x, self.z)

    @SuperExecutorMeta.execute_super
    def OnTicking(self):
        if not self.pos_ok:
            return
        if self._power_changed:
            if self.drill_finished():
                self.SetPower(PUMP_POWER)
            else:
                self.SetPower(DRILL_POWER)
            self._power_changed = False
        while self.IsActive():
            if self.ProcessOnce():
                self.work_once()
                self.CallSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.structure_flag = self.GetStructureDestroyFlag()
        self.sync.structure_lacked_blocks = self.GetStructureLackedBlocks()
        if self.StructureFinished():
            self.sync.drill_progress = float(self.current_drill_times) / (
                self.total_drill_times or 1
            )
            self.sync.lava_storage_left = float(self.rest_volume) / self.total_volume
            self.sync.fluid_id = self.get_fluid_output_io().fluid_id
            self.sync.fluid_volume = self.get_fluid_output_io().fluid_volume
            self.sync.max_volume = self.get_fluid_output_io().max_fluid_volume
        self.sync.MarkedAsChanged()

    def OnStructureChanged(self, structure_finished):
        if structure_finished:
            self.get_energy_input_io().SetMachineRef(self)
            self.get_fluid_output_io().SetMachineRef(self)
            self.get_fluid_output_io().SetOnReducedFluidCallback(self.on_reduced_fluid)

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        if slot == 0:
            return (
                "skybluetech:bedrock_lava_drill_acceptable" in item.GetBasicInfo().tags
            ) and item.durability is not None
        elif self.InUpgradeSlot(slot):
            return UpgradeControl.IsValidInput(self, slot, item)
        else:
            return False

    def OnSlotUpdate(self, slot):
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)

    def on_reduced_fluid(self, _, volume):
        if volume > 0:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)

    def init(self):
        self.bdata[K_POS_OK] = self.pos_ok = self.detect_block()
        if not self.pos_ok:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)

    def detect_block(self):
        if self.y > 5:
            return False
        down_block = GetBlockName(self.dim, (self.x, self.y - 1, self.z))
        if down_block != "minecraft:bedrock":
            return False
        return True

    def work_once(self):
        if self.drill_finished():
            self.pump_once()
        else:
            self.drill_once()

    def drill_once(self):
        s = self.GetSlotItem(0, get_user_data=True)
        if s is None or s.durability is None:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
            return
        s.durability -= 1
        if s.durability <= 0:
            s = Item("minecraft:air")
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE)
        self.SetSlotItem(0, s)
        self.current_drill_times += 1
        if self.current_drill_times >= self.total_drill_times:
            self._power_changed = True

    def pump_once(self):
        fluid_output = self.get_fluid_output_io()
        space = int(fluid_output.max_fluid_volume - fluid_output.fluid_volume)
        rest_vol = self.rest_volume
        vol = pump_deepslate_lava(self.x, self.z, min(space, self.pump_speed))
        self.rest_volume = rest_vol - vol
        fluid_output.AddFluid(DEEPSLATE_LAVA, vol)
        if space - vol <= 0:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)

    def get_energy_input_io(self):
        return self.GetMachine(EnergyInputInterface, IO_ENERGY)

    def get_fluid_output_io(self):
        return self.GetMachine(FluidOutputInterface, IO_FLUID1)

    def drill_finished(self):
        return self.current_drill_times >= self.total_drill_times

    @property
    def pos_ok(self):
        # type: () -> bool
        if self._pos_ok is None:
            self._pos_ok = self.bdata[K_POS_OK] or False
        return self._pos_ok

    @pos_ok.setter
    def pos_ok(self, value):
        # type: (bool) -> None
        self.bdata[K_POS_OK] = self._pos_ok = value

    @property
    def total_drill_times(self):
        # type: () -> int
        if self._total_drill_times is None:
            self._total_drill_times = self.bdata[K_DRILL_TIMES] or 1
        return self._total_drill_times

    @total_drill_times.setter
    def total_drill_times(self, value):
        # type: (int) -> None
        self.bdata[K_DRILL_TIMES] = self._total_drill_times = value

    @property
    def current_drill_times(self):
        # type: () -> int
        if self._current_drill_times is None:
            self._current_drill_times = self.bdata[K_DRILL_PROGRESS] or 0
        return self._current_drill_times

    @current_drill_times.setter
    def current_drill_times(self, value):
        # type: (int) -> None
        self.bdata[K_DRILL_PROGRESS] = self._current_drill_times = value

    @property
    def rest_volume(self):
        # type: () -> int
        if self._rest_volume_predicted is None:
            self._rest_volume_predicted, self._total_storage_volume = (
                get_available_lava_storage(self.x, self.z)
            )
        return self._rest_volume_predicted

    @rest_volume.setter
    def rest_volume(self, value):
        # type: (int) -> None
        self._rest_volume_predicted = value

    @property
    def total_volume(self):
        # type: () -> int
        "此地深层熔岩总储量, 需要和此地剩余储量区分。"
        if self._total_storage_volume is None:
            self._rest_volume_predicted, self._total_storage_volume = (
                get_available_lava_storage(self.x, self.z)
            )
        return self._total_storage_volume
