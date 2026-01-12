# coding=utf-8

from ...define.item import Item
from ..basic import ServerEvent


class PlayerAttackEntityEvent(ServerEvent):
    name = "PlayerAttackEntityEvent"

    playerId = '' # type: str
    """ 玩家id """
    victimId = '' # type: str
    """ 受击者id """
    damage = 0.0 # type: float
    """ 伤害值：引擎传过来的值是0 允许脚本层修改为其他数 """
    isValid = 0 # type: int
    """ 脚本是否设置伤害值：1表示是；0 表示否 """
    isKnockBack = False # type: bool
    """ 是否支持击退效果，默认支持，当不支持时将屏蔽武器击退附魔效果 """
    isCrit = False # type: bool
    """ 本次攻击是否产生暴击,不支持修改 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> PlayerAttackEntityEvent
        instance = cls()
        instance._orig = data
        instance.playerId = data["playerId"]
        instance.victimId = data["victimId"]
        instance.damage = data["damage"]
        instance.isValid = data["isValid"]
        instance.isKnockBack = data["isKnockBack"]
        instance.isCrit = data["isCrit"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "playerId": self.playerId,
            "victimId": self.victimId,
            "damage": self.damage,
            "isValid": self.isValid,
            "isKnockBack": self.isKnockBack,
            "isCrit": self.isCrit,
        }

    def cancel(self):
        # type: () -> None
        "取消该次攻击"
        self._orig["cancel"] = True


class ActuallyHurtServerEvent(ServerEvent):
    name = "ActuallyHurtServerEvent"

    srcId = "" # type: str
    """ 伤害源id """
    projectileId = "" # type: str
    """ 投射物id """
    entityId = "" # type: str
    """ 被伤害id """
    damage = 0.0 # type: float
    """ 伤害值（被伤害吸收后的值），允许修改，设置为0则此次造成的伤害为0，若设置数值和原来一样则视为没有修改 """
    invulnerableTime = 0 # type: int
    """ 实体受击后，剩余的无懈可击帧数，在无懈可击时间内，damage和damage_f为超过上次伤害的部分 """
    lastHurt = 0.0 # type: float
    """ 实体上次受到的伤害 """
    cause = "" # type: str
    """ 伤害来源，详见Minecraft枚举值文档的ActorDamageCause """
    customTag = "" # type: str
    """ 使用Hurt接口传入的自定义伤害类型 """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> ActuallyHurtServerEvent
        instance = cls()
        instance._orig = data
        instance.srcId = data["srcId"]
        instance.projectileId = data["projectileId"]
        instance.entityId = data["entityId"]
        instance.damage = data["damage"]
        instance.invulnerableTime = data["invulnerableTime"]
        instance.lastHurt = data["lastHurt"]
        instance.cause = data["cause"]
        instance.customTag = data["customTag"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "srcId": self.srcId,
            "projectileId": self.projectileId,
            "entityId": self.entityId,
            "damage": self.damage,
            "invulnerableTime": self.invulnerableTime,
            "lastHurt": self.lastHurt,
            "cause": self.cause,
            "customTag": self.customTag,
        }

    def modifyDamage(self, damage):
        # type: (float) -> None
        self._orig["damage"] = damage
        self.damage = damage


class PlayerHurtEvent(ServerEvent):
    name = "PlayerHurtEvent"

    id = "" # type: str
    """ 受击玩家id """
    attacker = "" # type: str
    """ 伤害来源实体id，若没有实体攻击，例如高空坠落，id为-1 """
    customTag = "" # type: str
    """ 使用Hurt接口传入的自定义伤害类型 """
    cause = "" # type: str
    """ 伤害来源，详见Minecraft枚举值文档的ActorDamageCause """

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> PlayerHurtEvent
        instance = cls()
        instance.id = data["id"]
        instance.attacker = data["attacker"]
        instance.customTag = data["customTag"]
        instance.cause = data["cause"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "id": self.id,
            "attacker": self.attacker,
            "customTag": self.customTag,
            "cause": self.cause,
        }

