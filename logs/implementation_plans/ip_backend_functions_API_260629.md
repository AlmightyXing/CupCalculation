# FastAPI 后端 API 搭建实现计划

该计划标志着系统正式迈入第 5 阶段，目标是将底层的战斗引擎和 129 个动态干员脚本封装为标准化的 HTTP 接口，为接下来的前端 UI 提供数据源。

## Proposed Changes

### 1. 依赖安装
- 执行 `pip install fastapi uvicorn pydantic` 安装后端核心框架。

### 2. 干员仓库 (Operator Repository)
#### [NEW] `backend/main/operator_repo.py`
提取 `run_team_synergy.py` 中的动态加载逻辑，创建一个在内存中驻留的仓库：
- `load_all_operators()`: 在服务器启动时，遍历 `data/parsed_data` 下的 JSON 以及 `backend/function/logic/operators` 下的 Python 脚本，将所有 129 名干员的 Python Class 与 JSON 基础数据建立映射并缓存到内存中，避免每次请求都去读写硬盘。

### 3. FastAPI 服务器主程序
#### [NEW] `backend/main/api_server.py`
创建核心 Web API 应用。

**定义核心路由 (Endpoints):**
- `GET /api/operators`: 获取所有受支持的干员列表（干员名、ID、职业等），供前端渲染选人下拉框。
- `GET /api/enemies`: 获取支持的测试木桩列表（如轻甲、重甲、极限等）。
- `POST /api/simulate`: 核心计算接口。
  - **请求体 (Request Body)**:
    ```json
    {
      "enemy_level": 3, // 选择重甲木桩
      "team": [
        {"name": "仇白", "skill_index": 2},
        {"name": "铃兰", "skill_index": 2}
      ]
    }
    ```
  - **处理逻辑**: 实例化请求的干员，注入所选技能，组装并运行 `BattleEnvironment.simulate()`。
  - **响应体 (Response Body)**: 组装战斗引擎返回的全队最终总伤、DPS 报告以及提取到的全局 Buff 列表。

## Verification Plan

### 自动化与手动测试
1. 执行 `uvicorn backend.main.api_server:app --reload` 启动本地服务器。
2. 使用系统预装的 curl/Invoke-RestMethod 进行接口调用测试：
   - 测试 `/api/operators` 能否秒级返回 129 个干员的元数据。
   - 提交一个带有团队协同的 `/api/simulate` POST 请求，验证能否稳定触发 Monkey Patching 并返回正确的伤害（与之前的 `run_team_synergy.py` 数据一致）。
3. 检查是否有内存泄漏或路径加载错误。

> [!IMPORTANT]
> 服务器加载机制决定了每次重启才读取最新干员逻辑。这完全符合生产环境的设计。此 API 架构极其灵活，如果后期增加新的前端展示字段，也只需在路由中微调。请您审阅。
