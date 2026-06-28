import json

def generate_professions_py():
    with open('scratch_all_professions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Standardized mapping for the 45 sub-professions
    # Plus a few variations that might be in the JSON
    zh_to_en = {
        "重剑手": "Crusher",
        "无畏者": "Dreadnought",
        "钩索师": "Hookmaster",
        "领主": "Lord",
        "武者": "Fighter",
        "医师": "Physician",
        "投掷手": "Flinger",
        "炮手": "Artilleryman",
        "情报官": "IntelligenceOfficer",
        "哨戒铁卫": "SentinelDefender",
        "斗士": "Brawler",
        "中坚术师": "CoreCaster",
        "吟游者": "Bard",
        "傀儡师": "Dollkeeper",
        "巫役": "IncantationMedic",
        "塑灵术师": "Ritualist",
        "咒愈师": "CurseHealer",  # Distinguish from 巫役
        "扩散术师": "SplashCaster",
        "群愈师": "RingHealer",
        "尖兵": "Pioneer",
        "伏击客": "Ambusher",
        "护佑者": "Abjurer",
        "炼金师": "Alchemist",
        "剑豪": "Swordmaster",
        "疗养师": "Therapist",
        "削弱者": "Hexer",
        "策士": "Strategist",
        "阵法术师": "PhalanxCaster",
        "解放者": "Liberator",
        "守护者": "Guardian",
        "神射手": "Deadeye",
        "铁卫": "Protector",
        "行商": "Merchant",
        "怪杰": "Geek",
        "驭法铁卫": "ArtsProtector",
        "秘术师": "MysticCaster",
        "行医": "WanderingMedic",
        "术战者": "ArtsFighter",
        "速射手": "Marksman",
        "收割者": "Reaper",
        "处决者": "Executor",
        "重射手": "HeavyShooter",
        "教官": "Instructor",
        "召唤师": "Summoner",
        "本源铁卫": "PrimalProtector",
        "陷阱师": "Trapmaster",
        "守望者": "Watcher",
        "战术家": "Tactician",
        "散射手": "Spreadshooter",
        "推击手": "Pusher",
        "不屈者": "Juggernaut",
        "凝滞师": "DecelBinder",
        "本源术师": "PrimalCaster",
        "猎手": "Hunter",
        "强攻手": "Centurion",
        "轰击术师": "BlastCaster",
        "工匠": "Artificer",
        "冲锋手": "Charger",
        "决战者": "Duelist",
        "链术师": "ChainCaster",
        "撼地者": "Earthshaker",
        "回环射手": "Loopshooter",
        "攻城手": "Besieger",
        "驭械术师": "MechAccordCaster",
        "执旗手": "StandardBearer",
        "要塞": "Fortress"
    }
    
    lines = [
        "from backend.function.logic.base_operator import Operator",
        "from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage",
        "\n"
    ]
    
    for zh_name, info in data.items():
        en_name = zh_to_en.get(zh_name, "UnknownProfession")
        desc = info['description'].replace("\n", " ")
        atk_time = info['atk_time']
        
        lines.append(f"class {en_name}(Operator):")
        lines.append(f'    """')
        lines.append(f'    职业：{zh_name}')
        lines.append(f'    特性：{desc}')
        lines.append(f'    """')
        lines.append(f"    def __init__(self, data: dict):")
        lines.append(f"        super().__init__(data)")
        lines.append(f"        self.attack_interval = {atk_time}")
        
        # Override calculate_normal_hit where necessary based on trait mechanics affecting target DPS
        
        # 1. Swordmaster (hit twice)
        if en_name == "Swordmaster":
            lines.append("")
            lines.append("    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:")
            lines.append("        # 剑豪：普通攻击连续造成两次伤害")
            lines.append("        single_hit = super().calculate_normal_hit(enemy, target_count)")
            lines.append("        return single_hit * 2.0")
            
        # 2. Flinger (hit 100% and 50%)
        elif en_name == "Flinger":
            lines.append("")
            lines.append("    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:")
            lines.append("        # 投掷手：两次物理伤害，第二次为50%")
            lines.append("        # 注：投掷手伤害均为物理伤害，此处的简化假设基类计算为物理")
            lines.append("        first_hit = calculate_physical_damage(self.final_base_atk, enemy.current_def)")
            lines.append("        second_hit = calculate_physical_damage(self.final_base_atk * 0.5, enemy.current_def)")
            lines.append("        return first_hit + second_hit")

        # 3. Hunter (consumes ammo, ATK 120%)
        elif en_name == "Hunter":
            lines.append("")
            lines.append("    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:")
            lines.append("        # 猎手：攻击力提升至120%")
            lines.append("        # 假定伤害为物理（如果为法术，子类需覆写）")
            lines.append("        return calculate_physical_damage(self.final_base_atk * 1.2, enemy.current_def)")
        
        # 4. Instructor (attack non-blocked enemies ATK 120%)
        elif en_name == "Instructor":
            lines.append("")
            lines.append("    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:")
            lines.append("        # 教官：假设默认攻击未阻挡敌人（单体测试环境通常为桩，未阻挡），提升至120%")
            lines.append("        return calculate_physical_damage(self.final_base_atk * 1.2, enemy.current_def)")

        # 5. PhalanxCaster & Liberator (0 damage normally)
        elif en_name in ["PhalanxCaster", "Liberator"]:
            lines.append("")
            lines.append("    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:")
            lines.append(f"        # {zh_name}：通常时不攻击")
            lines.append("        return 0.0")

        # 6. MechAccordCaster (Drone ramp up)
        elif en_name == "MechAccordCaster":
            lines.append("")
            lines.append("    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:")
            lines.append("        # 驭械术师：浮游单元最高110%。为了简化DPS计算平均值，取常态（本体100% + 单元满层110% = 210%）")
            lines.append("        return calculate_arts_damage(self.final_base_atk * 2.1, enemy.current_res)")
            
        # 7. Spreadshooter (150% front row)
        elif en_name == "Spreadshooter":
            lines.append("")
            lines.append("    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:")
            lines.append("        # 散射手：正前方一横排150%，默认为最优输出环境")
            lines.append("        return calculate_physical_damage(self.final_base_atk * 1.5, enemy.current_def)")
            
        # 8. Tactician (150% blocked by reinforcement)
        elif en_name == "Tactician":
            lines.append("")
            lines.append("    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:")
            lines.append("        # 战术家：攻击援军阻挡的敌人150%，默认为最优输出环境")
            lines.append("        return calculate_physical_damage(self.final_base_atk * 1.5, enemy.current_def)")
            
        # 9. Loopshooter (attack interval based on distance)
        elif en_name == "Loopshooter":
            lines.append("")
            lines.append("    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:")
            lines.append("        # 回环射手：攻击间隔根据距离变化，出伤本身系数不变")
            lines.append("        return super().calculate_normal_hit(enemy, target_count)")

        else:
            # Default pass
            pass
            
        lines.append("")
        
    with open('backend/function/logic/professions.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

if __name__ == "__main__":
    generate_professions_py()
