# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent


class TransmitterVisualCheckerCheckRequest(CustomC2SEvent):
    name = "st:TmVCR"

    MODE_GET_BY_TRANSMITTER = 0
    MODE_GET_BY_MACHINE = 1

    def __init__(self, x=0, y=0, z=0, mode=0):
        # type: (int, int, int, int) -> None
        self.x = x
        self.y = y
        self.z = z
        self.mode = mode

    def marshal(self):
        return {"x": self.x, "y": self.y, "z": self.z, "mode": self.mode}

    def unmarshal(self, data):
        self.player_id = data["__id__"]
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.mode = data["mode"]


class TransmitterVisualCheckerCheckResponse(CustomS2CEvent):
    name = "st:TmVCR"

    TYPE_WIRE = 0
    TYPE_CABLE = 1
    TYPE_PIPE = 2

    def __init__(
        self,
        nodes=[], # type: list[tuple[int, int, int]]
        inputs=[], # type: list[tuple[int, int, int]]
        outputs=[], # type: list[tuple[int, int, int]]
        type=0
    ):
        # type: (...) -> None
        self.nodes = nodes
        self.inputs = inputs
        self.outputs = outputs
        self.type = type

    def marshal(self):
        return {
            "nodes": self.nodes,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "type": self.type
        }

    def unmarshal(self, data):
        self.nodes = data["nodes"]
        self.inputs = data["inputs"]
        self.outputs = data["outputs"]
        self.type = data["type"]


class TransmitterVisualCheckerCheckMultiResponse(CustomS2CEvent):
    name = "st:TmVCMR"

    TYPE_CABLE = 0
    TYPE_PIPE = 1
    TYPE_WIRE = 2

    def __init__(
        self,
        reses=[] # type: list[tuple[list[tuple[int, int, int]], list[tuple[int, int, int]], list[tuple[int, int, int]], int]]
    ):
        # type: (...) -> None
        self.reses = reses

    def marshal(self):
        return {
            "reses": self.reses
        }

    def unmarshal(self, data):
        self.reses = data["reses"]
