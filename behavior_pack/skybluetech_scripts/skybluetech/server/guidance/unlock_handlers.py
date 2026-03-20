# coding=utf-8
from mod.server.extraServerApi import GetMinecraftEnum
from ...common.define import id_enum
from .chapter_unlock_helper import RegisterCallback

ACQ_ENUM = GetMinecraftEnum().ItemAcquisitionMethod


@RegisterCallback(id_enum.Ingots.TIN)
def onGetTin(player_id, acq_method):
    # type: (str, int) -> None
    if acq_method == ACQ_ENUM.Smelted:
        pass
