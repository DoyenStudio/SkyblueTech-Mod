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


class MachineryWorkstationTransferRecipe(CustomC2SEvent):
    name = "st:MWTR"

    def __init__(self, x, y, z, output_item_id, player_id=""):
        # type: (int, int, int, str, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.output_item_id = output_item_id
        self.player_id = player_id

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "output_item_id": self.output_item_id,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["x"],
            data["y"],
            data["z"],
            data["output_item_id"],
            data["__id__"],
        )
