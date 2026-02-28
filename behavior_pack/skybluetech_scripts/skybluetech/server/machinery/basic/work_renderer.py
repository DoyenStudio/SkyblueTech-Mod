# coding=utf-8
#
from skybluetech_scripts.tooldelta.api.server.block import UpdateBlockStates
from .base_machine import BaseMachine


class WorkRenderer(BaseMachine):
    """
    表示一个存在 active 状态的机器方块基类。
    机器外观会随 active 状态的改变而改变。

    派生自: `BaseMachine`

    覆写:
        `SetDeactiveFlag`
        `UnsetDeactiveFlag (super)`
        `ResetDeactiveFlags (super)`
        `FlushDeactiveFlags (super)`
    """

    _last_work_status = False

    def SetDeactiveFlag(self, flag, flush=True):
        # type: (int, bool) -> None
        if flush:
            self._update_work_status()

    def UnsetDeactiveFlag(self, flag, flush=True):
        # type: (int, bool) -> None
        if not self.HasDeactiveFlag(flag):
            return
        BaseMachine.UnsetDeactiveFlag(self, flag)
        if flush:
            self._update_work_status()

    def ResetDeactiveFlags(self):
        BaseMachine.ResetDeactiveFlags(self)
        self._update_work_status()

    def FlushDeactiveFlags(self):
        # type: () -> None
        BaseMachine.FlushDeactiveFlags(self)
        self._update_work_status()

    def OnWorkStatusUpdated(self):
        "子类方法覆写当状态改变时执行的操作。"

    def _update_work_status(self):
        # type: () -> None
        active = self.deactive_flags == 0
        if active != self._last_work_status:
            UpdateBlockStates(
                self.dim, (self.x, self.y, self.z), {"skybluetech:active": active}
            )
            self._last_work_status = active
            self.OnWorkStatusUpdated()
