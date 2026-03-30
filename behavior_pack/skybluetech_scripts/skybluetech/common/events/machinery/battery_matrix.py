# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent


class BatteryMatrixActionRequest(CustomC2SEvent):
    name = "st:BMAR"
    OPERATION_INPUT = 0
    OPERATION_OUTPUT = 1

    def __init__(self, x, y, z, op, value, player_id=""):
        # type: (int, int, int, int, int | bool, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.op = op
        self.value = value
        self.player_id = player_id

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "op": self.op,
            "value": self.value,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["x"], data["y"], data["z"], data["op"], data["value"], data["__id__"]
        )


class BatteryMatrixPopBatteryRequest(CustomC2SEvent):
    name = "st:BMPBR"

    def __init__(self, x, y, z, index, player_id=""):
        # type: (int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.index = index
        self.player_id = player_id

    def marshal(self):
        return {"x": self.x, "y": self.y, "z": self.z, "index": self.index}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["x"], data["y"], data["z"], data["index"], data["__id__"])


class BatteryMatrixStoreBatteryRequest(CustomC2SEvent):
    name = "st:BMBSBR"

    def __init__(self, x, y, z, player_id=""):
        # type: (int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.player_id = player_id

    def marshal(self):
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["x"], data["y"], data["z"], data["__id__"])


class BatteryMatrixCheckCoreBatterysRequest(CustomC2SEvent):
    name = "st:BMCCBR"

    def __init__(self, x, y, z, player_id=""):
        # type: (int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.player_id = player_id

    def marshal(self):
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["x"], data["y"], data["z"], data["__id__"])


class BatteryMatrixCoreStatusUpdate(CustomS2CEvent):
    name = "st:BMCSU"

    def __init__(self, battery_datas, first=False):
        # type: (list[tuple[str, int, int]], bool) -> None
        self.battery_datas = battery_datas
        self.first = first

    def marshal(self):
        return {"d": self.battery_datas, "f": self.first}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["d"], data["f"])


class BatteryMatrixStatesUpdate(CustomS2CEvent):
    name = "st:BMSU"

    def __init__(self, enable_input, enable_output):
        # type: (bool, bool) -> None
        self.enable_input = enable_input
        self.enable_output = enable_output

    def marshal(self):
        return {"ei": self.enable_input, "eo": self.enable_output}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["ei"], data["eo"])
