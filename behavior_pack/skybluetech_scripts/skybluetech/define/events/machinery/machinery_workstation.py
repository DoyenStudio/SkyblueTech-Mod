# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent, CustomS2CEvent


class MachineryWorkstationDoCraft(CustomC2SEvent):
    name = "st:MWDC"

    def __init__(self, x, y, z, craft_strength, player_id=""):
        # type: (int, int, int, float, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.craft_strength = craft_strength
        self.player_id = player_id

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "craft_strength": self.craft_strength,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["x"],
            data["y"],
            data["z"],
            data["craft_strength"],
            data["__id__"],
        )
