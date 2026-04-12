# coding=utf-8

from ..server.machinery.basic import (
    BaseClicker,
    BaseGenerator,
    BaseMachine,
    Processor,
    BaseSpeedControl,
    FluidContainer,
    GUIControl,
    HeatCtrl,
    ItemContainer,
    Processor,
    MultiBlockStructure,
    MultiFluidContainer,
    PowerControl,
    SPControl,
    UpgradeControl,
    WorkRenderer,
    RegisterMachine,
)


class MachineryDefine:
    @staticmethod
    def GetBascClickerCls():
        return BaseClicker

    @staticmethod
    def GetBaseGeneratorCls():
        return BaseGenerator

    @staticmethod
    def GetBaseMachineCls():
        return BaseMachine

    @staticmethod
    def GetProcessorCls():
        return Processor

    @staticmethod
    def GetBaseSpeedControlCls():
        return BaseSpeedControl

    @staticmethod
    def GetFluidContainerCls():
        return FluidContainer

    @staticmethod
    def GetGUIControlCls():
        return GUIControl

    @staticmethod
    def GetHeatCtrlCls():
        return HeatCtrl

    @staticmethod
    def GetItemContainerCls():
        return ItemContainer

    @staticmethod
    def GetMultiBlockStructureCls():
        return MultiBlockStructure

    @staticmethod
    def GetMultiFluidContainerCls():
        return MultiFluidContainer

    @staticmethod
    def GetPowerControlCls():
        return PowerControl

    @staticmethod
    def GetSPControlCls():
        return SPControl

    @staticmethod
    def GetUpgradeControlCls():
        return UpgradeControl

    @staticmethod
    def GetWorkRendererCls():
        return WorkRenderer

    RegisterMachine = staticmethod(RegisterMachine)
