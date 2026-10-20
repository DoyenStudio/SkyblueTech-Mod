# 管道网络可视化检查器接口

附属模组可向 `skybluetech:transmitter_visual_checker` 注册自己的传输网络类型。
只需在服务端注册已有的 `LogicModule` 实例, 客户端不需要注册类型或同步管道 ID 列表。

## 接入示例

在附属的服务端 `LogicModule` 实例创建完成后, 通过 ModSDK `ImportModule` 获取接口:

```python
# coding=utf-8
import mod.server.extraServerApi as serverApi

# logic_module 为附属已经创建并正常工作的蔚蓝科技 LogicModule 实例。
checker = serverApi.ImportModule(
    "skybluetech_scripts.skybluetech.server.export.transmitter_visual_checker"
)
checker.RegisterTransmitterType(
    "myaddon:heat_pipe",
    "热量",
    logic_module,
    input_label="吸热端",
    output_label="供热端",
)
```

也可从 `skybluetech_scripts.skybluetech.server.export` 获取同一个函数。
跨模组使用 `ImportModule`, 避免直接跨包导入触发机审告警。
此接口不创建管道或网络, 不负责启动 `LogicModule`, 也不修改网络的传输行为。

## RegisterTransmitterType

```python
RegisterTransmitterType(
    type_id, display_name, logic_module, input_label="输入", output_label="抽取"
)
```

| 参数 | 含义 |
| --- | --- |
| `type_id` | 类型的唯一 ID, 使用 `namespace:name` 格式, 例如 `myaddon:heat_pipe`。它是可视化类型 ID, 不要求与方块 ID 或 `BaseNetwork.network_type` 相同。 |
| `display_name` | 机器多网络视图中的类型名称, 例如“热量”。 |
| `logic_module` | 蔚蓝科技 `server.transmitters.base.LogicModule` 的实例或其子类实例。 |
| `input_label` | 网络向目标输入时的端点文案, 默认“输入”。 |
| `output_label` | 网络从目标抽取时的端点文案, 默认“抽取”。 |

名称和端点文案接受非空的 UTF-8 字符串或 Unicode 字符串。
函数返回 `None`; 参数类型不符或 ID 冲突时抛出 `TypeError` / `ValueError`。
同一 `type_id` 和同一 `LogicModule` 实例重复注册会更新显示配置, 保持原来的注册顺序。
同一 ID 不能绑定另一个实例, 同一实例也不能注册到多个 ID。
注册立即对后续查询生效, 不写入存档。

## 查询行为

- 点击管道: 服务端按注册顺序调用 `logic_module.transmitter_check_func(block_name)`, 首个命中类型通过 `GetNetworkByTransmitter(dim, x, y, z)` 查询网络。不同类型应使用互不重叠的管道识别条件。
- 点击机器或容器: 未命中管道时, 对各类型调用 `transmittable_block_check_func(block_name, dim, pos)`; 通过后调用 `GetContainerNode(dim, x, y, z)`, 合并其输入和输出网络。同一类型的同一网络只绘制一次, 即使它连接了多个面。
- 网络中的 `nodes` 作为管道坐标, `group_inputs` / `group_outputs` 中接入点的 `target_pos` 作为端点坐标。附属继续遵循 `LogicModule` / `BaseNetwork` 的现有约定。
- 单网络端点显示自定义文案; 机器多网络视图显示“类型名称: 端点文案”。内置电线使用“用电器 / 能量源”。
- 保留现有的 0.5 秒操作限流、单网络青色、多网络随机颜色、重新查看清除旧图形及 10 秒自动清理。

附属方块需要能触发客户端的 `ClientBlockUseEvent`。检查器保留箱子和木桶的额外监听;
若接入其他需要白名单的方块, 附属应在客户端初始化完成后通过
`skybluetech_scripts.tooldelta.events.client.ClientBlockUseEvent.AddExtraBlocks`
添加相应方块 ID。这是点击事件的要求, 不需要在客户端重复注册网络类型。

检查器内部响应改用字符串类型 ID 和随响应下发的显示配置, 不再使用旧的数字类型编号。
附属应调用此注册接口, 避免自行构造或监听内部检查器通信事件。

## 游戏内验收

1. 验证内置物品管道、流体管道和电线的单网络 / 机器多网络视图, 检查电线端点文案。
2. 注册一个附属类型, 点击其管道和连接的机器, 检查类型名称、输入和输出坐标及自定义文案; 同时覆盖 UTF-8 和 Unicode 文案。
3. 给同一机器连接内置类型和附属类型, 并让同一网络连接多个面, 确认各网络正常绘制且不会重复。
4. 点击未连接网络的方块应提示“未找到网络”并清除机器查询的旧图形; 验证连续点击限流、图形替换和 10 秒清理。
5. 同一 ID 和实例重新注册后应显示新文案; ID 绑定不同实例、同一实例绑定不同 ID 时应报告注册冲突。
