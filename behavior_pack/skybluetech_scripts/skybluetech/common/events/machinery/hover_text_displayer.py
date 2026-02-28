# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent, CustomS2CEvent


class HoverTextDisplayerContentUpload(CustomC2SEvent):
    name = "st:HTDCUl"

    def __init__(self, x, y, z, new_text, player_id=""):
        # type: (int, int, int, str, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.new_text = new_text
        self.player_id = player_id

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "new_text": self.new_text,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            new_text=data["new_text"],
            player_id=data["__id__"],
        )


class HoverTextDisplayerContentUpdate(CustomS2CEvent):
    name = "st:HTDCUd"

    def __init__(self, x, y, z, new_text, power_cost):
        # type: (int, int, int, str, int) -> None
        self.x = x
        self.y = y
        self.z = z
        self.new_text = new_text
        self.power_cost = power_cost

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "new_text": self.new_text,
            "power_cost": self.power_cost,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            new_text=data["new_text"],
            power_cost=data["power_cost"],
        )
