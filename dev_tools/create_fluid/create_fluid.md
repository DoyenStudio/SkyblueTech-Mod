---
description: 注册创建新的流体方块
argument-hint: [流体ID] [RGBA] [基础材质路径] [中文名] [是否气体]
arguments: [fluid-id, fluid-rgba-value, fluid-texture-path, fluid-name, fluid-is-gas]
---

创建一个标准的模组内流体. 全流程共 7 步, 也可以直接用 `dev_tools/create_fluid/create_fluid.py` 一步完成 (见文末).

## 0. 动手前先定好三件事

- **基础材质**: 从 `common/define/fluids/texture.py` 的 `BasicFluidTexture` 常量里选 (`WATER` / `LAVA` / `MOLTEN_METAL` / `AIR` ...). 它指向的贴图必须已经在 `resource_pack/textures/terrain_texture.json` 注册.
- **RGBA**: 四个 `0..255` 整数, 并且世界液体 / 流动液体 / 机器 UI 三处保持一致.
- **枚举组**: `CommonLiquid` / `CommonGas` / `Acid` / `HotFluid` / `ExtremeHotFluid`, 这个选择直接决定哪些管道能运输它 (`server/transmitters/pipe/define.py`).

## 1. Behavior Pack: 世界液体方块 (两个 JSON)

在 `behavior_pack/netease_blocks/liquid/` 下创建静态形式 `skybluetech_$fluid-id.json`:

```json
{
    "format_version": "1.21.70",
    "minecraft:block": {
        "components": {
            "netease:liquid": {
                "bucket_name": "skybluetech:$fluid-id_bucket"
            }
        },
        "description": {
            "base_block": "liquid",
            "category": "none",
            "identifier": "skybluetech:$fluid-id"
        }
    }
}
```

再创建流动形式 `skybluetech_flowing_$fluid-id.json`, 流动参数只写在流动文件里:

```json
{
    "format_version": "1.21.70",
    "minecraft:block": {
        "components": {
            "netease:liquid": {
                "bucket_name": "skybluetech:$fluid-id_bucket",
                "spread_delay": 5,
                "spread_range": 8
            }
        },
        "description": {
            "base_block": "flowing_liquid",
            "category": "none",
            "identifier": "skybluetech:flowing_$fluid-id"
        }
    }
}
```

注意:

- `base_block` 静态是 `liquid`, 流动是 `flowing_liquid`, 不要写反.
- `bucket_name` 只在确实要做桶时写, 且两个文件保持一致; 其他可选组件 (`can_float_boat`, `mob_effects`, `remove_effects`, `spread_fire`) 按需求加.
- 不写 `liquid_color`，保留 `netease:liquid` 组件；省略颜色时默认为 `[255, 255, 255, 255]`。颜色和透明度已乘入独立 PNG。

## 2. Resource Pack: 注册方块渲染

在 `resource_pack/blocks.json` 里给两个 ID 各加一个字段. 基础材质有 `_static` / `_flowing` 一对时用四键形式:

```json
"skybluetech:$fluid-id": {
    "blockshape": "water",
    "textures": {
        "down": "skybluetech:baked_$fluid-id_static",
        "side": "skybluetech:baked_$fluid-id_flowing",
        "up": "skybluetech:baked_$fluid-id_static"
    }
},
"skybluetech:flowing_$fluid-id": {
    "blockshape": "water",
    "textures": {
        "down": "skybluetech:baked_$fluid-id_static",
        "side": "skybluetech:baked_$fluid-id_flowing",
        "up": "skybluetech:baked_$fluid-id_flowing"
    }
}
```

基础材质只有单张贴图时 (如 `water_vapor` / `methane_mud` / `gas`), 两个 ID 都写成单键:

```json
"skybluetech:$fluid-id": {
    "blockshape": "water",
    "textures": "skybluetech:baked_$fluid-id_static"
}
```

## 3. 流体枚举

在 `common/define/id_enum/fluids.py` 里把稳定 ID 加进第 0 步选定的组:

```python
class CommonLiquid(Common):
    "对流体管道无特殊要求的液体"

    WATER = Vanilla.WATER
    $FLUID_CONST = "skybluetech:$fluid-id"
```

只加稳定 ID, 不要加 `flowing_` 形式.

## 4. UI 流体材质

在 `common/define/fluids/texture.py` 的 `FLUID_TEXTURES` 里加一行, 它控制机器 UI 里的流体条:

```python
fluids.CommonLiquid.$FLUID_CONST: $MATERIAL_CONST,
```

基础材质若是新的, 先补一条常量 (帧数与帧间隔按贴图实际翻页长度填):

```python
$MATERIAL_CONST = BasicFluidTexture("textures/fluid/baked/skybluetech.$fluid-id/static", 32, 2)
```

## 5. 桶 (可选)

四处加一个分组:

- `behavior_pack/netease_items_beh/buckets/skybluetech_$fluid-id_bucket.json`: 必须是游戏桶 (`custom_item_type: "bucket"`) 或带 `skybluetech:liquid_bucket` 标签, 否则 `fluid_container.py` 不认.
- `resource_pack/netease_items_res/skybluetech_$fluid-id_bucket.json`: 图标 identifier 与桶 ID 同名.
- `resource_pack/textures/item_texture.json`: 加图标条目, 指向 `textures/items/buckets/$fluid-id_bucket`.
- `resource_pack/textures/items/buckets/$fluid-id_bucket.png`: 桶图标本体.
- `behavior_pack/netease_group/skybluetech_bucket.json`: 把桶 ID 加进桶分组的 `list`, 才会出现在创造栏.

约束:

- 桶 ID 必须等于 `<流体ID>_bucket`, 机器是靠砍掉 `_bucket` 反推流体 ID 的, 名字对不上就灌不进机器.
- **桶图标是套模板的**: 全模组桶图标在固定的 24 个像素之外完全一致 (16x16 图标第 3~5 行的一层梯形, 即 `x 4..11` / `x 3..12` / `x 5..10`), 只有这 24 个像素承载流体颜色. 做法就是复制最接近的桶图标, 按模板的相对明暗把这 24 个像素换成目标流体色, 不需要重画.
- **气体桶 = 液体桶整图上下翻转**, 现成的 `water_vapor_bucket.png` 就是 `distilled_water_bucket.png` 的垂直翻转.

## 6. 储罐展示（复用方块贴图）

当前 `client/utils/fluid_model.py` 的 `GetFluidTexturePath()` 通过 `GetBlockTextures(fluid_id)` 读取源流体方块顶面的首个贴图路径。储罐直接复用方块注册的烘焙贴图，不再读取 `textures/fluid_models/`；不要创建该目录或独立的首帧 PNG。

在 `client/utils/fluid_texture_frames.py` 的 `FLUID_TEXTURE_FRAMES` 中登记实际顶面贴图的帧数和每秒帧数，动画速率与 flipbook 一致。不要为旧 `fluid_models` 路径新增登记。

创建脚本仍保留旧的储罐贴图生成步骤，当前调用必须传入 `--no-tank`；该参数只跳过冗余资产，不会禁用游戏内储罐显示。

## 7. 本地化

在 `resource_pack/texts/zh_CN.lang` 补三行 (桶那行视情况):

```text
tile.skybluetech:$fluid-id.name=$中文名
tile.skybluetech:flowing_$fluid-id.name=流动$中文名
item.skybluetech:$fluid-id_bucket.name=$中文名桶
```

## 自检清单

- 稳定 ID / 流动 ID / 桶 ID 都在预期命名空间下, 流体枚举与机器配方只引用稳定 ID.
- 世界源方块、流动方块、UI 均直接使用烘焙 PNG 的颜色和透明度；运行时不再传 RGB / alpha。新流体三处保持一致；迁移前已有差异按各自原值保留。
- `blocks.json` 两个条目的面贴图布局正确, 引用到的图集 key 都存在.
- 选定的枚举类确实产生了期望的管道兼容性.
- 新改 JSON 能被标准 `json` 解析, `git diff --check` 干净.
- 不要跑或编译模组 Python; 进游戏验证液体铺展、颜色透明度、管道运输、UI 与储罐显示、桶的取放 (如果做了桶).

## 一键脚本

以上 7 步可以直接用 `dev_tools/create_fluid/create_fluid.py` (Python 3, 不在打包范围内) 完成:

```bash
python dev_tools/create_fluid/create_fluid.py <mod路径> --id skybluetech:$fluid-id --rgba 0,229,255,128 \
    --material textures/fluid/basic_water_static --name $中文名 --no-tank [--gas]
```

它会按 `entities` / `entity` 标记自行定位行为包与资源包, 依次写入世界液体方块、`blocks.json`、`fluids.py`、`texture.py`、桶 (物品 + 图标 + 分组) 与本地化; 贴图和动画会同步注册，已有注册不会重复插入。使用 `--no-tank` 跳过旧储罐资产生成，另行补齐客户端动画帧登记。建议先加 `--dry-run` 看一眼。

常用参数: `--group` (默认 `--gas` 时为 `CommonGas`, 否则 `CommonLiquid`)、`--no-bucket`、`--no-tank`、`--boat`、`--spread-delay` / `--spread-range`、`--frames` / `--ticks-per-frame`、`--bucket-template`、`--force`.

注意: 脚本不添加机器配方与管道用途 (那属于功能需求), 并且要求基础材质已在 `terrain_texture.json` 注册.

## 离线乘算与迁移资产

RGBA 仅作为离线生成参数保留。静态及流动帧条的全部像素均按
`out[channel] = base[channel] * rgba[channel] // 255` 处理，包括 alpha。
贴图写入 `resource_pack/textures/fluid/baked/<namespace>.<name>/`，
图集键使用 `<namespace>:baked_<name>_static` / `_flowing`；
复制基础图集的 `quad` 和动画的 `replicate`、`ticks_per_frame` 等属性。
UI 的动画帧数及帧间隔默认从基础材质推导，可用参数显式指定。

运行时只保留 `BasicFluidTexture` 数据类。
`RegisterFluidTexture(fluid_id, basic_texture)` 直接保存材质，
`GetFluidTexture(fluid_id)` 直接返回材质，不再有包装类。

`baked_textures.json` 保存本次迁移的基础 PNG 路径和原 RGBA；
它位于开发工具目录，不会随双包发布。可用以下离线命令重新生成这些 PNG：

```bash
python dev_tools/create_fluid/bake_textures.py <mod路径>
```

本次保留原有差异：硫酸流动 alpha 为 64，源方块/UI 为 128；
润滑油流动 alpha 为 128，源方块/UI 为 192；气体世界与 UI 基础图不同；
深板岩熔岩源方块有乘色而 UI/流动方块没有，轻/中熔岩流动方块也沿用原无乘色外观。
