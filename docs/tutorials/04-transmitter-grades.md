# 4. 扩展已有管线

[上一章](03-recipe-machines.md) · [下一章](05-custom-network.md)

增加等级表示复用内置网络算法，只改变方块 ID、速率、容量或流体兼容性。不需要复制 `LogicModule`，也不要让多个逻辑实例同时识别同一个方块。

## 完整注册模块

`stdb_scripts/stdb/server/transmitter_grades.py`：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import RequireModule

lines = RequireModule("skybluetech_scripts.skybluetech.server.export.transmitters")
fluids = RequireModule("skybluetech_scripts.skybluetech.common.export.fluids")

def accepts_common(fluid_id):
    return fluid_id in fluids.Common.all_sub()

lines.RegisterItemPipe("stdb:fast_item_pipe", 8)
lines.RegisterFluidPipe(
    "stdb:fast_fluid_pipe", 1000, 5000,
    can_transmit_fluid=accepts_common,
)
lines.RegisterWire("stdb:fast_wire", 8192)
```

在服务端初始化链导入该模块。客户端不重复调用等级注册：主模组自动同步 ID 到相应类别集合，并为点击事件补充监听。所有数值使用每 tick 单位，内部每 5 tick 分配一次五倍预算；流体管网容量是全网缓冲，不按管道数量乘算。

## 方块与资源文件

为保留完整六面状态、模型骨骼、碰撞箱和扳手操作，完整复制以下行为 JSON 到附属，然后只按表中规则替换。复制的源文件本身是本例的资源定义，不是省略了状态的伪代码；不要把数千行碰撞箱 permutations 手抄一遍。

| 主模组源文件 | 附属目标文件 | identifier |
| --- | --- | --- |
| [物品管道](../../behavior_pack/netease_blocks/transmitters/item_pipe/skybluetech_item_pipe_steel.json) | `netease_blocks/stdb_fast_item_pipe.json` | `stdb:fast_item_pipe` |
| [流体管道](../../behavior_pack/netease_blocks/transmitters/fluid_pipe/skybluetech_fluid_pipe_bronze.json) | `netease_blocks/stdb_fast_fluid_pipe.json` | `stdb:fast_fluid_pipe` |
| [电缆](../../behavior_pack/netease_blocks/transmitters/wire/skybluetech_wire_copper.json) | `netease_blocks/stdb_fast_wire.json` | `stdb:fast_wire` |

每个目标文件精确修改：

1. `minecraft:block.description.identifier` 改成表中的附属 ID；`category` 改为 `construction`，无需创建新的创造栏分类。
2. `netease:custom_tips.value` 更新为该示例的速率，或写“速率由附属配置”；保留其他组件和 permutations。
3. 保留源文件中的 `tag:skybluetech_item_pipe` / `tag:skybluetech_fluid_pipe` / `tag:skybluetech_wire`，分别供内置逻辑识别。
4. 保留 `skybluetech:connection_*`、`skybluetech:cable_io_*` 的完整状态声明、几何引用和 bone_visibility；这些状态名属于前置协议，不改成 stdb 前缀。
5. 保留 `netease:block_entity`、邻居变化通知、移除通知及源文件原有碰撞/交互配置。

源 JSON 直接引用前置纹理和模型，故本示例无需新图片。需要自有外观时，另注册附属材质和模型并修改对应引用；不要只改本地化名就误以为模型也是独立资产。

资源包 `texts/zh_CN.lang`：

```text
tile.stdb:fast_item_pipe.name=高速物品管道
tile.stdb:fast_fluid_pipe.name=高速流体管道
tile.stdb:fast_wire.name=高速电缆
```

## 更新正在运行的网络

以下函数可加到同一个服务端模块，由附属已授权的配置流程调用：

```python
def apply_faster_fluid_setting():
    lines.RegisterFluidPipe(
        "stdb:fast_fluid_pipe", 2000, 10000,
        can_transmit_fluid=accepts_common, replace=True,
    )

def apply_smaller_buffer():
    lines.RegisterFluidPipe(
        "stdb:fast_fluid_pipe", 1000, 1000,
        can_transmit_fluid=accepts_common, replace=True,
    )

def override_builtin_wire():
    lines.RegisterWire("skybluetech:wire_copper", 1024, replace=True)
```

缩容不清空流体、不拆网。已有缓冲超出新容量时只能输出，排到新容量以下后再抽取。过滤变严也不会抹掉旧流体。重新进世界恢复为初始化模块注册的参数，运行时调整不自动写入存档。

同配置重复调用可以省略 `replace=True`；使用不同函数对象的过滤器视为配置变化。不要把“允许显式覆盖”理解成可以切换一个 ID 的类别，流体管道 ID 不能改注册成电缆。

## 验收

先把同一种 ID 的管线连起来，测试源供给充足、目标有容量时的多周期总传输量；不同等级默认不连通。打开机器的管道设置页，再运行时注册新增等级，检查旧页面和扳手都能识别；第二个玩家晚加入也应看到相同分类。

新等级仍由内置检查器类型显示。检查单网络和机器多网络视图；无需为每个等级调用 `RegisterTransmitterType`。详细异常和同步契约见[注册参考](../reference/transmitters.md)。
