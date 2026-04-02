# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import (
    ServerEntityTryPlaceBlockEvent,
    ServerBlockUseEvent,
    BlockNeighborChangedServerEvent,
)
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockAuxValueFromStates,
    GetBlockName,
    GetBlockStates,
    SetBlock,
    UpdateBlockStates,
    MayPlace,
    PlayerUseItemToPos,
)
from ....common.events.machinery.rf_repeater_plant import (
    RFRepeaterPlantSettingsUpdate,
)
from ....common.define.id_enum.machinery import RF_REPEATER_PLANT as MACHINE_ID
from ....common.define.facing import DXYZ_FACING, FACING_EN
from ....common.define.ui_keys import RF_REPEATER_PLANT_UI
from ....common.machinery_def.rf_repeater_plant import MODE_INPUT, MODE_OUTPUT
from ....common.ui_sync.machinery.rf_repeater_plant import RFRepeaterPlantUISync
from ....common.utils.block_sync import BlockSync
from ...transmitters.wire.logic import isWire
from ..basic import BaseMachine, GUIControl, ItemContainer, RegisterMachine
from ..pool import GetMachineStrict
from .node import (
    NetworkData,
    NodeData,
    get_node,
    get_network,
    sum_network_data,
    add_single_node,
    remove_node_and_flush,
)


K_GLOBAL_NETWORK_DATAS = "st:global_rf_repeater_network_datas"
K_GLOBAL_NODES = "st:global_rf_repeater_nodes"


block_sync = BlockSync(MACHINE_ID, side=BlockSync.SIDE_SERVER)


@RegisterMachine
class RFRepeaterPlant(BaseMachine, GUIControl, ItemContainer):
    bound_ui = RF_REPEATER_PLANT_UI
    block_name = MACHINE_ID
    store_rf_max = 120000
    energy_io_mode = (0, 0, 0, 0, 0, 0)

    def __init__(self, dim, x, y, z, block_entity_data):
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = RFRepeaterPlantUISync.NewServer(self).Activate()
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
        states = {}
        for dx, dy, dz in DXYZ_FACING.keys():
            facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
            bname = GetBlockName(self.dim, (self.x + dx, self.y + dy, self.z + dz))
            if not bname:
                continue
            connectToWire = isWire(bname)
            states["skybluetech:connection_" + facing_en] = connectToWire
        UpdateBlockStates(
            self.dim,
            (self.x, self.y, self.z),
            states,
        )
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
        dx = event.neighborPosX - self.x
        dy = event.neighborPosY - self.y
        dz = event.neighborPosZ - self.z
        facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
        if facing_en not in {"south", "north", "east", "west"}:
            return
        connectToWire = isWire(event.toBlockName)
        UpdateBlockStates(
            self.dim,
            (self.x, self.y, self.z),
            {"skybluetech:connection_" + facing_en: connectToWire},
        )

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
        else:
            my_node = get_node(self.dim, (self.x, self.y, self.z))
            self.nodes_in_network = {}
            if my_node is not None:
                network = get_network(my_node.bound_network_uuid)
                if network is not None:
                    self.nodes_in_network = network.nodes
                self.energy_io_mode = (
                    1,
                    1,
                    int(self.mode),
                    int(self.mode),
                    int(self.mode),
                    int(self.mode),
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


def requireWireModule():
    global GetContainerNode, pool
    if requireWireModule.has_cache:
        return
    from ...transmitters.wire.logic import logic_module
    from .. import pool

    GetContainerNode = logic_module.GetContainerNode
    requireWireModule.has_cache = True


requireWireModule.has_cache = False
