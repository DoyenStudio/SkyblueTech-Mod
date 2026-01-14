# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent


class TransmitterVisualCheckerCheckRequest(CustomC2SEvent):
    name = "st:TmVCR"

    MODE_GET_BY_TRANSMITTER = 0
    MODE_GET_BY_MACHINE = 1

    def __init__(self, x=0, y=0, z=0, mode=0, player_id=""):
        # type: (int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.mode = mode
        self.player_id = player_id

    def marshal(self):
        return {"x": self.x, "y": self.y, "z": self.z, "mode": self.mode}

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            mode=data["mode"],
            player_id=data["__id__"],
        )


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

    @classmethod
    def unmarshal(cls, data):
        return cls(
            nodes=data["nodes"],
            inputs=data["inputs"],
            outputs=data["outputs"],
            type=data["type"],
        )


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

    @classmethod
    def unmarshal(cls, data):
        return cls(
            reses=data["reses"],
        )
