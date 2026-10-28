# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent
from .basic import MachineryOperationC2S


class TeslaPlantSettingsUpload(MachineryOperationC2S):
    name = "st:TPSU"
    extra_attrs = (
        "work_range",
        "do_attack_monster",
        "do_attack_mob",
        "do_attack_player",
    )

    def __init__(
        self,
        dim,  # type: int
        x,  # type: int
        y,  # type: int
        z,  # type: int
        work_range,  # type: int
        do_attack_monster,  # type: bool
        do_attack_mob,  # type: bool
        do_attack_player,  # type: bool
        player_id="",
    ):
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.work_range = work_range
        self.do_attack_monster = do_attack_monster
        self.do_attack_mob = do_attack_mob
        self.do_attack_player = do_attack_player
        self.player_id = player_id

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "work_range": self.work_range,
            "do_attack_monster": self.do_attack_monster,
            "do_attack_mob": self.do_attack_mob,
            "do_attack_player": self.do_attack_player,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["dim"],
            data["x"],
            data["y"],
            data["z"],
            data["work_range"],
            data["do_attack_monster"],
            data["do_attack_mob"],
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
        work_range,  # type: int
        do_attack_monster,  # type: bool
        do_attack_mob,  # type: bool
        do_attack_player,  # type: bool
    ):
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.work_range = work_range
        self.do_attack_monster = do_attack_monster
        self.do_attack_mob = do_attack_mob
        self.do_attack_player = do_attack_player

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "work_range": self.work_range,
            "do_attack_monster": self.do_attack_monster,
            "do_attack_mob": self.do_attack_mob,
            "do_attack_player": self.do_attack_player,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["dim"],
            data["x"],
            data["y"],
            data["z"],
            data["work_range"],
            data["do_attack_monster"],
            data["do_attack_mob"],
            data["do_attack_player"],
        )


class TeslaPlantAttack(CustomS2CEvent):
    name = "st:TsPA"

    def __init__(self, dim, x, y, z, to_entity_ids, target_positions=None):
        # type: (int, int, int, int, list[str], list[list[float]] | None) -> None
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.entity_ids = to_entity_ids
        # Capture successful hit positions on the server, including lethal hits
        # whose actors may already have disappeared when clients receive this.
        self.target_positions = target_positions or []

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "eids": self.entity_ids,
            "positions": self.target_positions,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["dim"], data["x"], data["y"], data["z"], data["eids"],
            data.get("positions", []),
        )
