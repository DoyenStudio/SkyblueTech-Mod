# coding=utf-8

from ..basic import ServerEvent
from ...define.item import Item


class BlockRandomTickServerEvent(ServerEvent):
    name = "BlockRandomTickServerEvent"

    posX = 0 # type: int
    """方块x坐标"""
    posY = 0 # type: int
    """方块y坐标"""
    posZ = 0 # type: int
    """方块z坐标"""
    blockName = '' # type: str
    """方块名称"""
    fullName = '' #  type: str
    """方块的identifier，包含命名空间及名称"""
    auxValue = 0 # type: int
    """方块附加值"""
    brightness = 0 # type: int
    """方块亮度"""
    dimensionId = 0 # type: int
    """实体维度"""

    @classmethod
    def unmarshal(
        cls,
        data, # type: dict
    ):
        instance = cls()
        instance.posX = data["posX"]
        instance.posY = data["posY"]
        instance.posZ = data["posZ"]
        instance.blockName = data["blockName"]
        instance.fullName = data["fullName"]
        instance.auxValue = data["auxValue"]
        instance.brightness = data["brightness"]
        instance.dimensionId = data["dimensionId"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "posX": self.posX,
            "posY": self.posY,
            "posZ": self.posZ,
            "blockName": self.blockName,
            "fullName": self.fullName,
            "auxValue": self.auxValue,
            "brightness": self.brightness,
            "dimensionId": self.dimensionId,
        }


class ServerBlockEntityTickEvent(ServerEvent):
    name = "ServerBlockEntityTickEvent"

    blockName = '' # type: str
    """该方块名称"""
    dimension = 0 # type: int
    """该方块所在的维度"""
    posX = 0 # type: int
    """该方块的x坐标"""
    posY = 0 # type: int
    """该方块的y坐标"""
    posZ = 0 # type: int
    """该方块的z坐标"""

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ServerBlockEntityTickEvent
        instance = cls()
        instance.blockName = data["blockName"]
        instance.dimension = data["dimension"]
        instance.posX = data["posX"]
        instance.posY = data["posY"]
        instance.posZ = data["posZ"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "blockName": self.blockName,
            "dimension": self.dimension,
            "posX": self.posX,
            "posY": self.posY,
            "posZ": self.posZ,
        }


class ServerPlaceBlockEntityEvent(ServerEvent):
    name = "ServerPlaceBlockEntityEvent"

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ServerPlaceBlockEntityEvent
        instance = cls()
        instance.blockName = data["blockName"]
        instance.dimension = data["dimension"]
        instance.posX = data["posX"]
        instance.posY = data["posY"]
        instance.posZ = data["posZ"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "blockName": self.blockName,
            "dimension": self.dimension,
            "posX": self.posX,
            "posY": self.posY,
            "posZ": self.posZ,
        }


class ServerBlockUseEvent(ServerEvent):
    name = "ServerBlockUseEvent"

    playerId = '' # type: str
    """玩家Id"""
    blockName = '' # type: str
    """方块的identifier，包含命名空间及名称"""
    aux = 0 # type: int
    """方块附加值"""
    x = 0 # type: int
    """方块x坐标"""
    y = 0 # type: int
    """方块y坐标"""
    z = 0 # type: int
    """方块z坐标"""
    clickX = 0.0 # type: float
    """点击点的x比例位置"""
    clickY = 0.0 # type: float
    """点击点的y比例位置"""
    clickZ = 0.0 # type: float
    """点击点的z比例位置"""
    face = 0 # type: int
    """点击方块的面，参考Facing枚举"""
    item = Item("") # type: Item
    """使用的物品的物品信息"""
    dimensionId = 0 # type: int
    """维度id"""

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ServerBlockUseEvent
        instance = cls()
        instance._orig = data  # type: ignore
        instance.playerId = data["playerId"]
        instance.blockName = data["blockName"]
        instance.aux = data["aux"]
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.clickX = data["clickX"]
        instance.clickY = data["clickY"]
        instance.clickZ = data["clickZ"]
        instance.face = data["face"]
        instance.item = Item.from_dict(data["itemDict"])
        instance.dimensionId = data["dimensionId"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "playerId": self.playerId,
            "blockName": self.blockName,
            "aux": self.aux,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "clickX": self.clickX,
            "clickY": self.clickY,
            "clickZ": self.clickZ,
            "face": self.face,
            "itemDict": self.item.marshal(),
            "dimensionId": self.dimensionId,
        }

    def cancel(self):
        """ 拦截与方块交互的逻辑。 """
        self._orig["cancel"] = True


class BlockNeighborChangedServerEvent(ServerEvent):
    name = "BlockNeighborChangedServerEvent"

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> BlockNeighborChangedServerEvent
        instance = cls()
        instance.dimensionId = data["dimensionId"]
        instance.posX = data["posX"]
        instance.posY = data["posY"]
        instance.posZ = data["posZ"]
        instance.blockName = data["blockName"]
        instance.auxValue = data["auxValue"]
        instance.neighborPosX = data["neighborPosX"]
        instance.neighborPosY = data["neighborPosY"]
        instance.neighborPosZ = data["neighborPosZ"]
        instance.fromBlockName = data["fromBlockName"]
        instance.fromBlockAuxValue = data["fromBlockAuxValue"]
        instance.toBlockName = data["toBlockName"]
        instance.toAuxValue = data["toAuxValue"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "dimensionId": self.dimensionId,
            "posX": self.posX,
            "posY": self.posY,
            "posZ": self.posZ,
            "blockName": self.blockName,
            "auxValue": self.auxValue,
            "neighborPosX": self.neighborPosX,
            "neighborPosY": self.neighborPosY,
            "neighborPosZ": self.neighborPosZ,
            "fromBlockName": self.fromBlockName,
            "fromBlockAuxValue": self.fromBlockAuxValue,
            "toBlockName": self.toBlockName,
            "toAuxValue": self.toAuxValue,
        }


class ServerPlayerTryDestroyBlockEvent(ServerEvent):
    name = "ServerPlayerTryDestroyBlockEvent"

    x = 0 # type: int
    """方块x坐标"""
    y = 0 # type: int
    """方块y坐标"""
    z = 0 # type: int
    """方块z坐标"""
    face = 0 # type: int
    """方块被敲击的面向id，参考Facing枚举"""
    fullName = '' # type: str
    """方块的identifier，包含命名空间及名称"""
    auxData = 0 # type: int
    """方块附加值"""
    playerId = '' # type: str
    """试图破坏方块的玩家ID"""
    dimensionId = 0 # type: int
    """维度id"""
    spawnResources = False # type: bool
    """是否生成掉落物，默认为True，在脚本层设置为False就能取消生成掉落物"""

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ServerPlayerTryDestroyBlockEvent
        instance = cls()
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.face = data["face"]
        instance.fullName = data["fullName"]
        instance.auxData = data["auxData"]
        instance.playerId = data["playerId"]
        instance.dimensionId = data["dimensionId"]
        instance.spawnResources = data["spawnResources"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "face": self.face,
            "fullName": self.fullName,
            "auxData": self.auxData,
            "playerId": self.playerId,
            "dimensionId": self.dimensionId,
            "cancel": self.cancel,
            "spawnResources": self.spawnResources,
        }
        
    def cancel(self):
        self._orig["cancel"] = True


class BlockRemoveServerEvent(ServerEvent):
    name = "BlockRemoveServerEvent"

    x = 0 # type: int
    """方块位置x"""
    y = 0 # type: int
    """方块位置y"""
    z = 0 # type: int
    """方块位置z"""
    fullName = '' # type: str
    """方块的identifier，包含命名空间及名称"""
    auxValue = 0 # type: int
    """方块的附加值"""
    dimension = 0 # type: int
    """该方块所在的维度"""

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> BlockRemoveServerEvent
        instance = cls()
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.fullName = data["fullName"]
        instance.auxValue = data["auxValue"]
        instance.dimension = data["dimension"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "fullName": self.fullName,
            "auxValue": self.auxValue,
            "dimension": self.dimension,
        }

    @classmethod
    def AddExtraBlocks(
        cls,
        blocks # type: set[str]
    ):
        from ...api.server import AddBlocksToBlockRemoveListener
        AddBlocksToBlockRemoveListener(blocks)
        return cls


class ServerEntityTryPlaceBlockEvent(ServerEvent):
    name = "ServerEntityTryPlaceBlockEvent"

    x = 0 # type: int
    """ 方块x坐标,支持修改 """
    y = 0 # type: int
    """ 方块y坐标,支持修改 """
    z = 0 # type: int
    """ 方块z坐标,支持修改 """
    fullName = '' # type: str
    """ 方块的identifier，包含命名空间及名称,支持修改 """
    auxData = 0 # type: int
    """ 方块附加值,支持修改 """
    entityId = '' # type: str
    """ 试图放置方块的生物ID """
    dimensionId = 0 # type: int
    """ 维度id """
    face = 0 # type: int
    """ 点击方块的面，参考Facing枚举 """
    clickX = 0.0 # type: float
    """ 点击点的x比例位置 """
    clickY = 0.0 # type: float
    """ 点击点的y比例位置 """
    clickZ = 0.0 # type: float
    """ 点击点的z比例位置 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ServerEntityTryPlaceBlockEvent
        instance = cls()
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.fullName = data["fullName"]
        instance.auxData = data["auxData"]
        instance.entityId = data["entityId"]
        instance.dimensionId = data["dimensionId"]
        instance.face = data["face"]
        instance.clickX = data["clickX"]
        instance.clickY = data["clickY"]
        instance.clickZ = data["clickZ"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "fullName": self.fullName,
            "auxData": self.auxData,
            "entityId": self.entityId,
            "dimensionId": self.dimensionId,
            "face": self.face,
            "clickX": self.clickX,
            "clickY": self.clickY,
            "clickZ": self.clickZ,
        }

    def cancel(self):
        self._orig["cancel"] = True

class DestroyBlockEvent(ServerEvent):
    name = "DestroyBlockEvent"

    x = 0 # type: int
    """ 方块x坐标 """
    y = 0 # type: int
    """ 方块y坐标 """
    z = 0 # type: int
    """ 方块z坐标 """
    face = 0 # type: int
    """ 方块被敲击的面向id，参考Facing枚举 """
    fullName = '' # type: str
    """ 方块的identifier，包含命名空间及名称 """
    auxData = 0 # type: int
    """ 方块附加值 """
    playerId = '' # type: str
    """ 破坏方块的玩家ID """
    dimensionId = 0 # type: int
    """ 维度id """
    dropEntityIds = [] # type: list[str]
    """ 掉落物实体id列表 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> DestroyBlockEvent
        instance = cls()
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.face = data["face"]
        instance.fullName = data["fullName"]
        instance.auxData = data["auxData"]
        instance.playerId = data["playerId"]
        instance.dimensionId = data["dimensionId"]
        instance.dropEntityIds = data["dropEntityIds"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "face": self.face,
            "fullName": self.fullName,
            "auxData": self.auxData,
            "playerId": self.playerId,
            "dimensionId": self.dimensionId,
            "dropEntityIds": self.dropEntityIds,
        }


class EntityPlaceBlockAfterServerEvent(ServerEvent):
    name = "EntityPlaceBlockAfterServerEvent"

    x = 0 # type: int
    """ 方块x坐标 """
    y = 0 # type: int
    """ 方块y坐标 """
    z = 0 # type: int
    """ 方块z坐标 """
    fullName = "" # type: str
    """ 方块的identifier，包含命名空间及名称 """
    auxData = 0 # type: int
    """ 方块附加值 """
    entityId = "" # type: str
    """ 试图放置方块的生物ID """
    dimensionId = 0 # type: int
    """ 维度id """
    face = 0 # type: int
    """ 点击方块的面，参考Facing枚举 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> EntityPlaceBlockAfterServerEvent
        instance = cls()
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.fullName = data["fullName"]
        instance.auxData = data["auxData"]
        instance.entityId = data["entityId"]
        instance.dimensionId = data["dimensionId"]
        instance.face = data["face"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "fullName": self.fullName,
            "auxData": self.auxData,
            "entityId": self.entityId,
            "dimensionId": self.dimensionId,
            "face": self.face,
        }


class PistonActionServerEvent(ServerEvent):
    name = "PistonActionServerEvent"

    action = "" # type: str
    """ 推送时=expanding；缩回时=retracting """
    pistonFacing = 0 # type: int
    """ 活塞的朝向，参考Facing枚举 """
    pistonMoveFacing = 0 # type: int
    """ 活塞的运动方向，参考Facing枚举 """
    dimensionId = 0 # type: int
    """ 活塞方块所在的维度 """
    pistonX = 0 # type: int
    """ 活塞方块的x坐标 """
    pistonY = 0 # type: int
    """ 活塞方块的y坐标 """
    pistonZ = 0 # type: int
    """ 活塞方块的z坐标 """
    blockList = [] # type: list[list[int]]
    """ 活塞运动影响到产生被移动效果的方块坐标[x,y,z]，均为int类型 """
    breakBlockList = [] # type: list[list[int]]
    """ 活塞运动影响到产生被破坏效果的方块坐标[x,y,z]，均为int类型 """
    entityList = [] # type: list[str]
    """ 活塞运动影响到产生被移动或被破坏效果的实体的ID列表 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> PistonActionServerEvent
        instance = cls()
        instance._orig = data  # type: ignore
        instance.action = data["action"]
        instance.pistonFacing = data["pistonFacing"]
        instance.pistonMoveFacing = data["pistonMoveFacing"]
        instance.dimensionId = data["dimensionId"]
        instance.pistonX = data["pistonX"]
        instance.pistonY = data["pistonY"]
        instance.pistonZ = data["pistonZ"]
        instance.blockList = data["blockList"]
        instance.breakBlockList = data["breakBlockList"]
        instance.entityList = data["entityList"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "action": self.action,
            "pistonFacing": self.pistonFacing,
            "pistonMoveFacing": self.pistonMoveFacing,
            "dimensionId": self.dimensionId,
            "pistonX": self.pistonX,
            "pistonY": self.pistonY,
            "pistonZ": self.pistonZ,
            "blockList": self.blockList,
            "breakBlockList": self.breakBlockList,
            "entityList": self.entityList,
        }

    def cancel(self):
        # type: () -> None
        "允许触发，默认为False，若设为True，可阻止触发后续的事件"
        self._orig["cancel"] = True
