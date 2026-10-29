# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.define import Item

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
    cfg = CF.CreateConfigClient(LEVEL_ID).GetConfigData(CFG_KEY, False)
    cfg["favourites"] = favourite_items
    CF.CreateConfigClient(LEVEL_ID).SetConfigData(CFG_KEY, cfg, False)
    update()
    return True


def RemoveFavourite(category, item_id, display_item_id):
    # type: (str, str, str) -> bool
    favourite_items = GetFavourites()
    if not IsFavourite(category, item_id, display_item_id):
        return False
    favourite_items.remove((category, item_id, display_item_id))
    cfg = CF.CreateConfigClient(LEVEL_ID).GetConfigData(CFG_KEY, False)
    cfg["favourites"] = favourite_items
    CF.CreateConfigClient(LEVEL_ID).SetConfigData(CFG_KEY, cfg, False)
    update()
    return True


def GetFavourites():
    # type: () -> list[tuple[str, str, str]]
    global favourite_items
    if favourite_items is None:
        cfg = CF.CreateConfigClient(LEVEL_ID).GetConfigData(CFG_KEY, False)
        _favourite_items = _clean_fav_data(cfg.get("favourites", []))
        favourite_items = _favourite_items
        update()
        return _favourite_items
    else:
        return favourite_items


def IsFavourite(category, item_id, display_item_id):
    # type: (str, str, str) -> bool
    return (category, item_id, display_item_id) in GetFavourites()


def update():
    favourite_items_idauxs[:] = []
    for args in GetFavourites():
        try:
            _, _, id = args
            favourite_items_idauxs.append(Item(id).GetBasicInfo().id_aux)
        except ValueError:
            continue


def _clean_fav_data(data):
    return [
        d
        for d in data
        if len(d) == 3
        and isinstance(d[0], str)
        and isinstance(d[1], str)
        and isinstance(d[2], str)
    ]
