# coding=utf-8

STORE_RF_MAX = 10000
SHOCK_RF = 1000
SHOCK_BASE_DISTANCE = 2
SHOCK_RF_PER_EXTRA_BLOCK = SHOCK_RF // 5
SHOCK_DAMAGE = 10
SHOCK_INTERVAL = 2.0

DEFAULT_WORK_RANGE = 5
MIN_WORK_RANGE = 1
MAX_WORK_RANGE = 16

K_SETTING_ATTACK_MONSTER = "st:do_attack_monster"
K_SETTING_ATTACK_MOB = "st:do_attack_mob"
K_SETTING_ATTACK_PLAYER = "st:do_attack_player"
K_SETTING_WORK_RANGE = "st:work_range"


def get_shock_rf(distance):
    # type: (float) -> int
    """Each complete block beyond two adds 20% of the base hit cost."""
    extra_blocks = max(0, int(distance) - SHOCK_BASE_DISTANCE)
    return SHOCK_RF + extra_blocks * SHOCK_RF_PER_EXTRA_BLOCK
