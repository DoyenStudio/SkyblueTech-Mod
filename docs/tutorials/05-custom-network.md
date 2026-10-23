# 5. 创建独立的泵驱动管网

[上一章](04-transmitter-grades.md) · [下一章](06-extensions.md)

核能附属的加压管道由增压泵驱动，管网自身的 tick 只重置运输额度。本章保留这一设计，用 `stdb:pressure_pipe` 与 `stdb:pressure_pump` 做最小示例，复用前置的单流体缓冲算法。它不实现核能的压力接口、气体加工或惯量管道。

普通高速管道复用内置 LogicModule；本章拥有独立 LogicModule，并使用唯一 `network_type = "stdb:pressure_pipe"`。当前主模组没有 `TransmitterType.PIPE`。

## 网络、逻辑、操作与检查器

`stdb_scripts/stdb/server/pressure_network.py`：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import RequireModule
from stdb_scripts.tooldelta.api.server import BlockHasTag, GetBlockName

n = RequireModule("skybluetech_scripts.skybluetech.server.export.networks")
checker = RequireModule(
    "skybluetech_scripts.skybluetech.server.export.transmitter_visual_checker"
)

PIPE_ID = "stdb:pressure_pipe"
PUMP_ID = "stdb:pressure_pump"

class STDBPressureNetwork(n.FluidPipeNetwork):
    network_type = "stdb:pressure_pipe"

    def __init__(self, dim, group_inputs, group_outputs, nodes, transmitter_id):
        super(STDBPressureNetwork, self).__init__(
            dim, group_inputs, group_outputs, nodes, transmitter_id
        )
        self.pumped_this_cycle = False

    @classmethod
    def calc_transfer_speed(cls, block_name):
        return 1000 * 5

    @classmethod
    def calc_capacity(cls, block_name):
        return 5000

class STDBPressureAccessPoint(n.FluidPipeAccessPoint):
    pass

def is_pipe(block_name):
    return block_name == PIPE_ID

def is_container(block_name, dim=None, pos=None):
    return BlockHasTag(block_name, "skybluetech_fluid_container")

def is_provider(block_name, dim, pos):
    return block_name == PUMP_ID

def is_accepter(block_name, dim, pos):
    return block_name != PUMP_ID and is_container(block_name, dim, pos)

def on_container_placed(dim, x, y, z):
    pass

def on_network_tick(network):
    network.pumped_this_cycle = False

logic_module = n.LogicModule(
    STDBPressureNetwork,
    STDBPressureAccessPoint,
    transmitter_check_func=is_pipe,
    transmittable_block_check_func=is_container,
    on_transmittable_block_placed_later=on_container_placed,
    on_network_tick=on_network_tick,
    provider_check_func=is_provider,
    accepter_check_func=is_accepter,
)
action_module = n.ActionModule(logic_module, enable_io_mode_settings=False)
checker.RegisterTransmitterType(
    "stdb:pressure_network", "加压流体", logic_module,
    input_label="受液端", output_label="增压泵",
)

def pump_connected_networks(pump):
    for dx, dy, dz in n.DXYZ_FACING:
        x, y, z = pump.x + dx, pump.y + dy, pump.z + dz
        if GetBlockName(pump.dim, (x, y, z)) != PIPE_ID:
            continue
        network = logic_module.GetNetworkByTransmitter(pump.dim, x, y, z)
        if network is None or not network.enabled or network.pumped_this_cycle:
            continue
        if not pump.PowerEnough():
            break
        network.pumped_this_cycle = True
        pump.ReducePower()
        n.TransferFluidNetwork(network)
```

`LogicModule` 构造时已启用监听，无需再调用一次 enable。`ActionModule` 在本例禁用输入/提取切换，因为增压泵是源，其他容器是目标；仍提供扳手断连与标签等已有功能。

每个网络每周期只由一个泵驱动一次，同一网络连接同一泵多个面也不会多次运输。这里按一次驱动尝试收取 80 RF，即使目标满也收费，这是最小示例的明确规则；核能附属按实际运输结果计费，若要采用该规则，应写返回实际运输量的运输函数。

## 泵机器

`stdb_scripts/stdb/server/pressure_pump.py`：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import RequireModule
from stdb_scripts.stdb.server.pressure_network import PUMP_ID, pump_connected_networks

m = RequireModule("skybluetech_scripts.skybluetech.server.export.machinery")

@m.RegisterMachine
class STDBPressurePump(m.BaseClicker, m.MultiFluidContainer, m.PowerControl):
    block_name = PUMP_ID
    store_rf_max = 10000
    running_power = 80
    fluid_slot_max_volumes = {0: 10000}
    fluid_input_slots = (0,)
    fluid_output_slots = (0,)
    fluid_io_mode = (-1, -1, -1, -1, -1, -1)

    def __init__(self, dim, x, y, z, block_entity_data):
        super(STDBPressurePump, self).__init__(dim, x, y, z, block_entity_data)
        self.handler.SubscribeOnTicking(self.pressure_tick)

    def pressure_tick(self):
        pump_connected_networks(self)
```

泵缓存通过桶或普通流体管道补充。示例使用同一槽进出，不实现从下方机器主动抽液。普通管道的输入/提取面需要自己配置，避免普通管道从泵重新抽走液体。

把以下导入加入服务端初始化链：

```python
from stdb_scripts.stdb.server import pressure_network, pressure_pump
```

## 方块与客户端

管道完整复制[青铜流体管道 JSON](../../behavior_pack/netease_blocks/transmitters/fluid_pipe/skybluetech_fluid_pipe_bronze.json)至附属 `netease_blocks/stdb_pressure_pipe.json`。把 identifier 改为 `stdb:pressure_pipe`，category 改为 `construction`，删除 **`tag:skybluetech_fluid_pipe`**，改提示为“需增压泵驱动，1000 mB/t”。其余状态、模型、碰撞箱及引擎通知保留。

删除内置识别标签至关重要，否则普通流体 LogicModule 和独立网络会同时管理同一管道。不要为这个 ID 再调用 `RegisterFluidPipe`。

泵的 `netease_blocks/stdb_pressure_pump.json`：

```json
{
  "format_version": "1.21.70",
  "minecraft:block": {
    "description": {
      "identifier": "stdb:pressure_pump",
      "category": "construction"
    },
    "components": {
      "netease:block_entity": {"tick": true},
      "netease:listen_block_remove": {"value": true},
      "minecraft:geometry": {"identifier": "minecraft:geometry.full_block"},
      "minecraft:material_instances": {
        "*": {"texture": "skybluetech:frame", "render_method": "opaque"}
      },
      "minecraft:destructible_by_mining": {"seconds_to_destroy": 3.0},
      "tag:skybluetech_machine": {},
      "tag:skybluetech_fluid_container": {},
      "tag:redstoneflux_accepter": {},
      "tag:redstoneflux_connectable": {},
      "tag:piston_denier": {}
    }
  }
}
```

客户端初始化模块中补充点击监听：

```python
from stdb_scripts.stdb.common.modules import RequireModule

events = RequireModule("skybluetech_scripts.tooldelta.events.client")

@events.UiInitFinishedEvent.Listen()
def listen_pressure_blocks(_):
    events.ClientBlockUseEvent.AddExtraBlocks({
        "stdb:pressure_pipe", "stdb:pressure_pump",
    })
```

本例不把独立管道加入内置流体设置页，它的端点模式由 provider/accepter 固定决定。客户端只补点击事件，不再登记检查器类型。资源本地化：

```text
tile.stdb:pressure_pipe.name=示例加压流体管道
tile.stdb:pressure_pump.name=示例增压泵
```

## 数据流与存档

`BaseNetwork` 保存管道节点集合以及输入/输出接入点；`target_pos` 才是容器坐标。网络视角的 output 是抽取源，input 是接收目标，别把机器的输入输出方向反过来。

示例复用的 `FluidPipeNetwork` 使用网络中确定的节点保存 `fluid_id` 和 `fluid_volume` 标量；运输后保存，不把 Python 网络对象写入 NBT。`pumped_this_cycle` 只控制当前周期，重建后重置，无需持久化。拆网、合网、区块卸载和缓存更新由原始 LogicModule 路径处理，不复制核能旧版本的自愈代码作为通用要求。

需要完全不同传输介质时，从 `BaseNetwork`、`BaseAccessPoint` 开始实现自己的容量、预算、保存和运输回调，仍可复用 LogicModule/ActionModule。不要复用流体算法却声称支持热量或压力守恒。

## 验收

连接增压泵—加压管道—储罐，桶装液后供电。无泵或缺电不能运输；接两台泵后全网周期预算不翻倍；检查缓冲与目标总量。目标满时不丢液，余量保留。

分别点击管道、泵和连接内置管道的机器，检查可视化名称、端点和去重；测试断连、重连、卸载重载与退出重进。网络显示 ID `stdb:pressure_network` 与操作类型 `stdb:pressure_pipe` 刻意不同，二者均由各自注册路径使用。
