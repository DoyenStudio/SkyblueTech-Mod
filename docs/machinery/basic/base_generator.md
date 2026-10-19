# BaseGenerator 发电机基类

发电机基类, 适合产出稳定的发电机器使用。
提供了 SetOutputPower() 方法。
如果需要对溢出发电量进行管理或者控制单次的发电量, 请使用 BasePowerProvider。

派生自 `BasePowerProvider` 基类。

基类会在构造时直接向 `self.handler` 订阅所需事件, 无需重声明空方法。

## 实例属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| output_power | int | 发电机当前的输出功率 |

## 基类方法
```python
def SetOutputPower(self, power: int) -> None
```
设置发电机输出功率。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| power | int | 新的输出功率值 |
