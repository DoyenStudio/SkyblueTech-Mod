# coding=utf-8

from ..basic import ServerEvent


class EntityDieLoottableAfterServerEvent(ServerEvent):
    name = "EntityDieLoottableAfterServerEvent"

    dieEntityId = "" # type: str
    """ 死亡实体的entityId """
    attacker = "" # type: str
    """ 伤害来源的entityId """
    itemList = [] # type: list[dict]
    """ 掉落物品列表，每个元素为一个itemDict，格式可参考物品信息字典 """
    itemEntityIdList = [] # type: list[str]
    """ 掉落物品entityId列表 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> EntityDieLoottableAfterServerEvent
        instance = cls()
        instance.dieEntityId = data["dieEntityId"]
        instance.attacker = data["attacker"]
        instance.itemList = data["itemList"]
        instance.itemEntityIdList = data["itemEntityIdList"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "dieEntityId": self.dieEntityId,
            "attacker": self.attacker,
            "itemList": self.itemList,
            "itemEntityIdList": self.itemEntityIdList,
        }