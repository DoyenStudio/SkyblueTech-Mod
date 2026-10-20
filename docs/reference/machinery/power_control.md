# PowerControl

[基类索引](README.md) · [生命周期](../lifecycle.md)

额定功率与缺电停机控制，不负责处理配方。

直接继承：`BaseMachine`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.PowerControl`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

running_power=1000；power_pos_rate=1.0、power_neg_rate=1.0 供升级计算。

SetPower(power)、PowerEnough()、ReducePower(rf=None)、AddPower(rf)。

## 事件与组合

本类不新增订阅；AddPower/PowerEnough 更新缺电标志。

PowerEnough 会修改停机标志；自定义耗电工作应先检查再扣电。与速度控制组合可直接用 SPControl。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[power_control.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/power_control.py)。
