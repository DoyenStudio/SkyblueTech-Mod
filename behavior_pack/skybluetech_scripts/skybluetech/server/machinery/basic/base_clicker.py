# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import ServerBlockUseEvent
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter


class BaseClicker(object):
    """
    不具有自定义容器属性但是可被方块点击响应的机器类。
    继承了此类的机器可获得更好的 OnClick() 方法,
    例如, 玩家手持方块点击机器时不再会同时放下方块。

    需要 `__init__()`
    """

    onclick_delay = 0.25

    def __init__(self, dim, x, y, z, block_entity_data):
        self.rate_limiter = PlayerRateLimiter(self.onclick_delay)

    def _revOnClick(self, event):
        # type: (ServerBlockUseEvent) -> None
        if not self.rate_limiter.record(event.playerId):
            return
        self.OnClick(event)

    def OnClick(self, event):
        # type: (ServerBlockUseEvent) -> None
        pass
