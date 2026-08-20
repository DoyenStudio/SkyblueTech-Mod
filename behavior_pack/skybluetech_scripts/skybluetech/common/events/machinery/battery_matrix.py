# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent

from .basic import MachineryOperationC2S


class BatteryMatrixActionRequest(MachineryOperationC2S):
    name = "st:BMAR"
    extra_attrs = ("op", "value")

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


class BatteryMatrixPopBatteryRequest(MachineryOperationC2S):
    name = "st:BMPBR"
    extra_attrs = ("index",)

    def __init__(self, x, y, z, index, player_id=""):
        # type: (int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.index = index
        self.player_id = player_id


class BatteryMatrixStoreBatteryRequest(MachineryOperationC2S):
    name = "st:BMBSBR"

    def __init__(self, x, y, z, player_id=""):
        # type: (int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.player_id = player_id


class BatteryMatrixCheckCoreBatterysRequest(MachineryOperationC2S):
    name = "st:BMCCBR"

    def __init__(self, x, y, z, player_id=""):
        # type: (int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.player_id = player_id


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
