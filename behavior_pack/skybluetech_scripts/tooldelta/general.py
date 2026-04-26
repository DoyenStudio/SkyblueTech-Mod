# coding=utf-8
#
from .internal import SetClient, SetServer


# TYPE_CHECKING
if 0:
    from typing import Callable, TypeVar
    from .mod_server import ToolDeltaModServer as Server
    from .mod_client import ToolDeltaModClient as Client

    FuncT = TypeVar("FuncT", bound="Callable[[], None]")
# TYPE_CHECKING END

extra_server_init_register_funcs = {}  # type: dict[int, set[Callable[[], None]]]
extra_client_init_register_funcs = {}  # type: dict[int, set[Callable[[], None]]]
extra_server_uninit_register_funcs = {}  # type: dict[int, set[Callable[[], None]]]
extra_client_uninit_register_funcs = {}  # type: dict[int, set[Callable[[], None]]]


def run_by_priority(funcs):
    # type: (dict[int, set[Callable[[], None]]]) -> None
    for _, fns in sorted(funcs.items(), key=lambda x: x[0], reverse=True):
        for func in fns:
            func()


def InitClient(client):
    # type: (Client) -> None
    "在客户端类初始化时调用"
    SetClient(client)
    run_by_priority(extra_client_init_register_funcs)


def UninitClient(client):
    # type: (Client) -> None
    "在客户端类销毁时调用"
    run_by_priority(extra_client_uninit_register_funcs)


def InitServer(server):
    # type: (Server) -> None
    "在服务端类初始化时调用"
    SetServer(server)
    run_by_priority(extra_server_init_register_funcs)


def UninitServer(server):
    # type: (Server) -> None
    "在服务端类销毁时调用"
    run_by_priority(extra_server_uninit_register_funcs)


def ServerInitCallback(priority=0):
    "添加服务端初始化时注册的函数"

    def decorator(func):
        # type: (FuncT) -> FuncT
        extra_server_init_register_funcs.setdefault(priority, set()).add(func)
        return func

    return decorator


def ClientInitCallback(priority=0):
    "添加客户端初始化时注册的函数"

    def decorator(func):
        # type: (FuncT) -> FuncT
        extra_client_init_register_funcs.setdefault(priority, set()).add(func)
        return func

    return decorator


def ServerUninitCallback(priority=0):
    "添加服务端销毁时注册的函数"

    def decorator(func):
        # type: (FuncT) -> FuncT
        extra_server_uninit_register_funcs.setdefault(priority, set()).add(func)
        return func

    return decorator


def ClientUninitCallback(priority=0):
    "添加客户端销毁时注册的函数"

    def decorator(func):
        # type: (FuncT) -> FuncT
        extra_client_uninit_register_funcs.setdefault(priority, set()).add(func)
        return func

    return decorator


__all__ = [
    "ClientInitCallback",
    "ClientUninitCallback",
    "ServerInitCallback",
    "ServerUninitCallback",
]
