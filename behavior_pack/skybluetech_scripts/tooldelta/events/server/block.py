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


    def unmarshal(self, data):
        # type: (dict) -> None
        self.posX = data["posX"]
        self.posY = data["posY"]
        self.posZ = data["posZ"]
        self.blockName = data["blockName"]
        self.fullName = data["fullName"]
        self.auxValue = data["auxValue"]
        self.brightness = data["brightness"]
        self.dimensionId = data["dimensionId"]

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


    def unmarshal(self, data):
        # type: (dict) -> None
        self.blockName = data["blockName"]
        self.dimension = data["dimension"]
        self.posX = data["posX"]
        self.posY = data["posY"]
        self.posZ = data["posZ"]

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

    def __init__(self, blockName="", dimension=0, posX=0, posY=0, posZ=0):
        self.blockName = blockName
        self.dimension = dimension
        self.posX = posX
        self.posY = posY
        self.posZ = posZ

    def unmarshal(self, data):  # type: (dict) -> None
        self.blockName = data["blockName"]  # type: str
        self.dimension = data["dimension"]  # type: int
        self.posX = data["posX"]  # type: int
        self.posY = data["posY"]  # type: int
        self.posZ = data["posZ"]  # type: int


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


    def unmarshal(self, data):
        # type: (dict) -> None
        self._orig = data
        self.playerId = data["playerId"]
        self.blockName = data["blockName"]
        self.aux = data["aux"]
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.clickX = data["clickX"]
        self.clickY = data["clickY"]
        self.clickZ = data["clickZ"]
        self.face = data["face"]
        self.item = Item.from_dict(data["itemDict"])
        self.dimensionId = data["dimensionId"]

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

    def __init__(self,
                 dimensionId=0, posX=0, posY=0, posZ=0,
                 blockName="", auxValue=0,
                 neighborPosX=0, neighborPosY=0, neighborPosZ=0,
                 fromBlockName="", fromBlockAuxValue=0, toBlockName="", toAuxValue=0):
        self.dimensionId = dimensionId
        self.posX = posX
        self.posY = posY
        self.posZ = posZ
        self.blockName = blockName
        self.auxValue = auxValue
        self.neighborPosX = neighborPosX
        self.neighborPosY = neighborPosY
        self.neighborPosZ = neighborPosZ
        self.fromBlockName = fromBlockName
        self.toBlockName = toBlockName
        self.fromBlockAuxValue = fromBlockAuxValue
        self.toAuxValue = toAuxValue

    def unmarshal(self, data):
        # type: (dict) -> None
        self.dimensionId = data["dimensionId"]  # type: int
        self.posX = data["posX"]  # type: int
        self.posY = data["posY"]  # type: int
        self.posZ = data["posZ"]  # type: int
        self.blockName = data["blockName"]  # type: str
        self.auxValue = data["auxValue"]  # type: int
        self.neighborPosX = data["neighborPosX"]  # type: int
        self.neighborPosY = data["neighborPosY"]  # type: int
        self.neighborPosZ = data["neighborPosZ"]  # type: int
        self.fromBlockName = data["fromBlockName"]  # type: str
        self.fromBlockAuxValue = data["fromBlockAuxValue"]  # type: int
        self.toBlockName = data["toBlockName"]  # type: str
        self.toAuxValue = data["toAuxValue"]  # type: int


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


    def unmarshal(self, data):
        # type: (dict) -> None
        self._orig = data
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.face = data["face"]
        self.fullName = data["fullName"]
        self.auxData = data["auxData"]
        self.playerId = data["playerId"]
        self.dimensionId = data["dimensionId"]
        self.spawnResources = data["spawnResources"]

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


    def unmarshal(self, data):
        # type: (dict) -> None
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.fullName = data["fullName"]
        self.auxValue = data["auxValue"]
        self.dimension = data["dimension"]

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


    def unmarshal(self, data):
        # type: (dict) -> None
        self._orig = data
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.fullName = data["fullName"]
        self.auxData = data["auxData"]
        self.entityId = data["entityId"]
        self.dimensionId = data["dimensionId"]
        self.face = data["face"]
        self.clickX = data["clickX"]
        self.clickY = data["clickY"]
        self.clickZ = data["clickZ"]

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


    def unmarshal(self, data):
        # type: (dict) -> None
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.face = data["face"]
        self.fullName = data["fullName"]
        self.auxData = data["auxData"]
        self.playerId = data["playerId"]
        self.dimensionId = data["dimensionId"]
        self.dropEntityIds = data["dropEntityIds"]

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

    def unmarshal(self, data):
        # type: (dict) -> None
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.fullName = data["fullName"]
        self.auxData = data["auxData"]
        self.entityId = data["entityId"]
        self.dimensionId = data["dimensionId"]
        self.face = data["face"]

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

    def unmarshal(self, data):
        # type: (dict) -> None
        self._orig = data
        self.action = data["action"]
        self.pistonFacing = data["pistonFacing"]
        self.pistonMoveFacing = data["pistonMoveFacing"]
        self.dimensionId = data["dimensionId"]
        self.pistonX = data["pistonX"]
        self.pistonY = data["pistonY"]
        self.pistonZ = data["pistonZ"]
        self.blockList = data["blockList"]
        self.breakBlockList = data["breakBlockList"]
        self.entityList = data["entityList"]

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
