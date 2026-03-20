# coding=utf-8
import time
from skybluetech_scripts.tooldelta.api.server import (
    GetExtraData,
    SetExtraData,
)

if 0:
    from typing import Callable

K_RUNNING_QUESTS = "st:running_quests"
K_FINISHED_QUESTS = "st:finished_quests"


class Quest(object):
    def __init__(self, id, title, description):
        # type: (str, str, str) -> None
        self.id = id
        self.title = title
        self.description = description
        self.next_quests = []  # type: list[Quest]
        self.prev_quests = []  # type: list[Quest]

    def SetPrevQuests(
        self,
        quests_getter,  # type: Callable[[], list[Quest]]
    ):
        self.prev_quests = quests_getter()
        return self

    def SetNextQuests(
        self,
        quests_getter,  # type: Callable[[], list[Quest]]
    ):
        self.next_quests = quests_getter()
        return self

    def add_to_player(self, player_id):
        # type: (str) -> None
        prev_data = GetExtraData(player_id, K_RUNNING_QUESTS, {})
        prev_data[self.id] = {"_ctime": int(time.time())}
        SetExtraData(player_id, K_RUNNING_QUESTS, prev_data, auto_save=True)

    def get_data(self, player_id):
        # type: (str) -> dict
        return ReadQuestData(player_id, self.id)

    def save_data(self, player_id, data):
        # type: (str, dict) -> None
        SaveQuestData(player_id, self.id, data)

    def is_finished(self, player_id):
        # type: (str) -> bool
        return QuestIsFinished(player_id, self.id)

    def get_unfinished_prev_quests(self, player_id):
        # type: (str) -> list[Quest]
        return [quest for quest in self.prev_quests if not quest.is_finished(player_id)]

    def get_super_unfinished_prev_quests(self, player_id):
        # type: (str) -> set[Quest]
        quests_running = GetRunningQuests(player_id)

        def get_roots(quest):
            # type: (Quest) -> set[Quest]
            if quest.id in quests_running:
                return {quest}
            prevs = quest.prev_quests
            return {_q for q in prevs for _q in get_roots(q)}

        return get_roots(self)

    def can_finish(self, player_id):
        return False

    def finish(self, player_id):
        # type: (str) -> None
        SetQuestFinished(player_id, self.id)
        for quest in self.next_quests:
            quest.add_to_player(player_id)

    def try_finish(self, player_id):
        # type: (str) -> bool
        if self.get_unfinished_prev_quests(player_id):
            return False
        elif self.can_finish(player_id):
            self.finish(player_id)
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class ItemQuest(Quest):
    def __init__(self, id, title, description, require_items):
        # type: (str, str, str, dict[str, int]) -> None
        super(ItemQuest, self).__init__(id, title, description)
        self.id = id
        self.require_items = require_items

    def player_get_item(self, player_id, item_id, count=1):
        # type: (str, str, int) -> None
        data = self.get_data(player_id)
        items = data.get("items", {})
        items[item_id] = items.get(item_id, 0) + count
        self.save_data(player_id, {"items": items})
        self.try_finish(player_id)

    def can_finish(self, player_id):
        # type: (str) -> bool
        data = self.get_data(player_id)
        items = data.get("items", {})
        return all(
            items.get(item_id, 0) >= count
            for item_id, count in self.require_items.items()
        )


def GetRunningQuests(player_id):
    # type: (str) -> set[str]
    return set(GetExtraData(player_id, K_RUNNING_QUESTS, {}))


def QuestIsFinished(player_id, quest_id):
    # type: (str, str) -> bool
    return quest_id in GetExtraData(player_id, K_FINISHED_QUESTS, {})


def SetQuestFinished(player_id, quest_id):
    # type: (str, str) -> None
    prev_data = GetExtraData(player_id, K_FINISHED_QUESTS, {})
    prev_data[quest_id] = int(time.time())
    SetExtraData(player_id, K_FINISHED_QUESTS, prev_data, auto_save=True)


def ReadQuestData(player_id, quest_id):
    # type: (str, str) -> dict
    return GetExtraData(player_id, K_RUNNING_QUESTS, {}).get(quest_id, {})


def SaveQuestData(player_id, quest_id, data):
    # type: (str, str, dict) -> None
    prev_data = GetExtraData(player_id, K_RUNNING_QUESTS, {})
    prev_data[quest_id] = data
    SetExtraData(player_id, K_RUNNING_QUESTS, prev_data, auto_save=True)
