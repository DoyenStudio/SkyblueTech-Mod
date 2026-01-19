# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent


class ElectricCrafterUpdateRecipe(CustomS2CEvent):
    name = "st:ECUR"

    def __init__(self, slotitems):
        # type: (list[tuple[str, int] | None]) -> None
        self.slotitems = slotitems

    def marshal(self):
        return {
            "s": self.slotitems
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(data["s"])
