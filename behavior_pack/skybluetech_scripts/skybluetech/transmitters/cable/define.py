# coding=utf-8

from ...define.id_enum.blocks import Cable
from ..base import BaseNetwork, BaseAccessPoint

TRANSFER_SPEED_MAPPING = {
    Cable.STEEL: 1,
}  # pre 0.2s


class CableNetwork(BaseNetwork["CableAccessPoint"]):
    @classmethod
    def calc_transfer_speed(cls, block_name):
        # type: (str) -> int
        return TRANSFER_SPEED_MAPPING.get(block_name, 1)

    def __repr__(self):
        return "CableNetwork({}, {}, {})".format(
            self.dim, self.group_inputs, self.group_outputs
        )


class CableAccessPoint(BaseAccessPoint["CableNetwork"]):
    def __repr__(self):
        return "CableAP({}, {}, {}, {}, {})".format(
            self.dim, self.x, self.y, self.z, self.access_facing
        )
