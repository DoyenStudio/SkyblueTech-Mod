# coding=utf-8
import random
from skybluetech_scripts.tooldelta.events.server.block import (
    ServerPlaceBlockEntityEvent,
)
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockName,
    GetBlockStates,
    SetBlock,
    MayPlace,
    GetBlockAuxValueFromStates,
)
from skybluetech_scripts.tooldelta.events.server import (
    BlockNeighborChangedServerEvent,
    ServerBlockUseEvent,
    ServerEntityTryPlaceBlockEvent,
)
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.machinery_def.deepslate_lava_vibrator import (
    STORE_RF_MAX,
    K_DEEPSLATE_LAVA_PREDICTED,
    K_PREDICT_PROGRESS,
)
from ...common.define.id_enum.machinery import DEEPSLATE_LAVA_VIBRATOR as MACHINE_ID
from .basic import SPControl, RegisterMachine
from .bedrock_lava_drill.lava_storage import get_available_lava_storage
from .pool import GetMachineStrict

K_REAL_STORAGE = "st:real_storage"


@RegisterMachine
class DeepslateLavaVibrator(SPControl):
    block_name = MACHINE_ID
    store_rf_max = STORE_RF_MAX
    energy_io_mode = (2, 2, 0, 0, 0, 0)
    running_power = 400
    origin_process_ticks = 20

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        states = GetBlockStates(self.dim, (self.x, self.y, self.z))
        if states is None:
            raise ValueError("WindGenerator BlockState None")
        self.layer = states["skybluetech:layer"]  # type: int
        # 如果不是基座方块则无功能
        self.is_base_block = self.layer == 0
        if not self.is_base_block:
            self.energy_io_mode = (2, 2, 2, 2, 2, 2)
            self.is_non_energy_machine = True
        if self.predict_progress == 1.0:
            self.SetPower(0)

    def OnTicking(self):
        while self.IsActive():
            if self.ProcessOnce():
                self.work_once()
            else:
                break

    @classmethod
    def OnPrePlaced(cls, event):
        # type: (ServerEntityTryPlaceBlockEvent) -> None
        block_id = event.fullName
        dim = event.dimensionId
        x = event.x
        y = event.y
        z = event.z
        facing = event.face
        if not MayPlace(block_id, (x, y + 1, z), facing, dim):
            event.cancel()

    @SuperExecutorMeta.execute_super
    def OnPlaced(self, event):
        if not self.is_base_block:
            return
        SetBlock(
            self.dim,
            (self.x, self.y + 1, self.z),
            self.block_name,
            GetBlockAuxValueFromStates(self.block_name, {"skybluetech:layer": 1}),
        )
        self.set_predict_value(0)

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        base_y = self.y - self.layer
        for i in range(2):
            block_id = GetBlockName(self.dim, (self.x, base_y + i, self.z))
            if block_id == self.block_name and i != self.layer:
                SetBlock(self.dim, (self.x, base_y + i, self.z), "minecraft:air")

    def work_once(self):
        self.add_predict_precision()

    def add_predict_precision(self):
        last_progress = self.predict_progress
        last_progress = min(1, last_progress + 0.02)
        self.predict_progress = last_progress
        randrange = self.real_storage * (1 - last_progress) * 0.95
        self.set_predict_value(
            self.real_storage + int((random.random() * 2 - 1) * randrange)
        )
        if last_progress >= 1.0:
            self.SetPower(0)

    def set_predict_value(self, value):
        # type: (int) -> None
        self.bdata[K_DEEPSLATE_LAVA_PREDICTED] = value

    @property
    def predict_progress(self):
        # type: () -> float
        return self.bdata[K_PREDICT_PROGRESS] or 0.0

    @predict_progress.setter
    def predict_progress(self, value):
        # type: (float) -> None
        self.bdata[K_PREDICT_PROGRESS] = value

    @property
    def real_storage(self):
        # type: () -> int
        val = self.bdata[K_REAL_STORAGE]
        if val is None:
            val = get_available_lava_storage(self.x, self.z)[0]
        return val

    @real_storage.setter
    def real_storage(self, value):
        # type: (int) -> None
        self.bdata[K_REAL_STORAGE] = value
