# 蔚蓝科技附属开发手册

面向网易《我的世界》Python 2.7.13 附属开发者。本文档对应 **2026-10-20 当前开发工作区**，新增 `export` 门面与管线注册接口不代表所有已发布版本均已提供。发布附属前应检查前置版本和所需符号。

## 从这里开始

| 顺序 | 教程 | 完成后得到 |
| --- | --- | --- |
| 1 | [注册附属与加载顺序](tutorials/01-addon.md) | 两端依赖入口、命名空间与可靠的初始化链 |
| 2 | [第一台机器](tutorials/02-first-machine.md) | 可放置、可点击、可保存的计数器 |
| 3 | [配方机器与发电机](tutorials/03-recipe-machines.md) | 磨粉、熔融、燃料发电三个完整逻辑示例及界面 |
| 4 | [扩展已有管线](tutorials/04-transmitter-grades.md) | 高速物品管道、流体管道、电缆和动态更新 |
| 5 | [创建独立管网](tutorials/05-custom-network.md) | 泵驱动流体网络及可视化检查器接入 |
| 6 | [其他常用扩展](tutorials/06-extensions.md) | 配方、MiniJEI、UI、流体、指南、升级与多方块入口 |

示例统一使用 `stdb` 命名空间、`stdb_scripts` 脚本包。各教程标明附属内的文件位置，代码使用 Python 2 语法；复制示例时，主模组代码仍由前置提供，不打包进附属。

## 参考与设计资料

- [正式导出 API 与版本边界](reference/exports.md)
- [内置配方类型与扩展边界](reference/recipes.md)
- [18 个机器基类与组合选择](reference/machinery/README.md)
- [机器事件与生命周期](reference/lifecycle.md)
- [管线注册与运行中更新](reference/transmitters.md)
- [管道网络可视化检查器](reference/transmitter_visual_checker.md)
- [原生存档约定](reference/persistence.md)
- [验收与常见故障](reference/validation.md)
- [模型设计资料](design/README.md)

## 示例来源与使用边界

太阳能附属 `skybluetech_solarpanel` 的实际入口是 `behavior_pack/stasp_scripts/entry.py`，重点参考其加载事件桥接、按侧 `ImportModule`、命名空间注册、配方扩展和指南入口。核能附属 `skybluetech_nuclear` 的入口为 `stnc_bp/stnc_scripts/entry.py`，独立管网位于 `stnc/server/transmitters/pipe_pressurized/`。

它们是设计与用法参考，不是本手册的运行时依赖。核能旧代码中的 `TransmitterType.PIPE` 在当前主模组不存在；本手册改用字符串类型 ID。跨模组只通过 ModSDK `ImportModule` 获取模块，再使用具名的正式导出。ToolDelta 通用 API 和事件不重复造一套。

源码链接均指向本仓库相对路径；无需读者拥有作者电脑上的 `D:/addon` 目录。本文档的静态核对和游戏内验收是两种独立证据，见[验收记录](reference/validation.md)。
