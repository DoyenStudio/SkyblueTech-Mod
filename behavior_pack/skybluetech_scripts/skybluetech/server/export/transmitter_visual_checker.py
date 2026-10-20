# coding=utf-8
"""传输网络可视化检查器的服务端注册接口。"""
from skybluetech_scripts.tooldelta.utils.py_comp import py2_unicode

from ..transmitters.base import LogicModule


class _RegisteredTransmitterType:
    def __init__(self, type_id, display_name, logic_module, input_label, output_label):
        # type: (str, str, LogicModule, str, str) -> None
        self.type_id = type_id
        self.display_name = display_name
        self.logic_module = logic_module
        self.input_label = input_label
        self.output_label = output_label


_transmitter_types = []  # type: list[_RegisteredTransmitterType]


def RegisterTransmitterType(
    type_id, display_name, logic_module, input_label="输入", output_label="抽取"
):
    # type: (str, str, LogicModule, str, str) -> None
    """为检查器注册一个 LogicModule, 仅在服务端调用。

    type_id 使用 namespace:name 格式。相同 ID 和实例重复注册会更新显示配置;
    相同 ID 绑定不同实例、同一实例绑定不同 ID 均抛出 ValueError。
    多个类型的管道识别函数同时命中时, 使用最先注册的类型。
    此接口不创建网络, 也不改变 LogicModule 的传输行为。
    """
    if not isinstance(type_id, (str, py2_unicode)):
        raise TypeError("type_id must be a string")
    parts = type_id.split(":")
    if len(parts) != 2 or not all(parts) or type_id.strip() != type_id:
        raise ValueError("type_id must use namespace:name format")
    for label in (display_name, input_label, output_label):
        if not isinstance(label, (str, py2_unicode)) or not label.strip():
            raise ValueError("display_name and endpoint labels must be non-empty strings")
    if not isinstance(logic_module, LogicModule):
        raise TypeError("logic_module must be a LogicModule instance")
    registration = _RegisteredTransmitterType(
        type_id, display_name, logic_module, input_label, output_label
    )
    for index, current in enumerate(_transmitter_types):
        if current.type_id == type_id:
            if current.logic_module is not logic_module:
                raise ValueError("type_id is already bound to another LogicModule")
            _transmitter_types[index] = registration
            return
        if current.logic_module is logic_module:
            raise ValueError("LogicModule is already bound to another type_id")
    _transmitter_types.append(registration)


def _get_transmitter_types():
    # type: () -> tuple[_RegisteredTransmitterType, ...]
    return tuple(_transmitter_types)


__all__ = ["RegisterTransmitterType"]
