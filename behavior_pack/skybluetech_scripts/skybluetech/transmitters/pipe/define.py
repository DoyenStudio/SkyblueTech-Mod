# coding=utf-8

from ...define.id_enum.blocks import Pipe
from ..base.define import BaseNetwork, BaseAccessPoint


# TRANSFER_SPEED_MAPPING = (None, 100, 400, 1600, 6400, 14000)
TRANSFER_SPEED_MAPPING = {
    Pipe.BRONZE: 100,
}


class PipeNetwork(BaseNetwork["PipeAccessPoint"]):
    @classmethod
    def calc_transfer_speed(cls, block_name):
        return TRANSFER_SPEED_MAPPING.get(block_name, 1)

    def __repr__(self):
        return "PipeNetwork({}, {}, {})".format(
            self.dim, self.group_inputs, self.group_outputs
        )


class PipeAccessPoint(BaseAccessPoint["PipeNetwork"]):
    def __repr__(self):
        return "PipeAP({}, {}, {}, {}, {})".format(
            self.dim, self.x, self.y, self.z, self.access_facing
        )
