# coding=utf-8
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.api.server import (
    ItemExists,
    GetPlayerMainhandItem,
    SpawnItemToPlayerCarried,
    GiveItem,
    GetSelectedSlot,
    SetInventorySlotItemCount,
)
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from skybluetech_scripts.skybluetech.common.define.global_config import BUCKET_VOLUME
from skybluetech_scripts.skybluetech.common.machinery_def.basic import FluidSlotServer
from .gui_ctrl import GUIControl


class MultiFluidContainer(object):
    """
    可存储多种流体的机器基类。

    类属性:
        fluid_io_mode (tuple[int, int, int, int, int, int]): 每个面的流体输入输出模式, -1:兼容 0:输入 1:输出 其他:无
        fluid_input_slots (set[int]): 可接受输入的流体槽位
        fluid_output_slots (set[int]): 可输出的流体槽位
        fluid_slot_max_volumes (tuple[int, ...]): 每个流体槽最多可存储流体容量
        allow_player_use_bucket (bool): 是否允许玩家直接使用桶与机器进行交互
        allow_player_use_bucket_interact (bool): 是否允许玩家直接使用桶交互
        allow_player_use_bucket_push (bool): 是否允许玩家直接使用桶装填流体
        allow_player_use_bucket_pull (bool): 是否允许玩家直接使用桶取出流体

    覆写:
        - `__init__`
    """

    fluid_io_mode = (2, 2, 2, 2, 2, 2)  # type: tuple[int, int, int, int, int, int]
    fluid_input_slots = set()  # type: set[int]
    fluid_output_slots = set()  # type: set[int]
    fluid_slot_max_volumes = (4000, 4000)  # type: tuple[int, ...]
    allow_player_use_bucket_interact = True
    allow_player_use_bucket_push = True
    allow_player_use_bucket_pull = True

    def __init__(self, dim, x, y, z, block_entity_data):
        self.dim = dim
        self.xyz = (x, y, z)
        self.bdata = block_entity_data
        self.fluids = [
            FluidSlotServer(self.bdata, i, mv)
            for i, mv in enumerate(self.fluid_slot_max_volumes)
        ]

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        return True

    def OutputFluid(self, fluid_id, fluid_volume, slot_pos, is_final):
        # type: (str, float, int, bool) -> tuple[bool, float]
        if fluid_id is None or fluid_volume is None or fluid_volume <= 0:
            return False, fluid_volume
        fluid = self.fluids[slot_pos]
        if fluid.fluid_id is not None and fluid.fluid_id != fluid_id:
            return False, fluid_volume
        orig_volume = fluid.volume
        added_volume = min(fluid_volume, fluid.max_volume - orig_volume)
        if added_volume <= 0:
            return False, fluid_volume
        if fluid.fluid_id is None:
            fluid.fluid_id = fluid_id
        fluid.volume = orig_volume + added_volume
        self._on_added_fluid(slot_pos, fluid_id, added_volume, is_final)
        return True, max(0, fluid_volume - added_volume)

    def AddFluid(self, fluid_id, fluid_volume):
        # type: (str, float) -> tuple[bool, float]
        if fluid_id is None or fluid_volume is None or fluid_volume <= 0:
            return False, fluid_volume
        _orig = fluid_volume
        input_slots = [(i, self.fluids[i]) for i in self.fluid_input_slots]
        if not input_slots:
            return False, fluid_volume
        last_slot = input_slots[-1][0]
        for slot, fluid in input_slots:
            if fluid.canMerge(fluid_id) and self.IsValidFluidInput(slot, fluid_id):
                if fluid.fluid_id is None or fluid.volume == 0:
                    fluid.fluid_id = fluid_id
                free_volume = fluid.max_volume - fluid.volume
                if free_volume <= 0:
                    continue
                if fluid_volume <= free_volume:
                    fluid.volume += fluid_volume
                    self._on_added_fluid(
                        slot, fluid_id, fluid_volume, slot == last_slot
                    )
                    return True, 0
                else:
                    fluid.volume = fluid.max_volume
                    fluid_volume -= free_volume
                    self._on_added_fluid(slot, fluid_id, free_volume, slot == last_slot)
        return _orig != fluid_volume, fluid_volume

    def CanAddFluid(self, fluid_id):
        # type: (str) -> bool
        return any(self.fluids[s].canMerge(fluid_id) for s in self.fluid_input_slots)

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
            if item.newItemName == "minecraft:bucket":
                if not self.allow_player_use_bucket_pull:
                    return False
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
                        self._on_reduced_fluid(
                            slot, fluid_id, BUCKET_VOLUME, fluid is last_fluid
                        )
                        break
            else:
                if not self.allow_player_use_bucket_push:
                    return False
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
                        self._on_added_fluid(
                            slot, fluid_id, BUCKET_VOLUME, i == last_idx
                        )
            if isinstance(self, GUIControl):
                self.CallSync()
            return True
        else:
            return False

    def on_player_interact_with_glass_tube(self, player_id, item, test=False):
        # type: (str, object, bool) -> bool
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
        # 否则从容器舀出填充试管, 优先舀出输出槽的流体
        if not changed and self.allow_player_use_bucket_pull:
            output_slots = self.fluid_output_slots
            ordered_slots = list(output_slots) + [
                i for i in range(len(self.fluids)) if i not in output_slots
            ]
            last_slot = ordered_slots[-1] if ordered_slots else -1
            for slot in ordered_slots:
                if GLASS_TUBE_MAX_VOLUME - tube_volume <= 0:
                    break
                fluid = self.fluids[slot]
                if fluid.fluid_id is None or fluid.volume <= 0:
                    continue
                if tube_fluid_id is not None and tube_fluid_id != fluid.fluid_id:
                    continue
                pulled = min(GLASS_TUBE_MAX_VOLUME - tube_volume, fluid.volume)
                if pulled <= 0:
                    continue
                pulled_fluid_id = fluid.fluid_id
                fluid.volume -= pulled
                tube_fluid_id = pulled_fluid_id
                tube_volume += pulled
                self._on_reduced_fluid(slot, pulled_fluid_id, pulled, slot == last_slot)
                changed = True
        if changed:
            ApplyTubeContent(player_id, item, tube_fluid_id, tube_volume)
        return True

    @SuperExecutorMeta.execute_super
    def OnAddedFluid(self, slot, fluid_id, added_fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        "容器内流体体积已经增加时调用。"

    @SuperExecutorMeta.execute_super
    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        "容器内流体体积已经减少时调用。"

    @SuperExecutorMeta.execute_super
    def OnFluidSlotUpdate(self, slot_pos, is_final):
        # type: (int, bool) -> None
        "子类覆写在流体槽位发生更新时执行的回调。"

    def _on_added_fluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        self.OnAddedFluid(slot, fluid_id, fluid_volume, is_final)
        self._on_fluid_slot_update(slot, is_final)
        if isinstance(self, GUIControl):
            self.CallSync()

    def _on_reduced_fluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        self.OnReducedFluid(slot, fluid_id, fluid_volume, is_final)
        self._on_fluid_slot_update(slot, is_final)
        if isinstance(self, GUIControl):
            self.CallSync()

    def _on_fluid_slot_update(self, slot_pos, is_final):
        # type: (int, bool) -> None
        "子类覆写在流体槽位发生更新时执行的回调。"
        self.OnFluidSlotUpdate(slot_pos, is_final)
