# coding=utf-8
# TYPE_CHECKING
if 0:
    from typing import Any
# TYPE_CHECKING END

NBT_BYTE = 1
NBT_SHORT = 2
NBT_INT = 3
NBT_LONG = 4
NBT_FLOAT = 5
NBT_DOUBLE = 6
NBT_BYTE_ARRAY = 7
NBT_STRING = 8
NBT_LIST = 9
NBT_COMPOUND = 10
NBT_INT_ARRAY = 11


def Tp(typ, val):
    return {"__type__": typ, "__value__": val}


def Byte(val):
    # type: (bool) -> dict
    return Tp(NBT_BYTE, val)


def Short(val):
    # type: (int) -> dict
    return Tp(NBT_SHORT, val)


def Int(val):
    # type: (int) -> dict
    return Tp(NBT_INT, val)


def Long(val):
    # type: (int) -> dict
    return Tp(NBT_LONG, val)


def Float(val):
    # type: (float) -> dict
    return Tp(NBT_FLOAT, val)


def Double(val):
    # type: (float) -> dict
    return Tp(NBT_DOUBLE, val)


def ByteArray(val):
    # type: (list) -> dict
    return Tp(NBT_BYTE_ARRAY, val)


def String(val):
    # type: (str) -> dict
    return Tp(NBT_STRING, val)


def List(val):
    # type: (list) -> dict
    """WARNING: 一些地方可以直接使用 list。"""
    return Tp(NBT_LIST, val)


def GenericList(val):
    # type: (list) -> list
    return val


def Compound(val):
    # type: (dict) -> dict
    """WARNING: 大部分地方都可以直接使用 dict。"""
    return Tp(NBT_COMPOUND, val)


def IntArray(val):
    # type: (list) -> dict
    return Tp(NBT_INT_ARRAY, val)


def GetValueWithDefault(nbt, key, default):
    return nbt.get(key, {}).get("__value__", default)


def Py2NBT(arg):
    # type: (Any) -> Any
    """
    将 Python 基本类型转换为 NBT dict。

    Args:
        arg (Any): 传入对象

    Returns:
        _type_: NBT dict
    """
    if isinstance(arg, dict):
        return {k: Py2NBT(v) for k, v in arg.items()}
    elif isinstance(arg, list):
        for list_item in arg:
            if (
                not isinstance(list_item, (int, float, str, bool, dict))
                and list_item is not None
            ):
                raise ValueError(
                    "NBTList can only contain int, float, str, bool, dict, None, not {}".format(
                        list_item
                    )
                )
        return GenericList([Py2NBT(v) for v in arg])
    elif isinstance(arg, int):
        if -32768 <= arg <= 32767:
            return Short(arg)
        elif -2147483648 <= arg <= 2147483647:
            return Int(arg)
        elif -9223372036854775808 <= arg <= 9223372036854775807:
            return Long(arg)
        else:
            return Double(arg)
    elif isinstance(arg, float):
        if -2147483648 <= arg <= 2147483647:
            return Float(arg)
        else:
            return Double(arg)
    elif isinstance(arg, str):
        # str 一定要放在 bytes 上面, 否则会先检测为 bytes
        return String(arg)
    elif isinstance(arg, bytes):
        return ByteArray(list(arg))
    elif isinstance(arg, bool):
        return Byte(arg)
    elif arg is None:
        return None
    else:
        raise ValueError(
            "NBT can only contain int, float, str, bool, dict, list, None, not {}".format(
                arg
            )
        )


def NBT2Py(arg):
    # type: (Any) -> Any
    """
    将 NBT dict 转换为剔除 `__type__` 和 `__value__` Python 对象。
    注意: 这将丢失进一步的数值类型。

    Args:
        arg (Any): NBT dict

    Returns:
        Any: 转换后对象
    """
    if isinstance(arg, list):
        return [NBT2Py(v) for v in arg]
    elif not isinstance(arg, dict):
        return arg
    if "__type__" not in arg:
        return {k: NBT2Py(v) for k, v in arg.items()}
    return NBT2Py(arg["__value__"])
