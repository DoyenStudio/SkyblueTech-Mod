# coding=utf-8

from ..basic import ClientEvent
from ...define.item import Item


class PlayerTryPutCustomContainerItemClientEvent(ClientEvent):
    name = "PlayerTryPutCustomContainerItemClientEvent"

    item = Item("")  # type: Item
    """ 尝试放入物品的物品信息字典 """
    collectionName = ""  # type: str
    """ 放入容器名称，对应容器json中"custom_description"字段 """
    collectionType = ""  # type: str
    """ 放入容器类型，目前仅支持netease_container和netease_ui_container """
    collectionIndex = 0  # type: int
    """ 放入容器索引 """
    x = 0  # type: int
    """ 容器方块x坐标 """
    y = 0  # type: int
    """ 容器方块y坐标 """
    z = 0  # type: int
    """ 容器方块z坐标 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> PlayerTryPutCustomContainerItemClientEvent
        instance = cls()
        instance._orig = data
        instance.item = Item.from_dict(data["itemDict"])
        instance.collectionName = data["collectionName"]
        instance.collectionType = data["collectionType"]
        instance.collectionIndex = data["collectionIndex"]
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "itemDict": self.item.marshal(),
            "collectionName": self.collectionName,
            "collectionType": self.collectionType,
            "collectionIndex": self.collectionIndex,
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

    def cancel(self):
        """拒绝此次放入自定义容器的操作"""
        # type: () -> None
        self._orig["cancel"] = True


class PlayerTryRemoveCustomContainerItemClientEvent(ClientEvent):
    name = "PlayerTryRemoveCustomContainerItemClientEvent"

    item = Item("")  # type: Item
    """ 尝试移除物品的物品信息字典 """
    collectionName = ""  # type: str
    """ 放入容器名称，对应容器json中"custom_description"字段 """
    collectionType = ""  # type: str
    """ 放入容器类型，目前仅支持netease_container和netease_ui_container """
    collectionIndex = 0  # type: int
    """ 目标容器索引 """
    x = 0  # type: int
    """ 容器方块x坐标 """
    y = 0  # type: int
    """ 容器方块y坐标 """
    z = 0  # type: int
    """ 容器方块z坐标 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> PlayerTryRemoveCustomContainerItemClientEvent
        instance = cls()
        instance._orig = data
        instance.item = Item.from_dict(data["itemDict"])
        instance.collectionName = data["collectionName"]
        instance.collectionType = data["collectionType"]
        instance.collectionIndex = data["collectionIndex"]
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "itemDict": self.item.marshal(),
            "collectionName": self.collectionName,
            "collectionType": self.collectionType,
            "collectionIndex": self.collectionIndex,
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

    def cancel(self):
        """拒绝此次移除自定义容器的操作"""
        # type: () -> None
        self._orig["cancel"] = True


class ClientItemTryUseEvent(ClientEvent):
    name = "ClientItemTryUseEvent"

    playerId = ""  # type: str
    """ 玩家id """
    item = Item("")  # type: Item
    """ 使用的物品的物品信息 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ClientItemTryUseEvent
        instance = cls()
        instance._orig = data
        instance.playerId = data["playerId"]
        instance.item = Item.from_dict(data["itemDict"])
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "playerId": self.playerId,
            "itemDict": self.item.marshal(),
        }

    def cancel(self):
        """拒绝此次移除自定义容器的操作"""
        # type: () -> None
        self._orig["cancel"] = True


class ClientItemUseOnEvent(ClientEvent):
    name = "ClientItemUseOnEvent"

    entityId = ""  # type: str
    """ 玩家实体id """
    item = Item("")  # type: Item
    """ 使用的物品的物品信息 """
    x = 0  # type: int
    """ 方块 x 坐标值 """
    y = 0  # type: int
    """ 方块 y 坐标值 """
    z = 0  # type: int
    """ 方块 z 坐标값 """
    blockName = ""  # type: str
    """ 方块的identifier """
    blockAuxValue = 0  # type: int
    """ 方块的附加值 """
    face = 0  # type: int
    """ 点击方块的面，参考Facing枚举 """
    clickX = 0.0  # type: float
    """ 点击点的x比例位置 """
    clickY = 0.0  # type: float
    """ 点击点的y比例位置 """
    clickZ = 0.0  # type: float
    """ 点击点的z比例位置 """
    ret = False  # type: bool
    """ 设为True可取消物品的使用 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ClientItemUseOnEvent
        instance = cls()
        instance._orig = data
        instance.entityId = data["entityId"]
        instance.item = Item.from_dict(data["itemDict"])
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.blockName = data["blockName"]
        instance.blockAuxValue = data["blockAuxValue"]
        instance.face = data["face"]
        instance.clickX = data["clickX"]
        instance.clickY = data["clickY"]
        instance.clickZ = data["clickZ"]
        instance.ret = data["ret"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "entityId": self.entityId,
            "itemDict": self.item.marshal(),
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "blockName": self.blockName,
            "blockAuxValue": self.blockAuxValue,
            "face": self.face,
            "clickX": self.clickX,
            "clickY": self.clickY,
            "clickZ": self.clickZ,
            "ret": self.ret,
        }

    def cancel(self):
        """拒绝此次物品使用的操作"""
        # type: () -> None
        self._orig["ret"] = True
