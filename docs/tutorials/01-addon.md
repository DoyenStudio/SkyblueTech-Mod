# 1. 注册附属与加载顺序

[返回手册](../README.md) · [下一步：第一台机器](02-first-machine.md)

本章建立名为 `stdb` 的教学附属。准备独立行为包、资源包及各自 manifest，脚本包放在行为包 `stdb_scripts/`。不要复制主模组；附属自带的 ToolDelta 与已发布太阳能附属一样放在 `stdb_scripts/tooldelta/`。Studio 测试世界同时加载两个模组。

```text
behavior_pack/
  manifest.json
  stdb_scripts/
    __init__.py
    modMain.py
    entry.py
    tooldelta/              # 项目使用的 ToolDelta 库
    stdb/
      __init__.py
      common/
        __init__.py
        modules.py
        loaded_events.py
      server/__init__.py
      client/__init__.py
resource_pack/
  manifest.json
  texts/zh_CN.lang
  ui/_ui_defs.json
```

所有未展示内容的 `__init__.py` 先留空。manifest 的 UUID 必须独立，工程与包配置使用 Studio 当前模板；不要复用主模组或示例附属的 UUID。行为与资源清单也必须在测试世界中启用。

## 跨模组导入边界

附属内部使用 `stdb_scripts` 绝对导入。取主模组对象统一经过下面的包装；ModSDK 的按侧 `ImportModule` 在当前 ToolDelta API 中没有现成包装，所以仅在此边界选择原始 API，业务代码不重复选择客户端/服务端。

`stdb_scripts/stdb/common/modules.py`：

```python
# coding=utf-8
from stdb_scripts.tooldelta.internal import InServerEnv

def ImportModule(module_name):
    if InServerEnv():
        import mod.server.extraServerApi as api
    else:
        import mod.client.extraClientApi as api
    return api.ImportModule(module_name)

def RequireModule(module_name):
    module = ImportModule(module_name)
    if module is None:
        raise RuntimeError("STDB requires current SkyblueTech: " + module_name)
    return module
```

## 等待前置，同时兼容附属后加载

主模组和附属的 ToolDelta 各自有事件命名空间。参考太阳能附属，用自己库定义监听前置的事件桥，而不是把附属的同名普通事件误当成前置事件。

`stdb_scripts/stdb/common/loaded_events.py`：

```python
# coding=utf-8
from stdb_scripts.tooldelta.events.basic import ServerEvent, ClientEvent

class SkyblueTechServerLoaded(ServerEvent):
    name = "SkyblueTechServerLoaded"

    @classmethod
    def GetNamespace(cls):
        return "SkyblueTech"

    @classmethod
    def GetSystemName(cls):
        return "SkyblueTech.TDServer"

    def marshal(self):
        return {}

    @classmethod
    def unmarshal(cls, data):
        return cls()

class SkyblueTechClientLoaded(ClientEvent):
    name = "SkyblueTechClientLoaded"

    @classmethod
    def GetNamespace(cls):
        return "SkyblueTech"

    @classmethod
    def GetSystemName(cls):
        return "SkyblueTech.TDClient"

    def marshal(self):
        return {}

    @classmethod
    def unmarshal(cls, data):
        return cls()
```

`stdb_scripts/entry.py`：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import ImportModule
from stdb_scripts.stdb.common.loaded_events import (
    SkyblueTechServerLoaded, SkyblueTechClientLoaded,
)

_server_started = False
_client_started = False
_server_listening = False
_client_listening = False
EVENTS = "skybluetech_scripts.skybluetech.common.export.events"

def _start_server(_):
    global _server_started
    if _server_started:
        return
    from stdb_scripts.stdb import server
    _server_started = True

def _start_client(_):
    global _client_started
    if _client_started:
        return
    from stdb_scripts.stdb import client
    _client_started = True

def init_server():
    global _server_listening
    if not _server_listening:
        SkyblueTechServerLoaded.Listen()(_start_server)
        _server_listening = True
    events = ImportModule(EVENTS)
    if events is None:
        print("[STDB] SkyblueTech not available; waiting for its loaded event")
    elif not hasattr(events, "IsServerLoaded"):
        raise RuntimeError("STDB requires SkyblueTech addon-export development version")
    elif events.IsServerLoaded():
        _start_server(None)

def init_client():
    global _client_listening
    if not _client_listening:
        SkyblueTechClientLoaded.Listen()(_start_client)
        _client_listening = True
    events = ImportModule(EVENTS)
    if events is None:
        print("[STDB] SkyblueTech not available; waiting for its loaded event")
    elif not hasattr(events, "IsClientLoaded"):
        raise RuntimeError("STDB requires SkyblueTech addon-export development version")
    elif events.IsClientLoaded():
        _start_client(None)
```

模块存在不能证明前置完成业务初始化。新门面的 `IsServerLoaded()` / `IsClientLoaded()` 在广播 Loaded 前置为 True；先订阅、再检查标志可覆盖通知已发生的情况。缺少前置时不导入机器模块，日志会提示等待；发布版可按太阳能附属的 `dependency_warning` 做玩家提示。

`stdb_scripts/modMain.py`：

```python
# coding=utf-8
from stdb_scripts.tooldelta.mod_main import ToolDeltaMod, RegisterMod
from stdb_scripts import entry

@RegisterMod()
class STDB(ToolDeltaMod):
    name = "STDB"
    version = (1, 0, 0)

    def OnServerInited(self):
        entry.init_server()

    def OnClientInited(self):
        entry.init_client()
```

## 两端注册命名空间

以下内容分别放入 `stdb_scripts/stdb/server/__init__.py` 与 `client/__init__.py`：

```python
# coding=utf-8
from stdb_scripts.stdb.common.modules import RequireModule

registry = RequireModule(
    "skybluetech_scripts.skybluetech.common.export.addon_registry"
)
registry.RegisterAddonNamespace("stdb", "附属开发示例")
```

服务端与客户端各维护一份表，均注册才能在相应侧识别附属。MiniJEI 分类出现只说明命名空间注册成功；机器类还需服务端 `@RegisterMachine`，配方需两端导入，界面和配方渲染器需客户端导入。后续章节逐步在这里加入明确导入。

验收：交换加载顺序；重复调用初始化；缺失前置时不导入依赖机器；客户端 MiniJEI 出现“附属开发示例”。不要把前置版本不兼容当成无前置静默忽略。
