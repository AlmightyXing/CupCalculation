# Phase 6 修订与新功能计划 (Combat Sandbox)

由于收到前端设计的勘误反馈，现调整系统流转逻辑，并引入“战斗环境（沙盒）”模块，让全量榜单展示与动态单体计算严格分离。

## Proposed Changes

### 1. 任务单修订 (`前端设计与开发任务单.md`)

#### [MODIFY] 前端设计与开发任务单.md

将 Phase 6 中“前后台联动”的描述更新为：榜单数据严格读取自后端 `data/Operators` 的静态 JSON 文件。并新增“战斗环境模拟”任务项，明确由该模块调用引擎进行实时的指定干员+指定 Buff+指定敌人的自定义计算。

### 2. 榜单全量展示 (`frontend/pages/index/index.js`)

#### [MODIFY] index.js

移除目前在 `processListData` 中对数据的 `slice(0, 10)` 截断逻辑，使得“总杯榜”、“挂机榜”、“决战榜”均完整渲染所有 130 名干员。
> **性能考量**：考虑到上百名干员同屏渲染在微信小程序中可能引起卡顿，我们会将原先的 Top10 限制移除。但如果后续测试发现滑动严重掉帧，我们会在 Phase 7 中引入 Virtual List（长列表虚拟渲染）或分页机制。

### 3. API 与后端逻辑调整 (`backend/main/api_server.py` & `backend/function/battle/rank_engine.py`)

#### [MODIFY] rank_engine.py

剥离 `generate_ranking` 中的“静默自动补全计算”逻辑。
现在，`/api/rankings` 接口将**只负责纯粹的读取**，直接读取 `data/Operators/operator_{def}_{res}.json` 并返回。如果本地 JSON 不存在或缺失某些干员，它也不会去主动跑 `calculate_dps` 阻塞请求。

#### [MODIFY] api_server.py

新增专门用于“战斗环境”沙盒的 API 接口：
`POST /api/sandbox/simulate`
接收：干员名、技能序号、敌人护甲、敌人法抗、(可选)指定 Buff 等。
返回：实时的秒伤与总伤演算结果。
这个接口会直接调用 `backend/function/logic/operators` 里的脚本进行现场跑分。

### 4. 前端战斗环境模块预研 (New Sandbox Page)

#### [NEW] frontend/pages/sandbox/sandbox.wxml / .wxss / .js

创建一个全新的沙盒页面，供玩家：

1. 下拉/搜索选择“指定干员”与“特定技能”。
2. 输入或选择“敌人护甲/法抗/血量”。
3. 勾选“特定增益（如拐）”。
4. 点击“开始演算”，调用后端的 `POST /api/sandbox/simulate` 获取真实的战斗报告。

---

## User Review Required

> [!WARNING]
> **关于静态 JSON 的生成**
> 如果 `/api/rankings` 不再动态计算缺失干员，我们需要有一个一次性的脚本或管理接口来**事先生成**那 6 个基准护甲/法抗下的全量 JSON 文件。我会在后台写一个 `precalculate.py` 脚本来为您把这 6 个文件统统生成好存入 `data/Operators`。您是否同意此做法？

## Open Questions

> [!IMPORTANT]
> **关于新增的战斗环境页面**
> 对于新增的沙盒测试页面（战斗环境），您是否希望将其放在首页底部导航栏（TabBar）的一个独立 Tab 里，还是作为详情页里的一个衍生入口（例如点击“进入模拟”按钮）？
