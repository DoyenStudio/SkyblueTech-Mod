# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from ...common.events.misc.transmitter_registry import (
    TransmitterRegistryRequest,
    TransmitterRegistrySnapshot,
)
from ..export.transmitters import _get_snapshot

_limiter = PlayerRateLimiter(0.5)


@TransmitterRegistryRequest.Listen()
def on_registry_request(event):
    if _limiter.record(event.player_id):
        TransmitterRegistrySnapshot(_get_snapshot()).send(event.player_id)
