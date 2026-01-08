# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent


class TransmitterVisualCheckerCheckRequest(CustomC2SEvent):
    name = "st:TmVCR"

    def __init__(self, x=0, y=0, z=0):
        # type: (int, int, int) -> None
        self.x = x
        self.y = y
        self.z = z

    def marshal(self):
        return {"x": self.x, "y": self.y, "z": self.z}

    def unmarshal(self, data):
        self.player_id = data["__id__"]
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]


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
        suc=False,
        type=0
    ):
        # type: (...) -> None
        self.nodes = nodes
        self.inputs = inputs
        self.outputs = outputs
        self.suc = suc
        self.type = type

    def marshal(self):
        return {
            "nodes": self.nodes,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "suc": self.suc,
            "type": self.type
        }

    def unmarshal(self, data):
        self.nodes = data["nodes"]
        self.inputs = data["inputs"]
        self.outputs = data["outputs"]
        self.suc = data["suc"]
        self.type = data["type"]
