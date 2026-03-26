# coding=utf-8
from mod.client.extraClientApi import GetEngineCompFactory, GetLevelId, GetMinecraftEnum
from ..common.cacher import MethodCacher

CF = GetEngineCompFactory()


RegisterCustomKeyMapping = MethodCacher(
    lambda: CF.CreatePlayerView(GetLevelId()).RegisterCustomKeyMapping
)
RegisterCustomGamepadMapping = MethodCacher(
    lambda: CF.CreatePlayerView(GetLevelId()).RegisterCustomGamepadMapping
)
GetKeyMappings = MethodCacher(lambda: CF.CreatePlayerView(GetLevelId()).GetKeyMappings)
GetGamepadKeyMappings = MethodCacher(
    lambda: CF.CreatePlayerView(GetLevelId()).GetGamepadKeyMappings
)
GetKeyboardEnum = MethodCacher(lambda: GetMinecraftEnum().KeyBoardType)
GetGamepadKeyEnum = MethodCacher(lambda: GetMinecraftEnum().GamepadKeyType)


def RegisterGeneralKeyMapping(category, name, key, gamepad_key):
    # type: (str, str, int, int) -> tuple[bool, bool]
    return (
        RegisterCustomKeyMapping(name, key, category),
        RegisterCustomGamepadMapping(name, gamepad_key, category),
    )


__all__ = [
    "RegisterCustomKeyMapping",
    "RegisterCustomGamepadMapping",
    "RegisterGeneralKeyMapping",
    "GetKeyMappings",
    "GetKeyboardEnum",
    "GetGamepadKeyEnum",
    "GetGamepadKeyMappings",
]
