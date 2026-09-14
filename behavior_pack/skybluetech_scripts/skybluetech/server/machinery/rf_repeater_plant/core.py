# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.common.define.ui_keys import RF_REPEATER_PLANT_UI
from skybluetech_scripts.skybluetech.common.events.machinery.rf_repeater_plant import (
    RFRepeaterPlantSettingsUpdate,
)
from skybluetech_scripts.skybluetech.common.machinery_def.rf_repeater_plant import (
    MODE_INPUT,
    MODE_OUTPUT,
)
from skybluetech_scripts.skybluetech.common.utils.block_sync import BlockSync
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockAuxValueFromStates,
    GetBlockName,
    GetBlockStates,
    MayPlace,
    PlayerUseItemToPos,
    SetBlock,
)
from skybluetech_scripts.tooldelta.events.server import (
    BlockNeighborChangedServerEvent,
    ServerBlockUseEvent,
    ServerEntityTryPlaceBlockEvent,
)
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from ..basic import BaseClicker, BaseMachine, GUIControl, RegisterMachine
from ..pool import GetMachineStrict
from ..utils.transmitter_conn import TransmitterConn
from .node import (
    NetworkData,
    NodeData,
    add_single_node,
    get_network,
    get_node,
    remove_node_and_flush,
    sum_network_data,
)

K_GLOBAL_NETWORK_DATAS = "st:global_rf_repeater_network_datas"
K_GLOBAL_NODES = "st:global_rf_repeater_nodes"

TCON = TransmitterConn(wire=True)

block_sync = BlockSync(Machinery.RF_REPEATER_PLANT, side=BlockSync.SIDE_SERVER)


@RegisterMachine
class RFRepeaterPlant(BaseMachine, BaseClicker, GUIControl):
    bound_ui = RF_REPEATER_PLANT_UI
    block_name = Machinery.RF_REPEATER_PLANT
    store_rf_max = 120000
    energy_io_mode = (0, 0, 0, 0, 0, 0)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        states = GetBlockStates(self.dim, (self.x, self.y, self.z))
        if states is None:
            raise ValueError("RFRepeaterPlant BlockState None")
        self.layer = states["skybluetech:layer"]  # type: int
        self.is_base_block = self.layer == 0
        if not self.is_base_block:
            self.energy_io_mode = (2, 2, 2, 2, 2, 2)
        self.flush_data()

    @classmethod
    def OnPrePlaced(cls, event):
        # type: (ServerEntityTryPlaceBlockEvent) -> None
        block_id = event.fullName
        dim = event.dimensionId
        x = event.x
        y = event.y
        z = event.z
        if not MayPlace(block_id, (x, y + 1, z), 0, dim) or not MayPlace(
            block_id, (x, y + 2, z), 0, dim
        ):
            event.cancel()

    def OnClick(self, event, extra_datas=None):
        # type: (ServerBlockUseEvent, dict | None) -> None
        if not self.is_base_block:
            event.cancel()
            PlayerUseItemToPos(event.playerId, (self.x, self.y - self.layer, self.z), 2)
            return
        node = get_node(self.dim, (self.x, self.y, self.z))
        if node is None:
            io_mode = MODE_INPUT
            euid = "??????"
        else:
            io_mode = node.mode
            euid = node.bound_network_uuid[-6:]
        network_prof_data = sum_network_data(
            node.bound_network_uuid if node is not None else None
        )
        GUIControl.OnClick(
            self,
            event,
            {
                "st:init_content": RFRepeaterPlantSettingsUpdate(
                    self.dim,
                    self.x,
                    self.y,
                    self.z,
                    euid,
                    io_mode,
                    network_prof_data.network_plant_count,
                    network_prof_data.network_plant_online_count,
                    network_prof_data.total_output_count,
                    network_prof_data.total_output_active_count,
                    network_prof_data.total_input_count,
                    network_prof_data.total_input_active_count,
                ).marshal()
            },
        )

    def OnPlaced(self, event):
        if not self.is_base_block:
            return
        TCON.block_placed(self)
        for i in range(1, 3):
            SetBlock(
                self.dim,
                (self.x, self.y + i, self.z),
                self.block_name,
                GetBlockAuxValueFromStates(self.block_name, {"skybluetech:layer": i}),
            )
        add_single_node(self.dim, (self.x, self.y, self.z))

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        if not self.is_base_block:
            return
        TCON.neighbor_block_changed(self, event)

    def OnDestroy(self):
        remove_node_and_flush(self.dim, (self.x, self.y, self.z))
        base_y = self.y - self.layer
        for i in range(3):
            if i != self.layer:
                pos = (self.x, base_y + i, self.z)
                if GetBlockName(self.dim, pos) == self.block_name:
                    SetBlock(self.dim, (self.x, base_y + i, self.z), "minecraft:air")

    def OnUnload(self):
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)
        block_sync.discard_block((self.dim, self.x, self.y, self.z))

    def AddPower(self, rf):
        # type: (int) -> tuple[bool, int]
        ok = False
        for node_pos, io_mode in self.nodes_in_network.items():
            plant = GetMachineStrict(self.dim, *node_pos)
            if not isinstance(plant, RFRepeaterPlant):
                continue
            if io_mode == MODE_OUTPUT:
                _ok, rf = plant.recv_energy(rf)
                ok = ok or _ok
                if rf == 0:
                    return ok, 0
        return ok, rf

    def get_nearconn_plants(self):
        # type: () -> list[tuple[int, int, int]] | None
        node = get_node(self.dim, (self.x, self.y, self.z))
        if node is None:
            return None
        return node.connected_nodes

    def flush_data(self, from_network=None):
        # type: (NetworkData | None) -> None
        if from_network is not None:
            self.nodes_in_network = from_network.nodes
            mode = from_network.nodes.get((self.x, self.y, self.z), self.mode)
            self.sync_energy_io_mode(mode)
        else:
            my_node = get_node(self.dim, (self.x, self.y, self.z))
            self.nodes_in_network = {}
            if my_node is not None:
                network = get_network(my_node.bound_network_uuid)
                if network is not None:
                    self.nodes_in_network = network.nodes
                    mode = network.nodes.get((self.x, self.y, self.z), self.mode)
                    self.sync_energy_io_mode(mode)

    def sync_energy_io_mode(self, mode=None):
        # type: (int | None) -> None
        if not self.is_base_block:
            self.energy_io_mode = (2, 2, 2, 2, 2, 2)
            return
        if mode is None:
            mode = self.mode
        self.mode = int(mode)
        self.energy_io_mode = (
            1,
            1,
            int(mode),
            int(mode),
            int(mode),
            int(mode),
        )

    def recv_energy(self, rf):
        # type: (int) -> tuple[bool, int]
        return BaseMachine.AddPower(self, rf)

    def update_network_plants(self, inputs, outputs):
        # type: (list[tuple[int, int, int]], list[tuple[int, int, int]]) -> None
        # 不要把 list 换成 tuple 之类的
        # 因为传入的两个 list 需要保持引用
        self.input_plant_poses = inputs
        self.output_plant_poses = outputs

    @property
    def mode(self):
        # type: () -> int
        return self.bdata[NodeData.K_MODE] or MODE_INPUT

    @mode.setter
    def mode(self, value):
        # type: (int) -> None
        self.bdata[NodeData.K_MODE] = value
