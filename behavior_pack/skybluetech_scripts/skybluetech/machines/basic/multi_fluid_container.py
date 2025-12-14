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
from ...define.fluids.special_fluids import SPECIAL_FLUIDS
from .base_machine import BaseMachine
from .gui_ctrl import GUIControl
from .utils import FixIOModeByCardinalFacing, FixIOModeByDirection

K_FLUIDS = "fluids"


def requireLibraryFunc():
    global RequirePostFluid, PostFluidIntoNetworks
    if requireLibraryFunc._imported:
        return
    from ...transmitters.pipe.logic import RequirePostFluid, PostFluidIntoNetworks

    requireLibraryFunc._imported = True


requireLibraryFunc._imported = False


class FluidSlot:
    def __init__(self, fluid_id, fluid_volume, max_volume):
        # type: (str | None, float, float) -> None
        self.fluid_id = fluid_id
        self.volume = fluid_volume
        self.max_volume = max_volume

    def isFull(self):
        return self.volume >= self.max_volume

    def canMerge(self, fluid_id):
        # type： (str | None) -> bool
        if self.isFull():
            return False
        elif self.fluid_id is None or fluid_id == self.fluid_id:
            return True
        else:
            return False

    def marshal(self):
        return {
            "f": self.fluid_id,
            "v": self.volume,
        }

    @classmethod
    def unmarshal(cls, data, max_volume):
        # type: (dict, float) -> FluidSlot
        return cls(data["f"], data["v"], max_volume)


class MultiFluidContainer(object):
    """
    可存储多种流体的机器基类。

    需要调用 `__init__()`

    覆写: `Dump`
    """

    fluid_io_mode = (2, 2, 2, 2, 2, 2)  # type: tuple[int, int, int, int, int, int]
    "每个面的流体输入输出模式, -1:兼容 0:输入 1:输出 其他:无"
    fluid_input_slots = set()  # type: set[int]
    "可接受输入的流体槽位"
    fluid_output_slots = set()  # type: set[int]
    "可输出的流体槽位"
    fluid_slot_max_volumes = (4000, 4000)  # type: tuple[int, ...]
    "每个流体槽最多可存储流体容量"
    allow_player_use_bucket = True
    "是否允许玩家直接使用桶与机器进行交互"
    fluid_io_fix_mode = 1
    "使用 1 时调用 FixIOModeByCardinalFacing; 使用 2 时调用 FixIOModeByDirection; 其他则不适用修复"

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
        rawdatas = self.bdata[K_FLUIDS] or []
        if len(rawdatas) < len(self.fluid_slot_max_volumes):
            rawdatas += [{"f": None, "v": 0.0}] * (
                len(self.fluid_slot_max_volumes) - len(rawdatas)
            )
        self.fluids = [
            FluidSlot.unmarshal(rawdatas[i], mv)
            for i, mv in enumerate(self.fluid_slot_max_volumes)
        ]

    def Dump(self):
        self.bdata[K_FLUIDS] = [fluid.marshal() for fluid in self.fluids]

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        return True

    def OutputFluid(self, fluid_id, fluid_volume, slot_pos):
        # type: (str, float, int) -> None
        fluid = self.fluids[slot_pos]
        if fluid.fluid_id is None:
            fluid.fluid_id = fluid_id
        fluid.volume += fluid_volume
        self.OnFluidSlotUpdate(slot_pos)
        self.Dump()

    def AddFluid(self, fluid_id, fluid_volume, depth=0):
        # type: (str, float, int) -> tuple[bool, float]
        _orig = fluid_volume
        input_slots = ((i, self.fluids[i]) for i in self.fluid_input_slots)
        for slot, fluid in input_slots:
            if fluid.canMerge(fluid_id) and self.IsValidFluidInput(slot, fluid_id):
                if fluid.fluid_id is None:
                    fluid.fluid_id = fluid_id
                free_volume = fluid.max_volume - fluid.volume
                if fluid_volume <= free_volume:
                    fluid.volume += fluid_volume
                    self.OnFluidSlotUpdate(slot)
                    self.Dump()
                    return True, 0
                else:
                    fluid.volume = fluid.max_volume
                    fluid_volume -= free_volume
                    self.OnFluidSlotUpdate(slot)
                    self.Dump()
        return _orig != fluid_volume, fluid_volume

    def CanAddFluid(self, fluid_id):
        # type: (str) -> bool
        return any(self.fluids[s].canMerge(fluid_id) for s in self.fluid_input_slots)

    def RequireFluid(self, req_fluid_id, req_fluid_volume, strict_volume=False):
        # type: (str | None, float | None, bool) -> tuple[bool, str, float]
        "返回: 获取是否成功, 获取到的流体 ID, 获取到的流体容量"
        fluids = (self.fluids[i] for i in self.fluid_output_slots)
        for slot, fluid in enumerate(fluids):
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
                self.OnFluidSlotUpdate(slot)
                self.Dump()
                return True, fid, fvol
            else:
                fluid.volume -= req_fluid_volume
                self.OnFluidSlotUpdate(slot)
                self.Dump()
                return True, fid, req_fluid_volume
        return False, "", 0

    def RequireFluids(self):
        requireLibraryFunc()
        RequirePostFluid(self.dim, self.xyz)

    def RequirePost(self):
        # type: () -> None
        "让此容器向网络输出一次流体。"
        requireLibraryFunc()
        for i, fluid in enumerate(self.fluids):
            if fluid.fluid_id is not None:
                fluid.volume = PostFluidIntoNetworks(
                    self.dim, self.xyz, fluid.fluid_id, fluid.volume, None, 0
                )
                if fluid.volume <= 0.0:
                    fluid.fluid_id = None
                self.Dump()

    def RequireAnyFluidFromNetwork(self):
        requireLibraryFunc()
        RequirePostFluid(self.dim, self.xyz)

    def OnFluidSlotUpdate(self, slot_pos):
        # type: (int) -> None
        "子类覆写在流体槽位发生更新时执行的回调。"
        fluid = self.fluids[slot_pos]
        if slot_pos in self.fluid_output_slots and fluid.fluid_id is not None and fluid.volume > 0.0:
            fluid.volume = self.tryPostFluid(slot_pos, fluid.fluid_id, fluid.volume)

    def ifPlayerInteractWithBucket(self, player_id, test=False):
        # type: (str, bool) -> bool
        if not self.allow_player_use_bucket:
            return False
        item = GetPlayerMainhandItem(player_id)
        if item is None:
            return False
        elif item.GetBasicInfo().itemType == "bucket" or "skybluetech:liquid_bucket" in item.GetBasicInfo().tags:
            # TODO: 假设玩家都使用铁桶
            if test:
                return True
            if item.newItemName == "minecraft:bucket":
                for slot, fluid in enumerate(self.fluids):
                    if fluid.fluid_id is None or fluid.volume < BUCKET_VOLUME:
                        continue
                    bucket_id = fluid.fluid_id + "_bucket"
                    if ItemExists(bucket_id):
                        fluid.volume -= BUCKET_VOLUME
                        SetInventorySlotItemCount(
                            player_id, GetSelectedSlot(player_id), item.count - 1
                        )
                        GiveItem(player_id, Item(bucket_id, count=1))
                        self.OnFluidSlotUpdate(slot)
                        self.Dump()
                        break
            else:
                fluid_id = item.newItemName.replace("_bucket", "")
                if ItemExists(fluid_id) and self.CanAddFluid(fluid_id):
                    for slot, fluid in enumerate(self.fluids):
                        if not self.IsValidFluidInput(slot, fluid_id):
                            continue
                        elif fluid.volume + BUCKET_VOLUME > fluid.max_volume:
                            continue
                        elif fluid.fluid_id is None:
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
                        self.OnFluidSlotUpdate(slot)
                        self.Dump()
            if isinstance(self, GUIControl):
                self.OnSync()
            return True
        else:
            return False

    def tryPostFluid(self, slot_pos, fluid_id, fluid_volume, depth=0):
        # type: (int, str, float, int) -> float
        if depth >= 64:
            print ("[WARNING] fluid transfer max depth detected!")
            return fluid_volume
        requireLibraryFunc()
        return PostFluidIntoNetworks(
            self.dim, self.xyz, fluid_id, fluid_volume, None, depth=depth
        )
