# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.facing import (
    FACING_DXYZ,
    OPPOSITE_FACING,
    CARDINAL_TO_FACING,
    FrontFacingRes,
)
from skybluetech_scripts.skybluetech.common.misc.transmitter import TransmitterType
from skybluetech_scripts.skybluetech.common.events.misc.transmitter_settings import (
    TransmitterSwitchAccessMode,
)
from .base_page import PageBase

# 端口面按钮底色: -1 未连接管道 (灰) / 0 管道存入 = 机器输入 (蓝) / 1 管道抽取 = 机器输出 (橙)
IO_FACE_COLORS = {
    -1: (0.69, 0.69, 0.69),
    0: (0.651, 0.835, 0.969),
    1: (0.969, 0.804, 0.580),
}


def UpdateFaceButton(btn_ctrl, io_mode):
    # type: (UBaseCtrl, int) -> None
    "端口面按钮: 旧版 9x9 状态图标保留 (已隐藏), 新版用底色区分状态。"
    if io_mode == -1:
        uv_start = (0, 18)
    elif io_mode:
        uv_start = (0, 9)
    else:
        uv_start = (0, 0)
    img = btn_ctrl["icon"].asImage()
    img.SetUV(uv_start, (9, 9))
    img.SetAlpha(0.5)
    try:
        fill = btn_ctrl["fill"].asImage()
    except ValueError:
        return
    fill.SetSpriteColor(IO_FACE_COLORS[-1 if io_mode == -1 else int(bool(io_mode))])
    fill.SetAlpha(1.0)


class AccessMode(object):
    def __init__(self, face_helper, modes=None):
        # type: (FrontFacingRes, list[int] | None) -> None
        self._modes = modes or [-1, -1, -1, -1, -1, -1]
        self.facing_helper = face_helper

    @property
    def front(self):
        # type: () -> int
        return self._modes[self.facing_helper.front_face]

    @property
    def back(self):
        # type: () -> int
        return self._modes[self.facing_helper.back_face]

    @property
    def top(self):
        # type: () -> int
        return self._modes[1]

    @property
    def left(self):
        # type: () -> int
        return self._modes[self.facing_helper.left_face]

    @property
    def right(self):
        # type: () -> int
        return self._modes[self.facing_helper.right_face]

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


class TransmitterSettingsPageBase(PageBase):
    transmitter_type = TransmitterType.UNKNOWN
    transmitter_block_ids_set = set()  # type: set[str]

    def __init__(self, base, machine_pos):
        # type: (UBaseCtrl, tuple[int, int, int, int]) -> None
        PageBase.__init__(self, base, machine_pos)
        self.top_set_btn = (
            base["top_set_btn"]
            .asButton()
            .SetCallback(lambda _: self.switch(self.top_face))
        )
        self.left_set_btn = (
            base["left_set_btn"]
            .asButton()
            .SetCallback(lambda _: self.switch(self.left_face))
        )
        self.front_set_btn = (
            base["front_set_btn"]
            .asButton()
            .SetCallback(lambda _: self.switch(self.front_face))
        )
        self.right_set_btn = (
            base["right_set_btn"]
            .asButton()
            .SetCallback(lambda _: self.switch(self.right_face))
        )
        self.bottom_set_btn = (
            base["bottom_set_btn"]
            .asButton()
            .SetCallback(lambda _: self.switch(self.bottom_face))
        )
        self.back_set_btn = (
            base["back_set_btn"]
            .asButton()
            .SetCallback(lambda _: self.switch(self.back_face))
        )
        self.init()
        self.update()

    def get_access_mode(self, front_face_helper):
        # type: (FrontFacingRes) -> AccessMode
        modes = AccessMode(front_face_helper)
        for face, (dx, dy, dz) in enumerate(FACING_DXYZ):
            tx = self.machine_pos[1] + dx
            ty = self.machine_pos[2] + dy
            tz = self.machine_pos[3] + dz
            transmitter_name, aux = CF.CreateBlockInfo(LEVEL_ID).GetBlock((tx, ty, tz)) or (None, 0)
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
        _, aux = CF.CreateBlockInfo(LEVEL_ID).GetBlock(self.machine_pos[1:]) or (None, 0)
        aux = aux & 0b11
        r = FrontFacingRes(OPPOSITE_FACING[CARDINAL_TO_FACING[aux]])
        self.left_face = r.left_face
        self.right_face = r.right_face
        self.back_face = r.back_face
        self.front_face = r.front_face
        self.top_face = 1
        self.bottom_face = 0
        self.access_mode = self.get_access_mode(r)

    def update(self):
        self.update_btn_uv(self.top_set_btn, self.access_mode.top)
        self.update_btn_uv(self.left_set_btn, self.access_mode.left)
        self.update_btn_uv(self.front_set_btn, self.access_mode.front)
        self.update_btn_uv(self.right_set_btn, self.access_mode.right)
        self.update_btn_uv(self.bottom_set_btn, self.access_mode.bottom)
        self.update_btn_uv(self.back_set_btn, self.access_mode.back)

    def update_btn_uv(self, btn_ctrl, io_mode):
        # type: (UBaseCtrl, int) -> None
        UpdateFaceButton(btn_ctrl, io_mode)
