# coding=utf-8
#
from weakref import WeakSet
from mod_log import logger
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.api.timer import AsTimerFunc
from .base_machine import BaseMachine

active_machines = WeakSet() # type: WeakSet[AutoSaver]
auto_save_inited = False

def startAutoSave():
    global auto_save_inited
    if not auto_save_inited:
        logger.info("[SkyblueTech] AutoSave module inited")
        auto_save_inited = True
        autoSave()

@AsTimerFunc(1)
def autoSave():
    # TODO: 优化！
    for machine in active_machines:
        machine.Dump()


class AutoSaver(BaseMachine):
    """
    每隔 1 秒自动保存机器数据的基类。
    
    需要 `__init__()`
    
    覆写: `OnUnload`
    """
    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        self.hash_val = hash((dim, x, y, z))
        active_machines.add(self)
        startAutoSave()

    def OnUnload(self):
        active_machines.remove(self)

    def __hash__(self):
        return self.hash_val

