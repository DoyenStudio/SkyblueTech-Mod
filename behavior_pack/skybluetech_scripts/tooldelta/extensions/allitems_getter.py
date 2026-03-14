# coding=utf-8
from ..general import ClientInitCallback, ServerInitCallback
from ..events.basic import CustomC2SEvent, CustomS2CEvent
from ..events.server import DelServerPlayerEvent

allitems = set()  # type: set[str]
allitems_by_tag = {}  # type: dict[str, set[str]]
client_already_get_allitems = set()  # type: set[str]
items_getted_callback = []


class GetAllItemsRequest(CustomC2SEvent):
    name = "td:GetAllItemsRequest"

    def __init__(self, player_id=""):
        self.player_id = player_id

    def marshal(self):
        return {}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["__id__"])


class GetAllItemsResponse(CustomS2CEvent):
    name = "td:GetAllItemsResponse"

    def __init__(self, items=[], ok=True):
        # type: (list[str], bool) -> None
        self.items = items
        self.ok = ok

    def marshal(self):
        return {"i": self.items, "ok": self.ok}

    @classmethod
    def unmarshal(cls, data):
        return cls(
            items=data["i"],
            ok=data["ok"],
        )


@ServerInitCallback()
def onServerInited():
    from mod.server.extraServerApi import GetEngineCompFactory, GetLevelId

    CF = GetEngineCompFactory()
    levelId = GetLevelId()

    @DelServerPlayerEvent.Listen()
    def onDelPlayer(event):
        # type: (DelServerPlayerEvent) -> None
        client_already_get_allitems.discard(event.id)

    @GetAllItemsRequest.Listen()
    def onGetAllItems(event):
        # type: (GetAllItemsRequest) -> None
        player_id = event.player_id
        if player_id in client_already_get_allitems:
            GetAllItemsResponse(ok=False).send(player_id)
        else:
            items = CF.CreateItem(levelId).GetLoadItems()
            # if len(items) < 100:
            #     print("[ERROR] ITEMS COUNT TOO SMALL", items)
            GetAllItemsResponse(items).send(player_id)


@ClientInitCallback()
def onClientInit():
    # type: () -> None
    GetAllItemsRequest().send()

    @GetAllItemsResponse.Listen()
    def onGetResponse(event):
        # type: (GetAllItemsResponse) -> None
        global allitems
        if not event.ok:
            print("[ERROR] GetAllItemsResponse: Failed to get all items")
        else:
            print(
                "[INFO] GetAllItemsResponse: Got all items from server (%d)"
                % len(event.items)
            )
            loadAllItems(event.items)
            for cb in items_getted_callback:
                cb(allitems)

    def loadAllItems(_allitems):
        # type: (list[str]) -> None
        global allitems
        from mod.client.extraClientApi import GetEngineCompFactory, GetLevelId

        CF = GetEngineCompFactory()
        levelId = GetLevelId()
        allitems = set(_allitems)
        getTags = CF.CreateItem(levelId).GetItemTags
        for item in allitems:
            for tag in getTags(item) or []:
                allitems_by_tag.setdefault(tag, set()).add(item)


def GetAllItems():
    # type: () -> set[str]
    "ClientSide function"
    return allitems


def GetItemsByTag(tag):
    # type: (str) -> set[str]
    "ClientSide function"
    return allitems_by_tag.get(tag, set())


def AddItemGettedCallback(callback):
    "ClientSide function"
    items_getted_callback.append(callback)
