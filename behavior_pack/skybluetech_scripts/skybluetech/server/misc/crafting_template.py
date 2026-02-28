# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.extensions import rate_limiter
from skybluetech_scripts.tooldelta.events.server import (
    ServerItemUseOnEvent,
    PushUIRequest,
)
from skybluetech_scripts.tooldelta.api.server import (
    IsSneaking,
    GetPlayerMainhandItem,
    SpawnItemToPlayerCarried,
    GetRecipesByInput,
)
from skybluetech_scripts.tooldelta.extensions import (
    recipe_obj,
    schema,
)
from skybluetech_scripts.tooldelta.utils.nbt import Py2NBT, NBT2Py, Byte
from ...common.define.id_enum.items import CRAFTING_TEMPLATE
from ...common.events.misc.crafting_template_settings import (
    CraftingTemplateSettingsUpload,
    CraftingTemplateUpdateRecipe,
)
from ..machinery.utils.lore import SetLoreAuto


SLOTITEMS_SCHEMA = schema.ListSchema((schema.FixedTupleSchema(str, int), None))
limiter = rate_limiter.PlayerRateLimiter(limit_seconds=1)


def pack_template_slot_items(o):
    # type: (list[tuple[str, int] | None]) -> dict[str, dict]
    return {
        str(i): {"id": data[0], "aux": data[1]}
        for i, data in enumerate(o)
        if data is not None
    }


def unpack_template_slot_items(o):
    # type: (dict[str, dict]) -> list[tuple[str, int] | None]
    res = []  # type: list[tuple[str, int] | None]
    for i in range(9):
        data = o.get(str(i))
        if data is None:
            res.append(None)
        else:
            res.append((data["id"], data["aux"]))
    return res


@ServerItemUseOnEvent.ListenWithUserData()
def onServerItemUseOnEvent(event):
    # type: (ServerItemUseOnEvent) -> None
    if not limiter.record(event.entityId):
        return

    if event.item.id != CRAFTING_TEMPLATE or not IsSneaking(event.entityId):
        return
    uds = event.item.userData or {}

    PushUIRequest(
        "CraftingTemplateSettingsUI.main",
        params={
            "template_slot_items": unpack_template_slot_items(
                NBT2Py(uds.get("st:template_slot_items", {}))  # pyright: ignore[reportArgumentType]
            ),
            "template_recipe": NBT2Py(uds.get("st:template_recipe")) or None,
        },
    ).send(event.entityId)


@CraftingTemplateSettingsUpload.Listen()
def onCraftingTemplateSettingsUpload(event):
    # type: (CraftingTemplateSettingsUpload) -> None
    mh = GetPlayerMainhandItem(event.player_id)
    if mh is None or mh.id != CRAFTING_TEMPLATE:
        return
    if not SLOTITEMS_SCHEMA.check(event.template_slotitems):
        print(
            "[Warning] CraftingTemplateSettingsUpload: recv invalid slotitems_nbtdata"
        )
        return
    try:
        recipe = get_recipe(event.template_slotitems)
        items = {}  # type: dict[str, int]
        for i in event.template_slotitems:
            if i is None:
                continue
            items[i[0]] = items.get(i[0], 0) + 1
        res_items = {}  # type: dict[str, int]
        if recipe is not None:
            for res in recipe.result:
                res_items[res.item_id] = res_items.get(res.item_id, 0) + res.count
    except Exception:
        print("[Warning] CraftingTemplateSettingsUpload: recv Invalid data")
        return
    if mh.userData is None:
        mh.userData = {}
    mh.userData["st:template_slot_items"] = Py2NBT(
        pack_template_slot_items(event.template_slotitems)
    )
    if recipe is None:
        mh.userData["st:template_recipe"] = Byte(False)
    else:
        mh.userData["st:template_recipe"] = Py2NBT(recipe.data)
    if recipe is None:
        SetLoreAuto(mh.userData, "recipe_data_disp", "§r§7[§6!§7] §6未记录合成配方")
    else:
        desc = (
            "§r§7[§a√§7] §a配方已设定"
            + "\n§7 - 原料： §f"
            + "， ".join(
                Item(k).GetBasicInfo().itemName + "§r§fx" + str(v)
                for k, v in items.items()
            )
            + "\n§7 - 合成： §f"
            + "， ".join(
                Item(k).GetBasicInfo().itemName + "§r§fx" + str(v)
                for k, v in res_items.items()
            )
        )
        SetLoreAuto(mh.userData, "recipe_data_disp", desc)
    SpawnItemToPlayerCarried(event.player_id, mh)
    CraftingTemplateUpdateRecipe(recipe.data if recipe is not None else None).send(
        event.player_id
    )


def get_recipe(
    template_slot_items,  # type: list[tuple[str, int] | None]
):
    slotitems = {}  # type: dict[tuple[str, int], int]
    for it in template_slot_items:
        if it is None:
            continue
        if it in slotitems:
            slotitems[it] += 1
        else:
            slotitems[it] = 1
    recipes = set()  # type: set[recipe_obj.CraftingRecipeRes | recipe_obj.UnorderedCraftingRecipeRes]
    for item_id, aux in slotitems:
        if not recipes:
            recipes = {
                recipe_obj.GetCraftingRecipe(rcp)
                for rcp in GetRecipesByInput(item_id, "crafting_table", aux)
            }
        else:
            recipes &= {
                recipe_obj.GetCraftingRecipe(rcp)
                for rcp in GetRecipesByInput(item_id, "crafting_table", aux)
            }
    for recipe in recipes:
        if crafting_slots_completely_matched(template_slot_items, recipe):
            return recipe
    return None


def crafting_slots_completely_matched(template_slots, recipe):
    # type: (list[tuple[str, int] | None], recipe_obj.CraftingRecipeRes | recipe_obj.UnorderedCraftingRecipeRes) -> bool
    if isinstance(recipe, recipe_obj.CraftingRecipeRes):
        pats = recipe.pattern[:]  # 3x3
        for i, ln in enumerate(pats):
            if len(ln) < 3:
                ln += " " * (3 - len(ln))
                pats[i] = ln
        if len(pats) < 3:
            pats += [" " * 3] * (3 - len(pats))
        while pats[0][0] == pats[1][0] == pats[2][0] == " ":
            pats[0] = pats[0][1:] + " "
            pats[1] = pats[1][1:] + " "
            pats[2] = pats[2][1:] + " "
        while pats[0] == "   ":
            pats = pats[1:] + ["   "]
        ts = template_slots[:]  # 3x3
        while ts[0] is ts[3] is ts[6] is None:
            ts[0:3] = ts[1:3] + [None]
            ts[3:6] = ts[4:6] + [None]
            ts[6:9] = ts[7:9] + [None]
        while ts[0] is ts[1] is ts[2] is None:
            ts = ts[3:] + [None] * 3
        for row, pat_ln in enumerate(pats):
            for col, pat in enumerate(pat_ln):
                i = row * 3 + col
                item_and_aux = ts[i]
                if (
                    pat == " "
                    and item_and_aux is not None
                    or item_and_aux is None
                    and pat != " "
                ):
                    return False
                if item_and_aux is None:
                    continue
                rcp_input = recipe.pattern_key[pat]
                item_id, aux = item_and_aux
                if item_id not in rcp_input.item_ids or rcp_input.aux_value != aux:
                    return False
        return True
    else:
        item_counts = {}  # type: dict[tuple[str, int], int]
        for item_and_aux in template_slots:
            if item_and_aux is None:
                continue
            if item_and_aux in item_counts:
                item_counts[item_and_aux] += 1
            else:
                item_counts[item_and_aux] = 1
        inputs_single_item = [i for i in recipe.inputs if len(i.item_ids) == 1]
        input_multiple_item = [i for i in recipe.inputs if len(i.item_ids) > 1]
        for s_item_input in inputs_single_item:
            key = (s_item_input.item_ids[0], s_item_input.aux_value)
            have_count = item_counts.get(key, 0)
            if have_count < s_item_input.count:
                return False
            item_counts[key] = have_count - s_item_input.count
        for m_item_input in input_multiple_item:
            left_count = m_item_input.count
            for item_id in m_item_input.item_ids:
                key = (item_id, m_item_input.aux_value)
                if key in item_counts:
                    have_count = item_counts[key]
                    if have_count >= left_count:
                        item_counts[key] = have_count - left_count
                        left_count = 0
                        break
                    else:
                        left_count -= have_count
                        item_counts[key] = 0
            if left_count > 0:
                return False
        return all(count == 0 for count in item_counts.values())
