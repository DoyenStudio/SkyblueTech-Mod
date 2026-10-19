# WorkRenderer 工作状态渲染基类

表示一个存在 active 状态的机器方块基类。
机器外观会随 active 状态的改变而改变。

派生自 `BaseMachine` 基类。

基类会在构造时直接向 `self.handler` 订阅所需事件, 无需重声明空方法。

## 事件订阅
```python
self.handler.SubscribeOnWorkStatusUpdated(self.on_work_status_updated)
```
当机器工作状态改变时执行的操作。
例如, 改变机器的外观, 播放音效等。
