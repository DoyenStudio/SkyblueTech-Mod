# coding=utf-8
from skybluetech_scripts.tooldelta.events.client import LoadClientAddonScriptsAfter

from ..common.events.general import SkyblueTechClientLoaded
from . import guidance, machinery, mini_jei, misc, tools, ui


@LoadClientAddonScriptsAfter.Listen()
def onLoadClientAddonScriptsAfter(_):
    # type: (LoadClientAddonScriptsAfter) -> None
    SkyblueTechClientLoaded().broadcast()