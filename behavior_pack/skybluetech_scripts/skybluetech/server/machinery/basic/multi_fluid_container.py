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
from skybluetech_scripts.skybluetech.common.define.global_config import BUCKET_VOLUME
from skybluetech_scripts.skybluetech.common.machinery_def.basic import FluidSlotServer
from .gui_ctrl import GUIControl

from .base_machine import BaseMachine


class MultiFluidContainer(BaseMachine):
    """
    可存储多种流体的机器基类。

    类属性:
        fluid_io_mode (tuple[int, int, int, int, int, int]): 每个面的流体输入输出模式, -1:兼容 0:输入 1:输出 其他:无
        fluid_input_slots (set[int]): 可接受输入的流体槽位
        fluid_output_slots (set[int]): 可输出的流体槽位
        fluid_slot_max_volumes (tuple[float, ...]): 每个流体槽最多可存储流体容量
        player_fluid_input_slots (set[int] | None): 桶和试管可倒入的槽位, None 时跟随输入槽
        migrate_legacy_fluid_data (bool): 是否将旧单流体存档迁移到 0 号槽
        allow_player_use_bucket_interact (bool): 是否允许玩家直接使用桶交互
        allow_player_use_bucket_push (bool): 是否允许玩家直接使用桶装填流体
        allow_player_use_bucket_pull (bool): 是否允许玩家直接使用桶取出流体

    覆写:
        - `__init__`
    """

    fluid_io_mode = (2, 2, 2, 2, 2, 2)  # type: tuple[int, int, int, int, int, int]
    fluid_input_slots = set()  # type: set[int]
    fluid_output_slots = set()  # type: set[int]
    player_fluid_input_slots = None  # type: set[int] | None
    fluid_slot_max_volumes = (4000, 4000)  # type: tuple[float, ...]
    allow_player_use_bucket_interact = True
    allow_player_use_bucket_push = True
    allow_player_use_bucket_pull = True
    migrate_legacy_fluid_data = False

    def __init__(self, dim, x, y, z, block_entity_data):
        super(MultiFluidContainer, self).__init__(dim, x, y, z, block_entity_data)
        self.dim = dim
        self.xyz = (x, y, z)
        self.bdata = block_entity_data
        if self.migrate_legacy_fluid_data:
            self._migrate_legacy_fluid_data()
        self.fluids = [
            FluidSlotServer(self.bdata, i, mv)
            for i, mv in enumerate(self.fluid_slot_max_volumes)
        ]

    def _migrate_legacy_fluid_data(self):
        "只为原单槽设备迁移一次；已有新槽位数据优先，空槽也不能恢复旧液体。"
        if self.bdata["fluid_slot_migrated"]:
            return
        if self.bdata["fluid_id0"] is None and self.bdata["fluid_vol0"] is None:
            fluid_id = self.bdata["fluid_id"]
            volume = self.bdata["fluid_vol"] or 0.0
            if fluid_id is not None:
                self.bdata["fluid_id0"] = fluid_id
                # 创造储罐旧的无限体积可能已损坏，只保留其类型。
                self.bdata["fluid_vol0"] = (
                    1.0
                    if self.fluid_slot_max_volumes[0] == float("inf")
                    else min(self.fluid_slot_max_volumes[0], max(0.0, float(volume)))
                )
        self.bdata["fluid_id"] = None
        self.bdata["fluid_vol"] = 0.0
        self.bdata["max_volume"] = None
        self.bdata["fluid_slot_migrated"] = True

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        return True

    def OutputFluid(self, fluid_id, fluid_volume, slot_pos, is_final):
        # type: (str, float, int, bool) -> tuple[bool, float]
        if fluid_id is None or fluid_volume is None or fluid_volume <= 0:
            return False, fluid_volume
        fluid = self.fluids[slot_pos]
        if fluid.isFull():
            return False, fluid_volume
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
        return self._add_fluid_to_slots(fluid_id, fluid_volume, self.fluid_input_slots)

    def _add_fluid_to_slots(self, fluid_id, fluid_volume, slots):
        # type: (str, float, set[int]) -> tuple[bool, float]
        if fluid_id is None or fluid_volume is None or fluid_volume <= 0:
            return False, fluid_volume
        _orig = fluid_volume
        updates = []
        for slot in sorted(slots):
            fluid = self.fluids[slot]
            if fluid.canMerge(fluid_id) and self.IsValidFluidInput(slot, fluid_id):
                if fluid.fluid_id is None or fluid.volume == 0:
                    fluid.fluid_id = fluid_id
                free_volume = fluid.max_volume - fluid.volume
                if free_volume <= 0:
                    continue
                if fluid_volume <= free_volume:
                    fluid.volume += fluid_volume
                    updates.append((slot, fluid_volume))
                    fluid_volume = 0
                    break
                else:
                    fluid.volume = fluid.max_volume
                    fluid_volume -= free_volume
                    updates.append((slot, free_volume))
        for index, (slot, added_volume) in enumerate(updates):
            self._on_added_fluid(slot, fluid_id, added_volume, index == len(updates) - 1)
        return _orig != fluid_volume, fluid_volume

    def CanAddFluid(self, fluid_id):
        # type: (str) -> bool
        return any(
            self.fluids[s].canMerge(fluid_id) and self.IsValidFluidInput(s, fluid_id)
            for s in self.fluid_input_slots
        )

    def on_player_interact_with_bucket(self, player_id, test=False):
        # type: (str, bool) -> bool
        from ...tools.glass_tube import IsGlassTube

        input_slots = self._get_player_fluid_input_slots()
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
                            slot, fluid_id, BUCKET_VOLUME, True
                        )
                        break
            else:
                if not self.allow_player_use_bucket_push:
                    return False
                fluid_id = item.newItemName
                if fluid_id.endswith("_bucket"):
                    fluid_id = fluid_id[:-len("_bucket")]
                if ItemExists(fluid_id):
                    # 一桶只倒进一个槽位: 找到第一个装得下整桶的输入槽后立刻停止,
                    # 否则每个还装得下的槽位都会各加一桶, 凭空多出流体。
                    for slot in sorted(input_slots):
                        fluid = self.fluids[slot]
                        if not self.IsValidFluidInput(slot, fluid_id):
                            continue
                        elif fluid.isFull() or fluid.volume + BUCKET_VOLUME > fluid.max_volume:
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
                        # 这里就是本次操作的最后一个槽位更新, 必须让 is_final 为真,
                        # `Processor._processor_on_added_fluid` 才会去重查配方(输入槽空着时挂上的停机旗靠它唤醒)。
                        self._on_added_fluid(slot, fluid_id, BUCKET_VOLUME, True)
                        break
            if isinstance(self, GUIControl):
                self.CallSync()
            return True
        else:
            return False

    def _get_player_fluid_input_slots(self):
        # type: () -> set[int]
        # 输出接口允许手动倒液，但不允许管道向其输入。
        if self.player_fluid_input_slots is not None:
            return self.player_fluid_input_slots
        return self.fluid_input_slots

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
        ):
            ok, remaining = self._add_fluid_to_slots(
                tube_fluid_id, tube_volume, self._get_player_fluid_input_slots()
            )
            if ok:
                tube_volume = remaining
                if tube_volume <= 0:
                    tube_fluid_id = None
                    tube_volume = 0.0
                changed = True
        # 否则从容器舀出填充试管, 优先舀出输出槽的流体
        if not changed and self.allow_player_use_bucket_pull:
            output_slots = self.fluid_output_slots
            ordered_slots = sorted(output_slots) + [
                i for i in range(len(self.fluids)) if i not in output_slots
            ]
            updates = []
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
                updates.append((slot, pulled_fluid_id, pulled))
                changed = True
            for index, (slot, fluid_id, pulled) in enumerate(updates):
                self._on_reduced_fluid(slot, fluid_id, pulled, index == len(updates) - 1)
        if changed:
            ApplyTubeContent(player_id, item, tube_fluid_id, tube_volume)
        return True


    def _on_added_fluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        self.handler.CallOnAddedFluidHandlers(slot, fluid_id, fluid_volume, is_final)
        self._on_fluid_slot_update(slot, is_final)
        if isinstance(self, GUIControl):
            self.CallSync()

    def _on_reduced_fluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        self.handler.CallOnReducedFluidHandlers(slot, fluid_id, fluid_volume, is_final)
        self._on_fluid_slot_update(slot, is_final)
        if isinstance(self, GUIControl):
            self.CallSync()

    def _on_fluid_slot_update(self, slot_pos, is_final):
        # type: (int, bool) -> None
        "子类覆写在流体槽位发生更新时执行的回调。"
        self.handler.CallOnFluidSlotUpdateHandlers(slot_pos, is_final)
