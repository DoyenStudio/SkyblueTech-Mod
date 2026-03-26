# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import GetBlockEntityData
from ....common.define.id_enum.blocks import Pipe
from ..base.define import BaseNetwork, BaseAccessPoint

INT32 = 1 << 32

# TRANSFER_SPEED_MAPPING = (None, 100, 400, 1600, 6400, 14000)
TRANSFER_SPEED_MAPPING = {
    Pipe.BRONZE: 100,
}
CAPACITY_MAPPING = {
    Pipe.BRONZE: 1000,
}


class PipeNetwork(BaseNetwork["PipeAccessPoint"]):
    def __init__(self, dim, group_inputs, group_outputs, nodes, transfer_speed=0):
        super(PipeNetwork, self).__init__(
            dim, group_inputs, group_outputs, nodes, transfer_speed
        )
        self.capacity = 1000
        self.load_network_data()

    @classmethod
    def calc_transfer_speed(cls, block_name):
        return TRANSFER_SPEED_MAPPING.get(block_name, 1) * 5

    @classmethod
    def calc_capacity(cls, block_name):
        return CAPACITY_MAPPING.get(block_name, 1)

    def get_data_store_node(self):
        return min(
            self.nodes, key=lambda pos: pos[0] * INT32 * INT32 + pos[1] * INT32 + pos[2]
        )

    def load_network_data(self):
        b = GetBlockEntityData(self.dim, self.get_data_store_node())
        if b is not None:
            self.fluid_id = b["fluid_id"]
            self.fluid_volume = b["fluid_volume"] or 0.0

    def save_network_data(self):
        b = GetBlockEntityData(self.dim, self.get_data_store_node())
        if b is not None:
            b["fluid_id"] = self.fluid_id
            b["fluid_volume"] = self.fluid_volume

    def __repr__(self):
        return "PipeNetwork({}, {}, {})".format(
            self.dim, self.group_inputs, self.group_outputs
        )


class PipeAccessPoint(BaseAccessPoint["PipeNetwork"]):
    def __repr__(self):
        return "PipeAP({}, {}, {}, {}, {})".format(
            self.dim, self.x, self.y, self.z, self.access_facing
        )
