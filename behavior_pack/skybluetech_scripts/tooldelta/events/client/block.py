# coding=utf-8

from ..basic import ClientEvent


class ClientBlockUseEvent(ClientEvent):
    name = "ClientBlockUseEvent"

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
            "_orig": self._orig,
        }

    def cancel(self):
        # type: () -> None
        "设置为True可拦截与方块交互的逻辑。"
        self._orig["cancel"] = True


class ModBlockEntityLoadedClientEvent(ClientEvent):
    name = "ModBlockEntityLoadedClientEvent"

    def __init__(
        self,
        posX,  # type: int
        posY,  # type: int
        posZ,  # type: int
        dimensionId,  # type: int
        blockName,  # type: str
    ):
        self.posX = posX
        """ 自定义方块实体的位置X """
        self.posY = posY
        """ 自定义方块实体的位置Y """
        self.posZ = posZ
        """ 自定义方块实体的位置Z """
        self.dimensionId = dimensionId
        """ 维度id """
        self.blockName = blockName
        """ 方块的identifier，包含命名空间及名称 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            posX=data["posX"],
            posY=data["posY"],
            posZ=data["posZ"],
            dimensionId=data["dimensionId"],
            blockName=data["blockName"],
        )

    def marshal(self):
        # type: () -> dict
        return {
            "posX": self.posX,
            "posY": self.posY,
            "posZ": self.posZ,
            "dimensionId": self.dimensionId,
            "blockName": self.blockName,
        }


class ModBlockEntityRemoveClientEvent(ClientEvent):
    name = "ModBlockEntityRemoveClientEvent"

    def __init__(
        self,
        posX,  # type: int
        posY,  # type: int
        posZ,  # type: int
        dimensionId,  # type: int
        blockName,  # type: str
    ):
        self.posX = posX
        """ 自定义方块实体的位置X """
        self.posY = posY
        """ 自定义方块实体的位置Y """
        self.posZ = posZ
        """ 自定义方块实体的位置Z """
        self.dimensionId = dimensionId
        """ 维度id """
        self.blockName = blockName
        """ 方块的identifier，包含命名空间及名称 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            posX=data["posX"],
            posY=data["posY"],
            posZ=data["posZ"],
            dimensionId=data["dimensionId"],
            blockName=data["blockName"],
        )

    def marshal(self):
        # type: () -> dict
        return {
            "posX": self.posX,
            "posY": self.posY,
            "posZ": self.posZ,
            "dimensionId": self.dimensionId,
            "blockName": self.blockName,
        }


class PlayerTryDestroyBlockClientEvent(ClientEvent):
    name = "PlayerTryDestroyBlockClientEvent"

    def __init__(
        self,
        x,  # type: int
        y,  # type: int
        z,  # type: int
        face,  # type: int
        blockName,  # type: str
        auxData,  # type: int
        playerId,  # type: str
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
        self.blockName = blockName
        """ 方块的identifier，包含命名空间及名称 """
        self.auxData = auxData
        """ 方块附加值 """
        self.playerId = playerId
        """ 试图破坏方块的玩家ID """
        self._orig = _orig
        """ 原始事件数据 """

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            face=data["face"],
            blockName=data["blockName"],
            auxData=data["auxData"],
            playerId=data["playerId"],
            _orig=data,
        )

    def marshal(self):
        # type: () -> dict
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "face": self.face,
            "blockName": self.blockName,
            "auxData": self.auxData,
            "playerId": self.playerId,
            "_orig": self._orig,
        }

    def cancel(self):
        # type: () -> None
        "默认为False，在脚本层设置为True就能取消该方块的破坏"
        self._orig["cancel"] = True


class StartDestroyBlockClientEvent(ClientEvent):
    name = "StartDestroyBlockClientEvent"

    def __init__(
        self,
        pos,  # type: tuple[float,float,float]
        blockName,  # type: str
        auxValue,  # type: int
        playerId,  # type: str
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
            "face": self.face,
            "_orig": self._orig,
        }

    def cancel(self):
        # type: () -> None
        "修改为True时，可阻止玩家进入挖方块的状态。需要与StartDestroyBlockServerEvent一起修改。"
        self._orig["cancel"] = True
