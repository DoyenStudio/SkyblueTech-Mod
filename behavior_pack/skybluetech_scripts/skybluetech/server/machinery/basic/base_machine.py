# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from skybluetech_scripts.tooldelta.extensions.facing_utils import (
    get_relative_facing,
    get_relative_facing_by_facing_direction,
)
from skybluetech_scripts.skybluetech.common.define.facing import FACING_EN, OPPOSITE_FACING
from skybluetech_scripts.skybluetech.common.machinery_def.basic.base_machine import (
    K_DEACTIVE_FLAGS,
    K_STORE_RF,
)
from skybluetech_scripts.tooldelta.events.server.block import (
    ServerEntityTryPlaceBlockEvent,
)

from ..core.event_dispatcher import MachineEventDispatcher


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


    def __init__(self, dim, x, y, z, block_entity_data):
        "初始化机器坐标、方块实体数据和事件 handler。"
        self.bdata = block_entity_data
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.xyz = (x, y, z)
        self.handler = MachineEventDispatcher()
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


    # ==== API ====

    def GetRelativeFacing(self, absolute_face):
        # type: (str) -> str | None
        "将机器被接触的绝对面转为相对面；方向缺失或无效时返回 None。"
        states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(self.xyz, self.dim) or {}
        try:
            if "minecraft:facing_direction" in states:
                return get_relative_facing_by_facing_direction(
                    states["minecraft:facing_direction"], absolute_face
                )
            return get_relative_facing(
                states.get("minecraft:cardinal_direction"), absolute_face
            )
        except (ValueError, TypeError):
            return None

    def GetRelativeFacingFromAccessFacing(self, access_facing):
        # type: (int) -> str | None
        "接入方向指向机器，先取反得到机器被接触的面。"
        if access_facing not in FACING_EN:
            return None
        return self.GetRelativeFacing(FACING_EN[OPPOSITE_FACING[access_facing]])

    @staticmethod
    def _filter_slots_for_face(slots, slots_by_face, relative_face):
        # type: (tuple[int, ...], dict[str, tuple[int, ...]] | None, str | None) -> tuple[int, ...]
        "分面白名单只缩小原有槽位范围，保留原有顺序，不修改类属性。"
        if slots_by_face is None:
            return tuple(slots)
        if relative_face is None:
            return ()
        allowed_slots = slots_by_face.get(relative_face, ())
        return tuple(slot for slot in slots if slot in allowed_slots)

    def AddPower(self, rf):
        # type: (int) -> tuple[bool, int]
        """
        为自身增加能量。

        Args:
            rf (int): 能量

        Returns:
            tuple[bool, int]: 数值是否变动, 溢出的能量
        """
        from .gui_ctrl import GUIControl

        store_rf = self.store_rf
        if store_rf >= self.store_rf_max:
            return False, rf
        overflow = max(0, self.store_rf + rf - self.store_rf_max)
        if overflow > 0:
            self.store_rf = self.store_rf_max
        else:
            self.store_rf += rf
        if isinstance(self, GUIControl):
            self.CallSync()
        return True, overflow

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

    def TakeoutPower(self, rf):
        # type: (int) -> int
        """
        从自身中取出能量。

        Args:
            rf (int): 能量

        Returns:
            int: 实际取出的能量
        """
        store_rf = self.store_rf
        if rf <= store_rf:
            self.store_rf -= rf
            return rf
        else:
            self.store_rf = 0
            return store_rf

    def GivebackPower(self, rf):
        # type: (int) -> None
        """
        返还从 TakeoutPower 取出的能量。

        Args:
            rf (int): 返还的能量, 不应大于取走能量值
        """
        self.store_rf += rf

    def SetDeactiveFlag(self, flag, flush=True):
        # type: (int, bool) -> None
        "设置停机标志; flush 控制是否立即刷新机器工作外观。"
        self.deactive_flags |= flag
        self.handler.CallOnSetDeactiveFlagHandlers(flag, flush)
        self.handler.CallOnDeactiveFlagsChangedHandlers(flush)

    def UnsetDeactiveFlag(self, flag, flush=True):
        # type: (int, bool) -> None
        "取消停机标志; flush 控制是否立即刷新机器工作外观。"
        if not self.HasDeactiveFlag(flag):
            return
        self.deactive_flags &= ~flag
        self.handler.CallOnUnsetDeactiveFlagHandlers(flag, flush)
        self.handler.CallOnDeactiveFlagsChangedHandlers(flush)

    def HasDeactiveFlag(self, flag):
        # type: (int) -> bool
        """
        是否拥有某一停机标志。

        Args:
            flag (int): 标志位

        Returns:
            bool: 是否拥有该停机标志
        """
        return self.deactive_flags & flag != 0

    def FlushDeactiveFlags(self):
        # type: () -> None
        "刷新所有订阅停机状态的组件。"
        self.handler.CallOnDeactiveFlagsChangedHandlers(True)

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
        self.handler.CallOnDeactiveFlagsChangedHandlers()

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
        "值比对早退: 能量值没变化时跳过 bdata 写入, 避免每 tick 无谓触发引擎同步写(实测 __setitem__ 约 50us/次)。"
        if (self.bdata[K_STORE_RF] or 0) != value:
            self.bdata[K_STORE_RF] = value

    def __hash__(self):
        return hash((self.dim, self.x, self.y, self.z))
