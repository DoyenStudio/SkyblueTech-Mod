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
from ....common.ui_sync.machinery.rf_repeater_plant import RFRepeaterPlantUISync
from ...transmitters.wire.logic import isWire
from ....common.machinery.utils.block_sync import BlockSync
from ..basic import BaseMachine, GUIControl, ItemContainer, RegisterMachine
from ..pool import GetMachineStrict
from .node import (
    NetworkData,
    NodeData,
    get_node,
    get_network,
    unpack_modes,
    sum_network_data,
    add_single_node,
    remove_node_and_flush,
)


K_GLOBAL_NETWORK_DATAS = "st:global_rf_repeater_network_datas"
K_GLOBAL_NODES = "st:global_rf_repeater_nodes"


block_sync = BlockSync(MACHINE_ID)


@RegisterMachine
class RFRepeaterPlant(BaseMachine, GUIControl, ItemContainer):
    bound_ui = RF_REPEATER_PLANT_UI
    block_name = MACHINE_ID
    store_rf_max = 100000
    energy_io_mode = (1, 1, 0, 0, 0, 0)

    def __init__(self, dim, x, y, z, block_entity_data):
        BaseMachine.__init__(self, dim, x, y, z, block_entity_data)
        ItemContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = RFRepeaterPlantUISync.NewServer(self).Activate()
        states = GetBlockStates(self.dim, (self.x, self.y, self.z))
        if states is None:
            raise ValueError("RFRepeaterPlant BlockState None")
        self.facing = states["minecraft:cardinal_direction"]  # type: str
        self.layer = states["skybluetech:layer"]  # type: int
        self.is_base_block = self.layer == 0
        self.flush_data()

    @classmethod
    def OnPrePlaced(cls, event):
        # type: (ServerEntityTryPlaceBlockEvent) -> None
        block_id = event.fullName
        dim = event.dimensionId
        x = event.x
        y = event.y
        z = event.z
        facing = event.face
        if not MayPlace(block_id, (x, y + 1, z), facing, dim) or not MayPlace(
            block_id, (x, y + 2, z), facing, dim
        ):
            event.cancel()

    def OnClick(self, event):
        # type: (ServerBlockUseEvent) -> None
        if not self.is_base_block:
            event.cancel()
            PlayerUseItemToPos(event.playerId, (self.x, self.y - self.layer, self.z), 2)
            return
        node = get_node(self.dim, (self.x, self.y, self.z))
        if node is None:
            mode = 0b1111
            euid = "??????"
        else:
            mode = node.modes
            euid = node.bound_network_uuid[-6:]
        east_io_mode, west_io_mode, south_io_mode, north_io_mode = unpack_modes(mode)
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
                    east_io_mode,
                    west_io_mode,
                    south_io_mode,
                    north_io_mode,
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
                SetBlock(self.dim, (self.x, base_y + i, self.z), "minecraft:air")

    def OnUnload(self):
        BaseMachine.OnUnload(self)
        GUIControl.OnUnload(self)
        block_sync.discard_block((self.dim, self.x, self.y, self.z))

    def AddPower(self, rf, max_limit=None, passed=None):
        # type: (int, int | None, set[BaseMachine] | None) -> tuple[bool, int]
        ok = False
        if passed is not None:
            passed.add(self)
        for node_pos in self.nodes_in_network:
            plant = GetMachineStrict(self.dim, *node_pos)
            if not isinstance(plant, RFRepeaterPlant):
                continue
            if passed is not None and plant in passed:
                continue
            _ok, rf = plant.transfer_power_to(rf, max_limit, passed)
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

    def transfer_power_to(self, rf, max_limit=None, passed=None):
        # type: (int, int | None, set[BaseMachine] | None) -> tuple[bool, int]
        requireWireModule()
        ok = False
        east, west, south, north = unpack_modes(self.modes)
        valid_output_faces = []  # type: list[int]
        if passed is not None:
            passed.add(self)
        if east:
            valid_output_faces.append(5)
        if west:
            valid_output_faces.append(4)
        if south:
            valid_output_faces.append(3)
        if north:
            valid_output_faces.append(2)
        cnode = GetContainerNode(self.dim, self.x, self.y, self.z, enable_cache=True)
        valid_output_networks = [
            v for k, v in cnode.inputs.items() if k in valid_output_faces
        ]
        for network in valid_output_networks:
            if network is None:
                continue
            for ap in network.get_input_access_points():
                machine = pool.GetMachineStrict(self.dim, *ap.target_pos)
                if machine is not None and not machine.is_non_energy_machine:
                    if passed is not None and machine in passed:
                        continue
                    updated, rf = machine.AddPower(rf, network.transfer_speed, passed)
                    ok = ok or updated
                    if rf == 0:
                        break
        return ok, rf

    @property
    def modes(self):
        # type: () -> int
        return self.bdata[NodeData.K_MODES] or 0b0000

    @modes.setter
    def modes(self, value):
        # type: (int) -> None
        print("SetMode", value)
        self.bdata[NodeData.K_MODES] = value


def requireWireModule():
    global GetContainerNode, pool
    if requireWireModule.has_cache:
        return
    from ...transmitters.wire.logic import logic_module
    from .. import pool

    GetContainerNode = logic_module.GetContainerNode
    requireWireModule.has_cache = True


requireWireModule.has_cache = False
