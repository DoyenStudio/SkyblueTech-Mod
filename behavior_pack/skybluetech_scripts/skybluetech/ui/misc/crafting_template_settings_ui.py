# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import (
    ToolDeltaScreen,
    RegistToolDeltaScreen,
    Binder,
    UBaseCtrl,
    SCREEN_BASE_PATH,
)
from skybluetech_scripts.tooldelta.api.client import (
    GetRecipesByInput,
    GetLocalPlayerHotbarAndInvItems,
    GetItemTags,
    GetItemHoverName,
)
from skybluetech_scripts.tooldelta.extensions.recipe_obj import (
    CraftingRecipeRes,
    UnorderedCraftingRecipeRes,
    GetCraftingRecipe,
)
from skybluetech_scripts.tooldelta.events.client import OnKeyPressInGame
from ...define.events.misc.crafting_template_settings import (
    CraftingTemplateSettingsUpload,
    CraftingTemplateUpdateRecipe,
)

AIR_SLOT = 35
CLOSE_BTN_NODE = SCREEN_BASE_PATH / "close_btn"
GRID_NODE = SCREEN_BASE_PATH / "grid"
OUT_ITEM_NODE = SCREEN_BASE_PATH / "out_item"
LABEL_NODE = SCREEN_BASE_PATH / "databoard/label"


@RegistToolDeltaScreen("CraftingTemplateSettingsUI.main")
class CraftingTemplateSettingsUI(ToolDeltaScreen):
    name = "e_monitor"

    def __init__(self, screen_name, screen_instance, params):
        ToolDeltaScreen.__init__(self, screen_name, screen_instance, params)
        self.template_slot_items = params["template_slot_items"]  # type: list[tuple[str, int] | None]
        self.template_recipe = params["template_recipe"]  # type: dict | None

    def OnCreate(self):
        self.last_selected_slot = None
        self.item_selector_window = None
        self.close_btn = self.GetElement(CLOSE_BTN_NODE).asButton().SetCallback(lambda _: self.RemoveUI())
        self.grid = self.GetElement(GRID_NODE).asGrid()
        self.out_item = self.GetElement(OUT_ITEM_NODE)
        self.label = self.GetElement(LABEL_NODE).asLabel()
        self.grid.ExecuteAfterUpdate(self.update_template_slots)
        self.update_crafting_recipe()

    def OnDestroy(self):
        self.close_item_selector()

    def create_item_selector(self, x, y):
        # type: (float, float) -> UBaseCtrl
        if self.item_selector_window is not None:
            return self.item_selector_window
        window = self.AddElement(
            "SkybluePanelLib.item_selector_window", "item_selector_window"
        )
        window.SetLayer(90)
        stack = window["stack"]
        stack_sizex, _ = stack.GetSize()
        window.SetPos((x - stack_sizex / 2, y))
        self.item_selector_window = window
        self.item_selector_window["close_btn"].asButton().SetCallback(
            lambda _: self.close_item_selector()
        )
        _i0 = 0
        items = GetLocalPlayerHotbarAndInvItems()
        item_ids = set()  # type: set[str]
        for i in range(36):
            item = items[i] if i != AIR_SLOT else Item("minecraft:barrier")
            if item is None or item.id in item_ids:
                continue
            e = stack.AddElement(
                "SkybluePanelLib.item_selector_rect", "selector%d" % _i0
            )
            xsize, ysize = e.GetSize()
            e.SetPos((_i0 * xsize % stack_sizex, _i0 // (stack_sizex // xsize) * ysize))
            e["item_renderer"].asItemRenderer().SetUiItem(item)
            e["btn"].SetPropertyBag({"#index": i})
            item_ids.add(item.id)
            _i0 += 1
        return window

    def close_item_selector(self):
        if self.item_selector_window is not None:
            self.item_selector_window.Remove()
            self.item_selector_window = None

    def update_template_slots(self, slot=-1):
        if slot == -1:
            for i, it in enumerate(self.template_slot_items):
                if it is None:
                    self.grid.GetGridItem(i % 3, i // 3)["item_renderer"].SetVisible(False)
                else:
                    item_id, aux = it
                    ir = self.grid.GetGridItem(i % 3, i // 3)["item_renderer"].asItemRenderer()
                    ir.SetVisible(True)
                    ir.SetUiItem(Item(item_id, aux))
        else:
            it = self.template_slot_items[slot]
            ir = self.grid.GetGridItem(slot % 3, slot // 3)["item_renderer"].asItemRenderer()
            if it is None:
                ir.SetVisible(False)
            else:
                item_id, aux = it
                ir.SetVisible(True)
                ir.SetUiItem(Item(item_id, aux))

    def update_crafting_recipe(self):
        # type: () -> None
        rcp = GetCraftingRecipe(self.template_recipe) if self.template_recipe else None
        ir = self.out_item["item_renderer"].asItemRenderer()
        if rcp is not None:
            ir.SetVisible(True)
            ir.SetUiItem(Item(rcp.result[0].item_id, rcp.result[0].aux_value))
            self.label.SetText(
                (
                    "， ".join(
                        (
                            GetItemHoverName(input.item_ids[0])
                            + "§r§fx"
                            + str(input.count)
                        )
                        for input in (
                            rcp.inputs
                            if isinstance(rcp, UnorderedCraftingRecipeRes)
                            else rcp.get_items_count()
                        )
                    )
                )
                + " -> "
                + "， ".join(
                    (
                        GetItemHoverName(output.item_id)
                        + "§r§fx"
                        + str(output.count)
                    )
                    for output in rcp.result
                )
            )
        else:
            ir.SetUiItem(Item("minecraft:barrier"))
            ir.SetVisible(False)
            self.label.SetText("无配方")

    @ToolDeltaScreen.Listen(OnKeyPressInGame)
    def onKeyPress(self, event):
        # type: (OnKeyPressInGame) -> None
        if event.key == event.KeyBoardType.KEY_ESCAPE and event.isDown:
            self.RemoveUI()

    @ToolDeltaScreen.Listen(CraftingTemplateUpdateRecipe)
    def onRecvRecipe(self, event):
        # type: (CraftingTemplateUpdateRecipe) -> None
        self.template_recipe = event.recipe_data
        self.update_crafting_recipe()

    @Binder.binding(Binder.BF_ButtonClickUp, "#CraftingTemplateSettingsUI.slot_selected")
    def onSelectSlot(self, params):
        idx = params["#collection_index"]
        self.last_selected_slot = idx
        button_path = params["ButtonPath"][len("main/") :]
        x, y = self.GetElement(button_path).GetRootPos()
        self.create_item_selector(x, y)

    @Binder.binding(Binder.BF_ButtonClickUp, "#SkybluePanelLib.item_selector_rect.item_selected")
    def onSelectItem(self, params):
        button_path = params["ButtonPath"][len("main/") :]
        idx = self.GetElement(button_path).GetPropertyBag().get("#index", 0)  # type: int
        if idx == -1:
            return
        elif self.last_selected_slot is None:
            print(
                "[Error] CraftingTemplateSettingsUI: onItemSelected: last_selected_slot empty"
            )
            return
        selected_item = GetLocalPlayerHotbarAndInvItems()[idx]
        if idx == AIR_SLOT:
            self.template_slot_items[self.last_selected_slot] = None
        elif selected_item is None:
            return
        else:
            self.template_slot_items[self.last_selected_slot] = (
                selected_item.id,
                selected_item.newAuxValue,
            )
        self.update_template_slots(self.last_selected_slot)
        CraftingTemplateSettingsUpload(
            self.template_slot_items,
        ).send()
        self.close_item_selector()


