from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent


class FermenterSetTemperatureEvent(CustomC2SEvent):
    name = "st:FST"

    def __init__(self, x, y, z, temperature, player_id=""):
        # type: (int, int, int, float, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.temperature = temperature
        self.player_id = player_id

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "t": self.temperature
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            temperature=data["t"],
            player_id=data["__id__"]
        )


class FermenterSeMaxVolumeEvent(CustomC2SEvent):
    name = "st:FSMV"

    def __init__(self, x, y, z, volume, player_id=""):
        # type: (int, int, int, float, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.volume = volume
        self.player_id = player_id

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "v": self.volume
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            volume=data["v"],
            player_id=data["__id__"]
        )
