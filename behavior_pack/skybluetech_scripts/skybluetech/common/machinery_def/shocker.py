# coding=utf-8
from math import ceil

STORE_RF_MAX = 16000
MIN_GAP = 1
MAX_GAP = 3
MAX_TARGET_HEALTH = 40
RF_PER_HEALTH = 100
K_STUNNED = "skybluetech:shocker_stunned"


def get_half_energy_cost(health, gap):
    # type: (float, int) -> int
    return int(ceil(health * RF_PER_HEALTH * gap / 2.0))
