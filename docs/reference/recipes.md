# 内置配方类型与扩展边界

[返回手册](../README.md) · [配方扩展教程](../tutorials/06-extensions.md)

下面的类型均从 `common.export.recipes` 直接重导出。它们保留原位置参数、类身份与已有渲染器；按源码中各类的 `__init__` 传参，不将 `MachineRecipe` 的通用签名套到所有子类。

## 基础能力

- `Input(id, count=1, aux=0, is_tag=False)` 与 `Output` 描述输入输出；物品槽与流体槽分开编号。
- `RecipeBase`、`Recipe`、`MachineRecipeBase`、`MachineRecipe`、`GeneratorRecipe` 用于自定义类型。
- `RecipesCollection.get_collection(name)` 取原集合，缺少名称会抛 KeyError；`add_recipe(recipe)` 追加到原列表并注册 MiniJEI 查询。
- `GetRecipesByInput`、`GetRecipesByOutput`、`GetRecipesByCategory` 与 `RegisterRecipe` 是已有查询/登记接口。
- `MarshalOrderedInputs`、`MarshalOrderedOutputs`、`UnmarshalOrderedInputs`、`UnmarshalOrderedOutputs` 用于固定槽（Ordered）配方数据。
- `MarshalUnorderedInputs`、`MarshalUnorderedOutputs`、`UnmarshalUnorderedInputs`、`UnmarshalUnorderedOutputs` 用于允许槽位组形式的无序（Unordered）配方数据。
- `gen_preset_recipe`、`gen_tagged_preset_recipe` 是磨粉配方工厂；`Description` 与 `RegisterDescription` 用于说明页。

## 固定槽与无序槽位组

`Recipe`、`MachineRecipeBase`、`MachineRecipe`、`GeneratorRecipe` 通用类提供可选的 `inputs_unordered=None`、`outputs_unordered=None`。已定义的具体机型配方和预设工厂保持各自原有参数，不接收这两个附加关键字。原版工作台/熔炉资源包装和 `Description` 不使用此结构。

四个字段分别为：

| 字段 | 结构 |
| --- | --- |
| `inputs` | `{CategoryStr: {Slot: Input}}` |
| `outputs` | `{CategoryStr: {Slot: Output}}` |
| `inputs_unordered` | `{CategoryStr: {tuple[int, ...]: list[Input]}}` |
| `outputs_unordered` | `{CategoryStr: {tuple[int, ...]: list[Output]}}` |

tuple 表示这一组材料或产物允许使用的真实槽位集合，不与材料列表一一对应。每组需求都必须满足；数量允许在组内跨槽凑齐，同一槽也可以提供多个需求，但同一份库存只能计算一次。例如下面的数据表示：槽位 0、1、2 合计提供 3 圆石和 1 煤，产物允许放入槽位 3、4。

```python
recipe = MachineRecipe(
    inputs={},
    outputs={},
    power_cost=20,
    tick_duration=100,
    inputs_unordered={
        "item": {(0, 1, 2): [Input("minecraft:cobblestone", 3), Input("minecraft:coal")]},
    },
    outputs_unordered={
        "item": {(3, 4): [Output("minecraft:stone", 3)]},
    },
)
```

允许槽位使用非空 tuple，成员使用不重复的非负 `int`。组内列表保留重复条目，概率产物也不会自动合并。组之间及与固定槽之间可以表达重叠的槽位限制，处理器会统一分配库存和容量。

`GetMachineInputs()` / `GetMachineOutputs()` 返回固定槽字典；`GetMachineUnorderedInputs()` / `GetMachineUnorderedOutputs()` 返回分组字典，不将无序条目伪装为固定槽。

MiniJEI 和 MEI 展示时将每组条目按列表顺序填入 tuple 所列槽位，与固定槽一起渲染，不另加分组区域或槽位编号说明。配方需保证条目放得下，且展示槽位不重叠；渲染器不额外校验这些约束。此展示映射不改变配方的无序匹配语义。

### 序列化格式

tuple 不能作为 JSON 对象键，因此无序槽位组编码为逗号分隔的槽号字符串，解码后恢复为 tuple。例如上面的输入字段编码为：

```json
{
  "inputs_unordered": {
    "item": {
      "0,1,2": [
        {"item": "minecraft:cobblestone", "count": 3, "aux": 0},
        {"item": "minecraft:coal", "count": 1, "aux": 0}
      ]
    }
  }
}
```

输出字段 `outputs_unordered` 使用相同的槽号字符串键。通用配方通过 `Recipe.Marshal()` / `Recipe.Unmarshal()` 处理四个字段，未提供的侧使用 `None`；固定槽号也编码为字符串，解码后恢复为整数。具体机型的专用编解码只处理各自已有的固定配方数据。

`Processor` 与 `GeneratorProcessor` 已接入物品、流体的无序匹配、插入许可、跨槽扣料和产出。固定槽与无序组统一分配，标签需求与具体物品需求不会重复计算同一份库存；零数量输入需要存在匹配材料，但不扣除数量。输出根据当前内容和容量分配，物品还检查 aux 与合并条件，空槽只接收一种产物。概率产物预留完整容量，每个原始条目只抽取一次概率，拆到多个槽也不会重复抽取。

普通处理器在完工时扣料并产出；发电机在开工时扣料，完工时产出。发电机沿用存档中的配方索引恢复已扣料批次，输出阻塞时保留该批次；完成但未交付的批次解堵后只补交产物，不重新扣料或再发一轮电。

执行器懒缓存配方条目、按槽输入索引、身份匹配结果及物品最大堆叠信息；一轮选方共用一次物品库存读取。缓存核对配方对象、缓存类身份及四个输入输出字段的内容，字段或元素修改、浅拷贝与缓存类更新后会重新编译；标签缓存按实际物品 ID 与 aux 区分。库存、分配结果和随机结果不跨调用缓存，实际加工前按最新库存重新分配。配方应在初始化阶段完成登记，新增配方可继续通过集合的 `add_recipe()` 登记；运行中修改配方内容不会自动重建 MiniJEI/MEI 的登记索引。自定义匹配/结算的专用机器仍按各自流程执行，例如电动机件加工台；通用处理器的适配不会替代它们的专用逻辑。

合金炉的全部 20 条内置配方使用无序输入组 `(0, 1, 2, 3)`，输出保持有序并固定使用槽 4。`AlloyFurnaceRecipe` 保留原构造器、工厂参数与专用序列化格式；输入字典键只决定展示顺序，输出字典键仍指定实际产出槽位。材料可以换位或拆到多个输入槽；槽 4 容量不足时停止加工，不占用第二输出槽 5。

压缩机的 17 条单材料配方使用无序输入组 `(0, 1, 2)`，支持任一输入槽或跨槽凑量；4 条多材料配方保留固定输入槽，产物仍放入槽 3。`CompressorRecipe` 根据输入条目数量选择单材料无序或多材料有序，构造器、工厂参数和专用序列化格式保持一致。其他内置配方仍使用各自的固定槽定义。

## 类型与原实现

| 正式导出名称 | 原实现与签名 |
| --- | --- |
| `AirCompressorRecipe` | [air_compressor.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/air_compressor.py) |
| `AlloyFurnaceRecipe` | [alloy_furnace.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/alloy_furnace.py) |
| `ChargerRecipe` | [charger.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/charger.py) |
| `CompressorRecipe` | [compressor.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/compressor.py) |
| `CyroHeatMeltingChamberRecipe` | [cyro_heat_melting_chamber.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/cyro_heat_melting_chamber.py) |
| `DistillationChamberRecipe` | [distillation_chamber.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/distillation_chamber.py) |
| `EngraverRecipe` | [engraver.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/engraver.py) |
| `FluidCondenserRecipe` | [fluid_condenser.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/fluid_condenser.py) |
| `FreezerRecipe` | [freezer.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/freezer.py) |
| `GasBurningGeneratorRecipe` | [gas_burning_generator.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/gas_burning_generator.py) |
| `HydroponicBedRecipe` | [hydroponic_bed.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/hydroponic_bed.py) |
| `HydroponicBedSandRecipe` | [hydroponic_bed_sand.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/hydroponic_bed_sand.py) |
| `MaceratorRecipe` | [macerator.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/macerator.py) |
| `MachineryWorkstationRecipe` | [machinery_workstation.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/machinery_workstation.py) |
| `MagmaCentrifugeRecipe` | [magma_centrifuge.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/magma_centrifuge.py) |
| `MagmaFurnaceRecipe` | [magma_furnace.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/magma_furnace.py) |
| `MetalPressRecipe` | [metal_press.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/metal_press.py) |
| `MixedMaceratorRecipe` | [mixed_macerator.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/mixed_macerator.py) |
| `MixerRecipe` | [mixer.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/mixer.py) |
| `OilExtractorRecipe` | [oil_extractor.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/oil_extractor.py) |
| `PrecisionCutterRecipe` | [precision_cutter.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/precision_cutter.py) |
| `ReactingThermalGeneratorRecipe` | [reacting_thermal_generator.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/reacting_thermal_generator.py) |
| `RedstoneGeneratorRecipe` | [redstone_generator.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/redstone_generator.py) |
| `SawmillRecipe` | [sawmill.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/sawmill.py) |
| `TemplateAssemblerRecipe` | [template_assembler.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/template_assembler.py) |
| `VacuumFreezerRecipe` | [vacuum_freezer.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/machinery/vacuum_freezer.py) |
| `IndustrialResearchingRecipe` | [industrial_researching.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/misc/industrial_researching.py) |
| `MetalHammerRecipe` | [metal_hammer.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/misc/metal_hammer.py) |
| `GenericCraftingTableRecipe` | [common_recipe_cls.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/common/common_recipe_cls.py) |
| `GenericFurnaceRecipe` | [common_recipe_cls.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/common/common_recipe_cls.py) |
| `GenericBlastFurnaceRecipe` | [common_recipe_cls.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/common/common_recipe_cls.py) |
| `GenericSmokerRecipe` | [common_recipe_cls.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/common/common_recipe_cls.py) |
| `Description` | [description.py](../../behavior_pack/skybluetech_scripts/skybluetech/common/mini_jei/common/description.py) |

## 普通追加与专用集合

普通处理器在初始化阶段通过原集合的 `add_recipe()` 扩展，例如磨粉机、熔岩炉和红石发电机。客户端与服务端必须各执行一次，且在机器运行和查询缓存建立前完成。不要新建同名集合，不修改已有类的渲染器来增加一条配方。

并非所有机器仅遍历通用配方列表。冷冻机使用模式索引，水培床按种子 ID 查询，模板装配台按产物 ID 查询；其专用集合还维护 `recipes_mapping`。通用 `add_recipe()` 不会更新这些业务映射，本次门面也不新增专用索引更新或模式/UI 扩容协议。导出类型可用于创建附属自己的集合；向上述内置机器扩展前，需要先设计并验证它们的专用登记流程。低温熔融室配方类型存在，也不代表其机器实现已在当前版本启用。

`GenericCraftingTableRecipe`、`GenericFurnaceRecipe` 等包装 ToolDelta 已读取的原版配方资源；把包装对象加入 MiniJEI 并不会向引擎创建原版工作台/熔炉配方。真正的原版配方仍需行为包 JSON。

## 机器配方的共享界面

机器配方内容统一维护在 `resource_pack/ui/MachineRecipeLib.json`。`RecipeCheckerLib` 的 29 个机器/杂项配方定义保留原名作为 MiniJEI 薄包装；`ui/mei_recipes/` 的 32 类内容包装使用同一份布局。原版工作台、熔炉系列和说明页仍由 MiniJEI 原组件渲染。

共享布局通过 `$recipe_item_slot`、`$recipe_fluid_slot`、`$recipe_power_hover`、`$recipe_progress_hover` 选择两边各自的槽位和提示组件。默认组件属于蔚蓝，MiniJEI 不需要安装 MEI。新增或调整机器布局时，在公共内容中修改位置和尺寸，在包装中选择组件，不再复制一份 MiniJEI 机器布局。

普通机器的槽位事实表位于 `common/define/recipe_layouts.py`，MEI 旧 `_layouts.py` 只重导出此表。`inputs` / `outputs` 用 `(种类, 真实槽位号)` 映射到内容的 `body/input/<i>` / `body/output/<i>`，不能把稀疏槽位或物品/流体同号槽位直接当成格子序号。工具和模板使用 `body/cat/<i>`；水培、加工台、研究和金属锤保留各自的内容结构。

MiniJEI 包装的内容根为 `content`，普通行宽 180px。渲染器保留自己的查询、数量、概率、流体小数、点击跳转和收藏逻辑；附属自有 UI 定义仍可使用原来的平铺控件路径。内容需要随配方扩高时，渲染器通过 `GetRenderHeight(recipe)` 声明高度，同分类按最大行高分页。

可运行 `node tools/validate_recipe_ui.cjs` 检查共享模板、依赖和控件路径；可追加本地 MEI 资源包路径检查它的组件选择。这些检查不执行项目 Python。游戏内仍需检查未安装/安装 MEI 两种情况下的机器配方、材料与流体点击、工具提示、分页/返回、指南内嵌加工台，以及水培/沙培的作物预览。
