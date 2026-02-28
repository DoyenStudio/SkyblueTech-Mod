# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent


class HydroponicBedModelUpdateEvent(CustomS2CEvent):
    name = "st:HBUPD"

    def __init__(self, x, y, z, crop_id, aux):
        # type: (int, int, int, str | None, int) -> None
        self.x = x
        self.y = y
        self.z = z
        self.crop_id = crop_id
        self.aux = aux

    def marshal(self):
        return {"x": self.x, "y": self.y, "z": self.z, "c": self.crop_id, "a": self.aux}

    @classmethod
    def unmarshal(cls, data):
        return cls(
            x=data["x"], y=data["y"], z=data["z"], crop_id=data["c"], aux=data["a"]
        )


class HydroponicBedModelUpdatesEvent(CustomS2CEvent):
    name = "st:HBUPD"

    def __init__(self, updates=[]):
        # type: (list[tuple[int, int, int, str, int]]) -> None
        self.updates = updates

    def marshal(self):
        return self.updates

    @classmethod
    def unmarshal(
        cls,
        data,  # type: list[tuple[int, int, int, str, int]]
    ):
        return cls(data)
