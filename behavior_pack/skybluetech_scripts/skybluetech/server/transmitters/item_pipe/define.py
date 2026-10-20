# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum.blocks import ItemPipe
from skybluetech_scripts.skybluetech.common.misc.transmitter import TransmitterType
from ..base import BaseNetwork, BaseAccessPoint

TRANSFER_SPEED_MAPPING = {
    ItemPipe.STEEL: 1,
    ItemPipe.INVAR: 2,
}  # pre 0.2s


class ItemPipeNetwork(BaseNetwork["ItemPipeAccessPoint"]):
    network_type = TransmitterType.ITEM_PIPE

    def __init__(self, dim, group_inputs, group_outputs, nodes, transmitter_id):
        # type: (int, set[ItemPipeAccessPoint], set[ItemPipeAccessPoint], set[tuple[int, int, int]], str) -> None
        super(ItemPipeNetwork, self).__init__(
            dim, group_inputs, group_outputs, nodes, transmitter_id
        )
        # 跨 tick 容器缓存, 由 onNetworkTick 使用, 容器内容变化时经事件失效
        self._cache_datas = {}  # type: dict[tuple[int, int, int], dict | None]
        self._cache_block_names = {}  # type: dict[tuple[int, int, int], str]
        self._cache_slotposes = {}  # type: dict[tuple[int, int, int], tuple[tuple[int, ...], tuple[int, ...]]]
        self._cache_slotitems = {}  # type: dict[tuple[int, int, int], dict[int, Item | None]]
        # 输出端轮询游标, 用于公平分配容量
        self._output_cursor = 0
        # 接入点排序缓存, 接入点集合长度变化时自动重建
        self._sorted_inputs = None  # type: list[ItemPipeAccessPoint] | None
        self._sorted_outputs = None  # type: list[ItemPipeAccessPoint] | None

    @classmethod
    def calc_transfer_speed(cls, block_name):
        # type: (str) -> int
        return TRANSFER_SPEED_MAPPING.get(block_name, 1) * 5

    def get_input_access_points(self):
        # type: () -> list[ItemPipeAccessPoint]
        if (
            self._sorted_inputs is None
            or len(self._sorted_inputs) != len(self.group_inputs)
        ):
            self._sorted_inputs = sorted(
                self.group_inputs,
                key=lambda ap: ap.get_priority(),
                reverse=True,
            )
        return self._sorted_inputs

    def get_output_access_points(self):
        # type: () -> list[ItemPipeAccessPoint]
        if (
            self._sorted_outputs is None
            or len(self._sorted_outputs) != len(self.group_outputs)
        ):
            self._sorted_outputs = sorted(
                self.group_outputs,
                key=lambda ap: ap.get_priority(),
                reverse=True,
            )
        return self._sorted_outputs

    def __repr__(self):
        return "ItemPipeNetwork({}, {}, {})".format(
            self.dim, self.group_inputs, self.group_outputs
        )


class ItemPipeAccessPoint(BaseAccessPoint["ItemPipeNetwork"]):
    def __repr__(self):
        return "ItemPipeAP({}, {}, {}, {}, {})".format(
            self.dim, self.x, self.y, self.z, self.access_facing
        )
