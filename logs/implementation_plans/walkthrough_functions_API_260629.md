# 战斗环境与团队增益实现报告 & Backend API

## 阶段四：战斗框架大修完毕

1. **敌人实体系统重构** (`backend/function/battle/enemy.py`)
   - 为 `Enemy` 基类注入了全局状态字段：`is_cced`（是否被控）、`global_fragile`（全局脆弱）、`global_arts_flat_dmg`（全局法伤附加）。
   - 添加了快速生成从 0 防 0 抗到 5000 防 100 抗的 6 种标准木桩模型（以及专为本次协同测试生成的 `99号：2000防40抗木桩`）。
2. **抽象基类标准化** (`backend/function/logic/base_operator.py`)
   - 制定了包含 4 大类别、12 个细分属性的完整 `Buff 协议`。在基类 `Operator` 补充了虚方法 `get_team_buffs()`，供所有提供团队收益的“拐”调用。
3. **战斗引擎的 Monkey Patching (核心亮点)** (`backend/function/battle/engine.py`)
   - `BattleEnvironment.simulate()` 在战斗启动前，会抓取在场所有干员通过 `get_team_buffs` 暴露的团队增益，包括最大脆弱值、总减抗、受控状态等。
   - **动态劫持底层公式与注入环境**：拦截了 `formulas.py` 的物理和法伤公式，自动在每次伤害结算时附加全局法伤与最终脆弱乘区。并能在伤害计算前为干员叠加鼓舞面板，计算后复原。这使得我们不必去碰此前大模型生成的 129 个干员的独立算法，实现了 100% 的底层降维覆盖。

## 阶段五：FastAPI 后端集成搭建

为对接后续的前端 Web UI，我们将这一套计算逻辑封装成了标准化的 HTTP 接口：

1. **干员内存仓库** (`backend/main/operator_repo.py`)
   - **零延迟缓存**：在服务器启动时，系统会将 `data/parsed_data` 下的 129 份 JSON 数据与对应的 Python 脚本类一一映射，驻留在内存中。无需每次发起模拟请求时都去读写硬盘或使用低效的 `eval`。
2. **Web API 服务器** (`backend/main/api_server.py`)
   - **`GET /api/operators`**: 秒级返回所有干员的基础列表（已根据稀有度和姓名排序），可直接用于填充前端下拉列表。
   - **`GET /api/enemies`**: 返回标准的 0~5 级沙包，以及 99 号测试木桩的信息。
   - **`POST /api/simulate`**: 暴露了核心演算功能。前端传入选择的队伍名单，API 动态拼装干员模型，送入 `BattleEnvironment` 后返回结算总伤、DPS 和生成的 Buff 面板列表。

## 测试结果验证 (API 模式)

我们通过测试脚本对 HTTP `POST /api/simulate` 路由发起了仇白、逻各斯、铃兰开启三技能共同攻击 `2000防御/40法抗` 木桩的测试。

结果不仅 HTTP 状态码为 `200 OK`，而且引擎顺利实现了全队 Buff 数据提取并计算出了预期的结果：

- **自动提取的增益数据**:
  - `fragile`: 0.4
  - `res_shred`: 10.0
  - `arts_flat_dmg`: 150.0
  - `is_cced`: True
- **结算伤害**:
  - **仇白 (S3)**: 70,610.87 (因 100% 触发控制和附加伤害吃满红利)
  - **逻各斯 (S3)**: 53,859.9
  - **铃兰 (S3)**: 0.0

> [!TIP]
> 泛用的团队环境机制及后端 Web Server 已经完全搭建完毕！系统现在可以独立作为后端微服务运行。您可以随时执行 `uvicorn backend.main.api_server:app --reload` 启动它！
