# coding = utf-8
import mod.client.extraClientApi as clientApi
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.extensions.mod_settings import RegisterSetting
from skybluetech_scripts.tooldelta.events.client import UiInitFinishedEvent, OnScriptTickClient


SETTING_KEY = "skybluetech_show_achievement_button"
_visible = True
_pending = False


def SetCustomAchievementHudButtonVisible(visible):
    # type: (bool) -> bool
    achievementSys = clientApi.GetSystem("Minecraft", "achievement")
    if not achievementSys:
        return False

    gate = getattr(achievementSys, "mAchievementGate", None)
    if not gate:
        return False

    gate.SetVisible(gate.mGoodBtn, bool(visible), True)
    gate.UpdateScreen(True)
    return True


def onSettingChanged(key, value):
    # type: (str, bool) -> None
    global _visible, _pending
    _visible = bool(value)
    CF.CreateConfigClient(LEVEL_ID).SetConfigData(
        SETTING_KEY, {"visible": _visible}, False
    )
    _pending = not SetCustomAchievementHudButtonVisible(_visible)


@UiInitFinishedEvent.Listen()
def onUiInitFinished(_):
    global _visible, _pending
    config = CF.CreateConfigClient(LEVEL_ID).GetConfigData(SETTING_KEY, False) or {}
    _visible = config.get("visible", True)
    setting = RegisterSetting("skybluetech", "蔚蓝科技")
    if setting is not None:
        setting.AddText("title", "蔚蓝科技 - 客户端设置")
        setting.AddToggle(
            SETTING_KEY,
            "是否显示主屏幕成就按钮（可能影响其他模组成就）",
            onSettingChanged,
            default=_visible,
        )
    _pending = not SetCustomAchievementHudButtonVisible(_visible)


@OnScriptTickClient.Listen()
def onClientTick(_):
    global _pending
    # 成就界面可能晚于模组 UI 初始化，准备好后仅应用一次。
    if _pending:
        _pending = not SetCustomAchievementHudButtonVisible(_visible)
