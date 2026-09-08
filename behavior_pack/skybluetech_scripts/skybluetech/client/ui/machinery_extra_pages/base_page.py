# coding=utf-8
from skybluetech_scripts.tooldelta.ui import UBaseCtrl


class PageBase(object):
    def __init__(self, base, machine_pos):
        # type: (UBaseCtrl, tuple[int, int, int, int]) -> None
        self.base = base
        self.machine_pos = machine_pos

    def Init(self):
        pass

    def Active(self):
        pass

    def Deactive(self):
        pass

    @staticmethod
    def GetIconPath():
        # type: () -> str
        raise NotImplementedError("GetIconPath")

    @staticmethod
    def GetControlDef():
        # type: () -> str
        raise NotImplementedError("GetControlDef")


class MainPage(PageBase):
    "机器主界面, 仅占位用"

    def __init__(self):
        pass

    @staticmethod
    def GetIconPath():
        return "textures/blocks/machinery/frame"

    @staticmethod
    def GetControlDef():
        return "main"
