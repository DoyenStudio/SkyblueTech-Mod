# 2. 第一台机器：点击计数器

[上一章](01-addon.md) · [下一章](03-recipe-machines.md)

先做一个没有配方和 UI 的机器，确认注册、方块实体和存档路径。所有文件均属于上一章的附属。

## 服务端

`stdb_scripts/stdb/server/counter.py`：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import RequireModule
from stdb_scripts.tooldelta.api.server import SetOnePopupNotice
from stdb_scripts.tooldelta.utils.py_comp import py2_long

machines = RequireModule("skybluetech_scripts.skybluetech.server.export.machinery")

@machines.RegisterMachine
class STDBCounter(machines.BaseClicker):
    block_name = "stdb:counter"
    is_non_energy_machine = True
    energy_io_mode = (2, 2, 2, 2, 2, 2)

    def __init__(self, dim, x, y, z, block_entity_data):
        super(STDBCounter, self).__init__(dim, x, y, z, block_entity_data)
        value = self.bdata["stdb:clicks"]
        if isinstance(value, bool) or not isinstance(value, (int, py2_long)):
            value = 0
        self.clicks = int(max(0, min(2147483647, value)))
        self.handler.SubscribeOnClick(self.counter_click)

    def counter_click(self, event, extra_datas=None):
        self.clicks = int(min(2147483647, self.clicks + 1))
        self.bdata["stdb:clicks"] = self.clicks
        SetOnePopupNotice(event.playerId, "Clicks: %d" % self.clicks)
```

在 `server/__init__.py` 命名空间注册后加入：

```python
from stdb_scripts.stdb.server import counter
```

`BaseClicker` 处理非容器点击与限流；回调使用 `SubscribeOnClick`，不能只声明一个 `OnClick` 就认为引擎会自动调用。

## 行为与资源

`behavior_pack/netease_blocks/stdb_counter.json`：

```json
{
  "format_version": "1.21.70",
  "minecraft:block": {
    "description": {
      "identifier": "stdb:counter",
      "category": "construction"
    },
    "components": {
      "netease:block_entity": {},
      "netease:listen_block_remove": {"value": true},
      "minecraft:geometry": {"identifier": "minecraft:geometry.full_block"},
      "minecraft:material_instances": {
        "*": {"texture": "skybluetech:frame", "render_method": "opaque"}
      },
      "minecraft:destructible_by_mining": {"seconds_to_destroy": 1.0},
      "tag:skybluetech_machine": {},
      "tag:piston_denier": {}
    }
  }
}
```

示例直接依赖前置已经注册的 `skybluetech:frame` 纹理，不添加新 PNG。正式产品可把材质换为自己的 terrain texture 键。只在使用既有前置的前提下复用这些资产。

将下列条目合并进资源包 `texts/zh_CN.lang`：

```text
tile.stdb:counter.name=点击计数器
```

本例不需要 UI、配方、MiniJEI 渲染器或能源标签。若要按 tick 工作，把 `netease:block_entity` 改为 `{"tick": true}` 并订阅 `SubscribeOnTicking`；不要给每台实例注册一份全局引擎 tick 监听器。

## 验收

放置后点击，看到递增数字；连续点击受到 BaseClicker 限流；离开区块并返回、退出重进后继续累加。检查原生 NBT 中 `stdb:clicks` 是可持久化 int。破坏后新放置的机器从零开始，不把坐标缓存当成存档。

主模组实例：[BaseClicker](../reference/machinery/base_clicker.md)、[机器事件](../reference/lifecycle.md)。
