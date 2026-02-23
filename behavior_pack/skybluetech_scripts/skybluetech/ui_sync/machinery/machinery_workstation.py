# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_PROGRESS = "p"
K_OUTPUT_ITEM_ID = "i"


class MachineryWorkstationUISync(MachineUISync):
    progress = 0.0
    output_item_id = None  # type: str | None

    def Unmarshal(self, data):
        self.progress = data[K_PROGRESS]
        self.output_item_id = data[K_OUTPUT_ITEM_ID]

    def Marshal(self):
        return {
            K_PROGRESS: self.progress,
            K_OUTPUT_ITEM_ID: self.output_item_id,
        }
