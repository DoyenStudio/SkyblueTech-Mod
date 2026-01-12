
from ..internal import ServerComp, ClientComp, ClientLevelId, ServerLevelId, inClientEnv, inServerEnv
from ..general import ClientUninitCallback, ServerUninitCallback

# TYPE_CHECKING
if 0:
    from typing import Callable, Any, ParamSpec
    from mod.common.utils.timer import CallLater
    PT = ParamSpec("PT")
# TYPE_CHECKING END

cTimerPool = set() # type: set[CallLater]
sTimerPool = set() # type: set[CallLater]

def ExecLater(t, func, *args, **kwargs):
    # type: (float, Callable, Any, Any) -> None
    "执行延迟方法"
    if inServerEnv():
        LaterFunc = ServerComp.CreateGame(ServerLevelId).AddTimer
        pool = sTimerPool
    elif inClientEnv():
        LaterFunc = ClientComp.CreateGame(ClientLevelId).AddTimer
        pool = cTimerPool
    else:
        raise Exception("Not in client or server env")
    timer = LaterFunc(t, func, *args, **kwargs) # pyright: ignore[reportArgumentType]
    pool.add(timer)

def Delay(t):
    # type: (float) -> Callable[[Callable[PT, Any]], Callable[PT, Any]]
    """
    将方法固定作为延时方法
    
    将延迟设置为 0 即下一 tick 执行。
    """
    def wrapper(func):
        # type: (Callable[PT, Any]) -> Callable[PT, Any]
        def inner(*args, **kwargs):
            ExecLater(t, func, *args, **kwargs)
        inner.__name__ = func.__module__ + "." + func.__name__
        return inner
    return wrapper

def Repeat(t):
    # type: (float) -> Callable[[Callable[PT, Any]], Callable[PT, Any]]
    """
    将方法固定作为定时执行方法
    """
    def wrapper(func):
        # type: (Callable[PT, Any]) -> Callable[PT, Any]
        def inner(*args, **kwargs):
            if inClientEnv():
                game = ClientComp.CreateGame(ServerLevelId)
                pool = cTimerPool
            elif inServerEnv():
                game = ServerComp.CreateGame(ServerLevelId)
                pool = sTimerPool
            else:
                raise RuntimeError("Not in client or server env")
            timer = game.AddRepeatedTimer(t, func, *args, **kwargs) # pyright: ignore[reportArgumentType]
            pool.add(timer)
        inner.__name__ = func.__module__ + "." + func.__name__
        return inner
    return wrapper

@ServerUninitCallback()
def onServerUninit():
    game = ServerComp.CreateGame(ServerLevelId)
    for timer in sTimerPool:
        game.CancelTimer(timer)
    sTimerPool.clear()

@ClientUninitCallback()
def onClientUninit():
    game = ClientComp.CreateGame(ClientLevelId)
    for timer in cTimerPool:
        game.CancelTimer(timer)
    cTimerPool.clear()


AsDelayFunc = Delay
AsTimerFunc = Repeat

__all__ = [
    "ExecLater",
    "Delay",
    "Repeat",
    "AsDelayFunc",
    "AsTimerFunc"
]
