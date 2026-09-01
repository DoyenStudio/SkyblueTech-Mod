# coding=utf-8
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen

from ..machinery_extra_pages import CableSettingsPage
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx

POWER_PATH = MAIN_PATH / "power_bar"
PRGS_PATH = MAIN_PATH / "progress"


@RegistToolDeltaScreen("LexicalTransmuterUI.main", is_proxy=True)
class LexicalTransmuterUI(MachinePanelUIProxyEx):
    available_extra_pages = (CableSettingsPage,)
