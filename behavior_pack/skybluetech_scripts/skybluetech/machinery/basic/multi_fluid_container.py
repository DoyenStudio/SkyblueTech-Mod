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
from .base_machine import BaseMachine
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


class FluidSlot(object):
    def __init__(self, block_entity_data, index, max_volume):
        # type: (BlockEntityData, int, float) -> None
        self.bdata = block_entity_data
        self.index = index
        self.max_volume = max_volume
        self.k_id = K_FLUID_ID + str(index)
        self.k_vol = K_FLUID_VOLUME + str(index)
        self._cached_fluid_id = block_entity_data[self.k_id]
        self._cached_volume = block_entity_data[self.k_vol] or 0.0

    @property
    def fluid_id(self):
        # type: () -> str | None
        return self._cached_fluid_id

    @fluid_id.setter
    def fluid_id(self, value):
        # type: (str | None) -> None
        self._cached_fluid_id = self.bdata[self.k_id] = value

    @property
    def volume(self):
        # type: () -> float
        return self._cached_volume

    @volume.setter
    def volume(self, value):
        # type: (float) -> None
        self._cached_volume = self.bdata[self.k_vol] = value

    def isFull(self):
        return self.volume >= self.max_volume

    def canMerge(self, fluid_id):
        # type： (str | None) -> bool
        if self.isFull():
            return False
        fid = self.fluid_id
        if fid is None or self.volume == 0 or fluid_id == fid:
            return True
        else:
            return False


class MultiFluidContainer(object):
    """
    可存储多种流体的机器基类。

    类属性:
        fluid_io_mode (tuple[int, int, int, int, int, int]): 每个面的流体输入输出模式, -1:兼容 0:输入 1:输出 其他:无
        fluid_input_slots (set[int]): 可接受输入的流体槽位
        fluid_output_slots (set[int]): 可输出的流体槽位
        fluid_slot_max_volumes (tuple[int, ...]): 每个流体槽最多可存储流体容量
        allow_player_use_bucket (bool): 是否允许玩家直接使用桶与机器进行交互
        fluid_io_fix_mode (int): 使用 1 时调用 FixIOModeByCardinalFacing; 使用 2 时调用 FixIOModeByDirection; 其他则不适用修复

    需要调用 `__init__`

    覆写:
        `Dump`, `OnTryActivate`
    """

    fluid_io_mode = (2, 2, 2, 2, 2, 2)  # type: tuple[int, int, int, int, int, int]
    fluid_input_slots = set()  # type: set[int]
    fluid_output_slots = set()  # type: set[int]
    fluid_slot_max_volumes = (4000, 4000)  # type: tuple[int, ...]
    allow_player_use_bucket = True
    fluid_io_fix_mode = 1

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        self.dim = dim
        self.xyz = (x, y, z)
        self.bdata = block_entity_data
        if self.fluid_io_fix_mode == 1:
            self.fluid_io_mode = FixIOModeByCardinalFacing(
                dim, x, y, z, self.fluid_io_mode
            )
        elif self.fluid_io_fix_mode == 2:
            self.fluid_io_mode = FixIOModeByDirection(dim, x, y, z, self.fluid_io_mode)
        self.fluids = [
            FluidSlot(self.bdata, i, mv)
            for i, mv in enumerate(self.fluid_slot_max_volumes)
        ]
        self._sending_fluid = True

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        return True

    def OnTicking(self):
        if self._sending_fluid:
            res = self.PostFluid()
            if not res:
                self._sending_fluid = False

    def OnTryActivate(self):
        self._sending_fluid = True

    def OutputFluid(self, fluid_id, fluid_volume, slot_pos, is_final):
        # type: (str, float, int, bool) -> tuple[bool, float]
        fluid = self.fluids[slot_pos]
        if fluid.fluid_id is None:
            fluid.fluid_id = fluid_id
        orig_volume = fluid.volume
        new_vol = fluid.volume = orig_volume + fluid_volume
        ok = False
        if new_vol > orig_volume:
            self.onAddedFluid(slot_pos, fluid_id, fluid_volume, is_final)
            ok = True
        elif new_vol < orig_volume:
            self.onReducedFluid(slot_pos, fluid_id, fluid_volume, is_final)
            ok = True
        if fluid.volume > fluid.max_volume:
            overflow_vol = fluid.volume - fluid.max_volume
            fluid.volume = fluid.max_volume
        else:
            overflow_vol = 0
        return ok, overflow_vol

    def AddFluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> tuple[bool, float]
        _orig = fluid_volume
        input_slots = [(i, self.fluids[i]) for i in self.fluid_input_slots]
        last_slot = input_slots[-1][0]
        for slot, fluid in input_slots:
            if fluid.canMerge(fluid_id) and self.IsValidFluidInput(slot, fluid_id):
                if fluid.fluid_id is None or fluid.volume == 0:
                    fluid.fluid_id = fluid_id
                free_volume = fluid.max_volume - fluid.volume
                if fluid_volume <= free_volume:
                    fluid.volume += fluid_volume
                    self.onAddedFluid(slot, fluid_id, fluid_volume, slot == last_slot)
                    return True, 0
                else:
                    fluid.volume = fluid.max_volume
                    fluid_volume -= free_volume
                    self.onAddedFluid(slot, fluid_id, free_volume, slot == last_slot)
        return _orig != fluid_volume, fluid_volume

    def CanAddFluid(self, fluid_id):
        # type: (str) -> bool
        return any(self.fluids[s].canMerge(fluid_id) for s in self.fluid_input_slots)

    def RequireFluid(self, req_fluid_id, req_fluid_volume, strict_volume=False):
        # type: (str | None, float | None, bool) -> tuple[bool, str, float]
        "返回: 获取是否成功, 获取到的流体 ID, 获取到的流体容量"
        fluids = [(i, self.fluids[i]) for i in self.fluid_output_slots]
        last_slot = fluids[-1][0]
        for slot, fluid in fluids:
            if fluid.fluid_id is None:
                continue
            elif req_fluid_id is not None and fluid.fluid_id != req_fluid_id:
                continue
            fid = fluid.fluid_id
            fvol = fluid.volume
            if req_fluid_volume is None or req_fluid_volume >= fluid.volume:
                # NOTE: 遇到第一个有效槽位就立即返回, 不考虑后续槽位
                fluid.fluid_id = None
                fluid.volume = 0.0
                self.onReducedFluid(slot, fid, fvol, slot == last_slot)
                return True, fid, fvol
            else:
                fluid.volume = fvol - req_fluid_volume
                self.onReducedFluid(slot, fid, req_fluid_volume, slot == last_slot)
                return True, fid, req_fluid_volume
        return False, "", 0

    def RequireFluidsFromNetwork(self):
        "从流体管道网络请求一次流体。"
        requireLibraryFunc()
        RequirePostFluid(self.dim, self.xyz)

    def PostFluid(self):
        "让此容器向网络输出一次流体。"
        requireLibraryFunc()
        ok = False
        last_idx = len(self.fluid_output_slots) - 1
        for i, slot in enumerate(self.fluid_output_slots):
            fluid = self.fluids[slot]
            fluid_id = fluid.fluid_id
            if fluid_id is None:
                continue
            orig_vol = fluid.volume
            _ok, rest = self.tryPostFluid(fluid_id, orig_vol)
            ok = ok or _ok
            fluid.volume = rest
            if rest < orig_vol:
                self.onReducedFluid(slot, fluid_id, orig_vol - rest, i == last_idx)

    def RequireAnyFluidFromNetwork(self):
        """
        向流体管道网络索求一次流体。
        """
        requireLibraryFunc()
        RequirePostFluid(self.dim, self.xyz)

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
            if item.newItemName == "minecraft:bucket":
                last_fluid = self.fluids[-1]
                for slot, fluid in enumerate(self.fluids):
                    if fluid.fluid_id is None or fluid.volume < BUCKET_VOLUME:
                        continue
                    bucket_id = fluid.fluid_id + "_bucket"
                    if ItemExists(bucket_id):
                        fluid_id = fluid.fluid_id
                        fluid.volume -= BUCKET_VOLUME
                        if fluid.volume <= 0.0:
                            fluid.fluid_id = None
                        SetInventorySlotItemCount(
                            player_id, GetSelectedSlot(player_id), item.count - 1
                        )
                        GiveItem(player_id, Item(bucket_id, count=1))
                        self.onReducedFluid(
                            slot, fluid_id, BUCKET_VOLUME, fluid is last_fluid
                        )
                        break
            else:
                fluid_id = item.newItemName.replace("_bucket", "")
                if ItemExists(fluid_id) and self.CanAddFluid(fluid_id):
                    last_idx = len(self.fluid_input_slots) - 1
                    for i, slot in enumerate(self.fluid_input_slots):
                        fluid = self.fluids[slot]
                        if not self.IsValidFluidInput(slot, fluid_id):
                            continue
                        elif fluid.volume + BUCKET_VOLUME > fluid.max_volume:
                            continue
                        elif fluid.fluid_id is None or fluid.volume == 0:
                            fluid.fluid_id = fluid_id
                        elif fluid.fluid_id != fluid_id:
                            continue
                        fluid.volume += BUCKET_VOLUME
                        SetInventorySlotItemCount(
                            player_id, GetSelectedSlot(player_id), item.count - 1
                        )
                        SpawnItemToPlayerCarried(
                            player_id, Item("minecraft:bucket", count=1)
                        )
                        self.onAddedFluid(slot, fluid_id, BUCKET_VOLUME, i == last_idx)
            if isinstance(self, GUIControl):
                self.OnSync()
            return True
        else:
            return False

    def tryPostFluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> tuple[bool, float]
        requireLibraryFunc()
        return PostFluidIntoNetworks(self.dim, self.xyz, fluid_id, fluid_volume, None)

    def OnAddedFluid(self, slot, fluid_id, added_fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        "容器内流体体积已经增加时调用。"

    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        "容器内流体体积已经减少时调用。"

    def OnFluidSlotUpdate(self, slot_pos, is_final):
        # type: (int, bool) -> None
        "子类覆写在流体槽位发生更新时执行的回调。"

    def onAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        self.OnAddedFluid(slot, fluid_id, fluid_volume, is_final)
        self.onFluidSlotUpdate(slot, is_final)
        if isinstance(self, GUIControl):
            self.OnSync()

    def onReducedFluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        self.OnReducedFluid(slot, fluid_id, fluid_volume, is_final)
        self.onFluidSlotUpdate(slot, is_final)
        if isinstance(self, GUIControl):
            self.OnSync()

    def onFluidSlotUpdate(self, slot_pos, is_final):
        # type: (int, bool) -> None
        "子类覆写在流体槽位发生更新时执行的回调。"
        self._sending_fluid = True
        self.OnFluidSlotUpdate(slot_pos, is_final)
