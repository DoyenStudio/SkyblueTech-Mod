# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent, CustomS2CEvent


class MachineStatusUpdate(CustomS2CEvent):
    """
    机器停机标志变化时, 推给正打开该机器界面的玩家。
    界面上的状态灯 / 停机提示圈据此刷新, 客户端不需要轮询方块数据。
    """
    name = "st:MSTU"

    def __init__(self, x=0, y=0, z=0, flags=0):
        # type: (int, int, int, int) -> None
        self.x = x
        self.y = y
        self.z = z
        self.flags = flags

    def marshal(self):
        return {"x": self.x, "y": self.y, "z": self.z, "f": self.flags}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["x"], data["y"], data["z"], data["f"])


class MachineryOperationC2S(CustomC2SEvent):
    """
    玩家端对某一位置机器进行操作的请求。
    基础信息包括 x, y, z, player_id

    额外参数名需要在 extra_attrs 元组中写明
    """
    extra_attrs = ()  # type: tuple[str, ...]

    def __init__(self, x, y, z, player_id=""):
        # type: (int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.player_id = player_id

    def marshal(self):
        dic = {"x": self.x, "y": self.y, "z": self.z}
        for attr_name in self.extra_attrs:
            dic[attr_name] = getattr(self, attr_name)
        return dic

    @classmethod
    def unmarshal(cls, data):
        attrs = {attr_name: data[attr_name] for attr_name in cls.extra_attrs}
        attrs.update(data)
        attrs["player_id"] = attrs.pop("__id__")
        return cls(**attrs)
