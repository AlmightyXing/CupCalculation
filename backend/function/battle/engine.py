from typing import List, Dict, Any, Tuple
import backend.function.logic.formulas as formulas
from backend.function.battle.enemy import Enemy
from backend.function.logic.base_operator import Operator

class BattleEnvironment:
    """
    团队战斗协同环境 (Monkey Patching + 全局面板注入架构)
    """
    def __init__(self):
        self.operators: List[Tuple[Operator, int]] = [] # [(operator, skill_index), ...]
        self.enemies: List[Enemy] = []
        
    def add_operator(self, operator: Operator, skill_index: int = -1):
        self.operators.append((operator, skill_index))
        
    def add_enemy(self, enemy: Enemy):
        self.enemies.append(enemy)
        
    def _aggregate_buffs(self) -> Dict[str, Any]:
        """
        阶段一：从所有干员中提取暴露的团队增益，并进行正确的叠加或取最值
        """
        env_buffs = {
            # 1. 面向【干员面板】的增益
            "inspire_atk": 0.0,
            "inspire_def": 0.0,
            "aura_atk_ratio": 0.0,
            "aura_aspd": 0.0,
            
            # 2. 面向【敌人面板】的削弱
            "flat_def_shred": 0.0,
            "ratio_def_shred_multiplier": 1.0, # 最终计算方法：def * ratio_def_shred_multiplier
            "res_shred": 0.0,
            "ratio_res_shred_multiplier": 1.0,
            
            # 3. 面向【伤害结算】的乘区
            "fragile": 0.0,
            "arts_flat_dmg": 0.0,
            
            # 4. 面向【机制条件】的标志位
            "is_cced": False,
            "is_vigor": False
        }
        
        for op, skill_idx in self.operators:
            buffs = op.get_team_buffs(skill_idx)
            
            # 1. 干员面板
            env_buffs["inspire_atk"] = max(env_buffs["inspire_atk"], buffs.get("inspire_atk", 0.0))
            env_buffs["inspire_def"] = max(env_buffs["inspire_def"], buffs.get("inspire_def", 0.0))
            env_buffs["aura_atk_ratio"] += buffs.get("aura_atk_ratio", 0.0)
            env_buffs["aura_aspd"] += buffs.get("aura_aspd", 0.0)
            
            # 2. 敌人面板
            env_buffs["flat_def_shred"] += buffs.get("flat_def_shred", 0.0)
            # 比例减防/减抗叠乘计算 (1 - r1) * (1 - r2)
            env_buffs["ratio_def_shred_multiplier"] *= (1.0 - buffs.get("ratio_def_shred", 0.0))
            env_buffs["res_shred"] += buffs.get("res_shred", 0.0)
            env_buffs["ratio_res_shred_multiplier"] *= (1.0 - buffs.get("ratio_res_shred", 0.0))
            
            # 3. 伤害结算
            env_buffs["fragile"] = max(env_buffs["fragile"], buffs.get("fragile", 0.0))
            env_buffs["arts_flat_dmg"] += buffs.get("arts_flat_dmg", 0.0)
            
            # 4. 机制标志
            if buffs.get("is_cced", False):
                env_buffs["is_cced"] = True
            if buffs.get("is_vigor", False):
                env_buffs["is_vigor"] = True
                
        return env_buffs

    def simulate(self) -> dict:
        """
        阶段二~阶段四：注入面板、动态劫持底层公式并计算
        """
        results = {}
        
        # 记录原始公式以便恢复
        original_calc_arts = formulas.calculate_arts_damage
        original_calc_phys = formulas.calculate_physical_damage
        
        try:
            # 获取环境 Buff
            env_buffs = self._aggregate_buffs()
            
            # --- 阶段二：动态公式劫持 (Monkey Patching) ---
            def patched_calculate_arts_damage(atk: float, enemy_res: float, res_ignore_ratio: float = 0.0) -> float:
                base_dmg = original_calc_arts(atk, enemy_res, res_ignore_ratio)
                dmg_with_flat = base_dmg + self._current_enemy.global_arts_flat_dmg
                final_dmg = dmg_with_flat * (1 + self._current_enemy.global_fragile)
                return final_dmg

            def patched_calculate_physical_damage(atk: float, enemy_def: float, def_ignore_ratio: float = 0.0, def_ignore_flat: float = 0.0) -> float:
                base_dmg = original_calc_phys(atk, enemy_def, def_ignore_ratio, def_ignore_flat)
                final_dmg = base_dmg * (1 + self._current_enemy.global_fragile)
                return final_dmg

            formulas.calculate_arts_damage = patched_calculate_arts_damage
            formulas.calculate_physical_damage = patched_calculate_physical_damage
            
            # --- 阶段三：对每个敌人进行计算 ---
            for enemy in self.enemies:
                # 重置敌人状态
                enemy.reset()
                self._current_enemy = enemy
                
                # 注入敌人面板
                enemy.current_res = max(0, enemy.base_res * env_buffs["ratio_res_shred_multiplier"] - env_buffs["res_shred"])
                enemy.current_def = max(0, enemy.base_def * env_buffs["ratio_def_shred_multiplier"] - env_buffs["flat_def_shred"])
                enemy.is_cced = env_buffs["is_cced"]
                enemy.global_fragile = env_buffs["fragile"]
                enemy.global_arts_flat_dmg = env_buffs["arts_flat_dmg"]
                
                # 注入干员面板并计算伤害
                for op, skill_idx in self.operators:
                    # 记录并修改原始面板
                    original_final_atk = getattr(op, "final_base_atk", op.base_atk)
                    original_aspd = op.attack_speed
                    
                    # 应用光环和鼓舞
                    bonus_atk = op.base_atk * env_buffs["aura_atk_ratio"] + env_buffs["inspire_atk"]
                    op.final_base_atk = original_final_atk + bonus_atk
                    op.attack_speed = original_aspd + env_buffs["aura_aspd"]
                    
                    # 计算伤害
                    dmg_info = op.calculate_dps(enemy, skill_index=skill_idx)
                    
                    # 恢复干员面板
                    op.final_base_atk = original_final_atk
                    op.attack_speed = original_aspd
                    
                    if op.character_id not in results:
                        results[op.character_id] = []
                        
                    results[op.character_id].append({
                        "enemy_id": enemy.enemy_id,
                        "dps": dmg_info.get("dps", 0),
                        "total_damage": dmg_info.get("total_damage", 0)
                    })
                    
        finally:
            # --- 阶段四：现场恢复 ---
            formulas.calculate_arts_damage = original_calc_arts
            formulas.calculate_physical_damage = original_calc_phys
            
        return {
            "status": "success",
            "combat_report": results,
            "applied_buffs": env_buffs
        }
