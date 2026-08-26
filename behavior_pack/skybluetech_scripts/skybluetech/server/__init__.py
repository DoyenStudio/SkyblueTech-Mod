# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import LoadServerAddonScriptsAfter

from ..common.events.general import SkyblueTechServerLoaded
from . import commands, machinery, misc, player, tools, transmitters, world_loot


@LoadServerAddonScriptsAfter.Listen()
def onLoadServerAddonScriptsAfter(_):
    # type: (LoadServerAddonScriptsAfter) -> None
    SkyblueTechServerLoaded().broadcast()
