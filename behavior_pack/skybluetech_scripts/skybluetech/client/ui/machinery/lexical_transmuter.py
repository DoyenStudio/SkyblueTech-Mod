# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.flags import (
    DEACTIVE_FLAG_NO_INPUT,
    DEACTIVE_FLAG_NO_RECIPE,
)
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen

from ..machinery_extra_pages import ItemPipeSettingsPage
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx

POWER_PATH = MAIN_PATH / "power_bar"
PRGS_PATH = MAIN_PATH / "progress"


@RegistToolDeltaScreen("LexicalTransmuterUI.main", is_proxy=True)
class LexicalTransmuterUI(MachinePanelUIProxyEx):
    available_extra_pages = (ItemPipeSettingsPage,)
    STATUS_TEXTS = {DEACTIVE_FLAG_NO_RECIPE: "没有模板或物品与模板不符"}
    # 缺少输入只点亮输入槽 (默认的 ring_in_ 前缀会连模板槽一起点亮)
    STATUS_RINGS = {DEACTIVE_FLAG_NO_INPUT: ("ring_in_input",)}
