# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from skybluetech_scripts.skybluetech.common.define.id_enum import (
    Machinery,
    SeawaterReservoir,
)
from skybluetech_scripts.skybluetech.common.machinery_def.seawater_pump import (
    K_WATER_BLOCK_COUNT,
    MAX_FLUID_VOLUME,
    MIN_WATER_RATIO,
    OUTPUT_FLUID,
    RUNNING_POWER,
    STORE_RF_MAX,
    STRUCTURE_PALETTE,
    WATER_SCAN_HEIGHT,
    WATER_SCAN_RADIUS,
    WATER_SCAN_VOLUME,
    get_output_per_tick,
)
from skybluetech_scripts.skybluetech.server.machinery.basic import (
    GUIControl,
    MultiBlockStructure,
    MultiFluidContainer,
)
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine
from skybluetech_scripts.skybluetech.server.machinery.interfaces import EnergyInputInterface


EnergyInputInterface.AddExtraMachineId(SeawaterReservoir.IO_ENERGY)


@RegisterMachine
class SeawaterPump(GUIControl, MultiBlockStructure, MultiFluidContainer):
    block_name = Machinery.SEAWATER_PUMP
    store_rf_max = STORE_RF_MAX
    structure_palette = STRUCTURE_PALETTE
    functional_block_ids = {SeawaterReservoir.IO_ENERGY}
    fluid_slot_max_volumes = {0: MAX_FLUID_VOLUME}
    fluid_input_slots = ()
    fluid_output_slots = (0,)
    fluid_io_mode = (1, 1, 1, 1, 1, 1)
    allow_player_use_bucket_push = False

    def __init__(self, dim, x, y, z, block_entity_data):
        super(SeawaterPump, self).__init__(dim, x, y, z, block_entity_data)
        # 放置时扫描一次并保存水量；重载直接恢复产率，不重新扫描环境。
        water_count = int(max(0, min(
            WATER_SCAN_VOLUME, self.bdata[K_WATER_BLOCK_COUNT] or 0
        )))
        self._output_per_tick = get_output_per_tick(water_count)
        self._energy_in_ios = []  # type: list[EnergyInputInterface]
        self.handler.SubscribeOnPlaced(self._seawater_pump_on_placed)
        self.handler.SubscribeOnTicking(self._seawater_pump_on_ticking)
        self.handler.SubscribeOnStructureChanged(self._seawater_pump_on_structure_changed)
        self.handler.SubscribeOnUnload(self._seawater_pump_on_unload)

    def _seawater_pump_on_placed(self, _):
        # 包含泵所在的顶层，X/Z 各向两侧延伸 30 格，Y 向下延伸 19 格。
        palette = CF.CreateBlock(LEVEL_ID).GetBlockPaletteBetweenPos(
            self.dim,
            (
                self.x - WATER_SCAN_RADIUS,
                self.y - WATER_SCAN_HEIGHT + 1,
                self.z - WATER_SCAN_RADIUS,
            ),
            (
                self.x + WATER_SCAN_RADIUS,
                self.y,
                self.z + WATER_SCAN_RADIUS,
            ),
            eliminateAir=False,
        )
        water_count = 0
        if palette is not None:
            # 不指定 aux，合计所有水位的静水和流水方块。
            water_count = (
                palette.GetBlockCountInBlockPalette("minecraft:water")
                + palette.GetBlockCountInBlockPalette("minecraft:flowing_water")
            )
        # 范围内最多 74420 格，显式转为 Python int 后再写入方块实体数据。
        water_count = int(max(0, min(WATER_SCAN_VOLUME, water_count)))
        self.bdata[K_WATER_BLOCK_COUNT] = water_count
        self._output_per_tick = get_output_per_tick(water_count)

    def _seawater_pump_on_ticking(self):
        if not self.StructureFinished() or not self.IsActive():
            return
        water_count = self.bdata[K_WATER_BLOCK_COUNT] or 0
        if water_count < WATER_SCAN_VOLUME * MIN_WATER_RATIO:
            return
        if self.fluids[0].isFull() or self.store_rf < RUNNING_POWER:
            return
        # 达到最低水占比、储槽未满且电量充足时，固定消耗 80 RF。
        self.ReducePower(RUNNING_POWER)
        if self._output_per_tick > 0.0:
            # OutputFluid 只填入剩余容量；返回的溢出量直接丢弃，不缓存补产。
            self.OutputFluid(OUTPUT_FLUID, self._output_per_tick, 0, True)

    def _seawater_pump_on_structure_changed(self, ok):
        # type: (bool) -> None
        self.disconnect_ios()
        if ok:
            self._energy_in_ios = self.GetAllMachines(
                EnergyInputInterface, SeawaterReservoir.IO_ENERGY
            )
            for machine in self._energy_in_ios:
                machine.SetMachineRef(self)

    def _seawater_pump_on_unload(self):
        self.disconnect_ios()

    def disconnect_ios(self):
        for machine in self._energy_in_ios:
            machine.UnsetMachineRef()
        self._energy_in_ios = []
