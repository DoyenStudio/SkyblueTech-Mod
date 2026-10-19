# coding=utf-8
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

_K_FLUID_ID = "fluid_id"
_K_FLUID_VOLUME = "fluid_vol"
FLUID_VOLUME_EPSILON = 1e-6
INFINITY = float("inf")


class FluidSlotServer(object):
    def __init__(
        self,
        block_entity_data,
        index,  # type: int
        max_volume,  # type: float
    ):
        self.bdata = block_entity_data
        self.index = index
        self.max_volume = max_volume
        self.k_id = _K_FLUID_ID + str(index)
        self.k_vol = _K_FLUID_VOLUME + str(index)
        self._cached_fluid_id = block_entity_data[self.k_id]
        # 无限槽只持久化有限标记。液体类型存在即可在重载后恢复无限供应。
        if self.max_volume == INFINITY and self._cached_fluid_id is not None:
            self.volume = 1.0
        else:
            self.volume = block_entity_data[self.k_vol] or 0.0

    @property
    def fluid_id(self):
        # type: () -> str | None
        return self._cached_fluid_id

    @fluid_id.setter
    def fluid_id(self, value):
        # type: (str | None) -> None
        self._cached_fluid_id = self.bdata[self.k_id] = value
        if value is None:
            self._cached_volume = self.bdata[self.k_vol] = 0.0

    @property
    def volume(self):
        # type: () -> float
        return self._cached_volume

    @volume.setter
    def volume(self, value):
        # type: (float) -> None
        if (
            self._cached_fluid_id is None
            or value is None
            or value <= FLUID_VOLUME_EPSILON
            or value != value
        ):
            value = 0.0
            if self._cached_fluid_id is not None:
                self.fluid_id = None
        elif self.max_volume == INFINITY:
            self._cached_volume = INFINITY
            self.bdata[self.k_vol] = 1.0
            return
        else:
            value = min(float(value), self.max_volume)
        self._cached_volume = self.bdata[self.k_vol] = float(value)

    def isFull(self):
        return self.volume >= self.max_volume

    def canMerge(self, fluid_id):
        # type： (str | None) -> bool
        if fluid_id is None:
            return False
        if self.isFull():
            return False
        fid = self.fluid_id
        if fid is None or self.volume == 0 or fluid_id == fid:
            return True
        else:
            return False


class FluidSlotClient(object):
    def __init__(self, block_entity_data_ex, index=0, max_volume=None):
        self.data = block_entity_data_ex
        self.k_id = _K_FLUID_ID + str(index)
        self.k_vol = _K_FLUID_VOLUME + str(index)
        self.max_volume = max_volume

    @property
    def fluid_id(self):
        # type: () -> str | None
        return GetValue(self.data, self.k_id, None)

    @property
    def volume(self):
        # type: () -> float
        if self.max_volume == INFINITY and self.fluid_id is not None:
            return INFINITY
        return GetValue(self.data, self.k_vol, 0.0)
