# 《杯级计算器》 工作日志

**时间戳**：2026-06-25 21:50（UTC+10）

---

## 一、阶段目标

基于 PRD v1.1（`Whats_Your_Cup_PRDv1.1.md`）和伤害计算文档（`伤害计算.md`），完成项目离线计算端的完整脚手架搭建，实现可本地独立运行和验证的核心计算引擎。

---

## 二、文档勘误（用户确认）

| 原计划描述 | 实际正确值 | 说明 |
|---|---|---|
| 真银斩 +200% → `MULTIPLIER_ATK = 2.0`（误写为 3.0） | `MULTIPLIER_ATK = 2.0`，最终攻击力 = `ATK × (1+2.0) = ATK × 3.0` | +200% 是直接乘算，系数为 2.0，公式中的 3.0 是 `(1+D_t)` 的结果 |
| 计算基准 RES = 40 | RES = **20** | 用户确认标准法术抗性基准为 20 |

---

## 三、新建文件清单

### 3.1 项目配置 / 文档

| 文件路径 | 说明 |
|---|---|
| [`README.md`](file:///e:/Local_AI_Station/CupCalculation/README.md) | 项目说明文档，含环境配置、使用方式、数据格式、杯级阶梯 |

### 3.2 目录结构

| 目录 | 说明 |
|---|---|
| `data/raw/` | PRTS Wiki 原始 HTML 存放目录（Phase 2 抓取器使用） |
| `data/processed/` | 干员 JSON 输入目录（LLM 解析前的原始干员数据） |
| `data/processed/llm_cache/` | LLM 解析结果缓存（避免重复调用 API） |
| `data/output/` | 流水线最终计算输出目录 |

### 3.3 计算引擎（`src/calculator/`）

| 文件 | 核心内容 |
|---|---|
| [`models.py`](file:///e:/Local_AI_Station/CupCalculation/src/calculator/models.py) | 全部数据模型：`TalentData`、`SkillData`、`SkillParams`、`CharacterData`、`CalculationResult`、`RankedOperator`。字段与 `character_sample.json` / `damage_sample.json` 完全对应，并纳入 PRD v1.1 新增的 `manual_damage_total` / `manual_heal_total` 字段 |
| [`attribute.py`](file:///e:/Local_AI_Station/CupCalculation/src/calculator/attribute.py) | 实现四修饰器属性公式：`A_f = F_t × [(A+D_p) × (1+D_t) + F_p]`。含修正规则（任意值<0时补正为原值+1）、属性上下限、调试汇总方法、快捷构建攻击力计算器的 `build_atk_calculator()` 函数；标准基准 `STANDARD_DEF=1000`、`STANDARD_RES=20` 定义于此 |
| [`damage.py`](file:///e:/Local_AI_Station/CupCalculation/src/calculator/damage.py) | 实现五种伤害公式（物理/法术/元素/真实/治疗），使用 `match/case` 统一分发入口 `calc_damage_by_type()`，各类型独立函数便于单独测试 |
| [`dps.py`](file:///e:/Local_AI_Station/CupCalculation/src/calculator/dps.py) | 攻速公式（含 clamp 限幅）、挂机 DPS/HPS（永续 + 全周期平均）、决战总伤 + 平均 DPS、干员全技能批量计算入口 `calculate_operator_stats()` |
| [`cup_rating.py`](file:///e:/Local_AI_Station/CupCalculation/src/calculator/cup_rating.py) | 非线性加权评分：百分比排名→基础分、巅峰加权（前10名×300%乘数）、多技能最优值聚合、综合总分排名、五档杯级阶梯划分 |

### 3.4 数据解析层（`src/parser/`）

| 文件 | 核心内容 |
|---|---|
| [`llm_parser.py`](file:///e:/Local_AI_Station/CupCalculation/src/parser/llm_parser.py) | 调用 DeepSeek API（兼容 OpenAI SDK），内置精心设计的系统提示词（覆盖四修饰器字段说明、伤害类型判断规则、特殊写法映射），支持本地缓存（已有缓存则跳过 API 调用），API Key 通过环境变量 `DEEPSEEK_API_KEY` 注入 |
| [`data_loader.py`](file:///e:/Local_AI_Station/CupCalculation/src/parser/data_loader.py) | 加载 `character_sample.json` 格式文件，自动合并 `base_atk + confidence_atk` 为计算用攻击力，支持批量加载目录下所有干员 JSON |

### 3.5 流水线入口

| 文件 | 核心内容 |
|---|---|
| [`pipeline.py`](file:///e:/Local_AI_Station/CupCalculation/pipeline.py) | 五步完整流水线（加载→LLM解析→计算→评级→输出JSON），支持 `--skip-llm` 跳过解析直接重算，支持 `--single` 调试单个干员并打印详细结果 |

### 3.6 示例数据 / 测试

| 文件 | 核心内容 |
|---|---|
| [`data/processed/char_325_mlynar.json`](file:///e:/Local_AI_Station/CupCalculation/data/processed/char_325_mlynar.json) | 玛恩纳（解放者）示例干员数据，来自用户提供的 `character_sample.json`，用于 LLM 解析和集成测试 |
| [`tests/test_calculator.py`](file:///e:/Local_AI_Station/CupCalculation/tests/test_calculator.py) | 28 个单元测试，覆盖所有核心模块 |

---

## 四、单元测试覆盖情况

**运行结果：28/28 全部通过（0.06s）**

| 测试类 | 测试数 | 覆盖内容 |
|---|---|---|
| `TestAttributeCalculator` | 7 | 无修饰器、加算、乘算、最终乘算、负值补正、真银斩案例、综合公式 |
| `TestDamageFormulas` | 8 | 物理标准/下限/穿透%/穿透固定值、法术标准/下限、真实伤害、治疗、非法类型异常 |
| `TestAttackSpeed` | 5 | 默认攻速、间隔延长、clamp上限、clamp下限、APS换算 |
| `TestCupRating` | 4 | 五档阶梯、单干员顶级、排名顺序、巅峰加权触发 |
| `TestIntegration` | 3 | 玛恩纳最终攻击力（385×1.8=693）、物理伤害（5%下限=34.65）、28s决战总伤端到端 |

---

## 五、关键设计决策记录

| 决策 | 选择 | 原因 |
|---|---|---|
| LLM 接入方式 | DeepSeek 远程 API（兼容 OpenAI SDK） | 用户指定 |
| 计算基准 RES | 20 | 用户确认 |
| 多技能聚合策略 | 同一干员各字段取最大值参与排名 | 体现干员最强技能的极限能力 |
| LLM 缓存机制 | 按 `{character_id}_skill{id}.json` 粒度缓存 | 避免重复计费，支持部分重跑 |
| 信赖加成处理 | 加载时自动合并 `base_atk + confidence_atk` | PRD §5.1 标准：默认满信赖状态 |

---

## 六、待办（Phase 2 起点）

- [ ] **PRTS 数据抓取**：实现 `src/crawler/prts_crawler.py`，从 `prts.wiki` 抓取干员 HTML 并转换为 `character_sample.json` 格式
- [ ] **微信小程序框架**：搭建首页（杯级榜单）、子榜单、搜索页、干员详情页
- [ ] **微信云开发对接**：将 `data/output/result.json` 上传至云数据库，前端轻量拉取展示
- [ ] **时光机模块**：历史版本快照存储与切换功能
