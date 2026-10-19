# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import ServerBlockUseEvent
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter

from .base_machine import BaseMachine


class BaseClicker(BaseMachine):
    """
    不具有自定义容器属性但是可被方块点击响应的机器类。
    继承了此类的机器可订阅经点击限流处理的 handler 事件,
    例如, 玩家手持方块点击机器时不再会同时放下方块。

    覆写:
        - `__init__()`
    """

    onclick_delay = 0.25

    def __init__(self, dim, x, y, z, block_entity_data):
        super(BaseClicker, self).__init__(dim, x, y, z, block_entity_data)
        self.rate_limiter = PlayerRateLimiter(self.onclick_delay)

    def _can_click(self, event):
        # type: (ServerBlockUseEvent) -> bool
        return self.rate_limiter.record(event.playerId)
