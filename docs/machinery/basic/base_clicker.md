# BaseClicker 可点击机器基类

不具有自定义容器属性但是可被方块点击响应的机器类。
继承了此类的机器可订阅经点击限流处理的 handler 事件,
例如, 玩家手持方块点击机器时不再会同时放下方块。

## 类属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| onclick_delay | float | 点击间隔（秒）, 默认为 0.25 |

## 事件订阅
```python
self.handler.SubscribeOnClick(self.on_click)
```
机器被玩家点击时调用。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| event | ServerBlockUseEvent | 玩家点击事件 |
| extra_datas | dict \| None | 额外数据。默认为 None |
