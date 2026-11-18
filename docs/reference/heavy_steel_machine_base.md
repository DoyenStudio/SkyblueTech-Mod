# 重型钢机械底座

方块 ID：`skybluetech:heavy_steel_machine_base`，创造栏与 MEI 均有“重型钢机械底座”组。

工作台有序合成每次产出一个：中心一个殷钢板，上下左右各一个铁栏杆，四角各一个钢板。
板材输入使用 `common:invar_plate` 与 `common:steel_plate` tag，铁栏杆使用 `minecraft:iron_bars`。
配方见 [重型钢机械底座合成](../../behavior_pack/netease_recipes/skybluetech_heavy_steel_machine_base_craft.json)。

材质来自 `D:/addon/chisel_blocks` 的 `chisel_blocks:tyrian__plate`，
即截图中的“未来风格金属块（闪亮镶板）”，整面银灰镶边款。
同名的 `tyrian__elaborate` 是交错板款，本方块采用 `plate`。
四张 16×16 图原样复制到
`resource_pack/textures/blocks/multi_block_structure/heavy_steel_machine_base/`，
目录内 `SOURCE.txt`、GPLv2 许可及上游 README 保留来源信息。

只与同类底座连接，使用现有六向状态、事件去重队列和区块边界修复。
每面四个 8×8 象限由面内两条直接邻边选择原图、横接、竖接或无边图；不读取对角。
模型 48 组可见性条件、96 个备选面片，每状态每面显示四片。
内部面使用独立剔除层，物品栏显示完整有框图。

生成：`node tools/generate_heavy_steel_machine_base_connections.cjs`

静态验收：`node tools/validate_multiblock_connections.cjs`。

2026-11-17 静态检查通过：底座 64 种六向连接状态的六面逐像素覆盖、材质选择、
UV 和剔除引用均正确，四张 PNG 与来源逐字节一致，重复生成无变化；
包含现有外壳和导热块的全部 2112 组渲染场景检查通过。
当前开发桥连接 chisel_blocks 会话，未加载 SkyBlueTech，游戏内验收尚待进行。

游戏内需检查：单块、横纵直线、L 形、2×2、缺对角及上下连接；拆放、
快速重放、跨区块及存档重进；与其他外壳不连接；物品栏、创造栏、MEI、挖掘掉落和内部面剔除。
