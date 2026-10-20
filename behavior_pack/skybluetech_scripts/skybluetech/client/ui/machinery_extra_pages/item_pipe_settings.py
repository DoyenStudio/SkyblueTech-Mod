# coding=utf-8
from skybluetech_scripts.skybluetech.common.misc.transmitter import TransmitterType
from skybluetech_scripts.skybluetech.common.define.id_enum import ItemPipe
from .transmitter_settings_base import TransmitterSettingsPageBase


class ItemPipeSettingsPage(TransmitterSettingsPageBase):
    transmitter_type = TransmitterType.ITEM_PIPE
    transmitter_block_ids_set = ItemPipe.all()

    @staticmethod
    def GetIconPath():
        # type: () -> str
        return "textures/icon/item_pipe_steel_icon"

    @staticmethod
    def GetControlDef():
        # type: () -> str
        return "MachinePanelExPages.item_pipe_settings"
