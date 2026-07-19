# coding: utf-8
NEIGHBOR_BLOCKS_ENUM = (
    (0, -1, 0),
    (0, 1, 0),
    (0, 0, -1),
    (0, 0, 1),
    (-1, 0, 0),
    (1, 0, 0),
)
CARDINAL_TO_FACING = [2, 5, 3, 4]
OPPOSITE_FACING = (1, 0, 3, 2, 5, 4)


FACING_ZHCN = {0: "下", 1: "上", 2: "北", 3: "南", 4: "西", 5: "东"}
FACING_EN = {0: "down", 1: "up", 2: "north", 3: "south", 4: "west", 5: "east"}
FACING_EN2NUM = {v: k for k, v in FACING_EN.items()}
FACING_DXZ = (
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0),
)
FACING_DXYZ = ((0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1), (-1, 0, 0), (1, 0, 0))
DXYZ_FACING = {
    (0, 0, 1): 3,
    (0, 0, -1): 2,
    (0, 1, 0): 1,
    (0, -1, 0): 0,
    (1, 0, 0): 5,
    (-1, 0, 0): 4,
}

_XZ_FACINGS = (4, 2, 5, 3)


class FrontFacingRes(object):
    def __init__(self, front_face):
        # type: (int) -> None
        self.front_face = front_face
        self.left_face = _XZ_FACINGS[(_XZ_FACINGS.index(front_face) + 1) % 4]
        self.right_face = _XZ_FACINGS[(_XZ_FACINGS.index(front_face) - 1) % 4]
        self.back_face = _XZ_FACINGS[(_XZ_FACINGS.index(front_face) + 2) % 4]


class CardinalDirectionRes(object):
    def __init__(self, aux):
        self.aux = aux & 0b11

    @property
    def string(self):
        return ["south", "west", "north", "east"][self.aux]


def GetFacingByDxyz(dx, dy, dz):
    # type: (int, int, int) -> int
    return NEIGHBOR_BLOCKS_ENUM.index((dx, dy, dz))
