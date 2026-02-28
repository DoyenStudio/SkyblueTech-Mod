from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent


class ChargerItemModelUpdate(CustomS2CEvent):
    name = "st:CIMU"

    def __init__(self, x=0, y=0, z=0, item_id=None, enchanted=False):
        # type: (int, int, int, str | None, bool) -> None
        self.x = x
        self.y = y
        self.z = z
        self.item_id = item_id
        self.enchanted = enchanted

    def marshal(self):
        return {"item_id": self.item_id, "enchanted": self.enchanted, "xyz": [self.x, self.y, self.z]}

    @classmethod
    def unmarshal(cls, data):
        instance = cls()
        instance.item_id = data["item_id"]
        instance.enchanted = data["enchanted"]
        instance.x, instance.y, instance.z = data["xyz"]
        return instance


class ChargeItemModelRequest(CustomC2SEvent):
    name = "st:CIMR"

    def __init__(self, x=0, y=0, z=0):
        # type: (int, int, int) -> None
        self.x = x
        self.y = y
        self.z = z
        self.pid = ""

    def marshal(self):
        return {"x":  self.x, "y": self.y, "z": self.z}

    @classmethod
    def unmarshal(cls, data):
        instance = cls()
        instance.x = data["x"]
        instance.y = data["y"]
        instance.z = data["z"]
        instance.pid = data["__id__"]
        return instance
