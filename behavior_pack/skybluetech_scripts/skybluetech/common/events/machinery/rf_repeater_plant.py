# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent


class RFRepeaterPlantSettingUpload(CustomC2SEvent):
    name = "st:RFRPSU"

    IO_EAST = 3
    IO_WEST = 2
    IO_SOUTH = 1
    IO_NORTH = 0

    MODE_INPUT = False
    MODE_OUTPUT = True

    def __init__(
        self,
        x,
        y,
        z,
        io_dir,
        io_mode,
        player_id="",
    ):
        # type: (int, int, int, int, bool, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.io_dir = io_dir
        self.io_mode = io_mode
        self.player_id = player_id

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "io_mode": self.io_mode,
            "io_dir": self.io_dir,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["x"],
            data["y"],
            data["z"],
            data["io_dir"],
            data["io_mode"],
            data["__id__"],
        )


class RFRepeaterPlantSettingsUpdate(CustomS2CEvent):
    name = "st:RFRPSUD"

    MODE_INPUT = False
    MODE_OUTPUT = True

    def __init__(
        self,
        dim,  # type: int
        x,  # type: int
        y,  # type: int
        z,  # type: int
        network_euid,  # type: str
        east_io_mode,  # type: bool
        west_io_mode,  # type: bool
        south_io_mode,  # type: bool
        north_io_mode,  # type: bool
        network_plant_count,  # type: int
        network_plant_online_count,  # type: int
        total_output_count,  # type: int
        total_output_active_count,  # type: int
        total_input_count,  # type: int
        total_input_active_count,  # type: int
    ):
        self.network_euid = network_euid
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.east_io_mode = east_io_mode
        self.west_io_mode = west_io_mode
        self.north_io_mode = north_io_mode
        self.south_io_mode = south_io_mode
        self.network_plant_count = network_plant_count
        self.network_plant_online_count = network_plant_online_count
        self.total_output_count = total_output_count
        self.total_output_active_count = total_output_active_count
        self.total_input_count = total_input_count
        self.total_input_active_count = total_input_active_count

    def marshal(self):
        return {
            "dim": self.dim,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "network_euid": self.network_euid,
            "east": self.east_io_mode,
            "west": self.west_io_mode,
            "north": self.north_io_mode,
            "south": self.south_io_mode,
            "npc": self.network_plant_count,
            "npco": self.network_plant_online_count,
            "toc": self.total_output_active_count,
            "toac": self.total_output_active_count,
            "tic": self.total_input_count,
            "tiac": self.total_input_active_count,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["dim"],
            data["x"],
            data["y"],
            data["z"],
            data["network_euid"],
            data["east"],
            data["west"],
            data["south"],
            data["north"],
            data["npc"],
            data["npco"],
            data["toc"],
            data["toac"],
            data["tic"],
            data["tiac"],
        )


class RFRepeaterPlantBuildRequest(CustomC2SEvent):
    name = "st:RFRPBR"

    def __init__(
        self,
        x,
        y,
        z,
        to_x,
        to_y,
        to_z,
        player_id="",
    ):
        # type: (int, int, int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.to_x = to_x
        self.to_y = to_y
        self.to_z = to_z
        self.player_id = player_id

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "to_x": self.to_x,
            "to_y": self.to_y,
            "to_z": self.to_z,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["x"],
            data["y"],
            data["z"],
            data["to_x"],
            data["to_y"],
            data["to_z"],
            data["__id__"],
        )


class RFRepeaterPlantBuildResponse(CustomS2CEvent):
    name = "st:RFRPBResp"

    STATUS_SUCC = 0
    STATUS_TOO_FAR = 1
    STATUS_TOO_FAST = 2
    STATUS_INVALID_START = 3
    STATUS_INVALID_END = 4
    STATUS_ALREADY_CONNECTED = 5
    STATUS_INTERNAL_ERROR = 6
    STATUS_INTERNAL_ERROR2 = 7
    STATUS_CANT_CONNECT_SELF = 8

    def __init__(self, status_code):
        # type: (int) -> None
        self.status_code = status_code

    def marshal(self):
        return {"stat": self.status_code}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["stat"])


class RFRepeaterPlantBuildAddWire(CustomS2CEvent):
    name = "st:RFRPBR"

    def __init__(
        self,
        x,
        y,
        z,
        to_x,
        to_y,
        to_z,
    ):
        # type: (int, int, int, int, int, int) -> None
        self.x = x
        self.y = y
        self.z = z
        self.to_x = to_x
        self.to_y = to_y
        self.to_z = to_z

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "to_x": self.to_x,
            "to_y": self.to_y,
            "to_z": self.to_z,
        }

    @classmethod
    def unmarshal(cls, data):
        return cls(
            data["x"],
            data["y"],
            data["z"],
            data["to_x"],
            data["to_y"],
            data["to_z"],
        )
