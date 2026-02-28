# coding=utf-8
from ..server.machinery.pool import GetMachineStrict


def GetEnergyOfMachine(dimension, x, y, z):
    # type: (int, int, int, int) -> tuple[int, int]
    """
    获取某一机器方块所储存的能量和最大能量。

    Args:
        dimension (int): 维度 ID
        x (int): x 坐标
        y (int): y 坐标
        z (int): z 坐标

    Raises:
        Exception: 所给坐标不是机器/为非能量型机器

    Returns:
        tuple[int, int]: 当前能量值, 最大能量值
    """
    m = GetMachineStrict(dimension, x, y, z)
    if m is None:
        raise Exception("Not a machine at pos [%d] ~ %d, %d, %d" % (dimension, x, y, z))
    if m.is_non_energy_machine:
        raise Exception(
            "Not an energy machine at pos [%d] ~ %d, %d, %d" % (dimension, x, y, z)
        )
    return m.store_rf, m.store_rf_max


def AddEnergyForMachine(dimension, x, y, z, rf):
    # type: (int, int, int, int, int) -> int
    """
    为机器添加能量。

    Args:
        dimension (int): 维度 ID
        x (int): x 坐标
        y (int): y 坐标
        z (int): z 坐标
        rf (int): 能源值

    Returns:
        int: 溢出的能量
    """
    m = GetMachineStrict(dimension, x, y, z)
    if m is None or m.is_non_energy_machine:
        return -1
    _, overflow = m.AddPower(rf)
    return overflow


def MachineIsWorking(dimension, x, y, z):
    # type: (int, int, int, int) -> bool
    """
    判断机器是否正在工作。如果不是可工作机器将抛出异常。

    Args:
        dimension (int): 维度 ID
        x (int): x 坐标
        y (int): y 坐标
        z (int): z 坐标

    Raises:
        Exception: 所给坐标不是机器/为非能量型机器

    Returns:
        bool: 机器是否正在工作
    """
    m = GetMachineStrict(dimension, x, y, z)
    if m is None:
        raise Exception("Not a machine at pos [%d] ~ %d, %d, %d" % (dimension, x, y, z))
    return m.IsActive()
