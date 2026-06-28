# 补全干员子职业父类代码架构计划

目前的 `professions.py` 仅仅包含了一小部分硬编码的子职业，且多数默认设定了不准确的 `attack_interval = 1.0`。
这导致部分干员计算攻速和 DPS 时可能使用错误的基准时间，同时缺失的职业类会导致部分新干员（如本源术师、撼地者等）继承失败或使用默认保底逻辑。

## User Review Required
> [!IMPORTANT]
> 由于《明日方舟》干员的阻挡数 (block_count) 并没有包含在目前的爬虫 JSON 中，但它又可能决定了群攻干员（如强攻手、撼地者）的最大打击目标数上限。
> 为了彻底一劳永逸地解决 `professions.py` 的数据填充问题，我计划编写一个自动代码生成脚本 `generate_professions.py`，通过调用大模型（Gemini）一次性处理我们刚才提取的 45 个子职业数据，让大模型自动推断阻挡数，并生成严谨的 Python 代码覆盖 `professions.py`。
> 
> 请确认是否同意这一计划并执行？

## Proposed Changes

### 自动生成脚本
#### [NEW] `backend/src/crawler/generate_professions.py`
编写一个脚本，读取刚才提取到的 `scratch_professions_data.json`，并将所有 45 个职业的中文名、特性描述和攻击间隔等数据作为 Prompt 发送给大模型。
大模型将被要求：
1. 生成标准的继承自 `Operator` 的 Python Class。
2. 填入准确的 `attack_interval`。
3. 利用自身的游戏知识库，根据职业名称（如“重剑手”、“阵法术师”）推断合理的基准 `block_count`。
4. 在类内部的注释或文档字符串中记录职业特性 (Trait)。

### 子职业基类模块
#### [MODIFY] `backend/function/logic/professions.py`
由上述脚本全量覆盖生成，包含全部 45 个子职业的正确初始化逻辑。

## Verification Plan
1. 运行 `generate_professions.py`。
2. 检查生成的 `professions.py` 是否包含所有 45 个职业，语法是否正确。
3. 随机抽查几名干员的阻挡数和攻击间隔是否被正确设定（例如：重剑手阻挡数为2或3，速射手阻挡数为1且攻击间隔为1.0）。
