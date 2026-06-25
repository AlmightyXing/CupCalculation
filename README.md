# 《杯级计算器》(Whats Your Cup)

> 《明日方舟》六星干员数值量化分析工具。

## 项目简介

在统一基准（1000甲 / 20抗）下，对干员的伤害与治疗能力进行加权评分与**杯级评定**。

## 技术架构

- **计算引擎**：Python，实现完整的《明日方舟》属性修饰器公式（四种修饰器）和五种伤害公式
- **LLM 解析**：DeepSeek API（兼容 OpenAI SDK），将技能文字描述解析为结构化参数
- **前端**：微信小程序（Phase 2）
- **后端**：微信云开发（Phase 3）

## 目录结构

```
CupCalculation/
├── data/
│   ├── raw/           # PRTS Wiki 原始 HTML（待实现抓取）
│   ├── processed/     # 干员 JSON 文件（输入）
│   │   └── llm_cache/ # LLM 解析结果缓存
│   └── output/        # 计算输出结果
├── src/
│   ├── calculator/
│   │   ├── models.py      # 数据模型定义
│   │   ├── attribute.py   # 属性计算器（四修饰器公式）
│   │   ├── damage.py      # 五种伤害公式
│   │   ├── dps.py         # DPS/HPS/总伤计算
│   │   └── cup_rating.py  # 杯级评定算法
│   └── parser/
│       ├── llm_parser.py  # DeepSeek API 技能解析
│       └── data_loader.py # JSON 数据加载
├── tests/
│   └── test_calculator.py # 单元测试
└── pipeline.py            # 流水线入口脚本
```

## 环境配置

### 1. 激活虚拟环境

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. 安装依赖

```powershell
pip install openai pytest
```

### 3. 配置 DeepSeek API Key

```powershell
# PowerShell（临时，仅当前会话有效）
$env:DEEPSEEK_API_KEY = "your-api-key-here"

# 或写入 .env 文件（推荐，需要安装 python-dotenv）
echo DEEPSEEK_API_KEY=your-api-key-here > .env
```

## 使用方式

### 运行单元测试

```powershell
python -m pytest tests/ -v
```

### 测试单个干员（跳过 LLM，手动填 skill_params）

```powershell
python pipeline.py --single data/processed/char_325_mlynar.json
```

### 完整流水线（LLM 解析 + 计算）

```powershell
# 将干员 JSON 放入 data/processed/ 后运行：
python pipeline.py --input data/processed --output data/output/result.json
```

### 仅重新计算（跳过 LLM，使用已有缓存）

```powershell
python pipeline.py --input data/processed --output data/output/result.json --skip-llm
```

## 干员 JSON 格式

参考 `character_sample.json`，关键字段说明：

| 字段 | 说明 |
|------|------|
| `base_atk` | 精二满级攻击力（**不含**信赖） |
| `confidence_atk` | 信赖提供的攻击力加成 |
| `atk_time` | 基础攻击间隔（秒） |
| `skill_type` | `"auto"`（挂机）或 `"manual"`（决战） |
| `duration` | 决战技能持续时间（秒），挂机技能填 `null` |

计算引擎会自动将 `base_atk + confidence_atk` 合并为最终攻击力。

## 计算基准（PRD §5.1）

| 参数 | 标准值 |
|------|------|
| 物理防御 (DEF) | 1000 |
| 法术抗性 (RES) | 20 |
| 干员状态 | 精二满级、0潜能、技能专三 |
| 模组 | 默认满级模组数值 |

## 杯级阶梯

| 综合排名百分比 | 杯级 |
|:---|:---|
| 前 10% | 超大杯·上 |
| 10%~20% | 超大杯·中 |
| 20%~30% | 超大杯·下 |
| 30%~50% | 大杯 |
| 50% 以下 | 中杯 |
