# coding=utf-8

from ..basic import ClientEvent


class ClientBlockUseEvent(ClientEvent):
    name = "ClientBlockUseEvent"

    playerId = ""  # type: str
    """ 玩家Id """
    blockName = ""  # type: str
    """ 方块的identifier，包含命名空间及名称 """
    aux = 0  # type: int
    """ 方块附加值 """
    x = 0  # type: int
    """ 方块x坐标 """
    y = 0  # type: int
    """ 方块y坐标 """
    z = 0  # type: int
    """ 方块z坐标 """
    clickX = 0.0  # type: float
    """ 点击点的x比例位置 """
    clickY = 0.0  # type: float
    """ 点击点的y比例位置 """
    clickZ = 0.0  # type: float
    """ 点击点的z比例位置 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ClientBlockUseEvent
        instance = cls()
        instance._orig = data
        instance.playerId = data["playerId"]
        instance.blockName = data["blockName"]
        instance.aux = data["aux"]
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.clickX = data["clickX"]
        instance.clickY = data["clickY"]
        instance.clickZ = data["clickZ"]
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
        }

    def cancel(self):
        """拦截与方块交互的逻辑。"""
        self._orig["cancel"] = True

    @classmethod
    def AddExtraBlocks(
        cls,
        blocks,  # type: set[str]
    ):
        from ...api.client import AddBlockUseListener

        AddBlockUseListener(blocks)
        return cls


class ModBlockEntityLoadedClientEvent(ClientEvent):
    name = "ModBlockEntityLoadedClientEvent"

    posX = 0  # type: int
    """ 自定义方块实体的位置X """
    posY = 0  # type: int
    """ 自定义方块实体的位置Y """
    posZ = 0  # type: int
    """ 自定义方块实体的位置Z """
    dimensionId = 0  # type: int
    """ 维度id """
    blockName = ""  # type: str
    """ 方块的identifier，包含命名空间及名称 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ModBlockEntityLoadedClientEvent
        instance = cls()
        instance.posX = data["posX"]
        instance.posY = data["posY"]
        instance.posZ = data["posZ"]
        instance.dimensionId = data["dimensionId"]
        instance.blockName = data["blockName"]
        return instance

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

    posX = 0  # type: int
    """ 自定义方块实体的位置X """
    posY = 0  # type: int
    """ 自定义方块实体的位置Y """
    posZ = 0  # type: int
    """ 自定义方块实体的位置Z """
    dimensionId = 0  # type: int
    """ 维度id """
    blockName = ""  # type: str
    """ 方块的identifier，包含命名空间及名称 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ModBlockEntityRemoveClientEvent
        instance = cls()
        instance.posX = data["posX"]
        instance.posY = data["posY"]
        instance.posZ = data["posZ"]
        instance.dimensionId = data["dimensionId"]
        instance.blockName = data["blockName"]
        return instance

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

    x = 0  # type: int
    """ 方块x坐标 """
    y = 0  # type: int
    """ 方块y坐标 """
    z = 0  # type: int
    """ 方块z坐标 """
    face = 0  # type: int
    """ 方块被敲击的面向id，参考Facing枚举 """
    blockName = ""  # type: str
    """ 方块的identifier，包含命名空间及名称 """
    auxData = 0  # type: int
    """ 方块附加值 """
    playerId = ""  # type: str
    """ 试图破坏方块的玩家ID """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> PlayerTryDestroyBlockClientEvent
        instance = cls()
        instance._orig = data
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.face = data["face"]
        instance.blockName = data["blockName"]
        instance.auxData = data["auxData"]
        instance.playerId = data["playerId"]
        return instance

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
        }

    def cancel(self):
        # type: () -> None
        "默认为False，在脚本层设置为True就能取消该方块的破坏"
        self._orig["cancel"] = True
