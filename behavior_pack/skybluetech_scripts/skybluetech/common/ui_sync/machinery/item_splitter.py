# coding=utf-8

from .basic_machine_ui_sync import MachineUISync


class ItemSplitterUISync(MachineUISync):

    def Unmarshal(self, data):
        pass

    def Marshal(self):
        return {}
