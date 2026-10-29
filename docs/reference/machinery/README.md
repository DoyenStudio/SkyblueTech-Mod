# 机器基类参考

[返回手册](../../README.md) · [生命周期与 MRO](../lifecycle.md)

正式门面 `server.export.machinery` 导出下列 18 个类。属性、方法与默认值以当前源码为准，示例遵守 Python 2.7.13。优先选择功能已经齐全的 Processor 或 GeneratorProcessor；需要特殊流程时再组合组件。

| 类 | 直接父类 | 用途 |
| --- | --- | --- |
| [BaseMachine](base_machine.md) | object | 机器坐标、原生方块数据、能量缓存和停机标志的根组件。 |
| [BaseClicker](base_clicker.md) | BaseMachine | 非自定义容器的可点击机器，统一限流并拦截点击放置。 |
| [BasePowerProvider](base_power_provider.md) | BaseMachine | 一次性产生电力，管理直接供给邻接机器和自身缓冲。 |
| [BaseGenerator](base_generator.md) | BasePowerProvider | 持续发电的组件，每 tick 在活动状态按当前输出功率发电。 |
| [BaseSpeedControl](base_speed_control.md) | BaseMachine | 独立的进度与速度控制，不自动耗电或产物。 |
| [PowerControl](power_control.md) | BaseMachine | 额定功率与缺电停机控制，不负责处理配方。 |
| [SPControl](sp_control.md) | PowerControl, BaseSpeedControl | 把耗电检查与进度推进合并。 |
| [ItemContainer](item_container.md) | BaseMachine | 访问自定义物品容器及输入输出槽，参与玩家放入校验。 |
| [GUIControl](gui_ctrl.md) | BaseMachine | 机器点击打开 UI、维护 S2CSync 与卸载清理。 |
| [WorkRenderer](work_renderer.md) | BaseMachine | 将停机状态映射到方块工作外观。 |
| [UpgradeControl](upgrade_control.md) | SPControl, ItemContainer | 处理升级槽、速度和耗能倍率，并为产物输出接入自动输出功能。 |
| [ProcessorBase](processor_base.md) | WorkRenderer, UpgradeControl, GUIControl | 共享的配方匹配、输出检查和 GUI 进度基础，用于实现不同处理协议。 |
| [Processor](processor.md) | ProcessorBase | 消耗电力和输入，按时长产出物品/流体的标准机器。 |
| [GeneratorProcessor](generator_processor.md) | ProcessorBase, BaseGenerator | 按燃料配方持续产电，维护已启动配方及进度。 |
| [OperationListener](operation_listener.md) | BaseMachine | 将自定义客户端操作事件路由到对应机器实例。 |
| [MultiFluidContainer](multi_fluid_container.md) | BaseMachine | 按连续编号维护一个或多个流体槽，负责输入过滤与变化通知。 |
| [HeatCtrl](heat_ctrl.md) | BaseMachine | 热量产生、吸收、环境换热及可选邻接传热。 |
| [MultiBlockStructure](multi_block_structure.md) | BaseMachine | 检测主机周围结构、缺块提示、功能接口枚举与生命周期管理。 |

耗能配方链：`Processor → ProcessorBase → WorkRenderer + UpgradeControl + GUIControl`；升级链：`UpgradeControl → SPControl + ItemContainer`，`SPControl → PowerControl + BaseSpeedControl`。发电配方链：`GeneratorProcessor → ProcessorBase + BaseGenerator → BasePowerProvider`。所有路径最终汇入同一个 BaseMachine。

迁移注意：不存在 ProcessBase；现用 handler 订阅代替空 OnXXX 方法；发电功率是 SetOutputPower；允许升级项是 allow_upgraders；新机器的状态采用原生 NBT 兼容值。

多方块专用接口：[热力接口（受热口 / 供热口）](heat_interfaces.md)，从 `server.machinery.interfaces` 导入。
