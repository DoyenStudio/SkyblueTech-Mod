# coding=utf-8
MODE_INPUT = 0
"模式: 电网向中继器供能"
MODE_OUTPUT = 1
"模式: 中继器向电网供能"

REVERSED_MAPPING = {MODE_INPUT: MODE_OUTPUT, MODE_OUTPUT: MODE_INPUT}


def reverse_mode(mode):
    # type: (int) -> int
    return REVERSED_MAPPING[mode]
