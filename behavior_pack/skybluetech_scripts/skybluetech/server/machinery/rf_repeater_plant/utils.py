# coding=utf-8


def pack_modes(east, west, south, north):
    # type: (bool, bool, bool, bool) -> int
    return east << 3 | west << 2 | south << 1 | north


def unpack_modes(mode):
    # type: (int) -> tuple[bool, bool, bool, bool]
    return (
        bool(mode >> 3 & 1),
        bool(mode >> 2 & 1),
        bool(mode >> 1 & 1),
        bool(mode & 1),
    )


def hypot(*dis):
    # type: (float) -> float
    return sum(i**2 for i in dis) ** 0.5
