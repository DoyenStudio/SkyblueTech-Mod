# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_PROGRESS,
    K_STORE_RF,
)
from skybluetech_scripts.skybluetech.common.machinery_def.electric_crafter import (
    K_RECIPE_PREVIEW,
    STORE_RF_MAX,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import Binder, RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import CableSettingsPageIndirectional
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .machinery_workstation import EMPTY_ITEM_ID_AUX
from .utils import GetPreviewMaskColor, UpdateGenericProgressL2R, UpdatePowerBar

PROGRESS_PATH = MAIN_PATH / "progress"
POWER_PATH = MAIN_PATH / "power_bar"

CONTAINER_COLLECTION = "netease_container"
PREVIEW_SLOT_COUNT = 9


@RegistToolDeltaScreen("ElectricCrafterUI.main", is_proxy=True)
class ElectricCrafterUI(MachinePanelUIProxyEx):
    available_extra_pages = (CableSettingsPageIndirectional,)

    def OnCreate(self):
        self.power = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PROGRESS_PATH)
        self.preview_id_auxes = [None] * PREVIEW_SLOT_COUNT  # type: list[int | None]
        self._preview_raw = None  # type: str | None
        # 开界面时先取一次方块实体数据, 让首帧渲染就有正确状态
        data = GetBlockEntityData(*self.pos[1:])
        self.update_recipe_preview(
            GetValue(data["exData"], K_RECIPE_PREVIEW, None)
            if data is not None
            else None
        )

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        self.update_recipe_preview(GetValue(data, K_RECIPE_PREVIEW, None))
        store_rf = GetValue(data, K_STORE_RF, 0)
        progress = GetValue(data, K_PROGRESS, 0)
        UpdatePowerBar(self.power, store_rf, STORE_RF_MAX)
        UpdateGenericProgressL2R(self.progress, progress)

    def update_recipe_preview(self, raw):
        # type: (str | None) -> None
        if raw == self._preview_raw:
            return
        self._preview_raw = raw
        id_auxes = [None] * PREVIEW_SLOT_COUNT
        for index, entry in enumerate((raw or "").split(";")):
            if index >= PREVIEW_SLOT_COUNT or not entry:
                continue
            item_id, aux = entry.split("|")
            id_auxes[index] = Item(item_id, max(0, int(aux))).GetBasicInfo().id_aux
        self.preview_id_auxes = id_auxes

    def _preview_id_aux_at(self, index):
        # type: (int) -> int | None
        if index < 0 or index >= len(self.preview_id_auxes):
            return None
        return self.preview_id_auxes[index]

    @Binder.binding_collection(
        Binder.BF_BindColor,
        CONTAINER_COLLECTION,
        "#ElectricCrafterUI.crafting_preview_mask_color",
    )
    def get_crafting_preview_mask_color(self, index):
        # type: (int) -> tuple[float, float, float]
        return GetPreviewMaskColor(self._preview_id_aux_at(index))

    @Binder.binding_collection(
        Binder.BF_BindBool,
        CONTAINER_COLLECTION,
        "#ElectricCrafterUI.crafting_preview_item_visible",
    )
    def get_crafting_preview_item_visible(self, index):
        # type: (int) -> bool
        return self._preview_id_aux_at(index) is not None

    @Binder.binding_collection(
        Binder.BF_BindInt,
        CONTAINER_COLLECTION,
        "#ElectricCrafterUI.crafting_preview_item_id_aux",
    )
    def get_crafting_preview_item_id_aux(self, index):
        # type: (int) -> int
        id_aux = self._preview_id_aux_at(index)
        return EMPTY_ITEM_ID_AUX if id_aux is None else id_aux
