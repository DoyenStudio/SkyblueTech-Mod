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

    @classmethod
    def unmarshal(cls, data):
        instance = cls()
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.temperature = data["t"]
        instance.player_id = data["__id__"]
        return instance

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

    @classmethod
    def unmarshal(cls, data):
        instance = cls()
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.volume = data["v"]
        instance.player_id = data["__id__"]
        return instance
