# GUIControl GUI 控制基类

带有 GUI 的机器基类。

## 类属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| bound_ui | str \| None | 绑定的 UI key, 如果为自定义容器, 此处设置为 None |

## 事件订阅
```python
self.handler.SubscribeOnClick(self.on_click)
```
用于通知玩家打开 GUI。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| event | ServerBlockUseEvent | 玩家点击事件 |
| extra_datas | dict \| None | 额外数据。默认为 None |

---

```python
self.handler.SubscribeOnUnload(self.on_unload)
```
用于通知玩家关闭 GUI 和将同步项关闭。

---

```python
self.handler.SubscribeOnSync(self.on_sync)
```
用于将机器数据同步到客户端 UI。
