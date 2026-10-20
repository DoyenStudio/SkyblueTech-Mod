# coding=utf-8
"""加载通知与机器操作事件。事件的监听侧仍由原有事件类型决定。"""
from ..events.general import SkyblueTechClientLoaded, SkyblueTechServerLoaded
from ..events.machinery.basic import MachineryOperationC2S
from ..events.misc.transmitter_settings import TransmitterSwitchAccessMode

_server_loaded = False
_client_loaded = False


def IsServerLoaded():
    """本侧服务端业务是否已完成加载通知；模块存在不等于业务已就绪。"""
    return _server_loaded


def IsClientLoaded():
    """本侧客户端业务是否已完成加载通知。"""
    return _client_loaded


__all__ = [
    "SkyblueTechClientLoaded", "SkyblueTechServerLoaded",
    "MachineryOperationC2S", "TransmitterSwitchAccessMode", "IsServerLoaded", "IsClientLoaded",
]
