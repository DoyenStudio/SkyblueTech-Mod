# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events import (
    PlayerTryPutCustomContainerItemClientEvent,
    PlayerTryPutCustomContainerItemServerEvent,
)
from skybluetech_scripts.tooldelta.api.server import (
    GetContainerItem,
    SetContainerItem,
    PutItemIntoContainer,
    SetChestBoxItemNum,
    SpawnDroppedItem,
)
from skybluetech_scripts.tooldelta.extensions.item_utils import SortItems


def requireLibraryFunc():
    global RequireItems, PostItemIntoNetworks
    if requireLibraryFunc._imported:
        return
    from ...transmitters.cable.logic import RequireItems, PostItemIntoNetworks

    requireLibraryFunc._imported = True


requireLibraryFunc._imported = False


class ItemContainer(object):
    """
    可存储物品的机器基类。

    类属性:
        input_slots (tuple[int, ...]): 可用输入槽位
        output_slots (tuple[int, ...]): 可用输出槽位

    需要调用 `__init__()`
    """

    input_slots = ()  # type: tuple[int, ...]
    output_slots = ()  # type: tuple[int, ...]

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        self.dim = dim
        self.xyz = (x, y, z)

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        "子类覆写方法, 判定槽位物品是否为合法输入。超类防止物品输入到输出口。"
        return slot in self.input_slots

    def GetSlotItem(self, slot_pos, get_user_data=True):
        # type: (int, bool) -> Item | None
        """
        获取槽位内的物品。

        Args:
            slot_pos (int): 槽位 ID
            get_user_data (bool, optional): 是否获取物品的 userData

        Returns:
            Item (optional): 槽位内物品实例, 如果为空则返回 None
        """
        return GetContainerItem(self.dim, self.xyz, slot_pos, get_user_data)

    def SetSlotItem(self, slot_pos, item):
        # type: (int, Item | None) -> bool
        """
        设置槽位内的物品。

        Args:
            slot_pos (int): 槽位 ID
            item (Item | None): 设置的物品, 如果为 None 则设置槽位为空

        Returns:
            _type_: _description_
        """
        return SetContainerItem(
            self.dim, self.xyz, slot_pos, item or Item("minecraft:air", count=0)
        )

    def DropAllItems(self):
        for slot in self.input_slots + self.output_slots:
            item = self.GetSlotItem(slot)
            if item is not None:
                SpawnDroppedItem(self.dim, self.xyz, item)
                self.SetSlotItem(slot, None)

    def SetSlotItemCount(self, slot_pos, count):
        # type: (int, int) -> None
        """WARNING: 此 api 对于自定义容器有 bug"""
        SetChestBoxItemNum(None, self.xyz, slot_pos, count, self.dim)

    def GetSlotSize(self):
        """
        获取输入槽和输出槽的数量。

        Returns:
            int
        """
        return len(self.input_slots) + len(self.output_slots)

    def GetInputSlotItems(self, get_user_data=True):
        # type: (bool) -> dict[int, Item]
        """
        获取输入槽的所有物品。

        Returns:
            dict[int, Item]: 槽位对应的物品实例, 如果槽位里有物品
        """
        res = {}  # type: dict[int, Item]
        for slot_pos in self.input_slots:
            item = self.GetSlotItem(slot_pos, get_user_data=get_user_data)
            if item is not None:
                res[slot_pos] = item
        return res

    def GetOutputSlotItems(self):
        # type: () -> dict[int, Item]
        """
        获取输出槽的所有物品。

        Returns:
            dict[int, Item]: 槽位对应的物品实例, 如果槽位里有物品
        """
        res = {}  # type: dict[int, Item]
        for slot_pos in self.output_slots:
            item = self.GetSlotItem(slot_pos)
            if item is not None:
                res[slot_pos] = item
        return res

    def SetSlotItems(self, slotitems):
        # type: (dict[int, Item]) -> None
        """
        设置多个槽位内的物品。

        Args:
            slotitems (dict[int, Item]): 槽位 ID 对应物品实例
        """
        for slot_pos, item in slotitems.items():
            self.SetSlotItem(slot_pos, item)

    def PushItem(self, item):
        # type: (Item) -> Item | None
        """
        尝试将物品输入此容器。

        Args:
            item (Item): 将输入的物品

        Returns:
            Item (optional): 如有剩余物品则返回物品实例
        """
        for slot_pos in self.input_slots:
            orig_item = self.GetSlotItem(slot_pos, get_user_data=True)
            if orig_item is None:
                if not self.IsValidInput(slot_pos, item):
                    continue
                res = self.SetSlotItem(slot_pos, item)
                if res:
                    return None
                else:
                    continue
            elif not orig_item.CanMerge(item):
                continue
            sum_count = orig_item.count + item.count
            max_stack = orig_item.GetBasicInfo().maxStackSize
            if sum_count > max_stack:
                item_new = item.copy()
                item_new.count = max_stack
                res = self.SetSlotItem(slot_pos, item_new)
                if not res:
                    continue
                item.count = sum_count - max_stack
            else:
                item_new = item.copy()
                item_new.count = sum_count
                res = self.SetSlotItem(slot_pos, item_new)
                if not res:
                    continue
                return None
        return item

    def RequireItems(self):
        """
        此机器向物品管线网络请求一次物品。

        Returns:
            bool: 是否请求成功
        """
        requireLibraryFunc()
        RequireItems(self.dim, self.xyz)

    def OnSlotUpdate(self, slot_pos):
        # type: (int) -> None
        "覆写方法用于作为机器物品槽位更新的回调。"

    def OnCustomCotainerPutItem(self, event):
        # type: (PlayerTryPutCustomContainerItemServerEvent) -> None
        if not self.IsValidInput(event.collectionIndex, event.item):
            event.cancel()

    def CanOutputItems(self, items):
        # type: (list[Item]) -> bool
        """
        机器是否可以输出物品。

        Args:
            items (list[Item]): 物品列表

        Returns:
            bool
        """
        _c = [
            self.GetSlotItem(slot_pos, get_user_data=True)
            for slot_pos in self.output_slots
        ]
        current_items = [i for i in _c if i is not None]
        items_sorted = SortItems(items + current_items)
        return len(items_sorted) <= len(self.output_slots)

    def OutputItem(self, item):
        # type: (Item) -> Item | None
        # 在管道逻辑处已经能自动输出物品了
        # requireLibraryFunc()
        # item_res = PostItemIntoNetworks(self.dim, self.xyz, item, None)
        # if item_res is None:
        #     return None
        """
        输出产出的物品。

        Args:
            item (Item): 产出物

        Returns:
            Item: 剩余物品, 当没有剩余物时返回 None
        """
        return PutItemIntoContainer(self.dim, self.xyz, item, self.output_slots)
