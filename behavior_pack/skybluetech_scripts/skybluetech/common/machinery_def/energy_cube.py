# coding=utf-8
from ..define.machinery import EnergyIOMode

K_IO_MODE = "st:io_mode"
K_STATE_PREFIX = "skybluetech:"
K_STATE_SUFFIX = "_io_mode"
K_ENABLE_INPUT = "st:enable_input"
K_ENABLE_OUTPUT = "st:enable_output"
K_INPUT_POWER = "st:input_power"
K_OUTPUT_POWER = "st:output_power"

MAX_INPUT_POWER = 400
MAX_OUTPUT_POWER = 400
STORE_RF_MAX = 200000


class IOModes(object):
    NONE = EnergyIOMode.NONE
    INPUT = EnergyIOMode.INPUT
    OUTPUT = EnergyIOMode.OUTPUT

    def __init__(self, block_entity_data):
        self._data = block_entity_data
        modes = block_entity_data[K_IO_MODE] or {}  # type: dict[str, int]
        top = modes.get("top", IOModes.INPUT)
        bottom = modes.get("bottom", IOModes.OUTPUT)
        north = modes.get("north", IOModes.OUTPUT)
        south = modes.get("south", IOModes.OUTPUT)
        east = modes.get("east", IOModes.OUTPUT)
        west = modes.get("west", IOModes.OUTPUT)
        self._modes = [bottom, top, north, south, west, east]

    def save(self):
        self._data[K_IO_MODE] = {
            "bottom": self._modes[0],
            "top": self._modes[1],
            "north": self._modes[2],
            "south": self._modes[3],
            "west": self._modes[4],
            "east": self._modes[5],
        }

    def states(self):
        return {
            K_STATE_PREFIX + "bottom" + K_STATE_SUFFIX: self._modes[0],
            K_STATE_PREFIX + "top" + K_STATE_SUFFIX: self._modes[1],
            K_STATE_PREFIX + "north" + K_STATE_SUFFIX: self._modes[2],
            K_STATE_PREFIX + "south" + K_STATE_SUFFIX: self._modes[3],
            K_STATE_PREFIX + "west" + K_STATE_SUFFIX: self._modes[4],
            K_STATE_PREFIX + "east" + K_STATE_SUFFIX: self._modes[5],
        }

    def modes(self):
        bottom, top, north, south, west, east = self._modes
        return (bottom, top, north, south, west, east)
