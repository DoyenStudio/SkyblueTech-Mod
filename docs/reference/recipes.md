# 内置配方类型与扩展边界

[返回手册](../README.md) · [配方扩展教程](../tutorials/06-extensions.md)

下面的类型均从 `common.export.recipes` 直接重导出。它们保留原构造签名、类身份与已有渲染器；按源码中各类的 `__init__` 传参，不将 `MachineRecipe` 的通用签名套到所有子类。

## 基础能力

- `Input(id, count=1, aux=0, is_tag=False)` 与 `Output` 描述输入输出；物品槽与流体槽分开编号。
- `RecipeBase`、`Recipe`、`MachineRecipeBase`、`MachineRecipe`、`GeneratorRecipe` 用于自定义类型。
- `RecipesCollection.get_collection(name)` 取原集合，缺少名称会抛 KeyError；`add_recipe(recipe)` 追加到原列表并注册 MiniJEI 查询。
- `GetRecipesByInput`、`GetRecipesByOutput`、`GetRecipesByCategory` 与 `RegisterRecipe` 是已有查询/登记接口。
- `MarshalInputs`、`MarshalOutputs`、`UnmarshalInputs`、`UnmarshalOutputs` 为现有配方序列化工具。
- `gen_preset_recipe`、`gen_tagged_preset_recipe` 是磨粉配方工厂；`Description` 与 `RegisterDescription` 用于说明页。

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
