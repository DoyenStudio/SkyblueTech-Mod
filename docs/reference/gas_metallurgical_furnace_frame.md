# 气体冶金炉方块与连接纹理

> 2026-11-17 控制器业务、两物品槽、16 条加工配方与 UI 已补齐，运行规格与正式结构入口见 [实现记录](../../dev_todos/gas_metallurgical_furnace.md)。本页其余“仅外观／接口”表述记录前一阶段的外观验收范围。


已创建外壳、控制器和八种接口，创造栏与 MEI 均位于“气体冶金炉”组。
接口已复用现有 Interface 的缓冲、传输、保存与界面；控制器仍只有方块和外观，
整机加工、内部槽位、接口绑定与结构组装尚未实现。

全部方块使用 `skybluetech:gas_metallurgical_furnace_` 前缀：

| ID 后缀 | 中文名 | 材质文件 |
| --- | --- | --- |
| `frame` | 气体冶金炉外壳 | `frame` 及其三种连接变体 |
| `controller` | 气体冶金炉控制器 | 正面 `controller_front`／`controller_front_active`，其他五面为外壳 |
| `io_item_in` | 气体冶金炉物品输入口 | `io_item_in` |
| `io_item_out` | 气体冶金炉物品输出口 | `io_item_out` |
| `io_gas_in` | 气体冶金炉主气体输入口 | `io_gas_in` |
| `io_gas_in_2` | 气体冶金炉辅助气体输入口 | `io_gas_in_2` |
| `io_gas_out` | 气体冶金炉气体输出口 | `io_gas_out` |
| `io_fluid_in` | 气体冶金炉流体输入口 | `io_fluid_in` |
| `io_fluid_out` | 气体冶金炉流体输出口 | `io_fluid_out` |
| `io_energy_in` | 气体冶金炉能量输入口 | `io_energy_in` |

## 材质和连接

炉壳连接纹理最初取自 `D:/addon/chisel_blocks` 的“铝块 (格雷科稽)”
（`chisel_blocks:blockaluminum__badgreggy`，Chisel contributors，GPLv2），现为本地调整版本。
控制器和接口使用本轮提供的 16×16 PNG。所有材质均位于
`resource_pack/textures/blocks/multi_block_structure/gas_metallurgical_furnace/`。

每面按四个 8×8 象限分区；每个象限根据面内水平、垂直两个直接邻块，
选择原图、水平连接、垂直连接或完全无边图同位置 UV。
四张原图的中心明暗和螺丝并非只在窄边框内变化，因此不使用固定宽度边框或单像素螺丝近似。
每个象限再分成两个外围矩形和一个中心矩形，四块中心拼成对应尺寸的固定区域：

- 控制器、物品口：8×8，像素范围 `[4,12) × [4,12)`。
- 主／辅助气体输入口、气体输出口、流体输入／输出口：6×6，像素范围 `[5,11) × [5,11)`。
- 能量输入口：4×4，像素范围 `[6,10) × [6,10)`。

控制器只在局部 north 正面显示面板，其余五面保持外壳 CTM；八种接口无朝向，六面中心显示对应图案。
外围仍使用四种 CTM 纹理，原外壳中心也继续按原规则采样。
不查对角，本家族十种方块互相连接，与其他外壳、导热块保持独立。

复用 `multiblock_shell_connections.py` 的六向状态、拆放事件、去重队列和区块边界修复。
三种中心尺寸分别使用模型及剔除规则，每个模型仍为 48 个可见性条件组、288 个备选面片，
每种状态每面恰好显示 12 个无重叠矩形。三者共用本家族的剔除层，保持不同接口之间的内部面剔除；
物品栏使用完整有框方块。所有中心均保持原位置 UV 和像素比例，不缩放贴图。

控制器保留 `y_rotation_offset: 180`，四向模型旋转为 north=0、east=-90、south=180、west=90。
`skybluetech:active` 默认为 false，切换时只替换正面中心材质。仅实际推进配方时使用
`controller_front_active.png`；未成形、成形待机、缺电、输出堵塞及批次完成均使用
`controller_front.png`。恢复加工后重新点亮。材质 ID 保留
`skybluetech:gas_metallurgical_furnace_controller_active`，仅更新其 PNG 路径。
物品栏将控制器正面映射至可见的 south 面。

## 接口行为

接口由 `server/machinery/gas_metallurgical_furnace_interfaces.py` 显式注册，
复用已有通用接口类、界面和保存方式：

| 接口 | 通用行为 |
| --- | --- |
| 物品输入／输出口 | 各 5 个缓冲槽，对应既有输入／输出界面、物品管道和漏斗方向 |
| 主／辅助气体输入、流体输入 | 各自独立的 8000 mB 输入槽，复用 `FluidInputInterface` |
| 气体输出、流体输出 | 各自独立的 8000 mB 输出槽，复用 `FluidOutputInterface` |
| 能量输入口 | 复用 `EnergyInputInterface`，未绑定控制器时传输额度为零，拒收且不消耗 RF |

气体口沿现有气体接口方式复用通用流体接口，本轮不增加气液类别过滤或配方白名单。
流体输出口沿既有规则允许桶／试管手动装填，管道只向外抽取。
接口的 5 个物品缓冲槽与计划中控制器的 1 输入／1 输出加工槽属于不同层；
控制器搬运物料、处理配方及自动切换 active 的后续实现见 [实现记录](../../dev_todos/gas_metallurgical_furnace.md)。

生成：`node tools/generate_gas_metallurgical_furnace_connections.cjs`

静态验收：`node tools/validate_multiblock_connections.cjs`，每种方块覆盖六向全部 64 种连接组合。

该家族覆盖 1088 组场景：外壳 64、八种接口 512、控制器四朝向与双状态 512。
检查六面像素覆盖、中心面板、外围 CTM、原位置 UV、旋转、剔除和 PNG 引用；
包含其他外壳及导热块的全部场景共 3136 组。重复生成应无输出变化。
离线工具只处理资源和源码文本，不执行或编译模组 Python。

2026-11-17 静态验收通过：全部 3136 组场景及方块注册检查通过，17 个生成输出重复生成逐字节一致；
原有其他家族资源和本轮提供的 14 张 PNG 均未改动。

## 游戏内验收

- 单块、横纵直线、L 形、2×2、缺对角、上下连接，检查螺丝、明暗和外框。
- 控制器四朝向及两种 active 状态，接口六面中心在各种连接下保持完整。
- 混用本家族十种方块，检查接缝与内部面剔除。
- 拆除后接缝恢复，快速重放、跨区块加载及退出重进后连接正确。
- 确认不与其他多方块外壳、导热块相连，内部面剔除正确。
- 检查创造栏、MEI、中文名、物品栏图标和挖掘掉落。
- 检查物品口的玩家／漏斗／管道进出方向，主辅气口独立存储，流体界面与桶／试管交互。
- 检查接口库存跨区块加载与重进保存，能量口未绑定控制器时不接收或消耗 RF。

以上游戏内场景尚未验收。后续机器能力与槽位见 [气体冶金炉待办](../../dev_todos/gas_metallurgical_furnace.md)。
