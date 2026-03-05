# coding=utf-8
from mod.server.extraServerApi import GetMinecraftEnum
from ..basic import ServerEvent
from ...define.item import Item


class BlockRandomTickServerEvent(ServerEvent):
    name = "BlockRandomTickServerEvent"

    def __init__(
        self,
        posX,  # type: int
        posY,  # type: int
        posZ,  # type: int
        blockName,  # type: str
        fullName,  # type: str
        auxValue,  # type: int
        brightness,  # type: int
        dimensionId,  # type: int
    ):
        self.posX = posX
        """ 方块x坐标 """
        self.posY = posY
        """ 方块y坐标 """
        self.posZ = posZ
        """ 方块z坐标 """
        self.blockName = blockName
        """ 方块名称 """
        self.fullName = fullName
        """ 方块的identifier，包含命名空间及名称 """
        self.auxValue = auxValue
        """ 方块附加值 """
        self.brightness = brightness
        """ 方块亮度 """
        self.dimensionId = dimensionId
        """ 方块所在维度 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            posX=data["posX"],
            posY=data["posY"],
            posZ=data["posZ"],
            blockName=data["blockName"],
            fullName=data["fullName"],
            auxValue=data["auxValue"],
            brightness=data["brightness"],
            dimensionId=data["dimensionId"],
        )

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

    def __init__(
        self,
        blockName,  # type: str
        dimension,  # type: int
        posX,  # type: int
        posY,  # type: int
        posZ,  # type: int
    ):
        self.blockName = blockName
        """ 该方块名称 """
        self.dimension = dimension
        """ 该方块所在的维度 """
        self.posX = posX
        """ 该方块的x坐标 """
        self.posY = posY
        """ 该方块的y坐标 """
        self.posZ = posZ
        """ 该方块的z坐标 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            blockName=data["blockName"],
            dimension=data["dimension"],
            posX=data["posX"],
            posY=data["posY"],
            posZ=data["posZ"],
        )

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

    def __init__(
        self,
        blockName,  # type: str
        dimension,  # type: int
        posX,  # type: int
        posY,  # type: int
        posZ,  # type: int
    ):
        self.blockName = blockName
        """ 该方块名称 """
        self.dimension = dimension
        """ 该方块所在的维度 """
        self.posX = posX
        """ 该方块的x坐标 """
        self.posY = posY
        """ 该方块的y坐标 """
        self.posZ = posZ
        """ 该方块的z坐标 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            blockName=data["blockName"],
            dimension=data["dimension"],
            posX=data["posX"],
            posY=data["posY"],
            posZ=data["posZ"],
        )

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

    def __init__(
        self,
        playerId,  # type: str
        blockName,  # type: str
        aux,  # type: int
        x,  # type: int
        y,  # type: int
        z,  # type: int
        clickX,  # type: float
        clickY,  # type: float
        clickZ,  # type: float
        face,  # type: int
        item,  # type: Item
        dimensionId,  # type: int
        _orig,  # type: dict
    ):
        self.playerId = playerId
        """ 玩家Id """
        self.blockName = blockName
        """ 方块的identifier，包含命名空间及名称 """
        self.aux = aux
        """ 方块附加值 """
        self.x = x
        """ 方块x坐标 """
        self.y = y
        """ 方块y坐标 """
        self.z = z
        """ 方块z坐标 """
        self.clickX = clickX
        """ 点击点的x比例位置 """
        self.clickY = clickY
        """ 点击点的y比例位置 """
        self.clickZ = clickZ
        """ 点击点的z比例位置 """
        self.face = face
        """ 点击方块的面，参考Facing枚举 """
        self.item = item
        """ 使用的物品的物品信息字典 """
        self.dimensionId = dimensionId
        """ 维度id """
        self._orig = _orig
        """ 原始事件数据 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            playerId=data["playerId"],
            blockName=data["blockName"],
            aux=data["aux"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            clickX=data["clickX"],
            clickY=data["clickY"],
            clickZ=data["clickZ"],
            face=data["face"],
            item=Item.from_dict(data["itemDict"]),
            dimensionId=data["dimensionId"],
            _orig=data,
        )

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
            "_orig": self._orig,
        }

    def cancel(self):
        # type: () -> None
        "设置为True可拦截与方块交互的逻辑。"
        self._orig["cancel"] = True


class BlockNeighborChangedServerEvent(ServerEvent):
    name = "BlockNeighborChangedServerEvent"

    def __init__(
        self,
        dimensionId,  # type: int
        posX,  # type: int
        posY,  # type: int
        posZ,  # type: int
        blockName,  # type: str
        auxValue,  # type: int
        neighborPosX,  # type: int
        neighborPosY,  # type: int
        neighborPosZ,  # type: int
        fromBlockName,  # type: str
        fromBlockAuxValue,  # type: int
        toBlockName,  # type: str
        toAuxValue,  # type: int
    ):
        self.dimensionId = dimensionId
        """ 维度 """
        self.posX = posX
        """ 方块x坐标 """
        self.posY = posY
        """ 方块y坐标 """
        self.posZ = posZ
        """ 方块z坐标 """
        self.blockName = blockName
        """ 方块的identifier，包含命名空间及名称 """
        self.auxValue = auxValue
        """ 方块附加值 """
        self.neighborPosX = neighborPosX
        """ 变化方块x坐标 """
        self.neighborPosY = neighborPosY
        """ 变化方块y坐标 """
        self.neighborPosZ = neighborPosZ
        """ 变化方块z坐标 """
        self.fromBlockName = fromBlockName
        """ 方块变化前的identifier，包含命名空间及名称 """
        self.fromBlockAuxValue = fromBlockAuxValue
        """ 方块变化前附加值 """
        self.toBlockName = toBlockName
        """ 方块变化后的identifier，包含命名空间及名称 """
        self.toAuxValue = toAuxValue
        """ 方块变化后附加值 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            dimensionId=data["dimensionId"],
            posX=data["posX"],
            posY=data["posY"],
            posZ=data["posZ"],
            blockName=data["blockName"],
            auxValue=data["auxValue"],
            neighborPosX=data["neighborPosX"],
            neighborPosY=data["neighborPosY"],
            neighborPosZ=data["neighborPosZ"],
            fromBlockName=data["fromBlockName"],
            fromBlockAuxValue=data["fromBlockAuxValue"],
            toBlockName=data["toBlockName"],
            toAuxValue=data["toAuxValue"],
        )

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

    def __init__(
        self,
        x,  # type: int
        y,  # type: int
        z,  # type: int
        face,  # type: int
        fullName,  # type: str
        auxData,  # type: int
        playerId,  # type: str
        dimensionId,  # type: int
        spawnResources,  # type: bool
        _orig,  # type: dict
    ):
        self.x = x
        """ 方块x坐标 """
        self.y = y
        """ 方块y坐标 """
        self.z = z
        """ 方块z坐标 """
        self.face = face
        """ 方块被敲击的面向id，参考Facing枚举 """
        self.fullName = fullName
        """ 方块的identifier，包含命名空间及名称 """
        self.auxData = auxData
        """ 方块附加值 """
        self.playerId = playerId
        """ 试图破坏方块的玩家ID """
        self.dimensionId = dimensionId
        """ 维度id """
        self.spawnResources = spawnResources
        """ 是否生成掉落物，默认为True，在脚本层设置为False就能取消生成掉落物 """
        self._orig = _orig
        """ 原始事件数据 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            face=data["face"],
            fullName=data["fullName"],
            auxData=data["auxData"],
            playerId=data["playerId"],
            dimensionId=data["dimensionId"],
            spawnResources=data["spawnResources"],
            _orig=data,
        )

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
            "spawnResources": self.spawnResources,
            "_orig": self._orig,
        }

    def cancel(self):
        # type: () -> None
        "默认为False，在脚本层设置为True就能取消该方块的破坏"
        self._orig["cancel"] = True


class BlockRemoveServerEvent(ServerEvent):
    name = "BlockRemoveServerEvent"

    def __init__(
        self,
        x,  # type: int
        y,  # type: int
        z,  # type: int
        fullName,  # type: str
        auxValue,  # type: int
        dimension,  # type: int
    ):
        self.x = x
        """ 方块位置x """
        self.y = y
        """ 方块位置y """
        self.z = z
        """ 方块位置z """
        self.fullName = fullName
        """ 方块的identifier，包含命名空间及名称 """
        self.auxValue = auxValue
        """ 方块的附加值 """
        self.dimension = dimension
        """ 该方块所在的维度 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            fullName=data["fullName"],
            auxValue=data["auxValue"],
            dimension=data["dimension"],
        )

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
        blocks,  # type: set[str]
    ):
        from ...api.server import AddBlocksToBlockRemoveListener

        AddBlocksToBlockRemoveListener(blocks)
        return cls


class ServerEntityTryPlaceBlockEvent(ServerEvent):
    name = "ServerEntityTryPlaceBlockEvent"

    def __init__(
        self,
        x,  # type: int
        y,  # type: int
        z,  # type: int
        fullName,  # type: str
        auxData,  # type: int
        entityId,  # type: str
        dimensionId,  # type: int
        face,  # type: int
        clickX,  # type: float
        clickY,  # type: float
        clickZ,  # type: float
        _orig,  # type: dict
    ):
        self.x = x
        """ 方块x坐标,支持修改 """
        self.y = y
        """ 方块y坐标,支持修改 """
        self.z = z
        """ 方块z坐标,支持修改 """
        self.fullName = fullName
        """ 方块的identifier，包含命名空间及名称,支持修改 """
        self.auxData = auxData
        """ 方块附加值,支持修改 """
        self.entityId = entityId
        """ 试图放置方块的生物ID """
        self.dimensionId = dimensionId
        """ 维度id """
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
            x=data["x"],
            y=data["y"],
            z=data["z"],
            fullName=data["fullName"],
            auxData=data["auxData"],
            entityId=data["entityId"],
            dimensionId=data["dimensionId"],
            face=data["face"],
            clickX=data["clickX"],
            clickY=data["clickY"],
            clickZ=data["clickZ"],
            _orig=data,
        )

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
            "_orig": self._orig,
        }

    def cancel(self):
        # type: () -> None
        "默认为False，在脚本层设置为True就能取消该方块的放置"
        self._orig["cancel"] = True


class DestroyBlockEvent(ServerEvent):
    name = "DestroyBlockEvent"

    def __init__(
        self,
        x,  # type: int
        y,  # type: int
        z,  # type: int
        face,  # type: int
        fullName,  # type: str
        auxData,  # type: int
        playerId,  # type: str
        dimensionId,  # type: int
        dropEntityIds,  # type: list[str]
    ):
        self.x = x
        """ 方块x坐标 """
        self.y = y
        """ 方块y坐标 """
        self.z = z
        """ 方块z坐标 """
        self.face = face
        """ 方块被敲击的面向id，参考Facing枚举 """
        self.fullName = fullName
        """ 方块的identifier，包含命名空间及名称 """
        self.auxData = auxData
        """ 方块附加值 """
        self.playerId = playerId
        """ 破坏方块的玩家ID """
        self.dimensionId = dimensionId
        """ 维度id """
        self.dropEntityIds = dropEntityIds
        """ 掉落物实体id列表 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            face=data["face"],
            fullName=data["fullName"],
            auxData=data["auxData"],
            playerId=data["playerId"],
            dimensionId=data["dimensionId"],
            dropEntityIds=data["dropEntityIds"],
        )

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

    def __init__(
        self,
        x,  # type: int
        y,  # type: int
        z,  # type: int
        fullName,  # type: str
        auxData,  # type: int
        entityId,  # type: str
        dimensionId,  # type: int
        face,  # type: int
    ):
        self.x = x
        """ 方块x坐标 """
        self.y = y
        """ 方块y坐标 """
        self.z = z
        """ 方块z坐标 """
        self.fullName = fullName
        """ 方块的identifier，包含命名空间及名称 """
        self.auxData = auxData
        """ 方块附加值 """
        self.entityId = entityId
        """ 试图放置方块的生物ID """
        self.dimensionId = dimensionId
        """ 维度id """
        self.face = face
        """ 点击方块的面，参考Facing枚举 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            fullName=data["fullName"],
            auxData=data["auxData"],
            entityId=data["entityId"],
            dimensionId=data["dimensionId"],
            face=data["face"],
        )

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

    def __init__(
        self,
        action,  # type: str
        pistonFacing,  # type: int
        pistonMoveFacing,  # type: int
        dimensionId,  # type: int
        pistonX,  # type: int
        pistonY,  # type: int
        pistonZ,  # type: int
        blockList,  # type: list[list[int]]
        breakBlockList,  # type: list[list[int]]
        entityList,  # type: list[str]
        _orig,  # type: dict
    ):
        self.action = action
        """ 推送时=expanding；缩回时=retracting """
        self.pistonFacing = pistonFacing
        """ 活塞的朝向，参考Facing枚举 """
        self.pistonMoveFacing = pistonMoveFacing
        """ 活塞的运动方向，参考Facing枚举 """
        self.dimensionId = dimensionId
        """ 活塞方块所在的维度 """
        self.pistonX = pistonX
        """ 活塞方块的x坐标 """
        self.pistonY = pistonY
        """ 活塞方块的y坐标 """
        self.pistonZ = pistonZ
        """ 活塞方块的z坐标 """
        self.blockList = blockList
        """ 活塞运动影响到产生被移动效果的方块坐标[x,y,z]，均为int类型 """
        self.breakBlockList = breakBlockList
        """ 活塞运动影响到产生被破坏效果的方块坐标[x,y,z]，均为int类型 """
        self.entityList = entityList
        """ 活塞运动影响到产生被移动或被破坏效果的实体的ID列表 """
        self._orig = _orig
        """ 原始事件数据 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            action=data["action"],
            pistonFacing=data["pistonFacing"],
            pistonMoveFacing=data["pistonMoveFacing"],
            dimensionId=data["dimensionId"],
            pistonX=data["pistonX"],
            pistonY=data["pistonY"],
            pistonZ=data["pistonZ"],
            blockList=data["blockList"],
            breakBlockList=data["breakBlockList"],
            entityList=data["entityList"],
            _orig=data,
        )

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
            "_orig": self._orig,
        }

    def cancel(self):
        # type: () -> None
        "允许触发，默认为False，若设为True，可阻止触发后续的事件"
        self._orig["cancel"] = True


class FarmBlockToDirtBlockServerEvent(ServerEvent):
    name = "FarmBlockToDirtBlockServerEvent"

    def __init__(
        self,
        dimension,  # type: int
        x,  # type: int
        y,  # type: int
        z,  # type: int
        setBlockType,  # type: int
    ):
        self.dimension = dimension
        """ 方块维度 """
        self.x = x
        """ 方块x坐标 """
        self.y = y
        """ 方块y坐标 """
        self.z = z
        """ 方块z坐标 """
        self.setBlockType = setBlockType
        """ 耕地退化为泥土的原因，参考SetBlockType """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            dimension=data["dimension"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            setBlockType=data["setBlockType"],
        )

    def marshal(self):
        # type: () -> dict
        return {
            "dimension": self.dimension,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "setBlockType": self.setBlockType,
        }

    @property
    def is_manual(self):
        return self.setBlockType == GetMinecraftEnum().SetBlockType.MAN_MADE


class StartDestroyBlockServerEvent(ServerEvent):
    name = "StartDestroyBlockServerEvent"

    def __init__(
        self,
        pos,  # type: tuple[float,float,float]
        blockName,  # type: str
        auxValue,  # type: int
        playerId,  # type: str
        dimensionId,  # type: int
        face,  # type: int
        _orig,  # type: dict
    ):
        self.pos = pos
        """ 方块的坐标 """
        self.blockName = blockName
        """ 方块的identifier，包含命名空间及名称 """
        self.auxValue = auxValue
        """ 方块的附加值 """
        self.playerId = playerId
        """ 玩家id """
        self.dimensionId = dimensionId
        """ 维度id """
        self.face = face
        """ 方块被敲击面,参考Facing枚举 """
        self._orig = _orig
        """ 原始事件数据 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            pos=data["pos"],
            blockName=data["blockName"],
            auxValue=data["auxValue"],
            playerId=data["playerId"],
            dimensionId=data["dimensionId"],
            face=data["face"],
            _orig=data,
        )

    def marshal(self):
        # type: () -> dict
        return {
            "pos": self.pos,
            "blockName": self.blockName,
            "auxValue": self.auxValue,
            "playerId": self.playerId,
            "dimensionId": self.dimensionId,
            "face": self.face,
            "_orig": self._orig,
        }

    def cancel(self):
        # type: () -> None
        "修改为True时，可阻止玩家进入挖方块的状态。需要与StartDestroyBlockClientEvent一起修改。"
        self._orig["cancel"] = True
