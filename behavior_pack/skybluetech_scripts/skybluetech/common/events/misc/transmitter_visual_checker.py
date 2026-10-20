# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent
from skybluetech_scripts.tooldelta.utils.py_comp import py2_unicode


def _to_unicode(text):
    if isinstance(text, py2_unicode):
        return text
    return text.decode("utf-8")


class TransmitterVisualCheckerCheckRequest(CustomC2SEvent):
    name = "st:TmVCR"

    MODE_GET_BY_TRANSMITTER = 0
    MODE_GET_BY_MACHINE = 1
    MODE_AUTO = 2

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

    def __init__(
        self,
        nodes=None,  # type: list[tuple[int, int, int]] | None
        inputs=None,  # type: list[tuple[int, int, int]] | None
        outputs=None,  # type: list[tuple[int, int, int]] | None
        type_id="",  # type: str
        display_name="",  # type: str
        input_label="输入",  # type: str
        output_label="抽取",  # type: str
    ):
        # type: (...) -> None
        self.nodes = [tuple(pos) for pos in nodes] if nodes is not None else []
        self.inputs = [tuple(pos) for pos in inputs] if inputs is not None else []
        self.outputs = [tuple(pos) for pos in outputs] if outputs is not None else []
        self.type_id = type_id
        self.display_name = _to_unicode(display_name)
        self.input_label = _to_unicode(input_label)
        self.output_label = _to_unicode(output_label)

    def marshal(self):
        return {
            "nodes": self.nodes,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "type_id": self.type_id,
            "display_name": self.display_name,
            "input_label": self.input_label,
            "output_label": self.output_label,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            nodes=data["nodes"],
            inputs=data["inputs"],
            outputs=data["outputs"],
            type_id=data["type_id"],
            display_name=data["display_name"],
            input_label=data["input_label"],
            output_label=data["output_label"],
        )


class TransmitterVisualCheckerCheckMultiResponse(CustomS2CEvent):
    name = "st:TmVCMR"

    def __init__(
        self,
        reses=None,  # type: list[TransmitterVisualCheckerCheckResponse] | None
    ):
        # type: (...) -> None
        self.reses = list(reses) if reses is not None else []

    def marshal(self):
        return {
            "reses": [response.marshal() for response in self.reses]
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            reses=[
                TransmitterVisualCheckerCheckResponse.unmarshal(response)
                for response in data["reses"]
            ],
        )
