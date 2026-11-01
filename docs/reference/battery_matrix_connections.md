# 电池仓连接纹理

框架、控制器、能量输入口和能量输出口互相连接；储能核心不参与。每个面的四条邻边独立判断，不查询对角方块，也不要求多方块结构已经组装完成。

## 连接来源

连接特征通过六个自定义布尔方块状态实现：`skybluetech:connection_north/east/south/west/up/down`。全部由脚本根据直接邻居是否为上述四种外壳设置，纹理条件直接读取这些状态。核心、普通实心方块和对角方块均不参与连接。

不注册引擎不支持的自定义 JSON trait，也不依赖原生连接 trait、原生连接规则或额外的水平筛选状态。控制器继续使用原有放置朝向 trait。

`server/misc/battery_matrix_connections.py` 使用放置、邻块变化、移除和区块加载事件更新这些状态。更新延迟到下一 tick 并去重，仅在状态变化时写入，保留朝向、激活状态等其他状态。区块加载后延迟修复本区块及相邻区块边界的外壳；读取不到邻块时不把它当空气。没有逐 tick 扫描，也不写 `BlockEntityData`。

框架增加不启用 tick 的方块实体，以便区块加载事件可以枚举；四种外壳都启用邻块变化及移除通知。已有存档从无方块实体的旧框架定义升级时，仍需游戏内验证区块枚举是否补建，必要时重新放置旧框架。

## 材质与几何

有边框贴图和原有材质 identifier 保持不变，无边框区域统一复用 `skybluetech:battery_matrix_frame_edgeless`（`frame_edgeless.png`），不使用备份图。控制器正面（含激活态）、能量输入口和输出口的四张专用无边框图及其新增注册已移除：它们外侧两像素环与公共图逐像素一致，中心 12×12 区域与各自有边框原图逐像素一致。

共享模型 `battery_matrix_connected.geo.json` 将每面划分为中心、两像素边条和角区域。有连接的边使用公共无边框图；角区域仅由它相邻的两条边决定。只连接一条边时延长剩余直边，两条边都连接时使用公共无边框角。孤立方块完全采样原图；有连接时，框架及控制器侧面中心采样 `frame_edgeless`，控制器前面板和输入、输出口中心仍采样各自原图，保持图案及激活态不变。中心使用独立材质实例，避免共用无边框图时覆盖面板图案。

每面的四个深蓝色螺丝点位于贴图像素 `(2,2)`、`(13,2)`、`(2,13)`、`(13,13)`。仅当该角对应的两条邻边都未连接时，采样原图中的螺丝点；任意一边连接时，改采样公共 `frame_edgeless` 同位置的底色。不查询对角方块。中心区域挖出这四个像素并交由已有角区域条件控制，避免图案上残留固定螺丝或叠面闪烁。

模型使用 62 个可见性骨骼组、276 个备选单面片，每种连接状态实际覆盖每面十五个不重叠区域。保持一像素对应一模型单位，不修改或重采样 PNG。外壳之间的内部面通过同一 culling layer 剔除。控制器保留现有朝向旋转和激活材质，骨骼条件将局部方向映射回世界方向；物品栏使用完整有边框方块模型。

控制器的 `y_rotation_offset: 180` 已作用于存储的 `minecraft:cardinal_direction`，连接方向映射不能再叠加一次。当前 manifest 的 `min_engine_version` 为 `1.18.0`，Molang 会使用旧版嵌套三元结合性和逻辑运算优先级；因此方向选择使用四组显式括号包裹的“朝向匹配且对应世界方向已连接”条件，再将它们取或，避免左右连接状态为真却仍显示边框。

控制器的 `minecraft:item_visual` 单独将前面板材质映射到物品栏可见的 `south` 面，使物品图标展示前面板；世界模型仍以 `north` 为正面，并保留 `y_rotation_offset: 180` 及四向旋转。

这些重复 JSON 由开发工具维护：

```powershell
node tools/generate_battery_matrix_connections.cjs
```

该入口只处理四个电池仓外壳定义、共享模型、剔除规则和公共无边框材质注册；不运行模组 Python。分区与条件实现位于 `tools/lib/generate_multiblock_connections.cjs`，与基岩熔岩钻复用；修改后分别执行两个生成入口。服务端也共享原有事件与队列，但按机器类型分组，电池仓与基岩熔岩钻不互相连接。

## 版本与游戏内验收

四种外壳的格式版本为 `1.21.90`，用于现有模型剔除的 `culling_layer` 正式支持；连接逻辑本身不再要求原生连接 trait 或其对应实验开关。网易客户端仍需支持使用中的几何和剔除组件。本次未修改 pack manifest 或世界实验开关。

静态核查不能替代目标客户端验收。导入后检查：

1. 孤立四类外壳均保留完整边框；物品栏和掉落物显示正常。
2. 分别沿 X、Y、Z 放置同类和混合外壳，检查共享边消失、外轮廓保留；核心和普通石块不消除边框。
3. 搭建 L 形及 2×2 面；仅对角放置不连接，两个直邻都有而对角缺失时不补内角。
4. 控制器四种朝向、激活前后均检查六个面，确认前面板不换面、边框方向不反转。
5. 拆除、快速重新放置、通过现有接口创建外壳后检查邻块；跨正负区块坐标边界测试卸载、重载及存档重进。

参考：[方块状态与排列](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockstatesandpermutations)、[放置朝向偏移](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/traits/placement_direction#rotation-offset)、[Molang 版本兼容规则](https://learn.microsoft.com/en-us/minecraft/creator/documents/molang/syntax-guide#versioned-changes)、[方块剔除规则](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockcullingreference/examples/blockcullingrules/block_culling)。
