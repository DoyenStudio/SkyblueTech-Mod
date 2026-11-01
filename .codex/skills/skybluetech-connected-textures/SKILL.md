---
name: skybluetech-connected-textures
description: 为 SkyBlueTech／网易基岩版多方块外壳制作或修复脚本驱动的连接纹理，处理六向状态、邻边与角、螺丝点、共享 edgeless、控制器旋转和物品栏朝向。适用于类似电池仓的方块连接渲染，不用于普通贴图绘制或实体建模。
---

# 脚本驱动的方块连接纹理

以 SkyBlueTech 电池仓实现为已验证案例。将这里的几何分区和状态更新方法用于相似方块时，先确认其贴图尺寸、连接集合、正面方向及展示需求；不要把电池仓的像素坐标、材质名或用户选择强加到其他项目。

## 找到实现入口

在 SkyBlueTech 仓库根目录工作（本机为 `D:/addon/skybluetech`），按任务读取：

| 工作 | 入口 |
| --- | --- |
| 分区、UV、可见性、材质、物品展示 | `tools/generate_battery_matrix_connections.cjs` |
| 六向状态与更新事件 | `behavior_pack/skybluetech_scripts/skybluetech/server/misc/battery_matrix_connections.py` |
| 规则、版本、手工验收 | `docs/reference/battery_matrix_connections.md` |
| 四种外壳 | `behavior_pack/netease_blocks/multiblock/skybluetech_battery_matrix_{frame,controller,io_energy1,io_energy2}.json` |
| 模型和剔除 | `resource_pack/models/blocks/battery_matrix_connected.geo.json`、`resource_pack/block_culling/battery_matrix.json` |
| 贴图和注册 | `resource_pack/textures/blocks/multi_block_structure/battery_matrix/`、`resource_pack/textures/terrain_texture.json` |

修改生成器后从仓库根目录执行 `node tools/generate_battery_matrix_connections.cjs`。不要只改生成结果，否则下一次生成会覆盖修复。无需复制生成器到技能中。

## 连接定义与脚本

电池仓采用六个布尔状态 `skybluetech:connection_north/east/south/west/up/down`，默认 false，全部由脚本设置。用户已选择不使用 `minecraft:connection`；这里的“自定义 connection trait”是脚本与自定义状态的组合，不是在 JSON 中发明引擎未支持的 trait 键。

- 电池仓框架、控制器、输入口、输出口互相连接，核心除外；只查六个直接邻居，不查对角，也不依赖结构组装成功。
- 世界方向：north=-Z、south=+Z、east=+X、west=-X、up=+Y、down=-Y。每个面的边使用该面切平面内的邻居，不把面法线邻居当成面内的一条边。
- 用放置、移除、邻块变化、区块加载事件驱动，待更新坐标去重；移除回调同步读取可能仍是旧块，延后再刷新自身及六邻居。按现有 `ExecLater` 用法执行，不新增逐 tick 全量扫描。
- 保留已有朝向、active 等状态；只在值变化时写回。`GetBlockNew` 返回原生字典或 None，比较 `name` 字段；None 表示不可读，不能直接当空气清空连接。
- 当前连接只依赖方块类型，可忽略 from/to 方块名相同的邻块通知，避免状态写回循环。如果新需求依赖邻块状态，需要重新设计这条过滤。
- 区块加载要修复本区块及邻区块边界，包括新加载区块没有外壳的情况；卸载时清理索引。当前实现靠 blockEntities 枚举外壳，旧存档无方块实体的框架是否补建需要游戏内验证。

脚本沿用 ToolDelta 事件包装与 `skybluetech_scripts.tooldelta.srv` 的 `CF, LEVEL_ID`。新增 API 或事件行为先查现有代码或 minecraft_docs（短中文关键词），不猜接口。保持 Python 2.7.13 兼容，不在系统 Python 中执行或编译模组代码。

## 面分区与角规则

先从原图确定边框厚度和细节位置。电池仓是 16×16 图、两像素边框：外环拆成四条边和四个 2×2 角，内部为 12×12。每个区域使用单面几何和独立 UV 采样，不拉伸整个贴图来消除边框。

设角对应的水平、垂直直邻连接状态为 H、V：

| H | V | 2×2 角的采样 | 螺丝 |
| --- | --- | --- | --- |
| false | false | 有边框原图同位置 | 显示 |
| true | false | 有边框图的水平直边条，延续剩余边框 | 隐藏 |
| false | true | 有边框图的垂直直边条，延续剩余边框 | 隐藏 |
| true | true | 公共 edgeless 同位置 | 隐藏 |

电池仓单边连接角的源坐标：只有 H 为真时，把 sourceU 改成左角 2／右角 12；只有 V 为真时，把 sourceV 改成上角 2／下角 12。目标位置仍是原来的 2×2 角。两直邻都连接但缺少对角块，也不补一个依赖对角的内角。

螺丝位于 `(2,2)`、`(13,2)`、`(2,13)`、`(13,13)`，在 12×12 内部，不能只处理外侧 2×2 角。将中心拆为 `(u,v,w,h)=(3,2,10,12),(2,3,1,10),(13,3,1,10)`，给四个螺丝留下单独的 1×1 孔。螺丝片归入已有角骨骼：`!H && !V` 取原图螺丝，否则取公共 edgeless 同位置底色。不要叠加共面的遮盖片，否则可能闪烁。

## 共享 edgeless 与 identifier

复用贴图前逐像素比较对应区域，不能仅凭“来自同一张图”就把整面替换。电池仓此前四张专用 edgeless 的外环与公共图一致，中心与各自原图一致，因此已删除专用 PNG 及其新增注册，只保留公共 `frame_edgeless`。

当前材质分工：

- `side/front`：有边框原图，保存面板、接口符号和螺丝。
- `edgeless`：统一使用 `skybluetech:battery_matrix_frame_edgeless`，用于连接边、双连接角及被隐藏螺丝的底色。
- `side_center/front_center`：连接后的中心。框架和控制器侧面使用 frame_edgeless；控制器前面板及输入、输出口使用各自有边框原图。active 排列也同步保持正确的前面板纹理。
- 孤立状态采样有边框原图；中心中的四个螺丝仍由局部角条件单独决定。

不要把面板中心也映射成 frame_edgeless，或让中心大面片继续包含始终可见的螺丝。重命名 PNG 时只改路径及对应引用，保留原有材质 identifier；仅在用户要求清理且确认无引用后删除专用注册和文件。备份文件不因未引用就自动删除。

## 方向、旋转和物品栏

区分世界连接状态、模型局部方向、放置偏移和物品显示。电池仓世界模型正面为 north，保存的 `minecraft:cardinal_direction` 已包含 `y_rotation_offset: 180`。保持这个 offset，不要在连接映射中再次加 180 度。

电池仓排列的 Y 旋转为 north=0、east=-90、south=180、west=90。对局部水平序列 `[north,east,south,west]`，世界方向索引为 `(localIndex + facingIndex) % 4`；up/down 不变。此公式对应当前模型和排列，其他模型要根据自己的旋转推导。

查看 manifest 的 `min_engine_version`，不能仅凭实际客户端版本判断 Molang 语义。本次 1.18.0 兼容语义下，嵌套三元表达式结合性及逻辑优先级会造成两侧连接状态为真却仍有边。方向选择采用每项完整加括号的或式：`((朝向 == north) && 对应状态) || ((朝向 == east) && 对应状态) || ...`，外层也加括号，再用于更大的条件。不要改回未分组的混合逻辑或嵌套三元。

当前生成器先在世界／局部方向坐标中构造面，再对导出几何 X 取反。沿用它的 faceAxes 与坐标转换，避免一面 UV 镜像或东西互换；不要把该实现的 X 转换无条件推广到其他建模工具。

物品栏通过独立 `minecraft:item_visual` 展示完整有边框方块。电池仓的 full_block 物品模型将前面板映射到可见的 `south` 面，使图标朝向玩家；世界模型仍以 north 为正面，保留放置 offset。自定义物品模型要另行验证可见面，不能为了物品栏改世界旋转。

## 几何规模与剔除

合并相同可见性条件的面片到同一骨骼，避免超过方块几何 64 个 bone_visibility 条目的限制。电池仓目前是 2 个中心条件组 + 12 个边条件组 + 48 个角条件组 = 62；螺丝复用角组，不为每个螺丝再加条件组。

当前 276 个备选单面片，每种状态每面恰好 15 个不重叠区域。数量是此实现的校验线索，不是其他模型的目标。保持 UV 边界与每像素一个模型单位。

外壳共用 culling_layer，剔除规则引用具体 bone、cube 索引、face。新增中心或螺丝片后同步重新生成剔除规则。不要为了剔除把不参与连接的核心并入外壳连接集合。当前方块格式 1.21.90 用于稳定的 culling_layer 支持，不代表需要原生 connection；不要擅自升级 manifest 或实验开关。

## 有效验证

按改动选择验证，不把静态检查表述为游戏内验收：

1. 检查 JSON、PNG 路径、材质引用、删除资产的残留引用；重复生成应无变化。PNG 复用检查 RGBA 区域，特别是中心图案、active 和四个螺丝像素。
2. 几何／条件改动枚举六向 64 种连接组合及控制器四朝向。检查每面 256 个像素恰好覆盖一次、无重叠或空洞，螺丝只在对应两直邻均 false 时取原图；独立核对世界到局部映射。当前四种外壳总计 448 组朝向／连接场景。
3. 目标客户端检查孤立、直线、L 形、2×2、缺对角，以及上下连接；控制器四朝向与 active，物品栏前面板、外轮廓螺丝、接口图案和内部面剔除。
4. 脚本改动另查拆放、快速重放、区块边界和存档重载。修改 JSON／资源后可用现有开发桥的 addon+game reload；仅在工具可用且该开发会话适合重载时使用。截图确认具体视觉，不能代替状态／引用检查。

对于“连接状态为真但仍有边”，先核对该面使用的世界方向、offset 是否重复、旧 Molang 括号和实际生效排列；对于“正面图案消失”，先核对中心材质；对于“内部残留深色点”，先核对中心是否挖出了螺丝像素。
