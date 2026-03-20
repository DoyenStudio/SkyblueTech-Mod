# coding=utf-8
#
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

if 0:
    # TODO: 跨端导入!!! 必须更改!!!
    from ....client.ui.machinery.define import MachinePanelUI

rate_limiter = PlayerRateLimiter(0.4)


class GUIControl(object):
    """
    带有 GUI 的机器基类。

    覆写: `OnClick`, `OnUnload`
    """

    bound_ui = None  # type: str | None
    "绑定的 UI key, 如果为自定义容器, 此处设置为 None"
    sync = S2CSync.NewServer()
    "UI 同步器"

    def __init__(self, dim, x, y, z, block_entity_data):
        pass

    def OnClick(self, event, extra_datas=None):
        # type: (ServerBlockUseEvent, dict | None) -> None
        "超类方法用于通知玩家打开 GUI。"
        if not rate_limiter.record(event.playerId):
            return
        self.CallSync()
        AddSyncPending(event.playerId, self.sync)
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
                    self.sync.sync_id,
                    params,
                ),
            )

    def OnUnload(self):
        "超类方法用于通知玩家关闭 GUI 和将同步项关闭。"
        if self.bound_ui is not None:
            tIDs = GetAllPlayersInSync(self.sync.sync_id)
            NotifyToClients(tIDs, ForceRemoveUIRequest(self.bound_ui))
        self.sync.Deactivate()

    def OnSync(self):
        # type: () -> None
        "覆写方法用于将机器数据同步到客户端 UI。"

    def CallSync(self):
        self.OnSync()
