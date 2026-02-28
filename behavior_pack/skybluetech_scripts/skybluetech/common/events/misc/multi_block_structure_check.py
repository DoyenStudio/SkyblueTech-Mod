# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent, CustomS2CEvent


class MultiBlockStructureCheckRequest(CustomC2SEvent):
    def __init__(self, x, y, z, player_id=""):
        self.x = x
        self.y = y
        self.z = z
        self.player_id = player_id

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(data["x"], data["y"], data["z"], data["__id__"])


class MultiBlockStructureCheckResponse(CustomS2CEvent):
    def __init__(self, x, y, z, palette, pos_block_data):
        # type: (int, int, int, dict[int, str | list[str]], dict[int, list[tuple[int, int, int]]]) -> None
        self.x = x
        self.y = y
        self.z = z
        self.palette = palette
        self.pos_block_data = pos_block_data

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "palette": self.palette,
            "pos_block_data": self.pos_block_data,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["x"],
            data["y"],
            data["z"],
            data["palette"],
            data["pos_block_data"],
        )
