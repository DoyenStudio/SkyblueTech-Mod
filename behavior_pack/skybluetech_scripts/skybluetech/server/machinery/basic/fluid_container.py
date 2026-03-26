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
from ....common.define.global_config import BUCKET_VOLUME
from ....common.machinery_def.fluid_container import (
    K_FLUID_ID,
    K_FLUID_VOLUME,
    K_MAX_VOLUME,
)
from .gui_ctrl import GUIControl
from .utils import FixIOModeByCardinalFacing, FixIOModeByDirection


class FluidContainer(object):
    """
    可存储单种流体的机器基类。

    类属性:
        fluid_io_mode (tuple[int, int, int, int, int, int]): 流体输入输出模式, -1:兼容 0:输入 1:输出 其他:无
        max_fluid_volume (float): 最多可存储流体容量
        fluid_io_fix_mode (int): 使用 1 时调用 FixIOModeByCardinalFacing; 使用 2 时调用 FixIOModeByDirection; 其他则不适用修复
        allow_player_use_bucket_interact (bool): 是否允许玩家直接使用桶交互
        allow_player_use_bucket_push (bool): 是否允许玩家直接使用桶装填流体
        allow_player_use_bucket_pull (bool): 是否允许玩家直接使用桶取出流体

    需要调用 `__init__()`

    覆写: `OnTicking`, `OnTryActivate`
    """

    fluid_io_mode = (2, 2, 2, 2, 2, 2)  # type: tuple[int, int, int, int, int, int]
    max_fluid_volume = 1000
    fluid_io_fix_mode = 1
    allow_player_use_bucket_interact = True
    allow_player_use_bucket_push = True
    allow_player_use_bucket_pull = True

    def __init__(self, dim, x, y, z, block_entity_data):
        self.dim = dim
        self.xyz = (x, y, z)
        if self.fluid_io_fix_mode == 1:
            self.fluid_io_mode = FixIOModeByCardinalFacing(
                dim, x, y, z, self.fluid_io_mode
            )
        elif self.fluid_io_fix_mode == 2:
            self.fluid_io_mode = FixIOModeByDirection(dim, x, y, z, self.fluid_io_mode)
        self.bdata = block_entity_data
        self.bdata[K_MAX_VOLUME] = self.max_fluid_volume  # TODO: 改到 OnPlaced
        self._cached_fluid_id = self.bdata[K_FLUID_ID]
        self._cached_fluid_volume = self.bdata[K_FLUID_VOLUME] or 0.0

    def AddFluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> tuple[bool, float]
        if isinstance(self, GUIControl):
            self.OnSync()
        my_fluid_id = self.fluid_id
        if my_fluid_id is None:
            self.fluid_id = fluid_id
            self.fluid_volume = fluid_volume
            self.onAddedFluid(fluid_id, fluid_volume)
            return True, max(0, fluid_volume - self.max_fluid_volume)
        elif fluid_id != my_fluid_id:
            return False, fluid_volume
        else:
            orig_volume = self.fluid_volume
            new_volume = self.fluid_volume = min(
                self.max_fluid_volume, orig_volume + fluid_volume
            )
            added_fluid_volume = new_volume - orig_volume
            if added_fluid_volume > 0:
                self.onAddedFluid(fluid_id, new_volume - orig_volume)
            # 我们不知道 onAddedFluid 时容器流体体积有没有被改变
            # 所以不能使用 new_volume 代替 self.fluid_volume
            # self._reset_send_fluid_retries()
            return self.fluid_volume != orig_volume, max(
                0, fluid_volume - added_fluid_volume
            )

    def OutputFluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> tuple[bool, float]
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
        return self.fluid_id is None or (
            fluid_id == self.fluid_id and self.fluid_volume < self.max_fluid_volume
        )

    def RequireFluid(self, req_fluid_id, req_fluid_volume, strict_volume=False):
        # type: (str | None, float | None, bool) -> tuple[bool, str, float]
        # 返回: 获取是否成功, 获取到的流体 ID, 获取到的流体容量
        fid = self.fluid_id
        v = self.fluid_volume
        if req_fluid_id is None or req_fluid_id == fid:
            if fid is None:
                return False, "", 0.0
            if req_fluid_volume is None:
                self.fluid_id = None
                self.fluid_volume = 0.0
                self.onReducedFluid(fid, v)
                return True, fid, v
            else:
                if req_fluid_volume <= v:
                    self.fluid_volume = v - req_fluid_volume
                    if self.fluid_volume <= 0:
                        self.fluid_id = None
                    self.onReducedFluid(fid, v)
                    return True, fid, v
                elif not strict_volume:
                    self.fluid_volume = v - req_fluid_volume
                    if self.fluid_volume <= 0:
                        self.fluid_id = None
                    self.onReducedFluid(fid, req_fluid_volume)
                    return True, fid, req_fluid_volume
                else:
                    return False, "", 0.0
        else:
            return False, "", 0.0

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

    def onAddedFluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> None
        self.OnAddedFluid(fluid_id, fluid_volume)
        self.onFluidSlotUpdate()
        if isinstance(self, GUIControl):
            self.OnSync()

    def onReducedFluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> None
        # self.SelfRequireFluid()
        self.OnReducedFluid(fluid_id, fluid_volume)
        self.onFluidSlotUpdate()
        if isinstance(self, GUIControl):
            self.OnSync()

    def onFluidSlotUpdate(self):
        # type: () -> None
        # self._reset_send_fluid_retries()
        self.OnFluidSlotUpdate()

    def ifPlayerInteractWithBucket(self, player_id, test=False):
        # type: (str, bool) -> bool
        if not self.allow_player_use_bucket_interact:
            return False
        item = GetPlayerMainhandItem(player_id)
        if item is None:
            return False
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
                        if self.fluid_volume == 0:
                            self.fluid_id = None
                        SetInventorySlotItemCount(
                            player_id, GetSelectedSlot(player_id), item.count - 1
                        )
                        GiveItem(player_id, Item(bucket_id, count=1))
                        self.onReducedFluid(orig_fluid_id, BUCKET_VOLUME)
            else:
                if not self.allow_player_use_bucket_push:
                    return False
                fluid_id = item.newItemName.replace("_bucket", "")
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
                        self.onAddedFluid(fluid_id, BUCKET_VOLUME)
            if isinstance(self, GUIControl):
                self.OnSync()
            return True
        else:
            return False

    @property
    def fluid_id(self):
        # type: () -> str | None
        return self._cached_fluid_id

    @fluid_id.setter
    def fluid_id(self, value):
        # type: (str | None) -> None
        self._cached_fluid_id = self.bdata[K_FLUID_ID] = value

    @property
    def fluid_volume(self):
        # type: () -> float
        return self._cached_fluid_volume

    @fluid_volume.setter
    def fluid_volume(self, value):
        # type: (float) -> None
        self._cached_fluid_volume = self.bdata[K_FLUID_VOLUME] = value
