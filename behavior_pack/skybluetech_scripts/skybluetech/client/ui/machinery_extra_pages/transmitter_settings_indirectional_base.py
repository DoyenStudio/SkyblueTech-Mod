# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import GetBlockNameAndAux
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.facing import (
    FACING_DXYZ,
    OPPOSITE_FACING,
)
from skybluetech_scripts.skybluetech.common.misc.transmitter import TransmitterType
from skybluetech_scripts.skybluetech.common.events.misc.transmitter_settings import (
    TransmitterSwitchAccessMode,
)
from .base_page import PageBase
from .transmitter_settings_base import UpdateFaceButton


class AccessMode(object):
    def __init__(self, modes=None):
        # type: (list[int] | None) -> None
        self._modes = modes or [-1, -1, -1, -1, -1, -1]

    @property
    def south(self):
        # type: () -> int
        return self._modes[3]

    @property
    def north(self):
        # type: () -> int
        return self._modes[2]

    @property
    def top(self):
        # type: () -> int
        return self._modes[1]

    @property
    def west(self):
        # type: () -> int
        return self._modes[4]

    @property
    def east(self):
        # type: () -> int
        return self._modes[5]

    @property
    def bottom(self):
        # type: () -> int
        return self._modes[0]

    def __getitem__(self, key):
        # type: (int) -> int
        return self._modes[key]

    def __setitem__(self, key, value):
        # type: (int, int) -> None
        self._modes[key] = value


class TransmitterStates(object):
    def __init__(self, aux):
        # type: (int) -> None
        self.conn_west = bool(aux & 0x1)
        self.conn_up = bool(aux & 0x2)
        self.conn_south = bool(aux & 0x4)
        self.conn_north = bool(aux & 0x8)
        self.conn_east = bool(aux & 0x10)
        self.conn_down = bool(aux & 0x20)
        self.io_west = bool(aux & 0x40)
        self.io_up = bool(aux & 0x80)
        self.io_south = bool(aux & 0x100)
        self.io_north = bool(aux & 0x200)
        self.io_east = bool(aux & 0x400)
        self.io_down = bool(aux & 0x800)
        self.io_states = [
            self.io_down,
            self.io_up,
            self.io_north,
            self.io_south,
            self.io_west,
            self.io_east,
        ]
        self.conn_states = [
            self.conn_down,
            self.conn_up,
            self.conn_north,
            self.conn_south,
            self.conn_west,
            self.conn_east,
        ]


class TransmitterSettingsPageIndirectionalBase(PageBase):
    transmitter_type = TransmitterType.UNKNOWN
    transmitter_block_ids_set = set()  # type: set[str]

    def __init__(self, base, machine_pos):
        # type: (UBaseCtrl, tuple[int, int, int, int]) -> None
        PageBase.__init__(self, base, machine_pos)
        self.top_set_btn = (
            base["top_set_btn"].asButton().SetCallback(lambda _: self.switch(1))
        )
        self.west_set_btn = (
            base["west_set_btn"].asButton().SetCallback(lambda _: self.switch(4))
        )
        self.east_set_btn = (
            base["east_set_btn"].asButton().SetCallback(lambda _: self.switch(5))
        )
        self.south_set_btn = (
            base["south_set_btn"].asButton().SetCallback(lambda _: self.switch(3))
        )
        self.north_set_btn = (
            base["north_set_btn"].asButton().SetCallback(lambda _: self.switch(2))
        )
        self.bottom_set_btn = (
            base["bottom_set_btn"].asButton().SetCallback(lambda _: self.switch(0))
        )
        self.init()
        self.update()

    def get_access_mode(self):
        # type: () -> AccessMode
        modes = AccessMode()
        for face, (dx, dy, dz) in enumerate(FACING_DXYZ):
            tx = self.machine_pos[1] + dx
            ty = self.machine_pos[2] + dy
            tz = self.machine_pos[3] + dz
            transmitter_name, aux = GetBlockNameAndAux((tx, ty, tz))
            if transmitter_name not in self.transmitter_block_ids_set:
                continue
            transmitter_conn_face = OPPOSITE_FACING[face]
            transmitter_states = TransmitterStates(aux)
            if transmitter_states.conn_states[transmitter_conn_face]:
                modes[face] = int(transmitter_states.io_states[transmitter_conn_face])
            else:
                modes[face] = -1
        return modes

    def switch(self, face):
        if self.access_mode[face] == -1:
            return
        x, y, z = self.machine_pos[1:]
        x += FACING_DXYZ[face][0]
        y += FACING_DXYZ[face][1]
        z += FACING_DXYZ[face][2]
        self.access_mode[face] = not self.access_mode[face]
        TransmitterSwitchAccessMode(
            x, y, z, self.transmitter_type, OPPOSITE_FACING[face]
        ).send()
        self.update()

    def init(self):
        _, aux = GetBlockNameAndAux(self.machine_pos[1:])
        aux = aux & 0b11
        self.access_mode = self.get_access_mode()

    def update(self):
        self.update_btn_uv(self.top_set_btn, self.access_mode.top)
        self.update_btn_uv(self.west_set_btn, self.access_mode.west)
        self.update_btn_uv(self.east_set_btn, self.access_mode.east)
        self.update_btn_uv(self.south_set_btn, self.access_mode.south)
        self.update_btn_uv(self.north_set_btn, self.access_mode.north)
        self.update_btn_uv(self.bottom_set_btn, self.access_mode.bottom)

    def update_btn_uv(self, btn_ctrl, io_mode):
        # type: (UBaseCtrl, int) -> None
        UpdateFaceButton(btn_ctrl, io_mode)
