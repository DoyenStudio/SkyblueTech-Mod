# 管线等级注册

[返回手册](../README.md) · [操作教程](../tutorials/04-transmitter-grades.md)

```python
RegisterItemPipe(block_id, transfer_speed, replace=False)
RegisterFluidPipe(block_id, transfer_speed, capacity,
                  can_transmit_fluid=None, replace=False)
RegisterWire(block_id, transfer_speed, replace=False)
```

只在服务端调用 `server.export.transmitters`。资源包和行为包必须预先定义该方块、标签及状态；注册函数不动态创建方块。

| 字段 | 契约 |
| --- | --- |
| `block_id` | 不含空白的 `namespace:name` 字符串 |
| `transfer_speed` | 物品数/t 或 RF/t 为正整数；mB/t 可为正整数或浮点数；必须有限，拒绝 bool |
| `capacity` | 正的有限数值，单位 mB，表示整个流体网络容量 |
| `can_transmit_fluid` | `None` 或接受 `fluid_id`、返回 bool 的函数；None 不增加过滤条件 |
| `replace` | bool；不同配置覆盖必须显式 True，包括覆盖内置管线 |

返回 `None`。类型错误抛 `TypeError`，无效数值、ID 或配置冲突抛 `ValueError`。相同配置重复注册无副作用；函数过滤器按同一函数对象判定相同，重复创建 lambda 不属于相同配置。一个 ID 只能属于一种内置管线类别。

内置网络每 5 tick 调用运输回调，周期预算为 `transfer_speed * 5`。这不表示任意条件下都能达到标称流量：源供给、接收容量和流体缓冲均可能成为瓶颈。1000 mB/t 的流体管网宜至少提供 5000 mB 周期缓冲。

注册时将流体参数归一化为浮点数、物品和能量参数归一化为整数。Python 2 的大周期预算可以在内存中使用 long，实际搬运的堆叠数和回落到 int 范围的能量提取预算会转回 int；机器自身持久化的能量仍必须符合[原生存档约定](persistence.md)。

## 更新语义

完整校验通过后更新映射及该 ID 所有已加载、启用网络的参数。网络对象、接入点、缓冲流体不重建；新网络读取新参数。无注销接口，不支持一个方块 ID 从流体管道变成电缆。

缩容时已有液体保留，直到输出后低于容量才重新抽取；过滤条件收紧仅影响后续抽取，旧流体可继续输出。配置不会写入存档，下次进入世界应由附属重新注册；未加载区块中的旧流体也应按保留存量的规则恢复。

注册新 ID 后服务端广播类别/ID 完整快照，客户端 UI 就绪时主动请求同一快照，因此支持晚加入。客户端更新枚举的原集合，已有设置页立即能识别新 ID；扳手每次交互读取当前集合，不再缓存旧并集。只同步识别信息，不同步数值和 Python 过滤函数。

原生内置管网仍依靠标签识别，连接规则仍是同一方块 ID 相连。给新等级注册参数不代表不同等级自动混接。纯新等级自动被对应内置检查器类型识别，不需要再建一个 `LogicModule` 或重复注册检查器类型。

## 兼容性边界

电缆的碰撞伤害和是否发送实体进入事件由原有电缆实现与 JSON 决定，这三个接口不引入新的绝缘参数。静态物品提示文字也不会因运行中调速自动改变；附属应避免在提示中承诺动态值。

自定义网络使用命名空间字符串 `network_type`；内置 `TransmitterType.ITEM_PIPE / FLUID_PIPE / WIRE` 仍为数字。网络类型用于操作事件路由，检查器 `type_id` 用于显示注册，二者不要求相等。

源码：[注册实现](../../behavior_pack/skybluetech_scripts/skybluetech/server/export/transmitters.py)、[网络基类](../../behavior_pack/skybluetech_scripts/skybluetech/server/transmitters/base/define.py)。
