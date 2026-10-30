# BaseMachine

[基类索引](README.md) · [生命周期](../lifecycle.md)

机器坐标、原生方块数据、能量缓存和停机标志的根组件。

直接继承：`object`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.BaseMachine`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

block_name：唯一方块 ID；store_rf_max=10000；energy_io_mode=(0,0,0,0,0,0)，0 输入、1 输出、其他关闭；is_non_energy_machine=False。

AddPower(rf) 返回 (是否变化, 溢出量)；TakeoutPower(rf) 返回实际取出量；GivebackPower(rf) 返还；SetDeactiveFlag/UnsetDeactiveFlag/HasDeactiveFlag 管理停机位；UpdateDeactiveFlag(flag, on) 按条件设置或取消，标志已是目标状态时不触发回调也不写方块数据，适合在每 tick 的工作逻辑里调用；IsActive() 判断所有标志均清除。

## 事件与组合

构造 handler；停机方法分发状态事件，本类不订阅 tick。OnPrePlaced 是放置前类方法钩子。

普通功能组件继承本类；不直接覆写 deactive_flags 后忘记通知；保存整数不得为 long。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[base_machine.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/base_machine.py)。
