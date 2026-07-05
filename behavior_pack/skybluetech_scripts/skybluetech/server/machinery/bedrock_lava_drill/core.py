# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server.block import GetBlockName
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from skybluetech_scripts.skybluetech.common.define import flags
from skybluetech_scripts.skybluetech.common.define.id_enum.machinery import Machinery

MACHINE_ID = Machinery.BEDROCK_LAVA_DRILL_CONTROLLER
from skybluetech_scripts.skybluetech.common.define.id_enum.fluids import DeepLava
from skybluetech_scripts.skybluetech.common.machinery_def.bedrock_lava_drill import (
    STRUCTURE_PALETTE,
    STRUCTURE_REQUIRE_BLOCKS,
    IO_FLUID1,
    IO_ENERGY,
    DRILL_POWER,
    PUMP_POWER,
    STORE_RF_MAX,
    K_POS_OK,
    K_DRILL_TIMES,
    K_TOTAL_DRILL_TIMES,
    K_DRILL_PROGRESS,
    K_VOLUME_LEFT_PERCENT,
    K_FLUID_ID,
    K_FLUID_VOLUME,
    K_MAX_FLUID_VOLUME,
)
from ..basic import (
    GUIControl,
    MultiBlockStructure,
    UpgradeControl,
    RegisterMachine,
)
from ..interfaces import EnergyInputInterface, FluidOutputInterface
from .lava_storage import (
    pump_deepslate_lava,
    get_chunk_drill_time,
    get_available_lava_storage,
)

EnergyInputInterface.AddExtraMachineId(IO_ENERGY)
FluidOutputInterface.AddExtraMachineId(IO_FLUID1)


@RegisterMachine
class BedrockLavaDrill(GUIControl, MultiBlockStructure, UpgradeControl):
    block_name = MACHINE_ID
    store_rf_max = STORE_RF_MAX
    pump_speed = 400
    origin_process_ticks = 10
    running_power = DRILL_POWER
    structure_palette = STRUCTURE_PALETTE
    functional_block_ids = set(STRUCTURE_REQUIRE_BLOCKS)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self._pos_ok = None
        self._current_drill_times = None
        self._total_drill_times = None
        self._rest_volume_predicted = None
        self._total_storage_volume = None
        self._power_changed = False
        self._energy_in = None
        self._fluid_out = None

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        self.clean()

    def clean(self):
        # type: () -> None
        if self._energy_in is not None:
            self._energy_in.UnsetMachineRef()
            self._energy_in = None
        if self._fluid_out is not None:
            self._fluid_out.UnsetMachineRef()
            self._fluid_out = None

    @SuperExecutorMeta.execute_super
    def OnPlaced(self, _):
        self.pos_ok = self.detect_block()
        self.total_drill_times = get_chunk_drill_time(self.x, self.z)

    @SuperExecutorMeta.execute_super
    def OnTicking(self):
        if not self.pos_ok or not self.StructureFinished():
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
        if self.StructureFinished():
            self.bdata[K_DRILL_PROGRESS] = float(self.current_drill_times) / (
                self.total_drill_times or 1
            )
            if self.drill_finished():
                self.bdata[K_VOLUME_LEFT_PERCENT] = (
                    self.rest_volume * 1.0 / self.total_volume
                )
            else:
                self.bdata[K_VOLUME_LEFT_PERCENT] = 0
            self.bdata[K_FLUID_ID] = self.get_fluid_output_io().fluid_id
            self.bdata[K_FLUID_VOLUME] = self.get_fluid_output_io().fluid_volume
            self.bdata[K_MAX_FLUID_VOLUME] = self.get_fluid_output_io().max_fluid_volume

    def OnStructureChanged(self, structure_finished):
        if structure_finished:
            self._energy_in = self.get_energy_input_io()
            self._fluid_out = self.get_fluid_output_io()
            self._energy_in.SetMachineRef(self)
            self._fluid_out.SetMachineRef(self)
            self._fluid_out.SetOnReducedFluidCallback(self.on_reduced_fluid)
        else:
            self.clean()

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
        print("++++", self.current_drill_times)
        self.current_drill_times += 1
        if self.current_drill_times >= self.total_drill_times:
            self._power_changed = True

    def pump_once(self):
        fluid_output = self.get_fluid_output_io()
        space = int(fluid_output.max_fluid_volume - fluid_output.fluid_volume)
        rest_vol = self.rest_volume
        vol = pump_deepslate_lava(self.x, self.z, min(space, self.pump_speed))
        self.rest_volume = rest_vol - vol
        fluid_output.AddFluid(DeepLava.DEEPSLATE_LAVA, vol)
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
            self._total_drill_times = self.bdata[K_TOTAL_DRILL_TIMES] or 1
        return self._total_drill_times

    @total_drill_times.setter
    def total_drill_times(self, value):
        # type: (int) -> None
        self.bdata[K_TOTAL_DRILL_TIMES] = self._total_drill_times = value

    @property
    def current_drill_times(self):
        # type: () -> int
        if self._current_drill_times is None:
            self._current_drill_times = self.bdata[K_DRILL_TIMES] or 0
        return self._current_drill_times

    @current_drill_times.setter
    def current_drill_times(self, value):
        # type: (int) -> None
        self.bdata[K_DRILL_TIMES] = self._current_drill_times = value

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
