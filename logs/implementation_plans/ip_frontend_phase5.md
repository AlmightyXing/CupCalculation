# 方案 Phase 5：交互流串联与真实数据绑定

## 🎯 目标
将我们之前硬编码并跑通的 WXML UI 与真实的后端 JSON 数据串联起来。实现从“总杯榜/列表页”点击干员卡片，跳转至“干员详情页”，并通过 `wx.request` 动态请求后端的真实技能、天赋和面板数据进行渲染。

## 🛠️ 方案详情

### [MODIFY] backend/main/api_server.py
当前后端仅提供了一个全量干员列表的 API（`/api/operators`）和战斗模拟 API（`/api/simulate`），我们将新增一个查询干员详细数据的端点：
- **新增 Endpoint**: `GET /api/operator/{name}`
- **功能**: 根据干员名称，从 `OperatorRepository` 内存中提取并返回对应的完整 JSON 数据。

### [MODIFY] frontend/components/operator-card/operator-card.wxml & .js
这是首页与各榜单的干员卡片组件。我们需要为其加上点击跳转的交互：
- **wxml**: 为最外层的 `table-row` 容器加上 `bindtap="goToDetail"` 和 `data-name="{{item.name}}"` 属性。
- **js**: 实现 `goToDetail` 方法，调用 `wx.navigateTo` 携带 `name` 参数跳转到 `/pages/detail/detail` 页面。

### [MODIFY] frontend/pages/detail/detail.js
全面移除写死的 `loadMockData` 逻辑。
- 在 `onLoad(options)` 中提取传递来的干员 `name`。
- 调用 `frontend/utils/request.js` 中的 `get` 方法访问 `http://127.0.0.1:8000/api/operator/{name}`。
- 将返回的真实数据对象挂载到 `this.setData({ operator: res.data })` 上。
- *兼容性处理*：由于目前的爬虫数据 `parsed_data/*.json` 中尚未严格包含英文名、标签等装饰性字段，我们将使用逻辑短路（如 `enName: res.data.enName || 'UNKNOWN'`）为其填充占位符，保证 UI 不会因空指针崩溃。
- *动态伤害展板*：对于尚未与 `/api/simulate` 联调的具体伤害排名和数值，我们暂时在给 `operator.skills` 赋值时赋予占位的默认字符串（如 "等待演算"），以便后续 Phase 6 全面引入战斗计算引擎。

## ❓ User Review Required
> [!IMPORTANT]
> 1. 上述对于 `enName`、`position`、`tags` 以及尚未实时演算出的 `dps` 字段使用“默认展位符”的方式是否可以接受？
> 2. 我们是否需要我顺手把 `api_server.py` 跑起来，这样您就可以在微信开发者工具中直接点击体验完整的跳转和真实 JSON 加载链路了？

## 🧪 验证计划
1. 修改完成后，启动后端 `api_server.py`。
2. 在微信开发者工具中点击首页的“乌尔比安”或“锏”。
3. 观察是否能成功发生页面跳转。
4. 验证进入详情页后，展示的天赋和技能数值是否是我们刚才在上一阶段清理出来的真实数据。
