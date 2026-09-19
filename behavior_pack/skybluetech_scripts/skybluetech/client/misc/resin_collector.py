# coding=utf-8
import random

from skybluetech_scripts.tooldelta.events.client import ClientBlockUseEvent
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter

from ...common.define.id_enum import RESIN_COLLECTOR

limiter = PlayerRateLimiter(0.2)


@ClientBlockUseEvent.Listen()
def onClientBlockUse(event):
    # type: (ClientBlockUseEvent) -> None
    if event.blockName == RESIN_COLLECTOR and not limiter.record(event.playerId):
        event.cancel()
