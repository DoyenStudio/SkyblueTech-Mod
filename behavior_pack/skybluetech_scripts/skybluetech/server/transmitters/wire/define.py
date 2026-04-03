# coding=utf-8
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.api.server import Hurt, GetEntityTypeFamily
from ....common.define.id_enum.blocks import Wire
from ..base.define import BaseNetwork, BaseAccessPoint

ShockHurt = GetMinecraftEnum().ActorDamageCause.Lightning

TRANSFER_SPEED_MAPPING = {
    Wire.CREATIVE: 2147483647,
    Wire.CREATIVE_INSULATED: 2147483647,
    Wire.TIN: 384,
    Wire.TIN_INSULATED: 384,
    Wire.COPPER: 512,
    Wire.COPPER_INSULATED: 512,
    Wire.SILVER: 4096,
    Wire.SILVER_INSULATED: 4096,
    Wire.SUPER_CONDUCT: 1048576,
    Wire.SUPER_CONDUCT_INSULATED: 1048576,
}

WIRE_CAN_SHOCK = {
    Wire.CREATIVE,
    Wire.TIN,
    Wire.COPPER,
    Wire.SILVER,
    Wire.SUPER_CONDUCT,
}


def rf_to_damage(rf):
    # type: (int) -> float
    return rf / 36.0


class WireNetwork(BaseNetwork["WireAccessPoint"]):
    def __init__(self, dim, group_inputs, group_outputs, nodes, transfer_speed=0):
        super(WireNetwork, self).__init__(
            dim, group_inputs, group_outputs, nodes, transfer_speed
        )
        self.entities_hit_wire = {}  # type: dict[str, tuple[int, int, int]]

    @classmethod
    def calc_transfer_speed(cls, block_name):
        return TRANSFER_SPEED_MAPPING.get(block_name, 1) * 5

    def __repr__(self):
        return "WireNetwork({}, {}, {})".format(
            self.dim, self.group_inputs, self.group_outputs
        )

    def trigger_shock(self, transfer_rf):
        # type: (int) -> None
        if transfer_rf > 0 and self.entities_hit_wire:
            damage = min(2147483647, rf_to_damage(transfer_rf))
            for entity_id, hit_pos in self.entities_hit_wire.items():
                Hurt(entity_id, damage, ShockHurt)
        self.entities_hit_wire.clear()


class WireAccessPoint(BaseAccessPoint["WireNetwork"]):
    def __repr__(self):
        return "WireAP({}, {}, {}, {}, {})".format(
            self.dim, self.x, self.y, self.z, self.access_facing
        )
