# coding=utf-8
from skybluetech_scripts.tooldelta.general import ClientInitCallback
from skybluetech_scripts.tooldelta.api.client import (
    RegisterQueryMolang,
    SetQueryMolang,
)

registered_molangs = {}  # type: dict[str, float]


@ClientInitCallback()
def onClientInit():
    # type: () -> None
    for molang_name, default_value in registered_molangs.items():
        RegisterQueryMolang(molang_name, default_value)


class ClientMolang:
    def __init__(self, name, default_value=0.0):
        # type: (str, float) -> None
        self.name = name
        registered_molangs[name] = default_value

    def set_to_entity(self, entity_id, value):
        # type: (str, float) -> bool
        return SetQueryMolang(entity_id, self.name, value)


Y_SCALE = ClientMolang("query.mod.skybluetech_y_scale")
FACE = ClientMolang("query.mod.skybluetech_face")
ANIM_SPEED = ClientMolang("query.mod.skybluetech_anim_speed")
IS_BASE_BLOCK = ClientMolang("query.mod.skybluetech_is_base_block")
WIRE_CONNECT_EAST = ClientMolang("query.mod.skybluetech_wire_connect_east")
WIRE_CONNECT_WEST = ClientMolang("query.mod.skybluetech_wire_connect_west")
WIRE_CONNECT_NORTH = ClientMolang("query.mod.skybluetech_wire_connect_north")
WIRE_CONNECT_SOUTH = ClientMolang("query.mod.skybluetech_wire_connect_south")
