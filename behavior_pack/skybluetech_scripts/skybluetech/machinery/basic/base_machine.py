# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.events.server.block import (
    ServerPlaceBlockEntityEvent,
    BlockNeighborChangedServerEvent,
)
from .. import pool
from .gui_ctrl import GUIControl

K_STORE_RF = "store_rf"
K_DEACTIVE_FLAGS = "deactive_flags"


_getWireModule = False

def requireWireModule():
    global _getWireModule, GetNearbyWireNetwork, CallNetworkWake
    if _getWireModule:
        return
    from ...transmitters.wire.logic import (
        GetNearbyWireNetwork,
        CallNetworkWake,
    )
    _getWireModule = True



class BaseMachine(object):
    """
    所有机器方块的基类。
    """
    
    block_name = ""  # type: str
    "方块 ID"
    extra_block_names = () # type: tuple[str, ...]
    "额外可绑定的方块 ID"
    is_non_energy_machine = False
    "机器是否为非能源型机器"
    store_rf_max = 10000  # type: int
    "储存能量的最大值, 需要覆写"
    energy_io_mode = (0, 0, 0, 0, 0, 0) # type: tuple[int, int, int, int, int, int]
    "每个面的能量输入输出模式, 0:输入 1:输出 其他:无"

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        "超类主要用于获取方块实体数据, 设置 bdata(BlockEntityData) 和获取能量属性; 执行 OnLoad()。"
        self.bdata = block_entity_data
        "所储存能量的值"
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        if not self.is_non_energy_machine:
            self.initRFNetwork()
        self.OnLoad()

    # ==== overload ====

    def OnLoad(self):
        # type: () -> None
        """
        父类方法将 self.bdata 中的 BlockEntityData load 到自身;
        并初始化 / 更新红石通量网络信息。
        """
        if not self.is_non_energy_machine:
            self.store_rf = self.bdata[K_STORE_RF] or 0
        self.deactive_flags = self.bdata[K_DEACTIVE_FLAGS] or 0

    def OnPlaced(self, event):
        # type: (ServerPlaceBlockEntityEvent) -> None
        "超类方法用于初始化机器的能源数据。"
        pass

    def OnTicking(self):
        # type: () -> None
        "事件方法, 超类方法什么也不做。"
        return None

    # def OnFakeTicking(self):
    #     # type: () -> bool
    #     "事件方法, 超类方法什么也不做。"
    #     return False

    def OnUnload(self):
        # type: () -> None
        "超类方法, 方块实体被卸载时调用。"
        pass

    def OnDestroy(self):
        # type: () -> None
        "超类方法, 方块被破坏时调用。"

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        "什么也不做。"

    def OnMonitorCheck(self):
        # type: () -> str | None
        return None

    def OnTryActivate(self):
        "覆写方法尝试激活机器。"


    # ==== API ====

    def Dump(self):
        # type: () -> None
        """
        超类方法用于将能量数据 dump 到方块实体。
        覆写时将自身数据 dump 到 block_entity_data 属性。
        """
        if not self.is_non_energy_machine:
            self.bdata[K_STORE_RF] = self.store_rf
        self.bdata[K_DEACTIVE_FLAGS] = self.deactive_flags

    def AddPower(self, rf, is_generator=False, max_limit=None, depth=0):
        # type: (int, bool, int | None, int) -> tuple[bool, int]
        """
        为自身增加能量。

        Args:
            rf (int): 能量
            is_generator (bool): 自身是否为发电机(或供能器), 若是, 则优先向网络输出能量

        Returns:
            tuple[bool, int]: 数值是否变动, 溢出的能量
        """
        if max_limit is None:
            power_overflow = 0
        else:
            power_overflow = max(0, rf - max_limit)
            rf = min(rf, max_limit)
        if is_generator and depth < 4:
            rf = self.addPowerIntoWireNetwork(rf, depth+1)
        power_old = self.store_rf
        power_new = min(power_old + rf, self.store_rf_max)
        self.store_rf = power_new
        power_overflow += power_old + rf - power_new
        return power_new != power_old, power_overflow
    
    def ReducePower(self, rf):
        # type: (int) -> bool
        """
        减少自身能量。

        Args:
            rf (int): 能量

        Returns:
            bool: 数值是否变动
        """
        power_old = self.store_rf
        power_new = max(power_old - rf, 0)
        self.store_rf = power_new
        return power_new != power_old

    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        self.deactive_flags |= flag

    def UnsetDeactiveFlag(self, flag):
        # type: (int) -> None
        self.deactive_flags &= ~flag

    def HasDeactiveFlag(self, flag):
        # type: (int) -> bool
        """
        是否拥有某一停机标志。

        Args:
            flag (int): 标志位

        Returns:
            bool
        """
        return self.deactive_flags & flag != 0

    def IsActive(self):
        # type: () -> bool
        """
        机器是否处于工作状态。

        Returns:
            bool
        """
        return self.deactive_flags == 0

    def IsActiveIgnoreCondition(self, cond):
        # type: (int) -> bool
        """
        机器在排除某种停机标志可能的情况下是否还能工作。

        Args:
            cond (int): 一个或多个停机标志

        Returns:
            bool
        """
        return self.deactive_flags & ~cond == 0

    def ResetDeactiveFlags(self):
        # type: () -> None
        """
        重置所有停机标志, 即将机器设置为工作模式。
        """
        self.deactive_flags = 0

    def initRFNetwork(self):
        # type: () -> None
        "初始化此机器 6 面连接的所有能源线缆。"
        requireWireModule()
        self.rf_networks = GetNearbyWireNetwork(self.dim, self.x, self.y, self.z)
        for network in self.rf_networks:
            if network is not None:
                CallNetworkWake(self.dim, network)

    def addPowerIntoWireNetwork(self, rf, depth=0):
        # type: (int, int) -> int
        """ 在已连接的电缆网络中为机器添加能量。 返回溢出的能量 """
        if self.store_rf > 0:
            rf += self.store_rf
            self.store_rf = 0
        for network in self.rf_networks:
            if network is None:
                continue
            for x, y, z, _ in network.group_appliances:
                machine = pool.GetMachineStrict(self.dim, x, y, z)
                if machine is not None and not machine.is_non_energy_machine:
                    updated, rf = machine.AddPower(rf, False, network.get_power_limit(), depth)
                    if updated and isinstance(machine, GUIControl):
                        machine.OnSync()
                    if rf == 0:
                        break
        return rf

    def __hash__(self):
        return hash((self.dim, self.x, self.y, self.z))
                


