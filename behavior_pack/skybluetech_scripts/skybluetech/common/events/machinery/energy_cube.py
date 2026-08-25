# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent

from .basic import MachineryOperationC2S


class EnergyCubeActionRequest(MachineryOperationC2S):
    name = "st:ECAR"
    extra_attrs = ("op", "value")

    OPERATION_INPUT = 0
    OPERATION_OUTPUT = 1

    def __init__(self, x, y, z, op, value, player_id=""):
        # type: (int, int, int, int, bool, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.op = op
        self.value = value
        self.player_id = player_id


class EnergyCubeStatesUpdate(CustomS2CEvent):
    name = "st:ECSU"

    def __init__(self, enable_input, enable_output):
        # type: (bool, bool) -> None
        self.enable_input = enable_input
        self.enable_output = enable_output

    def marshal(self):
        return {"ei": self.enable_input, "eo": self.enable_output}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["ei"], data["eo"])


class EnergyCubeSetIOModes(MachineryOperationC2S):
    name = "st:ECSIOM"
    extra_attrs = ("face", "mode")

    def __init__(self, x, y, z, face, mode, player_id=""):
        # type: (int, int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.face = face
        self.mode = mode
        self.player_id = player_id
