# coding=utf-8
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server import SpawnDroppedItem
from ...common.define import flags
from ...common.define.id_enum import BATTERY_MATRIX_CONTROLLER as MACHINE_ID
from ...common.define.tag_enum import BatteryTag
from ...common.events.machinery.battery_matrix import (
    BatteryMatrixActionRequest,
    BatteryMatrixCheckCoreBatterysRequest,
    BatteryMatrixPopBatteryRequest,
    BatteryMatrixStoreBatteryRequest,
)
from ...common.machinery_def.battery_matrix import (
    STRUCTURE_PATTERN,
    STRUCTURE_PATTERN_MAPPING,
    STRUCTURE_REQUIRE_BLOCKS,
    IO_ENERGY_INPUT,
    IO_ENERGY_OUTPUT,
)
from ...common.ui_sync.machinery.battery_matrix import BatteryMatrixUISync
from .basic import (
    BaseMachine,
    GUIControl,
    ItemContainer,
    MultiBlockStructure,
    RegisterMachine,
)
from .basic.multi_block_structure import GenerateSimpleStructureTemplate
from .utils.action_commit import SafeGetMachine
from .interfaces import EnergyInputInterface, EnergyOutputInterface
from .battery_matrix_core import BatteryMatrixCore

INFINITY = float("inf")

K_STORE_RF = "store_rf"
K_ENABLE_INPUT = "st:enable_input"
K_ENABLE_OUTPUT = "st:enable_output"


EnergyInputInterface.AddExtraMachineId(IO_ENERGY_INPUT)
EnergyOutputInterface.AddExtraMachineId(IO_ENERGY_OUTPUT)


@RegisterMachine
class BatteryMatrix(GUIControl, ItemContainer, MultiBlockStructure):
    block_name = MACHINE_ID
    store_rf_max = 100000
    input_slots = (0, 1, 2, 3, 4, 5, 6)
    output_slots = (0, 1, 2, 3, 4, 5, 6)
    structure_palette = GenerateSimpleStructureTemplate(
        STRUCTURE_PATTERN_MAPPING,
        STRUCTURE_PATTERN,
        require_blocks_count=STRUCTURE_REQUIRE_BLOCKS,
    )
    functional_block_ids = set(STRUCTURE_REQUIRE_BLOCKS)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        MultiBlockStructure.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = BatteryMatrixUISync.NewServer(self).Activate()
        self._last_input = 0
        self._last_output = 0

    def OnTicking(self):
        if self.IsActive():
            if self.output_mode:
                self.provide_energy()
            self.get_core().core_tick()
            self.OnSync()
        self._last_input = 0
        self._last_output = 0

    def OnTryActivate(self):
        # type: () -> None
        self.ResetDeactiveFlags()

    def OnClick(self, event, extra_datas=None):
        GUIControl.OnClick(self, event, extra_datas)

    def OnSync(self):
        self.sync.enable_input = self.input_mode
        self.sync.enable_output = self.output_mode
        self.sync.structure_flag = self.GetStructureDestroyFlag()
        self.sync.structure_lacked_blocks = self.GetStructureLackedBlocks()
        self.sync.input_power = self._last_input
        self.sync.output_power = self._last_output
        if self.GetStructureDestroyFlag() == 0:
            self.sync.storage_rf = self.get_core().calculate_core_store_rf()
            self.sync.rf_max = self.get_core().calculate_core_store_rf_max()
        else:
            self.sync.storage_rf = 0
            self.sync.rf_max = 1
        self.sync.MarkedAsChanged()

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        pass

    def OnStructureChanged(self, ok):
        # type: (bool) -> None
        if ok:
            self.get_energy_in_io().SetMachineRef(self)
            self.get_energy_out_io().SetMachineRef(self)
        self.OnSync()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        return BatteryTag.COMMON in item.GetBasicInfo().tags

    def AddPower(
        self,
        rf,  # type: int
        max_limit=None,  # type: int | None
        passed=None,  # type: set[BaseMachine] | None
    ):
        # type: (...) -> tuple[bool, int]
        if passed is not None:
            passed.add(self)
        if self.GetStructureDestroyFlag() != 0:
            return False, rf
        if max_limit is None:
            wire_overflow = 0
        else:
            wire_overflow = max(0, rf - max_limit)
            rf = min(rf, max_limit)
        if not self.input_mode:
            return False, rf
        power_overflow = self.get_core().add_energy(rf)
        self._last_input += rf - power_overflow
        self.OnSync()
        overflow = power_overflow + wire_overflow
        return overflow != rf, overflow

    def OnUnload(self):
        # type: () -> None
        MultiBlockStructure.OnUnload(self)
        GUIControl.OnUnload(self)

    def push_batteries_to_core(self):
        if self.GetStructureDestroyFlag() != 0:
            return
        slotitems = self.GetInputSlotItems(get_user_data=True)
        core = self.get_core()
        for slot, item in slotitems.items():
            if item is None:
                continue
            ok = core.add_battery(item)
            if ok:
                self.SetSlotItem(slot, None)
            else:
                break
        core.update_core_data()
        self.OnSync()
        core.gen_update_event().sendMulti(self.sync.GetPlayersInSync())

    def pop_battery_from_core(self, index):
        # type: (int) -> None
        if self.GetStructureDestroyFlag() != 0:
            return
        slotitems = self.GetInputSlotItems(get_user_data=False)
        if not any(slotitems.get(i) is None for i in self.input_slots):
            return
        core = self.get_core()
        if index >= len(core.slots) or index < 0:
            return
        core.save_core_data()
        battery_item = core.pop_battery(index)
        if battery_item is None:
            return
        res = self.OutputItem(battery_item)
        if res is not None:
            # cannot happen
            SpawnDroppedItem(self.dim, (self.x, self.y, self.z), res)
        core.update_core_data()
        self.OnSync()
        core.gen_update_event().sendMulti(self.sync.GetPlayersInSync())

    def provide_energy(self):
        core = self.get_core()
        rf_out = core.output_energy()
        if rf_out <= 0:
            return
        output_io = self.get_energy_out_io()
        ok, overflow = output_io.GeneratePowerWithOverflow(rf_out)
        core.add_energy(overflow, from_overflow=True)
        self._last_output += rf_out - overflow
        if not ok and overflow > 0:
            self.SetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)

    def get_core(self):
        return self.GetMachine(BatteryMatrixCore)

    def get_energy_in_io(self):
        return self.GetMachine(EnergyInputInterface, IO_ENERGY_INPUT)

    def get_energy_out_io(self):
        return self.GetMachine(EnergyOutputInterface, IO_ENERGY_OUTPUT)

    def set_input_mode(self, value):
        if not isinstance(value, bool):
            return
        self.input_mode = value

    def set_output_mode(self, value):
        if not isinstance(value, bool):
            return
        self.output_mode = value

    @property
    def input_mode(self):
        # type: () -> bool
        res = self.bdata[K_ENABLE_INPUT]
        if res is None:
            self.bdata[K_ENABLE_INPUT] = res = True
        return res

    @input_mode.setter
    def input_mode(self, value):
        # type: (bool) -> None
        self.bdata[K_ENABLE_INPUT] = value

    @property
    def output_mode(self):
        # type: () -> bool
        res = self.bdata[K_ENABLE_OUTPUT]
        if res is None:
            self.bdata[K_ENABLE_OUTPUT] = res = True
        return res

    @output_mode.setter
    def output_mode(self, value):
        # type: (bool) -> None
        self.bdata[K_ENABLE_OUTPUT] = value


@BatteryMatrixActionRequest.Listen()
def onRequest(event):
    # type: (BatteryMatrixActionRequest) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, BatteryMatrix) or not m.StructureFinished():
        return
    if event.op == event.OPERATION_INPUT:
        m.set_input_mode(event.value)
    elif event.op == event.OPERATION_OUTPUT:
        m.set_output_mode(event.value)
    m.OnSync()


@BatteryMatrixCheckCoreBatterysRequest.Listen()
def onRecvCheckRequest(event):
    # type: (BatteryMatrixCheckCoreBatterysRequest) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, BatteryMatrix) or not m.StructureFinished():
        return
    m.get_core().gen_update_event(first=True).send(event.player_id)


@BatteryMatrixPopBatteryRequest.Listen()
def onRecvPopRequest(event):
    # type: (BatteryMatrixPopBatteryRequest) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, BatteryMatrix) or not m.StructureFinished():
        return
    m.pop_battery_from_core(event.index)


@BatteryMatrixStoreBatteryRequest.Listen()
def onRecvStoreRequest(event):
    # type: (BatteryMatrixStoreBatteryRequest) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, BatteryMatrix) or not m.StructureFinished():
        return
    m.push_batteries_to_core()
