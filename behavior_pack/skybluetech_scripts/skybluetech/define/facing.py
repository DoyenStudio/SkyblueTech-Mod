NEIGHBOR_BLOCKS_ENUM = (
    (0, -1, 0),
    (0, 1, 0),
    (0, 0, -1),
    (0, 0, 1),
    (-1, 0, 0),
    (1, 0, 0),
)

OPPOSITE_FACING = (1, 0, 3, 2, 5, 4)

def GetFacingByDxyz(dx, dy, dz):
    # type: (int, int, int) -> int
    return NEIGHBOR_BLOCKS_ENUM.index((dx, dy, dz))

FACING_ZHCN = {0: "下", 1: "上", 2: "北", 3: "南", 4: "西", 5: "东"}
FACING_EN = {0: "down", 1: "up", 2: "north", 3: "south", 4: "west", 5: "east"}
FACING_EN2NUM = {v: k for k, v in FACING_EN.items()}
FACING_DXZ = (
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0),
)
FACING_DXYZ = (
    (0, -1, 0),
    (0, 1, 0),
    (0, 0, -1),
    (0, 0, 1),
    (-1, 0, 0),
    (1, 0, 0),
)
DXYZ_FACING = {
    (0, 0, 1): 3,
    (0, 0, -1): 2,
    (0, 1, 0): 1,
    (0, -1, 0): 0,
    (1, 0, 0): 5,
    (-1, 0, 0): 4,
}
