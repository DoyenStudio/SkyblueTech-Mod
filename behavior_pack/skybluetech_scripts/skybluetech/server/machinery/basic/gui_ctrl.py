# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.ui_sync import S2CSync
from skybluetech_scripts.tooldelta.events.server.block import ServerBlockUseEvent
from skybluetech_scripts.tooldelta.events.server.ui import (
    PushUIRequest,
    ForceRemoveUIRequest,
)
from skybluetech_scripts.tooldelta.events.notify import NotifyToClient, NotifyToClients
from skybluetech_scripts.tooldelta.extensions.rate_limiter import (
    PlayerRateLimiter,
)
from skybluetech_scripts.tooldelta.extensions.ui_sync import (
    S2CSync,
    AddSyncPending,
    GetAllPlayersInSync,
)
from skybluetech_scripts.skybluetech.common.events.machinery.basic import (
    MachineStatusUpdate,
)

from .base_machine import BaseMachine

rate_limiter = PlayerRateLimiter(0.4)


class GUIControl(BaseMachine):
    """
    带有 GUI 的机器基类。

    覆写:
        - `__init__`
        - 向 handler 订阅点击和卸载事件
    """

    bound_ui = None  # type: str | None
    "绑定的 UI key, 如果为自定义容器, 此处设置为 None"

    def __init__(self, dim, x, y, z, block_entity_data):
        super(GUIControl, self).__init__(dim, x, y, z, block_entity_data)
        self.ui_sync = S2CSync.NewServer(
            "machine_%d_%d_%d_%d" % (dim, x, y, z)
        ).Activate()
        self._gui_sent_flags = None  # type: int | None
        self.handler.SubscribeOnClick(self._gui_control_on_click)
        self.handler.SubscribeOnUnload(self._gui_control_on_unload)
        self.handler.SubscribeOnDeactiveFlagsChanged(self._gui_control_on_flags_changed)

    def _gui_control_on_flags_changed(self, flush=True):
        # type: (bool) -> None
        "停机标志变化时推给正打开界面的玩家; 只在数值真的变了时发送 (SetDeactiveFlag 重复设置也会触发本回调)。"
        players = self.ui_sync.GetPlayersInSync()
        if not players:
            self._gui_sent_flags = None  # 没人看着就不发; 下次有人打开时界面自己读一次方块数据
            return
        flags = self.deactive_flags
        if flags == self._gui_sent_flags:
            return
        self._gui_sent_flags = flags
        MachineStatusUpdate(self.x, self.y, self.z, flags).sendMulti(players)

    def _gui_control_on_click(self, event, extra_datas=None):
        # type: (ServerBlockUseEvent, dict | None) -> None
        "超类方法用于通知玩家打开 GUI。"
        if not rate_limiter.record(event.playerId):
            return
        self.CallSync()
        AddSyncPending(event.playerId, self.ui_sync)
        if self.bound_ui is not None:
            params = {
                "st:dmpos": (event.dimensionId, event.x, event.y, event.z),
            }
            if extra_datas is not None:
                params.update(extra_datas)
            NotifyToClient(
                event.playerId,
                PushUIRequest(
                    self.bound_ui,
                    self.ui_sync.sync_id,
                    params,
                ),
            )

    def _gui_control_on_unload(self):
        "超类方法用于通知玩家关闭 GUI 和将同步项关闭。"
        if self.bound_ui is not None:
            tIDs = GetAllPlayersInSync(self.ui_sync.sync_id)
            NotifyToClients(tIDs, ForceRemoveUIRequest(self.bound_ui))
        self.ui_sync.Deactivate()

    def CallSync(self):
        self.handler.CallOnSyncHandlers()
