# coding=utf-8
from ...tooldelta.api.client import (
    RegisterGeneralKeyMapping as _reg,
    GetControlMode,
    GetControlModeEnum,
    GetKeyMappings,
    GetGamepadKeyMappings,
    GetKeyboardEnum,
    GetGamepadKeyEnum,
)
from ...tooldelta.events.client import (
    OnCustomGamepadChangedEvent,
    OnCustomKeyChangedEvent,
    OnCustomGamepadPressInGame,
    OnCustomKeyPressInGame,
)
from ...tooldelta.general import ClientInitCallback

loaded_controls = {}  # type: dict[str, list[Control]]

# TODO: 因为 OnCustomGamepadChangedEvent 和 OnCustomKeyChangedEvent
# 都没有提供 category 参数, 所以请避免 name 重复


class Control:
    def __init__(self, category, name, default_key, default_gamepad):
        # type: (str, str, int, int) -> None
        loaded_controls.setdefault(name, []).append(self)
        self.category = category
        self.name = name
        self.default_key = default_key
        self.default_gamepad = default_gamepad
        self._key_id = None
        self._gamepad_id = None
        self._ctrl_mode = None

    @property
    def key_id(self):
        if self._key_id is None:
            self._key_id = GetKeyMappings(self.name)
        return self._key_id

    @property
    def gamepad_id(self):
        if self._gamepad_id is None:
            self._gamepad_id = GetGamepadKeyMappings(self.name)
        return self._gamepad_id

    @property
    def key_str(self):
        from .ctrl_zhcn import KEYBOARD_STR_MAPPING

        return KEYBOARD_STR_MAPPING.get(self.key_id, "?")

    @property
    def gamepad_str(self):
        from .ctrl_zhcn import GAMEPAD_STR_MAPPING

        return GAMEPAD_STR_MAPPING.get(self.gamepad_id, "?")

    def get_general_str(self, with_prefix=False):
        CTRL = GetControlModeEnum()
        mode = GetControlMode()
        if mode == CTRL.Mouse:
            if with_prefix:
                return "键盘 " + self.key_str
            else:
                return self.key_str
        elif mode == CTRL.GamePad:
            if with_prefix:
                return "手柄 " + self.gamepad_str
            else:
                return self.gamepad_str
        else:
            return "未知按键"

    def is_this(self, event):
        # type: (OnCustomGamepadPressInGame | OnCustomKeyPressInGame) -> bool
        return event.category == self.category and event.name == self.name

    @staticmethod
    def KEY():
        return GetKeyboardEnum()

    @staticmethod
    def GAMEPAD():
        return GetGamepadKeyEnum()


@ClientInitCallback(0)
def onClientInit():
    for name, ctrls in loaded_controls.items():
        for ctrl in ctrls:
            _reg(ctrl.category, name, ctrl.default_key, ctrl.default_gamepad)


@OnCustomGamepadChangedEvent.Listen()
def onGamepadChanged(event):
    # type: (OnCustomGamepadChangedEvent) -> None
    old_key = int(event.oldKey)
    new_key = int(event.newKey)
    ctrls = loaded_controls.get(event.name, [])
    for ctrl in ctrls:
        if ctrl._gamepad_id == old_key:
            ctrl._gamepad_id = new_key


@OnCustomKeyChangedEvent.Listen()
def onKeyChanged(event):
    # type: (OnCustomKeyChangedEvent) -> None
    old_key = int(event.oldKey)
    new_key = int(event.newKey)
    ctrls = loaded_controls.get(event.name, [])
    for ctrl in ctrls:
        if ctrl._key_id == old_key:
            ctrl._key_id = new_key
