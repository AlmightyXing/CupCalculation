from typing import List
from backend.function.battle.enemy import Enemy
from backend.function.logic.base_operator import Operator

class BattleEnvironment:
    """
    独立战斗环境
    """
    def __init__(self):
        self.operators: List[Operator] = []
        self.enemies: List[Enemy] = []
        
    def add_operator(self, operator: Operator):
        self.operators.append(operator)
        
    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)
        
    def simulate(self) -> dict:
        """
        进行宏观的模拟运算。
        （当前采用宏观公式运算器，而非严格的帧时间轴模拟，以避免过度复杂化）
        """
        results = {}
        
        # 依次对每位干员针对所有敌人进行模拟计算
        for op in self.operators:
            op_results = []
            for enemy in self.enemies:
                # 调用各个干员自带的 DPS 公式计算
                dmg_info = op.calculate_dps(enemy)
                op_results.append({
                    "enemy_id": enemy.enemy_id,
                    "dps": dmg_info.get("dps", 0),
                    "total_damage": dmg_info.get("total_damage", 0)
                })
            results[op.character_id] = op_results
            
        return {
            "status": "success",
            "combat_report": results
        }
