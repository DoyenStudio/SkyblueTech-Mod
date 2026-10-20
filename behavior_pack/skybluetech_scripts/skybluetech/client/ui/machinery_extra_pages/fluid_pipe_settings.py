# coding=utf-8
from skybluetech_scripts.skybluetech.common.misc.transmitter import TransmitterType
from skybluetech_scripts.skybluetech.common.define.id_enum import FluidPipe
from .transmitter_settings_base import TransmitterSettingsPageBase


class FluidPipeSettingsPage(TransmitterSettingsPageBase):
    transmitter_type = TransmitterType.FLUID_PIPE
    transmitter_block_ids_set = FluidPipe.all()

    @staticmethod
    def GetIconPath():
        # type: () -> str
        return "textures/icon/fluid_pipe_bronze_icon"

    @staticmethod
    def GetControlDef():
        # type: () -> str
        return "MachinePanelExPages.fluid_pipe_settings"
