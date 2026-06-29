# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server.item import ItemExists
from skybluetech_scripts.tooldelta.api.server.player import (
    GetPlayerMainhandItem,
    SpawnItemToPlayerCarried,
    GiveItem,
    GetSelectedSlot,
    SetInventorySlotItemCount,
)
from skybluetech_scripts.skybluetech.common.define.global_config import BUCKET_VOLUME
from skybluetech_scripts.skybluetech.common.machinery_def.basic.fluid_container import (
    K_FLUID_ID,
    K_FLUID_VOLUME,
    K_MAX_VOLUME,
)
from .gui_ctrl import GUIControl

# 浮点传输（管道/机器分量产出）可能留下极小残留体积, 低于该阈值视为空,
# 避免出现"显示 0mB 却仍占用流体类型, 导致其它流体倒不进来"的情况。
FLUID_VOLUME_EPSILON = 1e-6


class FluidContainer(object):
    """
    可存储单种流体的机器基类。

    类属性:
        fluid_io_mode (tuple[int, int, int, int, int, int]): 流体容器六个面的输入输出模式, -1:兼容 0:输入 1:输出 其他:无
        max_fluid_volume (float): 最多可存储流体容量
        allow_player_use_bucket_interact (bool): 是否允许玩家直接使用桶交互
        allow_player_use_bucket_push (bool): 是否允许玩家直接使用桶装填流体
        allow_player_use_bucket_pull (bool): 是否允许玩家直接使用桶取出流体

    覆写:
        - `__init__`
    """

    fluid_io_mode = (2, 2, 2, 2, 2, 2)  # type: tuple[int, int, int, int, int, int]
    max_fluid_volume = 1000
    allow_player_use_bucket_interact = True
    allow_player_use_bucket_push = True
    allow_player_use_bucket_pull = True

    def __init__(self, dim, x, y, z, block_entity_data):
        self.dim = dim
        self.xyz = (x, y, z)
        # if self.fluid_io_fix_mode == 1:
        #     self.fluid_io_mode = FixIOModeByCardinalFacing(
        #         dim, x, y, z, self.fluid_io_mode
        #     )
        # elif self.fluid_io_fix_mode == 2:
        #     self.fluid_io_mode = FixIOModeByDirection(dim, x, y, z, self.fluid_io_mode)
        self.bdata = block_entity_data
        self.bdata[K_MAX_VOLUME] = self.max_fluid_volume  # TODO: 改到 OnPlaced
        self._cached_fluid_id = self.bdata[K_FLUID_ID]
        self._cached_fluid_volume = self.bdata[K_FLUID_VOLUME] or 0.0
        if self._cached_fluid_id is None or self._cached_fluid_volume <= 0:
            self._cached_fluid_id = self.bdata[K_FLUID_ID] = None
            self._cached_fluid_volume = self.bdata[K_FLUID_VOLUME] = 0.0

    def AddFluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> tuple[bool, float]
        """
        添加流体。

        Args:
            fluid_id (str): 流体类型
            fluid_volume (float): 流体容量

        Returns:
            tuple[bool, float]: 是否添加成功, 添加的流体容量
        """
        if fluid_id is None or fluid_volume is None or fluid_volume <= 0:
            return False, fluid_volume
        my_fluid_id = self.fluid_id
        if my_fluid_id is None:
            added_fluid_volume = min(self.max_fluid_volume, fluid_volume)
            if added_fluid_volume <= 0:
                return False, fluid_volume
            self.fluid_id = fluid_id
            self.fluid_volume = added_fluid_volume
            self._on_added_fluid(fluid_id, added_fluid_volume)
            return True, max(0, fluid_volume - added_fluid_volume)
        elif fluid_id != my_fluid_id:
            return False, fluid_volume
        else:
            orig_volume = self.fluid_volume
            free_volume = self.max_fluid_volume - orig_volume
            if free_volume <= 0:
                if orig_volume > self.max_fluid_volume:
                    self.fluid_volume = self.max_fluid_volume
                return False, fluid_volume
            added_fluid_volume = min(free_volume, fluid_volume)
            self.fluid_volume = orig_volume + added_fluid_volume
            if added_fluid_volume > 0:
                self._on_added_fluid(fluid_id, added_fluid_volume)
            # 我们不知道 _on_added_fluid 时容器流体体积有没有被改变
            # 所以不能使用 new_volume 代替 self.fluid_volume
            # self._reset_send_fluid_retries()
            return self.fluid_volume != orig_volume, max(
                0, fluid_volume - added_fluid_volume
            )

    def OutputFluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> tuple[bool, float]
        """
        产出流体。

        Args:
            fluid_id (str): 流体类型
            fluid_volume (float): 流体容量

        Returns:
            tuple[bool, float]: 是否产出成功, 产出的流体容量
        """
        # 暂时直接调用 AddFluid
        return self.AddFluid(fluid_id, fluid_volume)

    def CanAddFluid(self, fluid_id):
        # type: (str) -> bool
        """
        容器能否添加指定种类的流体。

        Args:
            fluid_id (str): 流体类型

        Returns:
            bool
        """
        if fluid_id is None:
            return False
        return self.fluid_id is None or (
            fluid_id == self.fluid_id and self.fluid_volume < self.max_fluid_volume
        )

    def OnFluidSlotUpdate(self):
        "流体内容更新时调用。"
        pass

    def OnAddedFluid(self, fluid_id, added_fluid_volume):
        # type: (str, float) -> None
        "容器内流体体积已经增加时调用。"
        pass

    def OnReducedFluid(self, fluid_id, reduced_fluid_volume):
        # type: (str, float) -> None
        "容器内流体体积已经减少时调用。"
        pass

    def on_player_interact_with_bucket(self, player_id, test=False):
        # type: (str, bool) -> bool
        from ...tools.glass_tube import IsGlassTube

        if not self.allow_player_use_bucket_interact:
            return False
        item = GetPlayerMainhandItem(player_id)
        if item is None:
            return False
        elif IsGlassTube(item):
            return self.on_player_interact_with_glass_tube(player_id, item, test)
        elif (
            item.GetBasicInfo().itemType == "bucket"
            or "skybluetech:liquid_bucket" in item.GetBasicInfo().tags
        ):
            # TODO: 假设玩家都使用铁桶
            if test:
                return True
            elif item.newItemName == "minecraft:bucket":
                if not self.allow_player_use_bucket_pull:
                    return False
                if self.fluid_id is not None and self.fluid_volume >= BUCKET_VOLUME:
                    bucket_id = self.fluid_id + "_bucket"
                    if ItemExists(bucket_id):
                        orig_fluid_id = self.fluid_id
                        self.fluid_volume -= BUCKET_VOLUME
                        if self.fluid_volume <= 0:
                            self.fluid_id = None
                        SetInventorySlotItemCount(
                            player_id, GetSelectedSlot(player_id), item.count - 1
                        )
                        GiveItem(player_id, Item(bucket_id, count=1))
                        self._on_reduced_fluid(orig_fluid_id, BUCKET_VOLUME)
            else:
                if not self.allow_player_use_bucket_push:
                    return False
                fluid_id = item.newItemName
                if fluid_id.endswith("_bucket"):
                    fluid_id = fluid_id[: -len("_bucket")]
                if self.CanAddFluid(fluid_id) and ItemExists(fluid_id):
                    if self.max_fluid_volume - self.fluid_volume >= BUCKET_VOLUME:
                        if self.fluid_id is None:
                            self.fluid_id = fluid_id
                        self.fluid_volume += BUCKET_VOLUME
                        SetInventorySlotItemCount(
                            player_id, GetSelectedSlot(player_id), item.count - 1
                        )
                        SpawnItemToPlayerCarried(
                            player_id, Item("minecraft:bucket", count=1)
                        )
                        self._on_added_fluid(fluid_id, BUCKET_VOLUME)
            if isinstance(self, GUIControl):
                self.CallSync()
            return True
        else:
            return False

    def on_player_interact_with_glass_tube(self, player_id, item, test=False):
        # type: (str, Item, bool) -> bool
        from ...tools.glass_tube import (
            GetTubeContent,
            ApplyTubeContent,
            GLASS_TUBE_MAX_VOLUME,
        )

        if test:
            return True
        tube_fluid_id, tube_volume = GetTubeContent(item)
        changed = False
        # 优先倒入容器
        if (
            self.allow_player_use_bucket_push
            and tube_fluid_id is not None
            and tube_volume > 0
            and self.CanAddFluid(tube_fluid_id)
        ):
            ok, remaining = self.AddFluid(tube_fluid_id, tube_volume)
            if ok:
                tube_volume = remaining
                if tube_volume <= 0:
                    tube_fluid_id = None
                    tube_volume = 0.0
                changed = True
        # 否则从容器舀出填充试管
        if (
            not changed
            and self.allow_player_use_bucket_pull
            and self.fluid_id is not None
            and self.fluid_volume > 0
            and (tube_fluid_id is None or tube_fluid_id == self.fluid_id)
        ):
            pulled = min(GLASS_TUBE_MAX_VOLUME - tube_volume, self.fluid_volume)
            if pulled > 0:
                container_fluid_id = self.fluid_id
                self.fluid_volume -= pulled
                tube_fluid_id = container_fluid_id
                tube_volume += pulled
                self._on_reduced_fluid(container_fluid_id, pulled)
                changed = True
        if changed:
            ApplyTubeContent(player_id, item, tube_fluid_id, tube_volume)
        return True

    def _on_added_fluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> None
        self.OnAddedFluid(fluid_id, fluid_volume)
        self._on_fluid_slot_update()
        if isinstance(self, GUIControl):
            self.CallSync()

    def _on_reduced_fluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> None
        self.OnReducedFluid(fluid_id, fluid_volume)
        self._on_fluid_slot_update()
        if isinstance(self, GUIControl):
            self.CallSync()

    def _on_fluid_slot_update(self):
        # type: () -> None
        # self._reset_send_fluid_retries()
        self.OnFluidSlotUpdate()

    @property
    def fluid_id(self):
        # type: () -> str | None
        return self._cached_fluid_id

    @fluid_id.setter
    def fluid_id(self, value):
        # type: (str | None) -> None
        self._cached_fluid_id = self.bdata[K_FLUID_ID] = value
        if value is None:
            self._cached_fluid_volume = self.bdata[K_FLUID_VOLUME] = 0.0

    @property
    def fluid_volume(self):
        # type: () -> float
        return self._cached_fluid_volume

    @fluid_volume.setter
    def fluid_volume(self, value):
        # type: (float) -> None
        if value is None or value <= FLUID_VOLUME_EPSILON:
            value = 0.0
            if self._cached_fluid_id is not None:
                self.fluid_id = None
        self._cached_fluid_volume = self.bdata[K_FLUID_VOLUME] = value
