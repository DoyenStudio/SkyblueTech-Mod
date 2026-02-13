# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server.item import ItemExists
from skybluetech_scripts.tooldelta.api.server.player import (
    GetPlayerMainhandItem,
    SpawnItemToPlayerCarried,
    GiveItem,
    GetSelectedSlot,
    SetInventorySlotItemCount,
)
from ...define.global_config import BUCKET_VOLUME
from .gui_ctrl import GUIControl
from .utils import FixIOModeByCardinalFacing, FixIOModeByDirection

K_FLUID_ID = "fluid_id"
K_FLUID_VOLUME = "fluid_vol"


def requireLibraryFunc():
    global RequirePostFluid, PostFluidIntoNetworks
    if requireLibraryFunc._imported:
        return
    from ...transmitters.pipe.logic import RequirePostFluid, PostFluidIntoNetworks

    requireLibraryFunc._imported = True


requireLibraryFunc._imported = False


class FluidContainer(object):
    """
    可存储单种流体的机器基类。

    类属性:
        fluid_io_mode (tuple[int, int, int, int, int, int]): 流体输入输出模式, -1:兼容 0:输入 1:输出 其他:无
        max_fluid_volume (float): 最多可存储流体容量
        fluid_io_fix_mode (int): 使用 1 时调用 FixIOModeByCardinalFacing; 使用 2 时调用 FixIOModeByDirection; 其他则不适用修复
        allow_player_use_bucket (bool): 是否允许玩家直接使用桶与机器进行交互

    需要调用 `__init__()`

    覆写: `OnTicking`, `OnTryActivate`, `Dump`
    """

    fluid_io_mode = (2, 2, 2, 2, 2, 2)  # type: tuple[int, int, int, int, int, int]
    max_fluid_volume = 1000
    fluid_io_fix_mode = 1
    allow_player_use_bucket = True

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        self.dim = dim
        self.xyz = (x, y, z)
        if self.fluid_io_fix_mode == 1:
            self.fluid_io_mode = FixIOModeByCardinalFacing(
                dim, x, y, z, self.fluid_io_mode
            )
        elif self.fluid_io_fix_mode == 2:
            self.fluid_io_mode = FixIOModeByDirection(dim, x, y, z, self.fluid_io_mode)
        self.bdata = block_entity_data
        self.fluid_id = block_entity_data[K_FLUID_ID]  # type: str | None
        self.fluid_volume = block_entity_data[K_FLUID_VOLUME] or 0.0
        self._sending_fluid = True

    def OnTicking(self):
        if self._sending_fluid:
            ok = self.PostFluid()
            if not ok:
                self._sending_fluid = False

    def OnTryActivate(self):
        self._sending_fluid = True

    def Dump(self):
        self.bdata[K_FLUID_ID] = self.fluid_id
        self.bdata[K_FLUID_VOLUME] = self.fluid_volume

    def AddFluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> tuple[bool, float]
        if isinstance(self, GUIControl):
            self.OnSync()
        if self.fluid_id is None:
            self.fluid_id = fluid_id
            self.fluid_volume = fluid_volume
            self.onAddedFluid(self.fluid_id, fluid_volume)
            self.Dump()
            return True, max(0, fluid_volume - self.max_fluid_volume)
        elif fluid_id != self.fluid_id:
            return False, fluid_volume
        else:
            orig_volume = self.fluid_volume
            self.fluid_volume = min(self.max_fluid_volume, orig_volume + fluid_volume)
            added_fluid_volume = self.fluid_volume - orig_volume
            if added_fluid_volume > 0:
                self.onAddedFluid(self.fluid_id, self.fluid_volume - orig_volume)
            if self.fluid_volume == 0:
                self.fluid_id = None
            self._sending_fluid = True
            self.Dump()
            return self.fluid_volume != orig_volume, max(
                0, fluid_volume - added_fluid_volume
            )

    def OutputFluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> tuple[bool, float]
        # 暂时直接调用 AddFluid
        return self.AddFluid(fluid_id, fluid_volume)

    def PostFluid(self):
        # type: () -> bool
        if self.fluid_id is None:
            return False
        orig_volume = self.fluid_volume
        ok, self.fluid_volume = self.tryPostFluid(self.fluid_id, orig_volume)
        if orig_volume > self.fluid_volume:
            self.onReducedFluid(self.fluid_id, orig_volume - self.fluid_volume)
        elif orig_volume < self.fluid_volume:
            self.onAddedFluid(self.fluid_id, self.fluid_volume - orig_volume)
        if self.fluid_volume == 0:
            self.fluid_id = None
        self.Dump()
        return ok

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
        if req_fluid_id is None or req_fluid_id == self.fluid_id:
            fid = self.fluid_id
            v = self.fluid_volume
            if fid is None:
                return False, "", 0.0
            if req_fluid_volume is None:
                self.fluid_id = None
                self.fluid_volume = 0.0
                self.onReducedFluid(fid, v)
                self.Dump()
                return True, fid, v
            else:
                if req_fluid_volume <= self.fluid_volume:
                    self.fluid_volume -= req_fluid_volume
                    if self.fluid_volume <= 0:
                        self.fluid_id = None
                    self.onReducedFluid(fid, v)
                    self.Dump()
                    return True, fid, v
                elif not strict_volume:
                    self.fluid_volume -= req_fluid_volume
                    if self.fluid_volume <= 0:
                        self.fluid_id = None
                    self.onReducedFluid(fid, req_fluid_volume)
                    self.Dump()
                    return True, fid, req_fluid_volume
                else:
                    return False, "", 0.0
        else:
            return False, "", 0.0

    def SelfRequireFluid(self):
        """
        容器自身向网络索取一次流体。
        """
        requireLibraryFunc()
        RequirePostFluid(self.dim, self.xyz)

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
        self.SelfRequireFluid()
        self.OnReducedFluid(fluid_id, fluid_volume)
        self.onFluidSlotUpdate()
        if isinstance(self, GUIControl):
            self.OnSync()

    def onFluidSlotUpdate(self):
        # type: () -> None
        self._sending_fluid = True
        self.OnFluidSlotUpdate()

    def ifPlayerInteractWithBucket(self, player_id, test=False):
        # type: (str, bool) -> bool
        if not self.allow_player_use_bucket:
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
                        self.Dump()
            else:
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
                        self.Dump()
            if isinstance(self, GUIControl):
                self.OnSync()
            return True
        else:
            return False

    def tryPostFluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> tuple[bool, float]
        """
        尝试向容器已连接的管道网络输出流体。
        """
        requireLibraryFunc()
        ok, rest = PostFluidIntoNetworks(
            self.dim, self.xyz, fluid_id, fluid_volume, None
        )
        return ok, rest
