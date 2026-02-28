# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent


class TeslaPlantSettingsUpload(CustomC2SEvent):
    name = "st:TPSU"

    def __init__(
        self,
        dim,
        x,
        y,
        z,
        working_range,
        do_enable,
        do_attack_monster,
        do_attack_player,
        player_id="",
    ):
        # type: (int, int, int, int, int, bool, bool, bool, str) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.working_range = working_range
        self.do_enable = do_enable
        self.do_attack_monster = do_attack_monster
        self.do_attack_player = do_attack_player
        self.player_id = player_id

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "working_range": self.working_range,
            "do_enable": self.do_enable,
            "do_attack_monster": self.do_attack_monster,
            "do_attack_player": self.do_attack_player,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["dim"],
            data["x"],
            data["y"],
            data["z"],
            data["working_range"],
            data["do_enable"],
            data["do_attack_monster"],
            data["do_attack_player"],
            data["__id__"],
        )


class TeslaPlantSettingsUpdate(CustomS2CEvent):
    name = "st:TPSU"

    def __init__(
        self,
        dim,
        x,
        y,
        z,
        working_range,
        do_enable,
        do_attack_monster,
        do_attack_player,
    ):
        # type: (int, int, int, int, int, bool, bool, bool) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.working_range = working_range
        self.do_enable = do_enable
        self.do_attack_monster = do_attack_monster
        self.do_attack_player = do_attack_player

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "working_range": self.working_range,
            "do_enable": self.do_enable,
            "do_attack_monster": self.do_attack_monster,
            "do_attack_player": self.do_attack_player,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["dim"],
            data["x"],
            data["y"],
            data["z"],
            data["working_range"],
            data["do_enable"],
            data["do_attack_monster"],
            data["do_attack_player"],
        )


class TeslaPlantAttack(CustomS2CEvent):
    name = "st:TsPA"

    def __init__(self, dim, x, y, z, to_entity_id):
        # type: (int, int, int, int, str) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.entity_id = to_entity_id

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "eid": self.entity_id,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(data["dim"], data["x"], data["y"], data["z"], data["eid"])
