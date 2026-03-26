# coding=utf-8


def hypot(*dis):
    # type: (float) -> float
    return sum(i**2 for i in dis) ** 0.5
