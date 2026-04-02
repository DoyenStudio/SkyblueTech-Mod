# coding=utf-8
from mod.client.extraClientApi import GetEngineCompFactory, GetLevelId
from skybluetech_scripts.tooldelta.api.client import (
    GetBlockEntityData,
    GetBlockNameAndAux,
    GetPlayerDimensionId,
)
from skybluetech_scripts.tooldelta.api.common import Repeat
from skybluetech_scripts.tooldelta.events.client.block import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.general import ClientInitCallback
from skybluetech_scripts.tooldelta.utils import nbt
from ...common.define.id_enum.machinery import DEEPSLATE_LAVA_VIBRATOR as MACHINE_ID
from ...common.machinery_def.deepslate_lava_vibrator import (
    K_DEEPSLATE_LAVA_PREDICTED,
    K_PREDICT_PROGRESS,
    K_STORE_RF,
    STORE_RF_MAX,
)
from ..ui.machinery.utils import FormatNum, FormatFluidVolume
from .utils.mod_block_event import asModBlockRemovedListener, asModBlockLoadedListener


CF = GetEngineCompFactory()
text_pool = {}  # type: dict[tuple[int, tuple[int, int, int]], DeepslateVibratorText]


class DeepslateVibratorText(object):
    def __init__(self, bound_x, bound_y, bound_z):
        # type: (int, int, int) -> None
        self.bound_x = bound_x
        self.bound_y = bound_y
        self.bound_z = bound_z
        self.shape = CF.CreateDrawing(GetLevelId()).AddTextShape(
            (
                self.bound_x + 0.5,
                self.bound_y + 1,
                self.bound_z + 0.5,
            ),
            "--",
        )
        self.update()

    def update(self):
        block_nbt = GetBlockEntityData(self.bound_x, self.bound_y, self.bound_z)
        if block_nbt is None:
            return
        ex_data = block_nbt.get("exData", {})
        predict_progress = nbt.GetValueWithDefault(ex_data, K_PREDICT_PROGRESS, 0)
        storage_predicted = nbt.GetValueWithDefault(
            ex_data, K_DEEPSLATE_LAVA_PREDICTED, 0
        )
        store_rf = nbt.GetValueWithDefault(ex_data, K_STORE_RF, 0)
        progress_color = (
            "c"
            if predict_progress < 0.4
            else (
                "6"
                if predict_progress < 0.6
                else ("e" if predict_progress < 0.8 else "a")
            )
        )
        self.shape.SetText(
            ("§e⚡ §c%s\n§7探测进度：      §%s%.1f%%\n§7预测储藏：   §6%s")
            % (
                "%s/%s RF"
                % (FormatNum(store_rf, "%.2f%s"), FormatNum(STORE_RF_MAX, "%.2f%s")),
                progress_color,
                predict_progress * 100,
                FormatFluidVolume(storage_predicted),
            )
        )

    def remove(self):
        self.shape.Remove()


def add_text(x, y, z):
    # type: (int, int, int) -> None
    key = (GetPlayerDimensionId(), (x, y, z))
    if key in text_pool:
        return
    text_pool[key] = DeepslateVibratorText(x, y, z)


def remove_text(x, y, z):
    # type: (int, int, int) -> None
    res = text_pool.pop((GetPlayerDimensionId(), (x, y, z)), None)
    if res is not None:
        res.remove()


@asModBlockLoadedListener(MACHINE_ID)
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    _, aux = GetBlockNameAndAux((event.posX, event.posY, event.posZ))
    if aux != 0:
        return
    add_text(event.posX, event.posY, event.posZ)


@asModBlockRemovedListener(MACHINE_ID)
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    remove_text(event.posX, event.posY, event.posZ)


@ClientInitCallback()
@Repeat(1)
def onRepeatUpdate():
    for v in text_pool.values():
        v.update()
