# coding=utf-8
from skybluetech_scripts.tooldelta.utils import nbt

def SetLoreAtPos(userdata, pos, lore, lore_name=None):
    # type: (dict, int, str, str | None) -> None
    userdata["display"]["Lore"][pos]["__value__"] = lore
    if lore_name is not None:
        userdata.setdefault("lore_pos", {})[lore_name] = nbt.Int(pos)

def GetLorePos(userdata, name, default=0):
    # type: (dict, str, int) -> int
    return nbt.GetValueWithDefault(userdata.get("lore_pos", {}), name, default)

def SetLoreAuto(userdata, lore_name, lore):
    # type: (dict, str, str) -> None
    lore_pos = GetLorePos(userdata, lore_name, -1)
    lores = userdata.setdefault("display", {}).setdefault("Lore", [])
    if lore_pos == -1:
        lore_pos = len(lores) - 1
        lores.append(nbt.String(lore))
        userdata.setdefault("lore_pos", {})[lore_name] = nbt.Int(lore_pos)
    else:
        lores[lore_pos] = nbt.String(lore)

    