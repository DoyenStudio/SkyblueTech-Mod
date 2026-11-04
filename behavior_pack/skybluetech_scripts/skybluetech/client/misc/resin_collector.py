# coding=utf-8
import random

from skybluetech_scripts.tooldelta.events.client import ClientBlockUseEvent
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter

from ...common.define.id_enum import RESIN_COLLECTOR, Machinery

limiter = PlayerRateLimiter(0.2)


@ClientBlockUseEvent.Listen()
def onClientBlockUse(event):
    # type: (ClientBlockUseEvent) -> None
    if event.blockName in (
        RESIN_COLLECTOR, Machinery.RESIN_COLLECTOR_OUTPUTER
    ) and not limiter.record(event.playerId):
        event.cancel()
