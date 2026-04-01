# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockName,
    UpdateBlockStates,
)
from skybluetech_scripts.tooldelta.events.server import BlockNeighborChangedServerEvent
from ....common.define.facing import DXYZ_FACING, FACING_EN
from ...transmitters.cable.logic import isCable
from ...transmitters.pipe.logic import isPipe
from ...transmitters.wire.logic import isWire
from ..basic import BaseMachine


class TransmitterConn(object):
    def __init__(self, cable=False, pipe=False, wire=False):
        # type: (bool, bool, bool) -> None
        self.cable = cable
        self.pipe = pipe
        self.wire = wire

    def block_placed(self, machine):
        # type: (BaseMachine) -> None
        states = {}
        for dx, dy, dz in DXYZ_FACING.keys():
            facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
            bname = GetBlockName(
                machine.dim, (machine.x + dx, machine.y + dy, machine.z + dz)
            )
            if not bname:
                continue
            if self.cable:
                states["skybluetech:%s_cable_connection" % facing_en] = isCable(bname)
            if self.pipe:
                states["skybluetech:%s_pipe_connection" % facing_en] = isPipe(bname)
            if self.wire:
                states["skybluetech:%s_wire_connection" % facing_en] = isWire(bname)
        UpdateBlockStates(machine.dim, (machine.x, machine.y, machine.z), states)

    def neighbor_block_changed(self, machine, event):
        # type: (BaseMachine, BlockNeighborChangedServerEvent) -> None
        dx = event.neighborPosX - machine.x
        dy = event.neighborPosY - machine.y
        dz = event.neighborPosZ - machine.z
        facing_en = FACING_EN[DXYZ_FACING[dx, dy, dz]]
        if facing_en not in {"south", "north", "east", "west"}:
            return
        states = {}
        if self.cable:
            states["skybluetech:%s_cable_connection" % facing_en] = isCable(
                event.toBlockName
            )
        if self.pipe:
            states["skybluetech:%s_pipe_connection" % facing_en] = isPipe(
                event.toBlockName
            )
        if self.wire:
            states["skybluetech:%s_wire_connection" % facing_en] = isWire(
                event.toBlockName
            )
        UpdateBlockStates(
            machine.dim,
            (machine.x, machine.y, machine.z),
            states,
        )
