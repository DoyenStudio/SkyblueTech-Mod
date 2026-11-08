# 3. 配方机器与发电机

[上一章](02-first-machine.md) · [下一章](04-transmitter-grades.md)

本章在同一 `stdb` 附属里增加三个机器。源码参考为主模组的 [macerator.py](../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/macerator.py)、[magma_furnace.py](../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/magma_furnace.py)、[redstone_generator.py](../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/redstone_generator.py)。

| 示例 | 基类 | 输入与输出 | 槽位 |
| --- | --- | --- | --- |
| `stdb:grinder` | Processor | 1 石头 → 1 沙子，30 RF/t，160 tick | 物品输入 0、输出 1、升级 2–5 |
| `stdb:melter` | Processor + MultiFluidContainer | 1 圆石 → 250 mB 熔岩，40 RF/t，100 tick | 物品输入 0、升级 1–4、流体输出槽 0 |
| `stdb:fuel_generator` | GeneratorProcessor | 1 红石 → 1 沙子，同时 20 RF/t、100 tick | 物品输入 0、输出 1、无升级槽 |

发电示例的沙子只是演示副产物。时间单位均为游戏 tick，20 tick 为一秒。不要把 `power_cost` 或 `output_power` 当成整次配方总能量。

## 公共配方：两端导入

`stdb_scripts/stdb/common/recipes.py`：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import RequireModule

r = RequireModule("skybluetech_scripts.skybluetech.common.export.recipes")
STORE_RF_MAX = 10000
FLUID_CAPACITY = 4000

class STDBGrinderRecipe(r.MachineRecipe):
    recipe_icon_id = "stdb:grinder"

class STDBMelterRecipe(r.MachineRecipe):
    recipe_icon_id = "stdb:melter"

class STDBFuelRecipe(r.GeneratorRecipe):
    recipe_icon_id = "stdb:fuel_generator"

grinder_recipes = r.RecipesCollection(
    "stdb:grinder",
    STDBGrinderRecipe(
        {"item": {0: r.Input("minecraft:stone", 1)}},
        {"item": {1: r.Output("minecraft:sand", 1)}},
        power_cost=30, tick_duration=160,
    ),
)
melter_recipes = r.RecipesCollection(
    "stdb:melter",
    STDBMelterRecipe(
        {"item": {0: r.Input("minecraft:cobblestone", 1)}},
        {"fluid": {0: r.Output("minecraft:lava", 250)}},
        power_cost=40, tick_duration=100,
    ),
)
fuel_recipes = r.RecipesCollection(
    "stdb:fuel_generator",
    STDBFuelRecipe(
        {"item": {0: r.Input("minecraft:redstone", 1)}},
        output_power=20, tick_duration=100,
        outputs={"item": {1: r.Output("minecraft:sand", 1)}},
    ),
)
```

独立配方子类使用附属前缀命名，避免配方类按类名登记时与其他模组冲突。`MachineRecipe`/`GeneratorRecipe` 已提供序列化方法；本例保持其构造签名，因此子类可继承原有 Marshal/Unmarshal。

## 服务端机器

`stdb_scripts/stdb/server/recipe_machines.py`：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import RequireModule
from stdb_scripts.stdb.common.recipes import (
    STORE_RF_MAX, FLUID_CAPACITY, grinder_recipes, melter_recipes, fuel_recipes,
)

m = RequireModule("skybluetech_scripts.skybluetech.server.export.machinery")

@m.RegisterMachine
class STDBGrinder(m.Processor):
    block_name = "stdb:grinder"
    store_rf_max = STORE_RF_MAX
    recipes = grinder_recipes
    process_item = True
    item_input_slots = (0,)
    item_output_slots = (1,)
    upgrade_slot_start = 2
    upgrade_slots = 4

@m.RegisterMachine
class STDBMelter(m.Processor, m.MultiFluidContainer):
    block_name = "stdb:melter"
    store_rf_max = STORE_RF_MAX
    recipes = melter_recipes
    process_item = True
    process_fluid = True
    item_input_slots = (0,)
    item_output_slots = ()
    upgrade_slot_start = 1
    upgrade_slots = 4
    fluid_slot_max_volumes = {0: FLUID_CAPACITY}
    fluid_input_slots = ()
    fluid_output_slots = (0,)
    fluid_io_mode = (1, 1, 1, 1, 1, 1)

@m.RegisterMachine
class STDBFuelGenerator(m.GeneratorProcessor):
    block_name = "stdb:fuel_generator"
    store_rf_max = STORE_RF_MAX
    recipes = fuel_recipes
    process_item = True
    item_input_slots = (0,)
    item_output_slots = (1,)
    upgrade_slots = 0
```

无需编写 tick 扣料和产物逻辑，也不要重复调用发电。自定义构造器存在时才写协作式 `super`。熔融机的流体槽号与物品槽号是两个独立空间，都是 0 没有冲突；物品槽与升级槽则不能重叠。

`Processor` 在加载及开始新批次时检查物品和流体输出空间；之后输出槽更新事件只标脏，下一 tick 在判断活动状态前统一重检，无更新的加工 tick 不扫描输出槽。堵塞时保留进度并停止加工耗电，腾出空间后继续同一批。普通耗电配方每个工作 tick 只扣一次电，按 `reduce_ticks` 推进，在进度到零的当 tick 结算；速度升级的剩余加工量可继续用于下一批，续批仍会重新检查原料和输出空间。缺料或换成另一配方时重置进度。

物品槽通知存在延迟，因此 `run_once()` 结算前仍直接核对当前库存，不复用推进阶段的可输出判断。流体输出的增加、减少及批量操作中的每个槽位更新都会标脏，配方内部写入也不例外；结算失败同样标脏，避免在延迟通知到达前沿用旧状态。直接修改流体数据的代码必须按容器约定派发槽位更新。

需要特殊加工速率时覆写 `ProcessOnce()`：它每 tick 最多调用一次，更新 `ticks_left` 并返回是否可以结算，不要提前重置下一批进度。需要特殊结算时覆写 `run_once()`，必须返回成功与否；失败时基类重新检查配方，同配方保留完成进度，后续重试不再消耗加工电量。普通配方机器无需覆写 `_processor_on_ticking`。

## 行为包 JSON

下面是 `netease_blocks/stdb_grinder.json` 的完整最小定义。给另两个机器建立独立文件，按其后的替换表修改；未列出的字段保持一致。

```json
{
  "format_version": "1.21.70",
  "minecraft:block": {
    "description": {
      "identifier": "stdb:grinder",
      "base_block": "netease_container",
      "category": "construction",
      "states": {"skybluetech:active": [false, true]},
      "traits": {
        "minecraft:placement_direction": {
          "enabled_states": ["minecraft:cardinal_direction"]
        }
      }
    },
    "components": {
      "netease:block_entity": {"tick": true},
      "netease:listen_block_remove": {"value": true},
      "netease:block_container": {
        "container_size": 6,
        "custom_description": "示例磨粉机",
        "screen_name": "STDBGrinderUI.main"
      },
      "minecraft:geometry": {"identifier": "minecraft:geometry.full_block"},
      "minecraft:material_instances": {
        "*": {"texture": "skybluetech:frame", "render_method": "opaque"}
      },
      "minecraft:destructible_by_mining": {"seconds_to_destroy": 3.0},
      "tag:piston_denier": {},
      "tag:skybluetech_machine": {},
      "tag:skybluetech_container": {},
      "tag:skybluetech_appliance": {},
      "tag:redstoneflux_appliance": {},
      "tag:redstoneflux_connectable": {},
      "tag:redstoneflux_accepter": {}
    }
  }
}
```

| 修改处 | `stdb_melter.json` | `stdb_fuel_generator.json` |
| --- | --- | --- |
| identifier | `stdb:melter` | `stdb:fuel_generator` |
| container_size | 5 | 2 |
| custom_description | 示例熔融机 | 示例燃料发电机 |
| screen_name | `STDBMelterUI.main` | `STDBFuelUI.main` |
| 标签 | 额外添加 `"tag:skybluetech_fluid_container": {}` | 将 `tag:redstoneflux_accepter` 改成 `tag:redstoneflux_provider` |

JSON 定义自定义容器时，`GUIControl.bound_ui` 保持 None；它不是这里的 `screen_name`。示例没有配置原版漏斗行为，需要漏斗时按源机器 JSON 补充 `hopper`，管道输入输出仍由槽位声明和标签决定。

## 客户端 UI

复用前置布局与图片，使用独立 UI 名称和代理类。分别建立资源包文件：

`ui/STDBGrinderUI.json`：

```json
{"namespace": "STDBGrinderUI", "main@MaceratorUI.main": {}}
```

`ui/STDBMelterUI.json`：

```json
{"namespace": "STDBMelterUI", "main@MagmaFurnaceUI.main": {}}
```

`ui/STDBFuelUI.json`：

```json
{"namespace": "STDBFuelUI", "main@RedstoneGeneratorUI.main": {}}
```

把这些路径加入资源包 `ui/_ui_defs.json` 的 `ui_defs` 数组；新包可使用：

```json
{
  "ui_defs": [
    "ui/STDBGrinderUI.json",
    "ui/STDBMelterUI.json",
    "ui/STDBFuelUI.json"
  ]
}
```

`stdb_scripts/stdb/client/recipe_machines.py`：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import RequireModule
from stdb_scripts.stdb.common import recipes as data

ui = RequireModule("skybluetech_scripts.skybluetech.client.export.machinery")
shared = RequireModule("skybluetech_scripts.skybluetech.common.export.machinery")
td_ui = RequireModule("skybluetech_scripts.tooldelta.ui")
api = RequireModule("skybluetech_scripts.tooldelta.api.client")
nbt = RequireModule("skybluetech_scripts.tooldelta.utils.nbt")
events = RequireModule("skybluetech_scripts.tooldelta.events.client")

class STDBRecipePanel(ui.MachinePanelUIProxyEx):
    recipe_collection = None
    title = ""
    has_fluid = False
    has_flame = False
    available_extra_pages = (ui.ItemPipeSettingsPage,)

    def OnCreate(self):
        self.power = self.GetElement(ui.MAIN_PATH / "power_bar")
        self.progress = self.GetElement(ui.MAIN_PATH / "progress")
        self.GetElement(ui.MAIN_PATH / "machine_label").asLabel().SetText(self.title)
        ui.AsRecipeCheckerBtn(
            self.GetElement(ui.MAIN_PATH / "recipe_check_btn").asButton(),
            self.recipe_collection,
        )
        if self.has_fluid:
            self.fluid = ui.FluidDisplayer(
                self.GetElement(ui.MAIN_PATH / "fluid_display")
            )
        if self.has_flame:
            self.flame = self.GetElement(ui.MAIN_PATH / "flame")

    def OnTicking(self):
        block_data = api.GetBlockEntityData(*self.pos[1:])
        if block_data is None:
            return
        ex = block_data["exData"]
        energy = nbt.GetValueWithDefault(ex, shared.K_STORE_RF, 0)
        progress = nbt.GetValueWithDefault(ex, shared.K_PROGRESS, 0.0)
        ui.UpdatePowerBar(self.power, energy, data.STORE_RF_MAX)
        ui.UpdateProgress(self.progress, progress)
        if self.has_fluid:
            slot = shared.FluidSlotClient(ex, 0, data.FLUID_CAPACITY)
            self.fluid.update(slot.fluid_id, slot.volume, data.FLUID_CAPACITY)
        if self.has_flame:
            ui.UpdateFlame(self.flame, 1 - progress if progress > 0 else 0)

@td_ui.RegistToolDeltaScreen("STDBGrinderUI.main", is_proxy=True)
class STDBGrinderPanel(STDBRecipePanel):
    title = "示例磨粉机"
    recipe_collection = data.grinder_recipes

@td_ui.RegistToolDeltaScreen("STDBMelterUI.main", is_proxy=True)
class STDBMelterPanel(STDBRecipePanel):
    title = "示例熔融机"
    recipe_collection = data.melter_recipes
    has_fluid = True
    available_extra_pages = (ui.ItemPipeSettingsPage, ui.FluidPipeSettingsPage)

@td_ui.RegistToolDeltaScreen("STDBFuelUI.main", is_proxy=True)
class STDBFuelPanel(STDBRecipePanel):
    title = "示例燃料发电机"
    recipe_collection = data.fuel_recipes
    has_flame = True

@events.UiInitFinishedEvent.Listen()
def listen_machine_clicks(_):
    events.ClientBlockUseEvent.AddExtraBlocks({
        "stdb:grinder", "stdb:melter", "stdb:fuel_generator",
    })
```

代理类继承主模组面板，因此这里用前置 ToolDelta 的注册器和客户端事件，保持它们与面板内部的坐标/同步上下文一致。UI 只显示服务端状态，不在客户端扣料、扣能量或产物。

`UpdateProgress` 按 JSON 控件自己声明的方向填充：进度控件里放一个名为 `fill_up` / `fill_down` / `fill_left` 的 0×0 隐藏子控件，就是自下而上 / 自上而下 / 自右向左，没有则自左向右（原版箭头）；带 `spin` 子控件的序列帧图标（如 `SkybluePanelLib.progress_icon_gear`）会在机器运行时转动、停机时暂停。直接引用 `SkybluePanelLib.progress_icon_*` / `progress_inset_*` 时这些标记已经带好，换样式只改 JSON。面板基类会按服务端推送的停机标志（继承 `GUIControl` 的机器自动推送）处理标题栏状态灯（使用 `SkybluePanelLib.machine_screen` 框架时）和停机提示圈：在 `main` 下放 `ring_in_*` / `ring_out_*` / `ring_tin_*` / `ring_tout_*` / `ring_energy` 命名的 `SkybluePanelLib.status_ring`，与对应槽位同位置同尺寸即可，不需要写代码。旧的 `UpdateGenericProgressL2R` / `T2B` / `B2T` 仍然可用。

状态灯和提示圈只看停机标志，所以机器空闲时（缺料、温度不够、没有日照等）要在服务端设上对应的标志，否则会一直显示运行中。每 tick 都要判断的状态用 `BaseMachine.UpdateDeactiveFlag(flag, on)`：标志已是目标状态时不触发回调，也不写方块数据。只用于显示、不该挡住工作逻辑的标志，要在相应的 `IsActive()` 判断里改用 `IsActiveIgnoreCondition(flag)`。面板类可以用 `STATUS_TEXTS = {标志: 文字}` 改写状态灯的原因文字，用 `STATUS_RINGS = {标志: (前缀, ...)}` 改写要亮的提示圈，空元组表示这个原因不亮提示圈。

## MiniJEI 渲染

`stdb_scripts/stdb/client/recipe_renderers.py`：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import RequireModule
from stdb_scripts.stdb.common import recipes as data

r = RequireModule("skybluetech_scripts.skybluetech.client.export.recipes")

class STDBGrinderRenderer(r.MachineRecipeRenderer):
    recipe_icon_id = "stdb:grinder"
    render_ui_def_name = "RecipeCheckerLib.macerator_recipes"

class STDBMelterRenderer(r.MachineRecipeRenderer):
    recipe_icon_id = "stdb:melter"
    render_ui_def_name = "RecipeCheckerLib.magma_furnace_recipes"

class STDBFuelRenderer(r.GeneratorRecipeRenderer):
    recipe_icon_id = "stdb:fuel_generator"
    render_ui_def_name = "RecipeCheckerLib.redstone_generator_recipes"

data.STDBGrinderRecipe.SetRenderer(STDBGrinderRenderer)
data.STDBMelterRecipe.SetRenderer(STDBMelterRenderer)
data.STDBFuelRecipe.SetRenderer(STDBFuelRenderer)
```

渲染器与机器运行配方是同一个数据模型的两个用途。物品显示控件对应 `slot0`、`slot1`，流体对应 `fluid0`；复用其他布局前核对这些名字。

## 导入与本地化清单

在 `server/__init__.py` 命名空间注册之后追加：

```python
from stdb_scripts.stdb.server import recipe_machines
```

在 `client/__init__.py` 命名空间注册之后追加：

```python
from stdb_scripts.stdb.client import recipe_machines, recipe_renderers
```

上述两个模块都会导入公共配方，因此两端都有集合。资源包 `texts/zh_CN.lang`：

```text
tile.stdb:grinder.name=示例磨粉机
tile.stdb:melter.name=示例熔融机
tile.stdb:fuel_generator.name=示例燃料发电机
```

## 验收

为耗能机器连接电缆，检查缺料、缺电、堵塞输出、恢复供电；熔融机连接可传熔岩的管道，检查满槽等待及排空后继续。发电机连接用电器并检查副产物槽满、缓冲满和恢复输出；不要假设所有发电机默认都无损自动停机，是否允许特定停机升级取决于类配置。

检查 UI 槽位可交互、升级槽不与产物重叠、配方按钮显示本附属配方、MiniJEI 分类及输入输出检索。带部分进度退出重进，检查输入与已启动燃料、发电功率、进度和流体均未复制或丢失。

修改 `Processor` 后还应在游戏内完成以下回归；这些是验收步骤，不代表已通过实测：

| 场景 | 预期 |
| --- | --- |
| 普通加工机、小型化学反应釜、电解机，无升级卡且供料充足 | 时长为 N 的配方在第 N 个工作 tick 产出，消耗 N × `power_cost`，无额外结算耗电 |
| 加工途中堵住物品输出，或填满任一流体输出槽 | 进度和加工耗电暂停，显示输出受阻；取出物品或抽走流体后从原进度继续 |
| 长配方加工期间输出库存不变；同一 tick 多次更新输出槽 | 稳定加工期间不调用 `_check_output()`、不扫描输出槽；多次输出更新合并到下一 tick 重检，结算及新批次另行校验 |
| 批量流体更新中输出槽不是最后一个通知，或向输出槽增加流体 | 仍能标脏，下一 tick 正确暂停或恢复；输出受阻停机时也能处理脏标记 |
| 加工途中断电，再恢复供电 | 不丢失进度，不重复扣料或产出 |
| 带速度、能量升级卡运行电解机 | 速度和耗电倍率生效；跨批次的剩余加工量保留，每 tick 只扣一次升级后的电费 |
| 在游戏内调试环境设置短配方，使 `reduce_ticks` 足以完成多批，储电仅够一个工作 tick | 当 tick 可完成多批，只扣一次电；每批都重新核对原料和输出，满槽后停止续批 |
| 结算前换料、抽走原料，或让结算钩子返回 False | 无错误产出；换方重新计时，同配方失败保留零剩余时间并可重试 |
| 以部分进度及零剩余时间等待结算的状态卸载区块、保存重进 | 保留进度；零不会恢复成默认时长，输出受阻状态与实际库存一致 |
| 精密切割机、真空冷冻机、充电台配方模式 | 锯片仅在成功产出后扣耐久；冷冻机保持温度速率与独立制冷耗电，输出受阻时停止配方推进；充电台配方模式使用统一流程，物品充能模式正常 |
