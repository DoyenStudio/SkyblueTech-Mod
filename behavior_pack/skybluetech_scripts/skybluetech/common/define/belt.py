# coding=utf-8
from .id_enum import TransmitBelt


OUTPUT_BELTS = frozenset((TransmitBelt.BELT, TransmitBelt.EXTRACTOR, TransmitBelt.DETECTOR))
BELTS = OUTPUT_BELTS | frozenset((TransmitBelt.INSERTER,))
BELT_STATUS = "skybluetech:transmit_belt_status"


class BeltState(object):
    STRAIGHT = "straight"
    CORNER_LEFT = "corner_left"
    CORNER_RIGHT = "corner_right"
    DIAGONAL_UP = "diagonal_up"
    DIAGONAL_DOWN = "diagonal_down"
