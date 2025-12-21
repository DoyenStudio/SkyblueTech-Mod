# coding=utf-8
from ..internal import ClientComp, ClientLevelId, ServerComp, ServerLevelId
from ..general import ClientInitCallback
from ..events.basic import CustomC2SEvent, CustomS2CEvent
from ..events.server import DelServerPlayerEvent

allitems = set() # type: set[str]
allitems_by_tag = {} # type: dict[str, set[str]]
client_already_get_allitems = set() # type: set[str]


class GetAllItemsRequest(CustomC2SEvent):
    name = "td:GetAllItemsRequest"

    def marshal(self):
        return {}

    def unmarshal(self, data):
        self.pid = data["__id__"]


class GetAllItemsResponse(CustomS2CEvent):
    name = "td:GetAllItemsResponse"

    def __init__(self, items=[], ok=True):
        # type: (list[str], bool) -> None
        self.items = items
        self.ok = ok

    def marshal(self):
        return {"i": self.items, "ok": self.ok}

    def unmarshal(self, data):
        self.items = data["i"]
        self.ok = data["ok"]

@DelServerPlayerEvent.Listen()
def onDelPlayer(event):
    # type: (DelServerPlayerEvent) -> None
    client_already_get_allitems.discard(event.id)

@GetAllItemsRequest.Listen()
def onGetAllItems(event):
    # type: (GetAllItemsRequest) -> None
    player_id = event.pid
    if player_id in client_already_get_allitems:
        GetAllItemsResponse(ok=False).send(player_id)
    else:
        items = ServerComp.CreateItem(ServerLevelId).GetLoadItems()
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
        print("[INFO] GetAllItemsResponse: Got all items from server (%d)" % len(event.items))
        loadAllItems(event.items)

def loadAllItems(_allitems):
    # type: (list[str]) -> None
    global allitems
    allitems = set(_allitems)
    getTags = ClientComp.CreateItem(ClientLevelId).GetItemTags
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
