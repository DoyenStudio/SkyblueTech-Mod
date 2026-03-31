# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_RF = "r"
K_RF_MAX = "m"
K_FLUID_ID = "f"
K_FLUID_VOLUME = "v"
K_MAX_FLUID_VOLUME = "M"
K_DIGGING_POS = "P"
K_WORK_MODE = "w"


class MiniMinerUISync(MachineUISync):
    class WorkMode:
        UNKNOWN = -1
        WORKING = 0
        FLUID_LACK = 1
        POWER_LACK = 2
        FINISHED = 3
        OUTPUT_FULL = 4
        FAST_SKIP = 5
        OTHER = 127

        @classmethod
        def zh_cn(cls, mode):
            # type: (int) -> str
            return {
                cls.WORKING: "§a工作中",
                cls.FLUID_LACK: "§6润滑油不足",
                cls.POWER_LACK: "§c能量不足",
                cls.FINISHED: "§2已完成",
                cls.OUTPUT_FULL: "§c输出槽已满",
                cls.FAST_SKIP: "§e快进中",
                cls.OTHER: "§7已停机",
            }.get(mode, "未知状态")

    storage_rf = 0
    rf_max = 0
    fluid_id = None  # type: str | None
    fluid_volume = 0.0
    max_volume = 1.0
    digging_pos = (-1, -1, -1)
    work_mode = WorkMode.UNKNOWN

    def Unmarshal(self, data):
        self.digging_pos = data[K_DIGGING_POS]
        self.storage_rf = data[K_RF]
        self.rf_max = data[K_RF_MAX]
        self.fluid_id = data[K_FLUID_ID]
        self.fluid_volume = data[K_FLUID_VOLUME]
        self.max_volume = data[K_MAX_FLUID_VOLUME]
        self.work_mode = data[K_WORK_MODE]

    def Marshal(self):
        return {
            K_DIGGING_POS: self.digging_pos,
            K_RF: self.storage_rf,
            K_RF_MAX: self.rf_max,
            K_FLUID_ID: self.fluid_id,
            K_FLUID_VOLUME: self.fluid_volume,
            K_MAX_FLUID_VOLUME: self.max_volume,
            K_WORK_MODE: self.work_mode,
        }
