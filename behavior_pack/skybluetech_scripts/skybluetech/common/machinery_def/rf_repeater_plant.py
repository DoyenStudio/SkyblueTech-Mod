# coding=utf-8
MODE_INPUT = 0
"模式: 电网向中继塔供能"
MODE_OUTPUT = 1
"模式: 中继塔向电网供能"

REVERSED_MAPPING = {MODE_INPUT: MODE_OUTPUT, MODE_OUTPUT: MODE_INPUT}


def reverse_mode(mode):
    # type: (int) -> int
    return REVERSED_MAPPING[mode]
