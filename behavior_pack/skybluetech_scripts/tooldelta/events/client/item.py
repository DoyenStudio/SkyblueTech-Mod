# coding=utf-8

from ..basic import ClientEvent
from ...define.item import Item


class PlayerTryPutCustomContainerItemClientEvent(ClientEvent):
    name = "PlayerTryPutCustomContainerItemClientEvent"

    def __init__(
        self,
        item,  # type: Item
        collectionName,  # type: str
        collectionType,  # type: str
        collectionIndex,  # type: int
        x,  # type: int
        y,  # type: int
        z,  # type: int
        _orig,  # type: dict
    ):
        self.item = item
        """ 尝试放入物品的物品信息字典 """
        self.collectionName = collectionName
        """ 放入容器名称，对应容器json中"custom_description"字段 """
        self.collectionType = collectionType
        """ 放入容器类型，目前仅支持netease_container和netease_ui_container """
        self.collectionIndex = collectionIndex
        """ 放入容器索引 """
        self.x = x
        """ 容器方块x坐标 """
        self.y = y
        """ 容器方块y坐标 """
        self.z = z
        """ 容器方块z坐标 """
        self._orig = _orig
        """ 原始事件数据 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            item=Item.from_dict(data["itemDict"]),
            collectionName=data["collectionName"],
            collectionType=data["collectionType"],
            collectionIndex=data["collectionIndex"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            _orig=data,
        )

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
        # type: () -> None
        "取消该操作，默认为false，事件中改为true时拒绝此次放入自定义容器的操作"
        self._orig["cancel"] = True


class PlayerTryRemoveCustomContainerItemClientEvent(ClientEvent):
    name = "PlayerTryRemoveCustomContainerItemClientEvent"

    def __init__(
        self,
        item,  # type: Item
        collectionName,  # type: str
        collectionType,  # type: str
        collectionIndex,  # type: int
        x,  # type: int
        y,  # type: int
        z,  # type: int
        _orig,  # type: dict
    ):
        self.item = item
        """ 尝试移除物品的物品信息字典 """
        self.collectionName = collectionName
        """ 放入容器名称，对应容器json中"custom_description"字段 """
        self.collectionType = collectionType
        """ 放入容器类型，目前仅支持netease_container和netease_ui_container """
        self.collectionIndex = collectionIndex
        """ 目标容器索引 """
        self.x = x
        """ 容器方块x坐标 """
        self.y = y
        """ 容器方块y坐标 """
        self.z = z
        """ 容器方块z坐标 """
        self._orig = _orig
        """ 原始事件数据 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            item=Item.from_dict(data["itemDict"]),
            collectionName=data["collectionName"],
            collectionType=data["collectionType"],
            collectionIndex=data["collectionIndex"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            _orig=data,
        )

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
        # type: () -> None
        "取消该操作，默认为false，事件中改为true时拒绝此次移除物品的操作"
        self._orig["cancel"] = True


class ClientItemTryUseEvent(ClientEvent):
    name = "ClientItemTryUseEvent"

    def __init__(
        self,
        playerId,  # type: str
        item,  # type: Item
        _orig,  # type: dict
    ):
        self.playerId = playerId
        """ 玩家id """
        self.item = item
        """ 使用的物品的物品信息字典 """
        self._orig = _orig
        """ 原始事件数据 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            playerId=data["playerId"],
            item=Item.from_dict(data["itemDict"]),
            _orig=data,
        )

    def marshal(self):
        # type: () -> dict
        return {
            "playerId": self.playerId,
            "itemDict": self.item.marshal(),
        }

    def cancel(self):
        # type: () -> None
        "取消使用物品"
        self._orig["cancel"] = True


class ClientItemUseOnEvent(ClientEvent):
    name = "ClientItemUseOnEvent"

    def __init__(
        self,
        entityId,  # type: str
        item,  # type: Item
        x,  # type: int
        y,  # type: int
        z,  # type: int
        blockName,  # type: str
        blockAuxValue,  # type: int
        face,  # type: int
        clickX,  # type: float
        clickY,  # type: float
        clickZ,  # type: float
        _orig,  # type: dict
    ):
        self.entityId = entityId
        """ 玩家实体id """
        self.item = item
        """ 使用的物品的物品信息字典 """
        self.x = x
        """ 方块 x 坐标值 """
        self.y = y
        """ 方块 y 坐标值 """
        self.z = z
        """ 方块 z 坐标值 """
        self.blockName = blockName
        """ 方块的identifier """
        self.blockAuxValue = blockAuxValue
        """ 方块的附加值 """
        self.face = face
        """ 点击方块的面，参考Facing枚举 """
        self.clickX = clickX
        """ 点击点的x比例位置 """
        self.clickY = clickY
        """ 点击点的y比例位置 """
        self.clickZ = clickZ
        """ 点击点的z比例位置 """
        self._orig = _orig
        """ 原始事件数据 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            entityId=data["entityId"],
            item=Item.from_dict(data["itemDict"]),
            x=data["x"],
            y=data["y"],
            z=data["z"],
            blockName=data["blockName"],
            blockAuxValue=data["blockAuxValue"],
            face=data["face"],
            clickX=data["clickX"],
            clickY=data["clickY"],
            clickZ=data["clickZ"],
            _orig=data,
        )

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
        }

    def cancel(self):
        # type: () -> None
        "设为True可取消物品的使用"
        self._orig["ret"] = True


class ActorAcquiredItemClientEvent(ClientEvent):
    name = "ActorAcquiredItemClientEvent"

    def __init__(
        self,
        actor,  # type: str
        secondaryActor,  # type: str
        item,  # type: Item
        acquireMethod,  # type: int
    ):
        self.actor = actor
        """ 获得物品玩家实体id """
        self.secondaryActor = secondaryActor
        """ 物品给予者玩家实体id，如果不存在给予者的话，这里为空字符串 """
        self.item = item
        """ 获取到的物品的物品信息字典 """
        self.acquireMethod = acquireMethod
        """ 获得物品的方法，详见ItemAcquisitionMethod """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            actor=data["actor"],
            secondaryActor=data["secondaryActor"],
            item=Item.from_dict(data["itemDict"]),
            acquireMethod=data["acquireMethod"],
        )

    def marshal(self):
        # type: () -> dict
        return {
            "actor": self.actor,
            "secondaryActor": self.secondaryActor,
            "itemDict": self.item.marshal(),
            "acquireMethod": self.acquireMethod,
        }
