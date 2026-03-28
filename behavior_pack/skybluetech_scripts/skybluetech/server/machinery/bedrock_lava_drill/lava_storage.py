# coding=utf-8
import time
import random
from mod.server.extraServerApi import GetLevelId, GetEngineCompFactory
from skybluetech_scripts.tooldelta.api.server import GetExtraData, SetExtraData, GetSeed
from skybluetech_scripts.tooldelta.general import ServerInitCallback

CF = GetEngineCompFactory()
last_save_time = 0

# 和 MC 的区块概念不同,
# 单个熔岩源区块大小为 8x8

K_LAVA_SOURCES = "st:lava_sources"
MAX_LAVA_STORAGE = 6400000
MAX_DRILL_SECONDS = 10

cached_lava_sources = {}  # type: dict[tuple[int, int], int]


def calcuate_lava_volume_from_seed(seed, chunk_x, chunk_z):
    # type: (int, int, int) -> int
    x = random.Random(seed + chunk_x + (1 << 28) + chunk_z).random()
    if x > 1:
        return MAX_LAVA_STORAGE
    elif x <= 0:
        return 0
    return int((1 - x**0.1) * MAX_LAVA_STORAGE)


def calcuate_drill_time_from_seed(seed, chunk_x, chunk_z):
    # type: (int, int, int) -> int
    return int(
        (
            float(calcuate_lava_volume_from_seed(seed, chunk_x, chunk_z))
            / MAX_LAVA_STORAGE
        )
        ** 0.5
        * MAX_DRILL_SECONDS
    )


def pos_to_chunk(x, z):
    # type: (int, int) -> tuple[int, int]
    return int(x // 8), int(z // 8)


def load_new_chunk(chunk_x, chunk_z, seed):
    # type: (int, int, int) -> int
    return calcuate_lava_volume_from_seed(seed, chunk_x, chunk_z)


def get_chunk_drill_time(x, z):
    # type: (int, int) -> int
    chunk_x, chunk_z = pos_to_chunk(x, z)
    seed = CF.CreateGame(GetLevelId()).GetSeed()
    return calcuate_drill_time_from_seed(seed, chunk_x, chunk_z)


def get_chunk_lava_storage(chunk_x, chunk_z, seed):
    # type: (int, int, int) -> int
    if (chunk_x, chunk_z) in cached_lava_sources:
        return cached_lava_sources[(chunk_x, chunk_z)]
    else:
        s = cached_lava_sources[(chunk_x, chunk_z)] = load_new_chunk(
            chunk_x, chunk_z, seed
        )
        return s


def get_nearby_lava_storage(chunk_x, chunk_z):
    # type: (int, int) -> int
    seed = GetSeed()
    return sum(
        get_chunk_lava_storage(_x, _y, seed)
        for _x in range(chunk_x - 1, chunk_x + 2)
        for _y in range(chunk_z - 1, chunk_z + 2)
    )


def get_total_nearby_lava_storage(chunk_x, chunk_z):
    # type: (int, int) -> int
    seed = GetSeed()
    return sum(
        calcuate_lava_volume_from_seed(_x, _y, seed)
        for _x in range(chunk_x - 1, chunk_x + 2)
        for _y in range(chunk_z - 1, chunk_z + 2)
    )


def save_lava_storages():
    global last_save_time
    nowtime = time.time()
    if nowtime - last_save_time < 5:
        return
    SetExtraData(GetLevelId(), K_LAVA_SOURCES, cached_lava_sources)


@ServerInitCallback(0)
def load_lava_storages():
    s = GetExtraData(GetLevelId(), K_LAVA_SOURCES, {})
    cached_lava_sources.update(s)


def set_chunk_lava_storage(chunk_x, chunk_z, storage_vol):
    # type: (int, int, int) -> None
    cached_lava_sources[(chunk_x, chunk_z)] = storage_vol


def reduce_chunk_lava_storage(chunk_x, chunk_z, reduce_volume):
    # type: (int, int, int) -> None
    cached_lava_sources[(chunk_x, chunk_z)] -= reduce_volume


def pump_deepslate_lava(x, z, max_pump_volume):
    # type: (int, int, int) -> int
    rest_volume = max_pump_volume
    chunk_x, chunk_z = pos_to_chunk(x, z)
    seed = GetSeed()
    for _x in range(chunk_x - 1, chunk_x + 2):
        for _y in range(chunk_z - 1, chunk_z + 2):
            storage_vol = get_chunk_lava_storage(_x, _y, seed)
            if storage_vol >= rest_volume:
                reduce_chunk_lava_storage(_x, _y, max_pump_volume)
                save_lava_storages()
                return max_pump_volume
            elif storage_vol <= 0:
                continue
            else:
                set_chunk_lava_storage(_x, _y, 0)
                save_lava_storages()
                rest_volume -= storage_vol
            if rest_volume <= 0:
                break
    return max_pump_volume - rest_volume


def get_available_lava_storage(x, z):
    # type: (int, int) -> tuple[int, int]
    chunk_x, chunk_z = pos_to_chunk(x, z)
    return (
        get_nearby_lava_storage(chunk_x, chunk_z),
        get_total_nearby_lava_storage(chunk_x, chunk_z),
    )
