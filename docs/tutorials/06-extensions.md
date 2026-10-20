# 6. 其他常用扩展

[返回手册](../README.md) · [正式接口](../reference/exports.md)

以下都是附属文件中的代码，继续使用第一章 `RequireModule`。公共注册在客户端与服务端分别导入；UI、渲染与指南只在客户端导入。不要把整个 `client` 包从公共文件导入。

## 给已有机器增加配方

`stdb_scripts/stdb/common/extra_recipes.py`：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import RequireModule

r = RequireModule("skybluetech_scripts.skybluetech.common.export.recipes")
collection = r.RecipesCollection.get_collection("skybluetech:macerator")
collection.add_recipe(
    r.MaceratorRecipe(
        r.Input("minecraft:gravel", 1),
        "minecraft:sand", 2, power_cost=30, tick_duration=100,
    )
)
```

两端初始化文件在前置就绪后各导入此模块即可，Python 模块缓存避免重复执行。内置配方类型已经有客户端渲染器，不再调用 `SetRenderer` 覆盖它。

太阳能附属给工作台及电动加工台扩展配方时，需要分别向两个实际集合追加；不要假定它们共享同一个集合对象。新增机器则按第三章建立自己的唯一集合和配方子类。当前教程仅保证初始化阶段扩展，不承诺运行中增删配方后所有索引和活动机器自动刷新。

## MiniJEI 的三个登记点

全部内置类型及特殊索引限制见[配方参考](../reference/recipes.md)。冷冻机模式、水培床和模板装配台等使用专用映射，不能把普通集合的追加示例直接套用到这些机器。

`RecipesCollection` 将配方加入输入输出查询；配方类的 `recipe_icon_id` 指定分类图标；客户端 `RecipeClass.SetRenderer(RendererClass)` 指定具体布局与绘制。缺任何一项都会出现“能工作但看不到配方”或“有列表但打不开页面”。

标准物品/流体配方使用第三章的 `MachineRecipeRenderer`，燃料配方使用 `GeneratorRecipeRenderer`；自定义布局继承 `RecipeRenderer`，实现 `RenderInit(panel)`、按需实现 `RenderUpdate(panel, render_ticks)` 与 `DeRender(panel)`。图标 ID、`slotN`、`fluidN` 和 `render_ui_def_name` 必须与资源对应。

## UI 数据绑定与操作同步

通常沿用第三章的 `OnTicking` 更新控件即可。若 JSON 通过绑定获取数据，使用 ToolDelta 的 Binder，不直接操作原始 ViewBinder。

在一个已经注册的代理类中添加：

```python
@td_ui.Binder.binding(td_ui.Binder.BF_BindString, "#STDB.status")
def get_status(self):
    return "Ready"
```

该代理的布局中加入以下控件（`controls` 的一项）：

```json
{
  "status": {
    "type": "label",
    "text": "#text",
    "bindings": [
      {
        "binding_name": "#STDB.status",
        "binding_name_override": "#text"
      }
    ]
  }
}
```

Binder 装饰方法必须属于已注册屏幕类；集合绑定另用 `binding_collection` 并精确匹配 collection_name。普通静态字段优先用类装饰器，不为固定绑定引入 DynaBinding。

玩家操作通过公共事件到服务端验证，不直接修改客户端读到的 `exData`。以下是可与第三章磨粉机组合的“手动停机”通信增量；示例事件字段沿用 paused，但它会重置加工进度，具体规则见下文。

`common/operations.py`：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import RequireModule
e = RequireModule("skybluetech_scripts.skybluetech.common.export.events")

class STDBPauseRequest(e.MachineryOperationC2S):
    name = "stdb:pause"
    extra_attrs = ("paused",)

    def __init__(self, x, y, z, paused, player_id=""):
        super(STDBPauseRequest, self).__init__(x, y, z, player_id)
        self.paused = paused
```

服务端把第三章的类头改为 `class STDBGrinder(m.Processor, m.OperationListener)`，在类定义之后增加：

```python
from stdb_scripts.stdb.common.operations import STDBPauseRequest
STDB_MANUAL_STOP = 1 << 16

@STDBGrinder.ForOperation(STDBPauseRequest)
def set_paused(event, machine):
    if not isinstance(event.paused, bool):
        return
    if not machine.ui_sync.PlayerInSync(event.player_id):
        return
    if event.paused:
        machine.SetDeactiveFlag(STDB_MANUAL_STOP)
    else:
        machine.UnsetDeactiveFlag(STDB_MANUAL_STOP)
    machine.CallSync()
```

客户端在相应代理类的方法中发送：

```python
def request_pause(self, paused):
    from stdb_scripts.stdb.common.operations import STDBPauseRequest
    STDBPauseRequest(
        self.pos[1], self.pos[2], self.pos[3], bool(paused)
    ).send()
```

此段演示服务端通信；`STDB_MANUAL_STOP` 是示例在自己的机器上保留的业务位，不是主模组预定义常量。当前主模组通用标志使用低 8 位。该位不属于保留进度的停机原因，**停机会重置本次加工进度**；正式项目若要求暂停续作，应另行设计进度保留规则。ForOperation 自带类型与多方块检查，但不会代替业务权限和参数检查。

## 注册流体

本节示例为 `stdb:coolant`：采用 WATER 基础材质、RGBA `(0, 229, 255, 128)`、`CommonLiquid` 分类。这组值仅用于教学，采用与蒸馏水相同的表现；真实流体应单独确定材质、RGBA、分类与桶/储罐需求。

`common/fluids.py`，两端初始化导入：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import RequireModule
f = RequireModule("skybluetech_scripts.skybluetech.common.export.fluids")

class STDBLiquids(f.CommonLiquid):
    COOLANT = "stdb:coolant"

f.RegisterFluidTexture(
    STDBLiquids.COOLANT, f.WATER, rgb=(0, 229, 255), alpha=128
)
```

继承分类会将附属 ID 加入 `Common.all_sub()`，因此普通流体管道可以识别兼容性。也可用现有分类的 `add_extras({"stdb:coolant"})`，不额外维护一份中央流体表。酸、高温、极高温分类会影响管道过滤，不能只为好看的分类名字随意选择。

世界液体、桶、机器流体条和储罐模型是不同展示路径。先完整复制[蒸馏水源方块](../../behavior_pack/netease_blocks/liquid/skybluetech_distilled_water.json)和[流动方块](../../behavior_pack/netease_blocks/liquid/skybluetech_flowing_distilled_water.json)到附属：

| 字段/文件 | 修改 |
| --- | --- |
| 两个 identifier | `stdb:coolant`、`stdb:flowing_coolant` |
| 两处 liquid_color | 均为 `[0,229,255,128]`，对照源文件实际字段格式填写 |
| bucket_name | 本最小世界液体例删除该可选字段；需桶时另建 `stdb:coolant_bucket` |
| 其他流动/碰撞组件 | 保留源文件；稳定 ID 用于配方，流动 ID 不加入分类 |

资源包 `blocks.json` 合并：

```json
{
  "format_version": [1, 1, 0],
  "stdb:coolant": {
    "blockshape": "water",
    "textures": {
      "down": "skybluetech:basic_water_static",
      "up": "skybluetech:basic_water_static",
      "side": "skybluetech:basic_water_flowing"
    }
  },
  "stdb:flowing_coolant": {
    "blockshape": "water",
    "textures": {
      "down": "skybluetech:basic_water_static",
      "up": "skybluetech:basic_water_flowing",
      "side": "skybluetech:basic_water_flowing"
    }
  }
}
```

本地化两条：

```text
tile.stdb:coolant.name=示例冷却液
tile.stdb:flowing_coolant.name=流动的示例冷却液
```

要进入储罐显示，提供 `textures/fluid_models/stdb.coolant.png`：本例颜色与蒸馏水相同，可复制前置对应蒸馏水模型纹理并改名；其他颜色应按基础贴图首帧着色生成。桶还需行为物品、资源物品、图标登记及本地化，按蒸馏水桶完整定义复制并替换 ID。只注册 FluidTexture 不会生成世界液体或桶。

## 指南入口

`client/guidance.py`：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import RequireModule
g = RequireModule("skybluetech_scripts.skybluetech.client.export.guidance")
p = g.pages_define

group = p.PageGroup(
    "stdb:guide",
    [p.TextPage("附属开发示例", "给磨粉机供电并放入石头，点击配方按钮查看配方。")],
)
g.AddAddition(p.MainTOCPageSection("stdb:grinder", 0, "附属开发示例", group))
```

客户端初始化只导入一次。`AddAddition` 接收 `MainTOCPageSection`，不是单个 TextPage；它将内容挂入主指南“附属模组”目录。

## 升级与多方块入口

机器允许已有升级卡时，覆写 `allow_upgraders`，使用 `common.export.machinery.Upgraders` 的 ID；不是旧文档中的标签白名单。自定义 `UpdateUpgraders(upgraders)` 先调用父实现，再计算业务配置，修改配方集合后按现有机器流程重新检查。

多方块从 `common.export.machinery.GenerateSimpleStructureTemplate` 与 `server.export.machinery.MultiBlockStructure` 开始。最小结构定义：

```python
shared = RequireModule("skybluetech_scripts.skybluetech.common.export.machinery")
palette = shared.GenerateSimpleStructureTemplate(
    {"F": "minecraft:iron_block"},
    {0: [" F ", "F#F", " F "]},
)
```

把 `structure_palette=palette` 放到组合 MultiBlockStructure 的主机类中；要出现“未完成结构不能工作”的完整行为，保留基类停机机制。功能接口另注册机器类并加入 `functional_block_ids`，结构图案必须允许接口所在位置。`.` 表示必须为空，空格表示不关心，`#` 唯一标识核心。

建议后续独立展开：自定义升级卡行为、复杂多方块接口、热量交换设备、资源制作与发布兼容矩阵。本次先给出已验证的代码入口和可组合方式，不把核能反应堆全部业务塞进入门教程。
