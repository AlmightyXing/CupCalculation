from typing import Dict, Any, List

class Operator:
    """
    所有干员的基础抽象类。
    """
    def __init__(self, data: Dict[str, Any]):
        self.character_id = data.get("character_id", "")
        self.name = data.get("name", "")
        self.profession = data.get("character_type", "")
        
        # 基础面板
        self.base_atk = data.get("base_atk", 0)
        self.base_def = data.get("base_def", 0)
        self.base_hp = data.get("base_hp", 0)
        self.base_res = data.get("base_res", 0.0)
        
        # 由职业父类或具体子类设定的属性
        self.attack_speed = 100
        self.attack_interval = 1.0
        self.block_count = 1
        self.redeploy_time = 70
        
        # 其他存储技能、天赋的信息
        self.skills = data.get("skills", [])
        self.raw_data = data

    def calculate_dps(self, enemy: 'Enemy', skill_index: int = -1) -> Dict[str, float]:
        """
        计算面对特定敌人时的 DPS（默认计算普通攻击，或指定技能）。
        在具体子类中可能会被 override 以支持特殊的伤害逻辑。
        """
        return {"dps": 0.0, "total_damage": 0.0}

    def __str__(self):
        return f"[{self.profession}] {self.name} (ATK: {self.base_atk})"
