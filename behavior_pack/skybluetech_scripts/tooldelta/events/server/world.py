from ..basic import ServerEvent


class DelServerPlayerEvent(ServerEvent):
    name = "DelServerPlayerEvent"

    id = '' # type: str
    """玩家id"""
    isTransfer = False # type: bool
    """是否是切服时退出服务器，仅用于Apollo。如果是True，则表示切服时退出服务器；若是False，则表示退出网络游戏"""
    uid = 0 # type: int
    """玩家的netease uid，玩家的唯一标识"""

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> DelServerPlayerEvent
        instance = cls()
        instance.id = data["id"]
        instance.isTransfer = data["isTransfer"]
        instance.uid = data["uid"]
        return instance


class ChunkAcquireDiscardedServerEvent(ServerEvent):
    name = "ChunkAcquireDiscardedServerEvent"

    dimension = 0 # type: int
    """ 区块所在维度 """
    chunkPosX = 0 # type: int
    """ 区块的x坐标，对应方块X坐标区间为[x * 16, x * 16 + 15] """
    chunkPosZ = 0 # type: int
    """ 区块的z坐标，对应方块Z坐标区间为[z * 16, z * 16 + 15] """
    entities = [] # type: list[str]
    """ 随区块卸载而从世界移除的实体id的列表。注意事件触发时已经无法获取到这些实体的信息，仅供脚本资源回收用。 """
    blockEntities = [] # type: list[dict]
    """ 随区块卸载而从世界移除的自定义方块实体的坐标的列表，列表元素dict包含posX，posY，posZ三个int表示自定义方块实体的坐标，blockName表示方块的identifier，包含命名空间及名称。注意事件触发时已经无法获取到这些方块实体的信息，仅供脚本资源回收用。 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ChunkAcquireDiscardedServerEvent
        instance = cls()
        instance.dimension = data["dimension"]
        instance.chunkPosX = data["chunkPosX"]
        instance.chunkPosZ = data["chunkPosZ"]
        instance.entities = data["entities"]
        instance.blockEntities = data["blockEntities"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "dimension": self.dimension,
            "chunkPosX": self.chunkPosX,
            "chunkPosZ": self.chunkPosZ,
            "entities": self.entities,
            "blockEntities": self.blockEntities,
        }


class ChunkLoadedServerEvent(ServerEvent):
    name = "ChunkLoadedServerEvent"

    dimension = 0 # type: int
    """ 区块所在维度 """
    chunkPosX = 0 # type: int
    """ 区块的x坐标，对应方块X坐标区间为[x * 16, x * 16 + 15] """
    chunkPosZ = 0 # type: int
    """ 区块的z坐标，对应方块Z坐标区间为[z * 16, z * 16 + 15] """
    blockEntities = [] # type: list[dict]
    """ 随区块加载而加载进世界的自定义方块实体的坐标的列表，列表元素dict包含posX，posY，posZ三个int表示自定义方块实体的坐标，blockName表示方块的identifier，包含命名空间及名称 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ChunkLoadedServerEvent
        instance = cls()
        instance.dimension = data["dimension"]
        instance.chunkPosX = data["chunkPosX"]
        instance.chunkPosZ = data["chunkPosZ"]
        instance.blockEntities = data["blockEntities"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "dimension": self.dimension,
            "chunkPosX": self.chunkPosX,
            "chunkPosZ": self.chunkPosZ,
            "blockEntities": self.blockEntities,
        }
