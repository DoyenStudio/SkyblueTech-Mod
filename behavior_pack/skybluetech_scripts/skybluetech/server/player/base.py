# coding=utf-8
from skybluetech_scripts.tooldelta.events.event_bus import GetMCServerEventBus
from skybluetech_scripts.tooldelta.events.service import EventListenerService


class PlayerService(EventListenerService):
    """每玩家服务基类。

    子类用 ``@PlayerService.Listen(...)`` 绑定服务端事件;若需要周期逻辑,
    将 ``tick_interval`` 设为大于 0 的 tick 间隔并重写 ``on_tick``,
    ``PlayerKit`` 会按间隔回调。生命周期由 ``PlayerKit`` 统一管理。
    """

    # 0 表示无需周期 tick;否则为 on_tick 的调用间隔(tick)
    tick_interval = 0  # type: int

    def __init__(self, player_id):
        # type: (str) -> None
        EventListenerService.__init__(self, GetMCServerEventBus())
        self.player_id = player_id
        self.enable_listeners()

    def on_tick(self):
        # type: () -> None
        """按 ``tick_interval`` 周期调用,默认无操作。"""
        pass

    def destroy(self):
        # type: () -> None
        self.disable_listeners()
