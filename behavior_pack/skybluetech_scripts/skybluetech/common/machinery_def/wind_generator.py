# coding=utf-8
from ..events.machinery.wind_generator import WindGeneratorStatesUpdate
from ..define.id_enum import Paddle

PaddleEnum = WindGeneratorStatesUpdate

K_MCW = "st:mcw"
K_OUTPUT_POWER = "st:output_power"

STORE_RF_MAX = 14400
MAX_MCW_HEIGHT_MULTIPLIER = 0.5
FINAL_OUTPUT_POWER_MULTIPLIER = 0.5


def item2paddle(item_id):
    # type: (str) -> int
    return {
        Paddle.IRON: PaddleEnum.PADDLE_IRON,
        Paddle.STEEL: PaddleEnum.PADDLE_STEEL,
        "minecraft:air": PaddleEnum.PADDLE_EMPTY,
    }.get(item_id, PaddleEnum.PADDLE_EMPTY)


def get_paddle_output(paddle_type):
    # type: (int) -> float
    return {
        PaddleEnum.PADDLE_IRON: 1,
        PaddleEnum.PADDLE_STEEL: 1.5,
    }.get(paddle_type, 0)
