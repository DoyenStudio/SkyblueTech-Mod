# # coding=utf-8
# #
# 
# from ..internal import InServerEnv
# from ..events.notify import NotifyToClient, NotifyToServer
# from ..events.server.internal import TDRpcCallS2C, TDRpcCallC2SRet
# from ..events.client.internal import TDRpcCallC2S, TDRpcCallS2CRet

# # TYPE_CHECKING
# if 0:
#     from typing import Callable, TypeVar, Any
#     FuncT = TypeVar("FuncT", bound=Callable)
# # TYPE_CHECKING END

# fCCallPool = {} # type: dict[str, Callable]
# fSCallPool = {} # type: dict[str, Callable]


# def ExposeAPI(funcname):
#     # type: (str) -> Callable[[FuncT], FuncT]
#     """
#     拉出函数作为跨端可调函数。

#     Args:
#         funcname (str): 函数标识名
#     """
#     def wrapper(func):
#         if InServerEnv():
#             fSCallPool[funcname] = func
#         else:
#             fCCallPool[funcname] = func
#         return func

#     return wrapper


# def callServer


# def CallAPI(funcname, *args, **kwargs):
#     # type: (str, Any, Any) -> Any
#     """
#     调用跨端可调函数。

#     Args:
#         funcname (str): 函数标识名
#         *args: 函数参数
#         **kwargs: 函数参数

#     Returns:
#         Any: 函数返回值
#     """
#     if InServerEnv():
#         NotifyToServer