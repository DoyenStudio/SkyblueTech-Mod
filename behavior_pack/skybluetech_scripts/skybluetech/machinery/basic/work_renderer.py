# coding=utf-8
#
from skybluetech_scripts.tooldelta.api.server.block import UpdateBlockStates
from .base_machine import BaseMachine


class WorkRenderer(BaseMachine):
    """
    表示一个存在 active 状态的机器方块基类。
    机器外观会随 active 状态的改变而改变。
    
    覆写: `SetDeactiveFlag`, `UnsetDeactiveFlag`[基调用]
    """

    _last_work_status = False
    
    def _updateWorkStatus(self):
        # type: () -> None
        active = self.deactive_flags == 0
        if active != self._last_work_status:
        #     print (self.x, self.y, self.z), "change status"
            UpdateBlockStates(self.dim, (self.x, self.y, self.z), {"skybluetech:active": active})
            self._last_work_status = active
            self.OnWorkStatusUpdated()


    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        self._updateWorkStatus()

    def UnsetDeactiveFlag(self, flag):
        # type: (int) -> None
        BaseMachine.UnsetDeactiveFlag(self, flag)
        self._updateWorkStatus()

    def OnWorkStatusUpdated(self):
        "子类方法覆写当状态改变时执行的操作。"
