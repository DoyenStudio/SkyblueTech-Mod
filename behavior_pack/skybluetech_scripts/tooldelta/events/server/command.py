# coding=utf-8
from ..basic import ServerEvent


class CustomCommandTriggerServerEvent(ServerEvent):
    name = "CustomCommandTriggerServerEvent"

    command = ""  # type: str
    """ 自定义命令名称，对应json中的name字段 """
    args = []  # type: list[dict]
    """ 自定义命令参数，详情见下方 """
    variant = 0  # type: int
    """ 表示是哪条变体，范围[0, 9]，对应json中args键中的数字，未配置变体则为0 """
    origin = {}  # type: dict
    """ 触发源的信息，详情见下方 """
    return_failed = False  # type: bool
    """ 设置自定义命令是否执行失败，默认为False，如果执行失败，返回信息以红色字体显示 """
    return_msg_key = ""  # type: str
    """ 设置返回给玩家或命令方块的信息，也支持通过语言文件(.lang)定义，默认值为commands.custom.success(自定义命令执行成功) """
    _orig = {}

    @classmethod
    def unmarshal(cls, data):
        # type: (dict) -> CustomCommandTriggerServerEvent
        instance = cls()
        instance._orig = data
        instance.command = data["command"]
        instance.args = data["args"]
        instance.variant = data["variant"]
        instance.origin = data["origin"]
        instance.return_failed = data["return_failed"]
        instance.return_msg_key = data["return_msg_key"]
        return instance

    def marshal(self):
        # type: () -> dict
        return {
            "command": self.command,
            "args": self.args,
            "variant": self.variant,
            "origin": self.origin,
            "return_failed": self.return_failed,
            "return_msg_key": self.return_msg_key,
        }

    def SetReturnFailed(self):
        self._orig["return_failed"] = self.return_failed = True

    def SetReturnMsg(self, msg):
        # type: (str) -> None
        self._orig["return_msg_key"] = self.return_msg_key = msg

    def SetReturnParams(self, *params):
        # type: (str) -> None
        # thanks D0FES
        self._orig["return_params"] = list(params)
