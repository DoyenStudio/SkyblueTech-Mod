# coding=utf-8
import time

from mod.server.extraServerApi import GetMinecraftEnum
from mod_log import logger

from skybluetech_scripts.skybluetech.common.define.id_enum import INSCRIBING_TEMPLATE
from skybluetech_scripts.skybluetech.common.events.misc.industrial_researching import (
    IndustrialResearchingInscribeRequest,
    IndustrialResearchingQueryRequest,
    IndustrialResearchingQueryResponse,
    IndustrialResearchingSubmitRequest,
)
from skybluetech_scripts.skybluetech.common.misc.industrial_researching import (
    all_researchings,
)
from skybluetech_scripts.skybluetech.common.misc.inscribing_template import (
    K_UD_TEMPLATE_GRAPH,
    GetTemplateGraph,
)
from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.api.server import (
    GetAllInventoryItems,
    GetExtraData,
    GetPlayerMainhandItem,
    GetSeed,
    SetExtraData,
    SetOnePopupNotice,
    SetPlayerAllItems,
)
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.event_bus import GetMCServerEventBus
from skybluetech_scripts.tooldelta.events.service import EventListenerService
from skybluetech_scripts.tooldelta.utils import nbt

if 0:
    from skybluetech_scripts.skybluetech.common.mini_jei.misc.industrial_researching import (
        IndustrialResearchingRecipe,  # noqa: F401
    )


ItemPosType = GetMinecraftEnum().ItemPosType
RESEARCHING_BY_ITEM_ID = {recipe.result_item_id: recipe for recipe in all_researchings}
VALID_RESEARCHING_ITEM_IDS = set(RESEARCHING_BY_ITEM_ID)
SUBMIT_RESPONSE_DELAYS = (0.0, 0.2, 0.8)


class IndustrialResearchingPlayerMgr(object):
    _instance = None
    _DATA_KEY = "st:researchings"

    def __init__(self):
        pass

    def record_researching(self, player_id, researching_id):
        # type: (str, str) -> None
        """
        记录玩家研究了某种可研究物。

        Args:
            player_id (str): 玩家 ID。
            researching_id (str): 可研究物 ID。为 IndustrialResearchingRecipe 的 result_item_id。
        """
        researchings = self.get_player_researchings(player_id)
        researchings[researching_id] = int(time.time())
        self._save_player_researchings(player_id, researchings)

    def has_researched(self, player_id, researching_id):
        # type: (str, str) -> bool
        """
        玩家是否研究了某种可研究物。

        Args:
            player_id (str): 玩家 ID。
            researching_id (str): 可研究物 ID。为 IndustrialResearchingRecipe 的 result_item_id。

        Returns:
            bool: 是否研究了。
        """
        return researching_id in self.get_player_researchings(player_id)

    def cancel_researching(self, player_id, researching_id):
        # type: (str, str) -> bool
        """
        取消玩家对某种可研究物的研究记录。

        Args:
            player_id (str): 玩家 ID。
            researching_id (str): 可研究物 ID。为 IndustrialResearchingRecipe 的 result_item_id。

        Returns:
            bool: 是否成功取消。
        """
        researchings = self.get_player_researchings(player_id)
        if researching_id not in researchings:
            return False
        del researchings[researching_id]
        self._save_player_researchings(player_id, researchings)
        return True

    def get_player_researchings(self, player_id):
        # type: (str) -> dict[str, int]
        """
        获取玩家所有已研究的物品。

        Args:
            player_id (str): 玩家 ID。

        Returns:
            dict[str, int]: 所有已研究的物品，键为 IndustrialResearchingRecipe 的 result_item_id，值为研究时间戳。
        """
        return GetExtraData(player_id, self._DATA_KEY) or {}

    def _save_player_researchings(self, player_id, researchings):
        # type: (str, dict[str, int]) -> None
        SetExtraData(player_id, self._DATA_KEY, researchings)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


class IndustrialResearchingQueryHandler(EventListenerService):
    def __init__(self):
        EventListenerService.__init__(self, GetMCServerEventBus())
        self.enable_listeners()

    @EventListenerService.Listen(IndustrialResearchingQueryRequest)
    def on_query_researchings(self, event):
        # type: (IndustrialResearchingQueryRequest) -> None
        researched_items = (
            IndustrialResearchingPlayerMgr.instance().get_player_researchings(
                event.player_id
            )
        )
        # BUG: 多发以避免数据包丢失
        for _ in range(3):
            IndustrialResearchingQueryResponse(researched_items).send(event.player_id)

    def _send_researching_response(self, player_id, researched_items):
        # type: (str, dict[str, int]) -> None
        IndustrialResearchingQueryResponse(researched_items).send(player_id)

    def _schedule_submit_response(self, player_id, researched_items):
        # type: (str, dict[str, int]) -> None
        for delay in SUBMIT_RESPONSE_DELAYS:
            payload = dict(researched_items or {})
            ExecLater(
                delay,
                self._send_researching_response,
                player_id,
                payload,
            )

    @EventListenerService.Listen(IndustrialResearchingSubmitRequest)
    def on_submit_researching(self, event):
        # type: (IndustrialResearchingSubmitRequest) -> None
        player_id = event.player_id
        item_id = event.item_id
        recipe = RESEARCHING_BY_ITEM_ID.get(item_id)
        if recipe is None:
            logger.error("Industrial researching submit invalid item: %s" % item_id)
            SetOnePopupNotice(player_id, "§c研究失败")
            return
        mgr = IndustrialResearchingPlayerMgr.instance()
        if mgr.has_researched(player_id, item_id):
            SetOnePopupNotice(player_id, "§e已经研究过该物品")
        elif self.consume_researching_items(player_id, recipe):
            mgr.record_researching(player_id, item_id)
            SetOnePopupNotice(player_id, "§a研究成功")
        else:
            SetOnePopupNotice(player_id, "§c研究材料不足")
            researched_items = mgr.get_player_researchings(player_id)
            self._schedule_submit_response(player_id, researched_items)
            return
        researched_items = mgr.get_player_researchings(player_id)
        self._schedule_submit_response(player_id, researched_items)

    def consume_researching_items(self, player_id, recipe):
        # type: (str, IndustrialResearchingRecipe) -> bool
        inventory_items = {
            slot: item.copy()
            for slot, item in GetAllInventoryItems(player_id, get_userdata=True).items()
        }
        new_items = {}  # type: dict[tuple[int, int], Item]
        for input_item in recipe.require_items:
            left_count = input_item.count
            for slot, item in inventory_items.items():
                if left_count <= 0:
                    break
                if not input_item.match_item_id(item.id):
                    continue
                cost_count = min(item.count, left_count)
                item.count -= cost_count
                left_count -= cost_count
                new_items[(ItemPosType.INVENTORY, slot)] = (
                    item if item.count > 0 else Item("minecraft:air", count=0)
                )
            if left_count > 0:
                return False
        SetPlayerAllItems(player_id, new_items)
        return True

    @EventListenerService.Listen(IndustrialResearchingInscribeRequest)
    def on_inscribe_template(self, event):
        # type: (IndustrialResearchingInscribeRequest) -> None
        player_id = event.player_id
        item_id = event.item_id
        if item_id not in VALID_RESEARCHING_ITEM_IDS:
            logger.error("Industrial researching inscribe invalid item: %s" % item_id)
            SetOnePopupNotice(player_id, "§c刻印不成功")
            return
        if not IndustrialResearchingPlayerMgr.instance().has_researched(
            player_id, item_id
        ):
            SetOnePopupNotice(player_id, "§c尚未研究该物品，无法刻印")
            return
        mainhand = GetPlayerMainhandItem(player_id)
        if mainhand is None or mainhand.id != INSCRIBING_TEMPLATE:
            SetOnePopupNotice(player_id, "§c主手物品不是刻印模版")
            return
        try:
            if self.inscribe_template(
                player_id, item_id, mainhand, ignore_not_empty=True
            ):
                SetOnePopupNotice(player_id, "§a刻印成功")
            else:
                SetOnePopupNotice(player_id, "§c刻印不成功")
        except Exception as err:
            logger.error(
                "Industrial researching inscribe failed: %s %s %s"
                % (player_id, item_id, err)
            )
            SetOnePopupNotice(player_id, "§c刻印不成功")

    def inscribe_template(self, player_id, item_id, mainhand, ignore_not_empty=False):
        # type: (str, str, Item, bool) -> bool
        if not ignore_not_empty and not self.is_empty_inscribing_template(mainhand):
            return False
        graph = GetTemplateGraph(item_id, GetSeed())
        user_data = mainhand.userData or {}
        user_data[K_UD_TEMPLATE_GRAPH] = [nbt.Int(i) for i in graph]
        user_data["display"] = {
            "Lore": [
                nbt.String("§r§d已刻录： " + Item(item_id).GetBasicInfo().itemName)
            ]
        }
        mainhand.userData = user_data
        SetPlayerAllItems(player_id, {(ItemPosType.CARRIED, 0): mainhand})
        return True

    def is_empty_inscribing_template(self, item):
        # type: (Item) -> bool
        if item.id != INSCRIBING_TEMPLATE or item.count != 1:
            return False
        graph_nbt = (item.userData or {}).get(K_UD_TEMPLATE_GRAPH)
        if graph_nbt is None:
            return True
        graph = nbt.NBT2Py(graph_nbt)
        return (
            isinstance(graph, list) and len(graph) == 25 and all(i == 0 for i in graph)
        )


_query_handler = IndustrialResearchingQueryHandler()
