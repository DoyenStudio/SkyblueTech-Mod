# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
#

from .base_machine import BaseMachine


class WorkRenderer(BaseMachine):
    """
    表示一个存在 active 状态的机器方块基类。
    机器外观会随 active 状态的改变而改变。

    派生自: `BaseMachine`

    订阅停机状态变化, 并在外观发生变化后派发工作状态更新事件。
    """

    def __init__(self, dim, x, y, z, block_entity_data):
        super(WorkRenderer, self).__init__(dim, x, y, z, block_entity_data)
        self._last_work_status = False
        self.handler.SubscribeOnDeactiveFlagsChanged(self._update_work_status)


    def _update_work_status(self, flush=True):
        # type: (bool) -> None
        if not flush:
            return
        active = self.deactive_flags == 0
        if active != self._last_work_status:
            block_state_comp = CF.CreateBlockState(LEVEL_ID)
            block_states = block_state_comp.GetBlockStates((self.x, self.y, self.z), self.dim)
            if block_states is not None:
                block_states.update({"skybluetech:active": active})
                block_state_comp.SetBlockStates((self.x, self.y, self.z), block_states, self.dim)
            self._last_work_status = active
            self.handler.CallOnWorkStatusUpdatedHandlers()
