# 阶段性成果：完全 Serverless 与面向对象的后端重构

我已全面根据您的反馈和设计指南，完成了新架构的底盘搭建。从这一刻开始，我们的系统彻底告别了“本地计算脚本”，进化为了支持完整模拟运作的“后端微服务系统”。

## 1. 结构与组件大洗牌
> [!NOTE]
> 我们完全贯彻了您要求的包规范（`src`, `function`, `main`）。
> 删除了旧版的 `calculator` 和硬编码管道 `pipeline.py`。

- **`data/`** 得到了最严密的层级化管理：`Operators`, `Enemies`, `raw_data`, `parsed_data`。
- 新增了 **`backend/src/crawler/batch_fetch.py`**：接入了 ArknightsGameData (Kengxxiao)，这使得我们**现在能够获取全部 182 名 6 星干员**的名单，并以此构建未来的全自动拉取。

## 2. 核心架构逻辑设计 (面向对象体系)
遵循您**“读取后进行动态搭建”**的原则，我在 `backend/function/logic` 和 `backend/function/battle` 中构建了整个模拟战斗的物理层：

1. **统一抽象实体**：
   开发了 `Operator` 和 `Enemy` 基础基类。不仅保存生命值等数据，还预留了被 buff 影响的“战斗状态”变量，以便承接复杂数值交互。
2. **战斗空间核心 (BattleEnvironment)**：
   开发了 `backend/function/battle/engine.py`，作为所有敌人和干员的对象池。我们在里面采用了直接**宏观公式计算器**，不仅实现了干员与敌人的多对多战斗模拟交互，还有效规避了无谓的 0.033s 时间轴运算造成的性能消耗。
3. **“动态搭建”引擎 (Builder)**：
   我在 `logic/builder.py` 编写了一个高度智能的扫描引擎。它将扫描 `parsed_data` 的干员 JSON 数据。**如果检测到前所未见的职业（比如“重射手”），它会自动在 `professions.py` 中为您生成这个父类！**随后再将具体干员生成为独立的 Python 实体对象，放入 `logic/operators/`。

## 3. Web 服务准备
在 `backend/main/` 包下，我使用 **FastAPI** 编写了 `app.py`。这是一个符合微服务化概念的服务器。一旦我们需要运行模拟，直接发送前端或 Postman 的请求至 `POST /api/simulate`，它将在后台将对象投入“对战空间”并以 JSON 返回最终 DPS 报表。

## 4. 下一步
> [!IMPORTANT]
> - 由于刚才服务器发生了重启，当前环境里的 `DEEPSEEK_API_KEY` 变量已经丢失，且批量处理 182 名 6 星干员的数据会耗费一定时间和额度。
> - 您可以在终端中确认 API_KEY 并随时运行 `python backend/src/crawler/batch_fetch.py` 开始全量洗库。一旦跑完，我们就能运行 `builder.py` 看它帮我们炫技般地“动态生成所有干员类”。
