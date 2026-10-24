# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
import time
from skybluetech_scripts.tooldelta.define import Item

from skybluetech_scripts.tooldelta.extensions.player_loader_utils import (
    AddPlayerCompletelyLoadedServerCallback,
)
from skybluetech_scripts.skybluetech.common.define.id_enum import GUIDANCE

EX_DATA_KEY = "st:player_inited"


def onPlayerLoaded(player_id):
    # type: (str) -> None
    players_loaded = CF.CreateExtraData(LEVEL_ID).GetExtraData(EX_DATA_KEY)
    if players_loaded is None:
        players_loaded = {}
    if player_id not in players_loaded:
        players_loaded[player_id] = time.time()
        CF.CreateExtraData(LEVEL_ID).SetExtraData(EX_DATA_KEY, players_loaded, True)
        CF.CreateItem(LEVEL_ID).SpawnItemToPlayerInv(Item(GUIDANCE).marshal(), player_id)


AddPlayerCompletelyLoadedServerCallback(onPlayerLoaded)
