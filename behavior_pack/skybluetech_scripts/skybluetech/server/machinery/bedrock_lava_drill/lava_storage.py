# coding=utf-8
import random
from mod.server.extraServerApi import GetLevelId
from skybluetech_scripts.tooldelta.api.server import GetExtraData, SetExtraData, GetSeed

# 和 MC 的区块概念不同,
# 单个岩浆源区块大小为 8x8

K_LAVA_SOURCES = "st:lava_sources"
MAX_LAVA_STORAGE = 6400000

cached_lava_sources = {}  # type: dict[tuple[int, int], int]


def lava_volume_map_func(x):
    # type: (float) -> int
    if x > 1:
        return MAX_LAVA_STORAGE
    elif x <= 0:
        return 0
    return (1 - x**0.1) * MAX_LAVA_STORAGE


def pos_to_chunk(x, y):
    # type: (int, int) -> tuple[int, int]
    return int(x // 8), int(y // 8)


def load_new_chunk(chunk_x, chunk_y, seed):
    return lava_volume_map_func(
        random.Random(seed + chunk_x + (2 << 28) + chunk_y).random()
    )


def get_chunk_lava_storage(chunk_x, chunk_y, seed):
    # type: (int, int, int) -> int
    if (chunk_x, chunk_y) in cached_lava_sources:
        return cached_lava_sources[(chunk_x, chunk_y)]
    else:
        s = cached_lava_sources[(chunk_x, chunk_y)] = load_new_chunk(
            chunk_x, chunk_y, seed
        )
        return s


def get_nearby_lava_storage(chunk_x, chunk_y):
    # type: (int, int) -> int
    seed = GetSeed()
    return sum(
        get_chunk_lava_storage(_x, _y, seed)
        for _x in range(chunk_x - 1, chunk_x + 2)
        for _y in range(chunk_y - 1, chunk_y + 2)
    )


def save_lava_storages():
    SetExtraData(GetLevelId(), K_LAVA_SOURCES, cached_lava_sources)


def load_lava_storages():
    s = GetExtraData(GetLevelId(), K_LAVA_SOURCES, {})
    cached_lava_sources.update(s)


def set_chunk_lava_storage(chunk_x, chunk_y, storage_vol):
    # type: (int, int, int) -> None
    cached_lava_sources[(chunk_x, chunk_y)] = storage_vol


def reduce_chunk_lava_storage(chunk_x, chunk_y, reduce_volume):
    # type: (int, int, int) -> None
    cached_lava_sources[(chunk_x, chunk_y)] -= reduce_volume


def pump_deepslate_lava(chunk_x, chunk_y, max_pump_volume):
    # type: (int, int, int) -> int
    rest_volume = max_pump_volume
    seed = GetSeed()
    for _x in range(chunk_x - 1, chunk_x + 2):
        for _y in range(chunk_y - 1, chunk_y + 2):
            storage_vol = get_chunk_lava_storage(_x, _y, seed)
            if storage_vol >= rest_volume:
                reduce_chunk_lava_storage(_x, _y, max_pump_volume)
                return max_pump_volume
            elif storage_vol <= 0:
                continue
            else:
                set_chunk_lava_storage(_x, _y, 0)
                rest_volume -= storage_vol
    return max_pump_volume - rest_volume
