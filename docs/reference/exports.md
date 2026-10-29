# 正式导出入口

[返回手册](../README.md)

以下模块名前缀统一为 `skybluetech_scripts.skybluetech.`。附属使用 `ImportModule(完整模块名)` 获取模块，不直接跨包 `import`。门面重导出原对象，旧导入路径仍有效；`isinstance`、配方集合及枚举仍与主模组共用同一份对象。

| 模块后缀 | 使用侧 | 内容 |
| --- | --- | --- |
| `common.export.addon_registry` | 两端分别调用 | `RegisterAddonNamespace`、命名空间与 MiniJEI 分类查询 |
| `common.export.events` | 两端，按事件种类监听 | 两端 Loaded 事件、`IsServerLoaded`/`IsClientLoaded` 就绪查询、`MachineryOperationC2S`、`TransmitterSwitchAccessMode` |
| `common.export.machinery` | 两端 | `K_*` 同步键、流体槽类型、`SimpleEnum`、`Upgraders`、`flags`、`Thermal`、结构调色板 |
| `common.export.recipes` | 两端 | `Input`、`Output`、`CategoryType`、配方基类、集合、注册/查询及[内置配方类型](recipes.md) |
| `common.export.fluids` | 两端 | 流体分类、基础材质、`RegisterFluidTexture`、`GetFluidTexture` |
| `server.export.machinery` | 服务端 | 18 个机器基类、注册/查询、事件分发器、结构检测 |
| `server.export.networks` | 服务端 | 网络/接入点/逻辑/操作基类、方向常量、流体网络复用组件 |
| `server.export.transmitters` | 服务端 | `RegisterItemPipe`、`RegisterFluidPipe`、`RegisterWire` |
| `server.export.transmitter_visual_checker` | 服务端 | `RegisterTransmitterType` |
| `client.export.machinery` | 客户端 | 机器面板、附加设置页、流体/功率/进度控件工具、配方查看按钮 |
| `client.export.recipes` | 客户端 | `RecipeRenderer`、`MachineRecipeRendererBase`、`MachineRecipeRenderer`、`GeneratorRecipeRenderer` |
| `client.export.guidance` | 客户端 | `AddAddition`、`pages_define` |

`server.export` 根模块也提供三个管线注册函数和检查器注册函数。其他能力使用上表具名子模块，不依赖根模块隐式加载全部实现。所有导出清单以对应文件的 `__all__` 为准。

## 关键签名

```python
RegisterAddonNamespace(namespace, display_name=None)
RegisterMachine(machine_cls)                 # 装饰器，返回原类
GetMachineCls(block_name)                    # 未注册会抛 KeyError
TryGetMachineCls(block_name)                 # 未注册返回 None
GetLoadedMachine(dimension, x, y, z)          # 只查已加载实例，可能 None
GetMachineWithoutCls(dimension, x, y, z, block_id=None)
RecipesCollection(collection_name, *recipes)
RecipesCollection.get_collection(collection_name)
RegisterFluidTexture(fluid_id, basic_texture)
```

流体材质只有 `BasicFluidTexture(texture_path, flipbook_frames, ticks_per_frame=1)` 一个数据类。`RegisterFluidTexture(fluid_id, basic_texture)` 直接保存该实例，`GetFluidTexture(fluid_id)` 直接返回该实例，不再经过 `FluidTexture` 包装，也不接收 RGB / alpha。颜色和透明度需预先乘算进 PNG，UI 直接使用贴图本身的 RGBA。

命名空间注册不会自动注册机器、配方、流体、GUI 或资源；两端各有注册表。配方集合名称使用唯一机器 ID，通过 `get_collection()` 取得原集合并在初始化时 `add_recipe()`。不要创建同名新集合来“扩展”，那会替换集合注册项。

流体网络复用门面提供 `FluidPipeNetwork`、`FluidPipeAccessPoint` 和 `TransferFluidNetwork(network)`（原运输函数的别名）。运输函数会先排出缓冲再从输出槽抽取，按接入点优先级分配；它使用内置按方块 ID 的流体过滤规则，未登记 ID 没有额外过滤。独立协议若需要不同的路由或过滤，应编写自己的运输回调。

## 加载与兼容

先等待前置的对应侧加载，再导入有注册副作用的门面。不要为了监听 Loaded 事件而提前导入主模组整棵业务包；[注册教程](../tutorials/01-addon.md)给出独立事件桥接。

新增门面没有复制旧实现，也没有要求旧附属迁移。新教程要求本次开发版提供的符号；缺失时应明确提示不兼容，不悄悄退回内部映射修改。不要把 `common` 理解成任意时机都可导入：它表示两端可用，仍需 ToolDelta 和前置完成初始化。

## 源码

- [公共门面目录](../../behavior_pack/skybluetech_scripts/skybluetech/common/export/)
- [服务端门面目录](../../behavior_pack/skybluetech_scripts/skybluetech/server/export/)
- [客户端门面目录](../../behavior_pack/skybluetech_scripts/skybluetech/client/export/)
