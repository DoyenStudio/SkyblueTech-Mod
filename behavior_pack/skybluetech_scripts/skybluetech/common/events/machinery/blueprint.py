# coding=utf-8
from .basic import MachineryOperationC2S
from skybluetech_scripts.tooldelta.events import CustomS2CEvent


class BlueprintAction(MachineryOperationC2S):
    name = "st:BlueprintAction"
    extra_attrs = ("action", "value")

    def __init__(self, x, y, z, action, value=None, player_id=""):
        super(BlueprintAction, self).__init__(x, y, z, player_id)
        self.action = action
        self.value = value


class BlueprintUpdate(CustomS2CEvent):
    name = "st:BlueprintUpdate"

    def __init__(self, location, action, value):
        self.location = tuple(location)
        self.action = action
        self.value = value

    def marshal(self):
        return {"location": self.location, "action": self.action, "value": self.value}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["location"], data["action"], data["value"])
