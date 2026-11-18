# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent

from .basic import MachineryOperationC2S


class FluidOutputFacesGet(MachineryOperationC2S):
    name = "st:FOFG"


class FluidOutputFacesSet(MachineryOperationC2S):
    name = "st:FOFS"
    extra_attrs = ("slot", "mask", "revision")

    def __init__(self, x, y, z, slot, mask, revision, player_id=""):
        MachineryOperationC2S.__init__(self, x, y, z, player_id)
        self.slot = slot
        self.mask = mask
        self.revision = revision


class FluidOutputFacesUpdate(CustomS2CEvent):
    name = "st:FOFU"

    def __init__(self, pos, masks, revision, status=""):
        self.pos = tuple(pos)
        self.masks = masks
        self.revision = revision
        self.status = status

    def marshal(self):
        return {
            "pos": list(self.pos),
            "masks": [[slot, mask] for slot, mask in self.masks],
            "revision": self.revision,
            "status": self.status,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(data["pos"], data["masks"], data["revision"], data["status"])
