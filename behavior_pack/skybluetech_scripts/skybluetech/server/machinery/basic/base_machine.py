# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.events.server.block import (
    ServerPlaceBlockEntityEvent,
    BlockNeighborChangedServerEvent,
    ServerEntityTryPlaceBlockEvent,
)
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from .gui_ctrl import GUIControl

K_STORE_RF = "store_rf"
K_DEACTIVE_FLAGS = "deactive_flags"


class BaseMachine(object):
    """
    所有机器方块的基类。
    """

    block_name = ""  # type: str
    "方块 ID"
    is_non_energy_machine = False
    "机器是否为非能源型机器"
    store_rf_max = 10000  # type: int
    "储存能量的最大值, 需要覆写"
    energy_io_mode = (0, 0, 0, 0, 0, 0)  # type: tuple[int, int, int, int, int, int]
    "每个面的能量输入输出模式, 0:输入 1:输出 其他:无"
    _extra_block_names = {}  # type: dict[type[BaseMachine], list[str]]
    "额外可绑定的方块 ID"

    __metaclass__ = SuperExecutorMeta

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        "超类主要用于获取方块实体数据, 设置 bdata(BlockEntityData) 和获取能量属性; 执行 OnLoad()。"
        self.bdata = block_entity_data
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self._cached_deactive_flags = None

    @classmethod
    def AddExtraMachineId(cls, id):
        # type: (str) -> None
        "注册额外的方块 ID。"
        cls._extra_block_names.setdefault(cls, []).append(id)

    @classmethod
    def OnPrePlaced(cls, event):
        # type: (ServerEntityTryPlaceBlockEvent) -> None
        "事件方法, 机器被放置前调用, 可 cancel()"
        pass

    def OnPlaced(self, event):
        # type: (ServerPlaceBlockEntityEvent) -> None
        "事件方法, 机器被放置时调用。"
        pass

    def OnTicking(self):
        # type: () -> None
        "事件方法, 方块实体 tick 调用。"
        return None

    # def OnFakeTicking(self):
    #     # type: () -> bool
    #     "事件方法, 超类方法什么也不做。"
    #     return False

    def OnUnload(self):
        # type: () -> None
        "事件方法, 方块实体被卸载时调用。"
        pass

    def OnDestroy(self):
        # type: () -> None
        "事件方法, 方块被破坏时调用。"

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        "事件方法, 邻近方块变化时调用。"

    def OnDeactiveFlagsChanged(self):
        "机器激活状态更改时调用。"
        pass

    def OnTryActivate(self):
        "覆写方法尝试激活机器。"

    # ==== API ====

    def AddPower(self, rf, max_limit=None, passed=None):
        # type: (int, int | None, set[BaseMachine] | None) -> tuple[bool, int]
        """
        为自身增加能量。

        Args:
            rf (int): 能量
            is_generator (bool): 自身是否为发电机(或供能器), 若是, 则优先向网络输出能量

        Returns:
            tuple[bool, int]: 数值是否变动, 溢出的能量
        """
        if passed is None:
            passed = set()
        if max_limit is None:
            power_overflow = 0
        else:
            power_overflow = max(0, rf - max_limit)
            rf = min(rf, max_limit)
        power_old = self.store_rf
        power_new = min(power_old + rf, self.store_rf_max)
        self.store_rf = power_new
        power_overflow += power_old + rf - power_new
        if isinstance(self, GUIControl):
            self.OnSync()
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
        self.OnDeactiveFlagsChanged()

    def UnsetDeactiveFlag(self, flag, flush=True):
        # type: (int, bool) -> None
        # type: (int) -> None
        if not self.HasDeactiveFlag(flag):
            return
        self.deactive_flags &= ~flag
        self.OnDeactiveFlagsChanged()

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

    def FlushDeactiveFlags(self):
        # type: () -> None
        pass

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
        self.OnDeactiveFlagsChanged()

    @property
    def deactive_flags(self):
        # type: () -> int
        if self._cached_deactive_flags is None:
            self._cached_deactive_flags = self.bdata[K_DEACTIVE_FLAGS] or 0
        return self._cached_deactive_flags

    @deactive_flags.setter
    def deactive_flags(self, value):
        # type: (int) -> None
        self._cached_deactive_flags = self.bdata[K_DEACTIVE_FLAGS] = value

    @property
    def store_rf(self):
        # type: () -> int
        return self.bdata[K_STORE_RF] or 0

    @store_rf.setter
    def store_rf(self, value):
        # type: (int) -> None
        self.bdata[K_STORE_RF] = value

    def __hash__(self):
        return hash((self.dim, self.x, self.y, self.z))
