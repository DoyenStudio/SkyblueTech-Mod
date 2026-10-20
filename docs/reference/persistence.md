# 原生存档规范

[返回手册](../README.md)

`BlockEntityData` 支持原生 `dict` / `list` 和字符串、int、float、None、bool。不要频繁 JSON 编码整台机器状态；使用附属自己的键前缀，避免覆盖主模组字段。

- 保存前递归复制可变数据；对整数校验范围，转换为 Python 2 `int`，不要直接写 `long`，即使数值很小。
- 字典键显式规范为字符串；同时存在 `1` 与 `"1"` 等规范化冲突时拒绝保存，不静默覆盖。
- 每一层列表的元素类型必须一致；不同结构或标量类型混排会导致 NBT 保存失败。记录使用命名字典，槽位用字符串键，升级配置用物品 ID 到数量的字典。
- 修改嵌套值后必须执行 `bdata[key] = 新快照`；仅修改缓存里的子字典不会持久化。
- 热量、进度、余量直接保存 float，接受引擎可能采用 float32 的精度。tuple 重载可能变 list，不依赖 tuple 身份。
- 即时读回只能证明缓存更新。必须检查序列化 NBT 和退出重进后的状态。

以下片段是确定结构的保存示例，不是通用序列化器：

```python
from stdb_scripts.tooldelta.utils.py_comp import py2_long

def save_counter(bdata, count, heat):
    if isinstance(count, bool) or not isinstance(count, (int, py2_long)):
        raise TypeError("count must be integer")
    if count < 0 or count > 2147483647:
        raise ValueError("count outside persisted int range")
    bdata["stdb:state"] = {
        "count": int(count),
        "heat": float(heat),
        "outputs": {"0": {"item": "minecraft:sand", "count": 1}},
    }
```

主模组的 `K_*` 键、流体槽和发电配方进度由各组件维护。自定义字段遵循上述规范即可，不要重写组件已有存档方案。新格式不增加旧 JSON 整体状态兼容层。
