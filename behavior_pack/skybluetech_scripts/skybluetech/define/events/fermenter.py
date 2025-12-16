from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent


class FermenterSetTemperatureEvent(CustomC2SEvent):
    name = "st:FST"

    def __init__(self, x=0, y=0, z=0, temperature=0):
        # type: (int, int, int, float) -> None
        self.x = x
        self.y = y
        self.z = z
        self.temperature = temperature

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "t": self.temperature
        }

    def unmarshal(self, data):
        # type: (dict) -> None
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.temperature = data["t"]
        self.player_id = data["__id__"]


class FermenterSeMaxVolumeEvent(CustomC2SEvent):
    name = "st:FSMV"

    def __init__(self, x=0, y=0, z=0, volume=0):
        # type: (int, int, int, float) -> None
        self.x = x
        self.y = y
        self.z = z
        self.volume = volume

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "v": self.volume
        }

    def unmarshal(self, data):
        # type: (dict) -> None
        self.x = data["x"]
        self.y = data["y"]
        self.z = data["z"]
        self.volume = data["v"]
        self.player_id = data["__id__"]
