# coding=utf-8

from ...define.item import Item
from ...internal import ServerComp, ServerLevelId
from ..basic import ServerEvent


class PlayerTryPutCustomContainerItemServerEvent(ServerEvent):
    name = "PlayerTryPutCustomContainerItemServerEvent"

    def __init__(
        self,
        item, # type: Item
        collectionName, # type: str
        collectionType, # type: str
        collectionIndex, # type: int
        playerId, # type: str
        x, # type: int
        y, # type: int
        z, # type: int
        _orig, # type: dict
    ):
        self.item = item
        """ 尝试放入物品的物品信息字典 """
        self.collectionName = collectionName
        """ 放入容器名称，对应容器json中"custom_description"字段 """
        self.collectionType = collectionType
        """ 放入容器类型，目前仅支持netease_container和netease_ui_container """
        self.collectionIndex = collectionIndex
        """ 放入容器索引 """
        self.playerId = playerId
        """ 玩家id """
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
            playerId=data["playerId"],
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
            "playerId": self.playerId,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "_orig": self._orig,
        }

    def cancel(self):
        # type: () -> None
        "取消该操作，默认为false，事件中改为true时拒绝此次放入自定义容器的操作"
        self._orig["cancel"] = True

    @classmethod
    def ListenWithUserData(cls, priority=0):
        # print("[TDEvent] Listen with user data: " + cls.name)
        ServerComp.CreateItem(ServerLevelId).GetUserDataInEvent(cls.name)
        return cls.Listen(priority)


class PlayerTryRemoveCustomContainerItemServerEvent(ServerEvent):
    name = "PlayerTryRemoveCustomContainerItemServerEvent"

    def __init__(
        self,
        item, # type: Item
        collectionName, # type: str
        collectionType, # type: str
        collectionIndex, # type: int
        playerId, # type: str
        x, # type: int
        y, # type: int
        z, # type: int
    ):
        self.item = item
        """ 尝试移除物品的物品信息字典 """
        self.collectionName = collectionName
        """ 放入容器名称，对应容器json中"custom_description"字段 """
        self.collectionType = collectionType
        """ 放入容器类型，目前仅支持netease_container和netease_ui_container """
        self.collectionIndex = collectionIndex
        """ 目标容器索引 """
        self.playerId = playerId
        """ 玩家id """
        self.x = x
        """ 容器方块x坐标 """
        self.y = y
        """ 容器方块y坐标 """
        self.z = z
        """ 容器方块z坐标 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            item=Item.from_dict(data["itemDict"]),
            collectionName=data["collectionName"],
            collectionType=data["collectionType"],
            collectionIndex=data["collectionIndex"],
            playerId=data["playerId"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
        )

    def marshal(self):
        # type: () -> dict
        return {
            "itemDict": self.item.marshal(),
            "collectionName": self.collectionName,
            "collectionType": self.collectionType,
            "collectionIndex": self.collectionIndex,
            "playerId": self.playerId,
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }


class ContainerItemChangedServerEvent(ServerEvent):
    name = "ContainerItemChangedServerEvent"

    pos = None # type: tuple[int,int,int] | None
    """ 容器坐标 """
    containerType = 0 # type: int
    """ 容器类型，类型含义见：容器类型枚举 """
    slot = 0 # type: int
    """ 容器槽位 """
    dimensionId = 0 # type: int
    """ 维度id """
    oldItem = Item("")
    """ 旧物品 """
    newItem = Item("")
    """ 新物品 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ContainerItemChangedServerEvent
        instance = cls()
        instance.pos = data["pos"]
        instance.containerType = data["containerType"]
        instance.slot = data["slot"]
        instance.dimensionId = data["dimensionId"]
        instance.oldItem = Item.from_dict(data["oldItemDict"])
        instance.newItem = Item.from_dict(data["newItemDict"])
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "pos": self.pos,
            "containerType": self.containerType,
            "slot": self.slot,
            "dimensionId": self.dimensionId,
            "oldItemDict": self.oldItem.marshal(),
            "newItemDict": self.newItem.marshal(),
        }

    @classmethod
    def ListenWithUserData(cls, priority=0):
        # print("[TDEvent] Listen with user data: " + cls.name)
        ServerComp.CreateItem(ServerLevelId).GetUserDataInEvent(cls.name)
        return cls.Listen(priority)


class ItemPushInCustomContainerServerEvent(ServerEvent):
    name = "ItemPushInCustomContainerServerEvent"

    def __init__(
        self,
        item, # type: Item
        collectionName, # type: str
        collectionIndex, # type: int
        x, # type: int
        y, # type: int
        z, # type: int
        _orig, # type: dict
    ):
        self.item = item
        """ 漏斗漏入物品的物品信息字典 """
        self.collectionName = collectionName
        """ 目标容器名称，目前仅支持netease_container """
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
            "collectionIndex": self.collectionIndex,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "_orig": self._orig,
        }

    def cancel(self):
        # type: () -> None
        "取消该操作，默认为false，事件中改为true时拒绝此次漏入物品的操作"
        self._orig["cancel"] = True


class ItemPullOutCustomContainerServerEvent(ServerEvent):
    name = "ItemPullOutCustomContainerServerEvent"

    def __init__(
        self,
        item, # type: Item
        collectionName, # type: str
        collectionIndex, # type: int
        x, # type: int
        y, # type: int
        z, # type: int
        _orig, # type: dict
    ):
        self.item = item
        """ 漏斗漏出物品的物品信息字典 """
        self.collectionName = collectionName
        """ 漏出物品的容器名称，目前仅支持netease_container """
        self.collectionIndex = collectionIndex
        """ 漏出物品的容器索引 """
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
            "collectionIndex": self.collectionIndex,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "_orig": self._orig,
        }

    def cancel(self):
        # type: () -> None
        "取消该操作，默认为false，事件中改为true时拒绝此次漏出物品的操作"
        self._orig["cancel"] = True


class ServerItemUseOnEvent(ServerEvent):
    name = "ServerItemUseOnEvent"

    def __init__(
        self,
        entityId, # type: str
        item, # type: Item
        x, # type: int
        y, # type: int
        z, # type: int
        blockName, # type: str
        blockAuxValue, # type: int
        face, # type: int
        dimensionId, # type: int
        clickX, # type: float
        clickY, # type: float
        clickZ, # type: float
        _orig, # type: dict
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
        self.dimensionId = dimensionId
        """ 维度id """
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
            dimensionId=data["dimensionId"],
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
            "dimensionId": self.dimensionId,
            "clickX": self.clickX,
            "clickY": self.clickY,
            "clickZ": self.clickZ,
            "_orig": self._orig,
        }

    def cancel(self):
        # type: () -> None
        "设为True可取消物品的使用"
        self._orig["ret"] = True

    @classmethod
    def ListenWithUserData(cls, priority=0):
        # print("[TDEvent] Listen with user data: " + cls.name)
        ServerComp.CreateItem(ServerLevelId).GetUserDataInEvent(cls.name)
        return cls.Listen(priority)

class ActorAcquiredItemServerEvent(ServerEvent):
    name = "ActorAcquiredItemServerEvent"

    actor = '' # type: str
    """ 获得物品玩家实体id """
    secondaryActor = '' # type: str
    """ 物品给予者玩家实体id，如果不存在给予者的话，这里为空字符串 """
    item = Item("") # type: Item
    """ 获得的物品的物品信息字典 """
    acquireMethod = 0 # type: int
    """ 获得物品的方法，详见ItemAcquisitionMethod枚举 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ActorAcquiredItemServerEvent
        instance = cls()
        instance.actor = data["actor"]
        instance.secondaryActor = data["secondaryActor"]
        instance.item = Item.from_dict(data["itemDict"])
        instance.acquireMethod = data["acquireMethod"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "actor": self.actor,
            "secondaryActor": self.secondaryActor,
            "itemDict": self.item.marshal(),
            "acquireMethod": self.acquireMethod,
        }


class OnCarriedNewItemChangedServerEvent(ServerEvent):
    name = "OnCarriedNewItemChangedServerEvent"

    oldItem = None # type: Item | None
    """ 旧物品的物品信息字典，当旧物品为空时，此项属性为None """
    newItem = None # type: Item | None
    """ 新物品的物品信息字典，当新物品为空时，此项属性为None """
    playerId = '' # type: str
    """ 玩家 entityId """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> OnCarriedNewItemChangedServerEvent
        instance = cls()
        instance.oldItem = Item.from_dict(data["oldItemDict"]) if data["oldItemDict"] else None
        instance.newItem = Item.from_dict(data["newItemDict"]) if data["newItemDict"] else None
        instance.playerId = data["playerId"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "oldItemDict": self.oldItem.marshal() if self.oldItem else None,
            "newItemDict": self.newItem.marshal() if self.newItem else None,
            "playerId": self.playerId,
        }


class ItemDurabilityChangedServerEvent(ServerEvent):
    name = "ItemDurabilityChangedServerEvent"

    def __init__(
        self,
        entityId, # type: str
        item, # type: Item
        durabilityBefore, # type: int
        durability, # type: int
        canChange, # type: bool
        _orig=None,
    ):
        self.entityId = entityId
        """ 物品拥有者的实体id """
        self.item = item
        """ 物品的物品信息字典 """
        self.durabilityBefore = durabilityBefore
        """ 变化前耐久度 """
        self.durability = durability
        """ 变化后耐久度,支持修改。但是请注意修改范围，支持范围为[-32768,32767) """
        self.canChange = canChange
        """ 是否支持修改，为true时支持通过durability修改，为false时不支持 """
        self._orig = _orig or {}

    @classmethod
    def unmarshal(cls, data):
        return cls(
            entityId=data["entityId"],
            item=Item.from_dict(data["itemDict"]),
            durabilityBefore=data["durabilityBefore"],
            durability=data["durability"],
            canChange=data["canChange"],
        )

    def marshal(self):
        # type: () -> dict
        return {
            "entityId": self.entityId,
            "itemDict": self.item.marshal(),
            "durabilityBefore": self.durabilityBefore,
            "durability": self.durability,
            "canChange": self.canChange,
        }

    def ModifyDurability(self, durability):
        # type: (int) -> None
        self.durability = self._orig["durability"] = durability

    @classmethod
    def ListenWithUserData(cls, priority=0):
        # print("[TDEvent] Listen with user data: " + cls.name)
        ServerComp.CreateItem(ServerLevelId).GetUserDataInEvent(cls.name)
        return cls.Listen(priority)


class ServerItemTryUseEvent(ServerEvent):
    name = "ServerItemTryUseEvent"

    def __init__(
        self,
        playerId, # type: str
        item, # type: Item
        _orig, # type: dict
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
            "_orig": self._orig,
        }

    @classmethod
    def ListenWithUserData(cls, priority=0):
        # print("[TDEvent] Listen with user data: " + cls.name)
        ServerComp.CreateItem(ServerLevelId).GetUserDataInEvent(cls.name)
        return cls.Listen(priority)

    def cancel(self):
        # type: () -> None
        "设为True可取消物品的使用"
        self._orig["cancel"] = True


class CraftItemOutputChangeServerEvent(ServerEvent):
    name = "CraftItemOutputChangeServerEvent"

    def __init__(
        self,
        playerId, # type: str
        item, # type: Item
        screenContainerType, # type: int
        _orig, # type: dict
    ):
        self.playerId = playerId
        """ 玩家实体id """
        self.item = item
        """ 生成的物品，格式参考物品信息字典 """
        self.screenContainerType = screenContainerType
        """ 当前界面类型,类型含义见：容器类型枚举 """
        self._orig = _orig
        """ 原始事件数据 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            playerId=data["playerId"],
            item=Item.from_dict(data["itemDict"]),
            screenContainerType=data["screenContainerType"],
            _orig=data,
        )

    def marshal(self):
        # type: () -> dict
        return {
            "playerId": self.playerId,
            "itemDict": self.item.marshal(),
            "screenContainerType": self.screenContainerType,
            "_orig": self._orig,
        }

    def cancel(self):
        # type: () -> None
        "取消生成物品"
        self._orig["cancel"] = True


class UIContainerItemChangedServerEvent(ServerEvent):
    name = "UIContainerItemChangedServerEvent"

    def __init__(
        self,
        playerId, # type: str
        slot, # type: int
        oldItem, # type: Item
        newItem, # type: Item
    ):
        self.playerId = playerId
        """ 玩家实体id """
        self.slot = slot
        """ 容器槽位，含义见：容器类型枚举 """
        self.oldItem = oldItem
        """ 旧物品，格式参考物品信息字典 """
        self.newItem = newItem
        """ 生成的物品，格式参考物品信息字典 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            playerId=data["playerId"],
            slot=data["slot"],
            oldItem=Item.from_dict(data["oldItem"]),
            newItem=Item.from_dict(data["newItem"]),
        )

    def marshal(self):
        # type: () -> dict
        return {
            "playerId": self.playerId,
            "slot": self.slot,
            "oldItem": self.oldItem.marshal(),
            "newItem": self.newItem.marshal(),
        }
