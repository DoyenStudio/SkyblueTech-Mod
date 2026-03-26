# coding=utf-8

from ....common.define.id_enum.blocks import Wire
from ..base.define import BaseNetwork, BaseAccessPoint


TRANSFER_SPEED_MAPPING = {
    Wire.CREATIVE: 2147483647,
    Wire.TIN: 384,
    Wire.COPPER: 512,
    Wire.SILVER: 4096,
    Wire.SUPER_CONDUCT: 1048576,
}


class WireNetwork(BaseNetwork["WireAccessPoint"]):
    def __init__(self, dim, group_inputs, group_outputs, nodes, transfer_speed=0):
        super(WireNetwork, self).__init__(
            dim, group_inputs, group_outputs, nodes, transfer_speed
        )

    @classmethod
    def calc_transfer_speed(cls, block_name):
        return TRANSFER_SPEED_MAPPING.get(block_name, 1) * 5

    def __repr__(self):
        return "WireNetwork({}, {}, {})".format(
            self.dim, self.group_inputs, self.group_outputs
        )


class WireAccessPoint(BaseAccessPoint["WireNetwork"]):
    def __repr__(self):
        return "WireAP({}, {}, {}, {}, {})".format(
            self.dim, self.x, self.y, self.z, self.access_facing
        )
