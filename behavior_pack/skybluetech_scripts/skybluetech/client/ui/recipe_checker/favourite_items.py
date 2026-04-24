# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.client import GetConfigData, SetConfigData

CFG_KEY = "skybluetech:favourite_items"
favourite_items = None  # type: list[tuple[str, str, str]] | None
favourite_items_idauxs = []  # type: list[int]

# TODO: 不支持 item_aux


def AddFavourite(category, item_id, display_item_id):
    # type: (str, str, str) -> bool
    favourite_items = GetFavourites()
    if item_id in favourite_items:
        return False
    favourite_items.append((category, item_id, display_item_id))
    cfg = GetConfigData(CFG_KEY)
    cfg["favourites"] = favourite_items
    SetConfigData(CFG_KEY, cfg)
    update()
    return True


def RemoveFavourite(category, item_id, display_item_id):
    # type: (str, str, str) -> bool
    favourite_items = GetFavourites()
    if not IsFavourite(category, item_id, display_item_id):
        return False
    favourite_items.remove((category, item_id, display_item_id))
    cfg = GetConfigData(CFG_KEY)
    cfg["favourites"] = favourite_items
    SetConfigData(CFG_KEY, cfg)
    update()
    return True


def GetFavourites():
    # type: () -> list[tuple[str, str, str]]
    global favourite_items
    if favourite_items is None:
        cfg = GetConfigData(CFG_KEY)
        _favourite_items = cfg.get("favourites", [])
        favourite_items = _favourite_items
        update()
        return _favourite_items
    else:
        return favourite_items


def IsFavourite(category, item_id, display_item_id):
    # type: (str, str, str) -> bool
    return (category, item_id, display_item_id) in GetFavourites()


def update():
    global favourite_items_idauxs
    favourite_items_idauxs[:] = [
        Item(id).GetBasicInfo().id_aux for _, _, id in GetFavourites()
    ]
