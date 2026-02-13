# coding=utf-8
import time
from ..api.timer import ExecLater

if 0:
    from typing import Callable, ParamSpec, TypeVar

    T = TypeVar("T")
    PT = ParamSpec("PT")


class PlayerRateLimiter(object):
    def __init__(self, limit_seconds=0):
        # type: (float) -> None
        self.limit_seconds = limit_seconds
        self._limits = {}  # type: dict[str, float]

    def is_limited(self, player_id):
        # type: (str) -> bool
        last_lmt = self._limits.get(player_id, 0)
        return time.time() - last_lmt < self.limit_seconds

    def get_delta_time(self, player_id):
        # type: (str) -> float
        return time.time() - self._limits.get(player_id, 0)

    def record(self, player_id):
        # type: (str) -> bool
        if self.is_limited(player_id):
            return False
        self._limits[player_id] = time.time()
        self._run_player(player_id)
        return True

    def _run_player(self, player_id):
        ExecLater(self.limit_seconds, self._cancel_delay, player_id)

    def _cancel_delay(self, player_id):
        # type: (str) -> None
        self._limits.pop(player_id, None)


def LimitCallRate(delay):
    def decorator(func):
        # type: (Callable[PT, T]) -> Callable[PT, T | None]
        def wrapper(*args, **kwargs):
            nowtime = time.time()
            if nowtime - decorator.last_launch_time < delay:
                return None
            decorator.last_launch_time = nowtime
            return func(*args, **kwargs)

        return wrapper

    decorator.last_launch_time = 0
    return decorator
