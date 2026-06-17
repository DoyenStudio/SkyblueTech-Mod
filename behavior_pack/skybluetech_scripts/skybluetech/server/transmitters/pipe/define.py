# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import GetBlockEntityData
from skybluetech_scripts.skybluetech.common.define.id_enum import Pipe, fluids
from skybluetech_scripts.skybluetech.common.misc.transmitter import TransmitterType
from ..base.define import BaseNetwork, BaseAccessPoint

INT32 = 1 << 32

# TRANSFER_SPEED_MAPPING = (None, 100, 400, 1600, 6400, 14000)
TRANSFER_SPEED_MAPPING = {
    Pipe.ACIDPROOF: 100,
    Pipe.BRONZE: 100,
    Pipe.CUPRONICKEL: 60,
    Pipe.ULTRAHEATINUM: 100,
}
CAPACITY_MAPPING = {
    Pipe.ACIDPROOF: 1000,
    Pipe.BRONZE: 1000,
    Pipe.CUPRONICKEL: 1000,
    Pipe.ULTRAHEATINUM: 1000,
}
PIPE_CAN_TRANSMIT_FLUID_MAPPING = {
    Pipe.ACIDPROOF: lambda f: (
        f in fluids.Common.all_sub() or f in fluids.Acid.all_sub()
    ),
    Pipe.BRONZE: lambda f: f in fluids.Common.all_sub(),
    Pipe.CUPRONICKEL: lambda f: (
        f in fluids.Common.all_sub() or f in fluids.HotFluid.all_sub()
    ),
    Pipe.ULTRAHEATINUM: lambda f: (
        f in fluids.Common.all_sub()
        or f in fluids.HotFluid.all_sub()
        or f in fluids.ExtremeHotFluid.all_sub()
    ),
}


class PipeNetwork(BaseNetwork["PipeAccessPoint"]):
    network_type = TransmitterType.PIPE

    def __init__(self, dim, group_inputs, group_outputs, nodes, transmitter_id):
        super(PipeNetwork, self).__init__(
            dim, group_inputs, group_outputs, nodes, transmitter_id
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
            if self.fluid_id is None or self.fluid_volume <= 0:
                self.fluid_id = None
                self.fluid_volume = 0.0

    def save_network_data(self):
        b = GetBlockEntityData(self.dim, self.get_data_store_node())
        if b is not None:
            if self.fluid_id is None or self.fluid_volume <= 0:
                self.fluid_id = None
                self.fluid_volume = 0.0
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
