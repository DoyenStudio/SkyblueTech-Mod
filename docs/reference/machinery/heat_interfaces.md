# 热力接口

[HeatCtrl](heat_ctrl.md) · [基类索引](README.md)

服务端入口为 `skybluetech_scripts.skybluetech.server.machinery.interfaces` 中的
`HeatInputInterface` 和 `HeatOutputInterface`。二者继承 `BaseHeatInterface(BaseInterface)`，
属于非能源机器，不继承 `HeatCtrl`，也不创建独立热值、热容、产热或环境换热状态。

## 绑定与注册

控制器必须继承 `HeatCtrl`。结构形成后，对每个接口调用 `io.SetMachineRef(controller)`；
结构失效或控制器卸载时调用 `io.UnsetMachineRef()`。控制器无需与接口相邻。
类型错误会抛出 `TypeError`，并保留原绑定。绑定使用弱引用，不写入 NBT；重新加载后，
结构逻辑必须再次绑定。接口自身卸载会解绑。

`getMachineRef()` 仅返回仍是机器池当前实例的控制器。控制器已经卸载或同位置加载了
新实例时，即使旧对象仍有引用，也不会继续传热；必须显式绑定新控制器。

按既有接口模式注册具体方块：

```python
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine
from skybluetech_scripts.skybluetech.server.machinery.interfaces import HeatInputInterface

# IO_HEAT 为具体多方块结构已有的受热口 ID。
HeatInputInterface.AddExtraMachineId(IO_HEAT)
RegisterMachine(HeatInputInterface)
```

接口方块需要 `netease:block_entity`、`netease:listen_block_remove: {"value": true}`
和 `tag:piston_denier`。受热口无需 tick；供热口必须使用
`netease:block_entity: {"tick": true}`。

卤水池的 `BrineEvaporationPond.IO_HEAT` 已注册为受热口。`BrineEvaporationPondController`
在结构形成且三个接口均加载后绑定控制器；结构失效或控制器卸载时解绑。

## 传热行为与 API

| 对象 | GetHeatInputTarget() | 调度 |
| --- | --- | --- |
| 普通 HeatCtrl | 自身 | spread_heat=True 时按原热周期向邻居传热 |
| HeatInputInterface | 有效控制器，未绑定或失效时为 None | 被动接收，不主动输出 |
| HeatOutputInterface | None，拒绝输入 | 每 WORK_INTERVAL=5 tick 查询六面邻居并从控制器输出 |

`HeatCtrl.TransferHeatTo(target, dt=None) -> float` 接受普通热机或热力接口，解析接收热体，
核对源机器、接触方块和接收热体仍是当前加载的实例，再调用 `Thermal.ConductHeat`。
默认 `dt=self.WORK_INTERVAL`；供热口显式传入自身周期，因此控制器的周期不会改变接口流速。
返回实际转移的 RF 热量。无效目标、供热口、同一热体、相同温度或温差反向均返回 `0.0`。

传热使用控制器实际的 `heat_value` 和 `heat_capacity`，沿用 Thermal 默认导热系数与
平衡温度限制。每个接触面独立结算，并立即写回两侧热值；下一个邻居使用更新后的热量。
热量只按「外部→受热口→控制器→供热口→外部」方向流动，不做功、不泵热。

供热口独立调度，不要求控制器开启 `spread_heat`；普通停机不阻止被动传热。
结构失效时需要解绑，不能只设置停机标志。同一控制器的接口互接不传热；不同控制器的
供热口与受热口相邻时可以单向换热。多接口可以增加换热能力，默认六面均可连接。

热量仍通过控制器 `heat_value` setter 按现有格式保存；接口没有额外热量存档。
HeatCtrl 的邻居缓存会响应既有缓存失效事件，清除已移除邻居，并识别新加载的热力接口。

## 游戏内验收

本地不运行或编译项目 Python。以下项目需在游戏内验证；已提供卤水池控制器和受热口，
供热口行为需使用另行注册的测试方块验证。

- 关闭双方环境换热并设 heat_power=0：高温外部热机向受热口传热，外部失去的热量等于控制器增加的热量；反向温差和等温均不传热。
- 控制器 heat_capacity 与外部热机不同：按温度判断方向，热量守恒且不越过平衡温度。
- 供热口每 5 tick 输出；控制器 spread_heat=False 或普通停机时仍能输出。更热的外部热机不能向供热口灌热。
- 多接口、多邻居逐个结算；同控制器接口互接不改变热量，不同控制器之间可经供热口与受热口换热。
- 未绑定、显式解绑、接口移除、控制器卸载或同位置替换后停止传热；重新加载并绑定后恢复。先放热机或先放接口都能正确刷新邻居。
- 将非 HeatCtrl 机器传给 SetMachineRef：抛出 TypeError 且原绑定保留。
- 保存并重新进入，检查控制器热量在原生浮点精度内恢复；确认接口未写入 heat_value。绑定由结构逻辑恢复，不能只用缓存读回来判定持久化成功。
