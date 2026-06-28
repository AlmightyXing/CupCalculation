from backend.function.logic.base_operator import Operator
from backend.function.logic.formulas import calculate_physical_damage, calculate_arts_damage

# --- 父类定义 (截取片段) ---
class Crusher(Operator):
    """
    职业：重剑手
    特性：同时攻击阻挡的所有敌人
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.5

class Dreadnought(Operator):
    """
    职业：无畏者
    特性：能够阻挡一个敌人
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.5

class Hookmaster(Operator):
    """
    职业：钩索师
    特性：技能可以使敌人产生位移，可以放置于远程位
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.8

class Lord(Operator):
    """
    职业：领主
    特性：可以进行远程攻击，但此时攻击力降低至80%
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.3

class Fighter(Operator):
    """
    职业：武者
    特性：不成为其他角色的治疗目标，每次攻击到敌人后回复自身70生命
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.2

class Physician(Operator):
    """
    职业：医师
    特性：恢复友方单位生命
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.85

class Flinger(Operator):
    """
    职业：投掷手
    特性：攻击对小范围的地面敌人造成两次物理伤害（第二次为余震，伤害降低至攻击力的一半）
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.1

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 投掷手：两次物理伤害，第二次为50%
        # 注：投掷手伤害均为物理伤害，此处的简化假设基类计算为物理
        first_hit = calculate_physical_damage(self.final_base_atk, enemy.current_def)
        second_hit = calculate_physical_damage(self.final_base_atk * 0.5, enemy.current_def)
        return first_hit + second_hit

class Artilleryman(Operator):
    """
    职业：炮手
    特性：攻击造成群体物理伤害
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.8

class IntelligenceOfficer(Operator):
    """
    职业：情报官
    特性：再部署时间减少，可使用远程攻击
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.0

class SentinelDefender(Operator):
    """
    职业：哨戒铁卫
    特性：能够阻挡三个敌人，可以进行远程攻击
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.2

class Brawler(Operator):
    """
    职业：斗士
    特性：能够阻挡一个敌人
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 0.78

class CoreCaster(Operator):
    """
    职业：中坚术师
    特性：攻击造成法术伤害
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

class Bard(Operator):
    """
    职业：吟游者
    特性：不攻击，持续恢复范围内所有友军生命（每秒相当于自身攻击力10%的生命），自身不受鼓舞影响
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.3

class Dollkeeper(Operator):
    """
    职业：傀儡师
    特性：受到致命伤时不撤退，切换成<替身>作战（替身阻挡数为0），持续20秒后自身再次替换<替身>
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.2

class IncantationMedic(Operator):
    """
    职业：巫役
    特性：攻击造成法术伤害，可以造成元素损伤
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

class Ritualist(Operator):
    """
    职业：塑灵术师
    特性：攻击造成法术伤害，可以通过击倒敌人生成召唤物，可攻击到自身召唤物阻挡的敌人
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

class CurseHealer(Operator):
    """
    职业：咒愈师
    特性：攻击造成法术伤害，攻击敌人时为攻击范围内一名友方干员治疗相当于50%伤害的生命值
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

class SplashCaster(Operator):
    """
    职业：扩散术师
    特性：攻击造成群体法术伤害
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.9

class RingHealer(Operator):
    """
    职业：群愈师
    特性：同时恢复三个友方单位的生命
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.85

class Pioneer(Operator):
    """
    职业：尖兵
    特性：能够阻挡两个敌人
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.05

class Ambusher(Operator):
    """
    职业：伏击客
    特性：对攻击范围内所有敌人造成伤害；拥有50%的物理和法术闪避且不容易成为敌人的攻击目标
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 3.5

class Abjurer(Operator):
    """
    职业：护佑者
    特性：攻击造成法术伤害，技能开启后改为治疗友方单位（治疗量相当于75%攻击力）
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

class Alchemist(Operator):
    """
    职业：炼金师
    特性：可以投掷炼金单元协助作战
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.5

class Swordmaster(Operator):
    """
    职业：剑豪
    特性：普通攻击连续造成两次伤害
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.3

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 剑豪：普通攻击连续造成两次伤害
        single_hit = super().calculate_normal_hit(enemy, target_count)
        return single_hit * 2.0

class Therapist(Operator):
    """
    职业：疗养师
    特性：拥有较大治疗范围，但在治疗较远目标时治疗量变为80%
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.85

class Hexer(Operator):
    """
    职业：削弱者
    特性：攻击造成法术伤害
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

class Strategist(Operator):
    """
    职业：策士
    特性：能够阻挡两个敌人，可以支援待部署区的我方单位
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.2

class PhalanxCaster(Operator):
    """
    职业：阵法术师
    特性：通常时不攻击且防御力和法术抗性大幅度提升，技能开启时攻击造成群体法术伤害
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.0

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 阵法术师：通常时不攻击
        return 0.0

class Liberator(Operator):
    """
    职业：解放者
    特性：通常不攻击且阻挡数为0，技能未开启时40秒内攻击力逐渐提升至最高+200%且技能结束时重置攻击力
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.2

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 解放者：通常时不攻击
        return 0.0

class Guardian(Operator):
    """
    职业：守护者
    特性：技能可以治疗友方单位
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.2

class Deadeye(Operator):
    """
    职业：神射手
    特性：优先攻击攻击范围内防御力最低的敌方单位
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.7

class Protector(Operator):
    """
    职业：铁卫
    特性：能够阻挡三个敌人
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.2

class Merchant(Operator):
    """
    职业：行商
    特性：再部署时间减少，撤退时不返还部署费用，在场时每3秒消耗3点部署费用（不足时自动撤退）
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.0

class Geek(Operator):
    """
    职业：怪杰
    特性：自身生命会不断流失
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.3

class ArtsProtector(Operator):
    """
    职业：驭法铁卫
    特性：技能开启时普通攻击会造成法术伤害
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

class MysticCaster(Operator):
    """
    职业：秘术师
    特性：攻击造成法术伤害，在找不到攻击目标时可以将攻击能量储存起来之后一齐发射（最多3个）
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 3.0

class WanderingMedic(Operator):
    """
    职业：行医
    特性：恢复友方单位生命，并回复相当于攻击力50%的元素损伤（可以回复未受伤友方单位的元素损伤）
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.85

class ArtsFighter(Operator):
    """
    职业：术战者
    特性：攻击造成法术伤害
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.25

class Marksman(Operator):
    """
    职业：速射手
    特性：优先攻击空中单位
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.0

class Reaper(Operator):
    """
    职业：收割者
    特性：无法被友方角色治疗，攻击造成群体伤害，每攻击到一个敌人回复自身50生命，最大生效数等于阻挡数
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.3

class Executor(Operator):
    """
    职业：处决者
    特性：再部署时间大幅度减少，可以且优先攻击自身阻挡的单位（即使目标处于攻击范围外或为飞行单位）。
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 0.93

class HeavyShooter(Operator):
    """
    职业：重射手
    特性：高精度的近距离射击
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

class Instructor(Operator):
    """
    职业：教官
    特性：可以攻击到较远敌人，攻击自身未阻挡的敌人时攻击力提升至120%
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.05

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 教官：假设默认攻击未阻挡敌人（单体测试环境通常为桩，未阻挡），提升至120%
        return calculate_physical_damage(self.final_base_atk * 1.2, enemy.current_def)

class Summoner(Operator):
    """
    职业：召唤师
    特性：攻击造成法术伤害，可以使用召唤物协助作战
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

class PrimalProtector(Operator):
    """
    职业：本源铁卫
    特性：能够阻挡三个敌人，可以造成元素损伤
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

class Trapmaster(Operator):
    """
    职业：陷阱师
    特性：可以使用陷阱来协助作战，但陷阱无法放置于敌人已在的格子中
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 0.85

class Watcher(Operator):
    """
    职业：守望者
    特性：恢复友方单位生命，并且可以起飞
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.85

class Tactician(Operator):
    """
    职业：战术家
    特性：可以在攻击范围内选择一次战术点来召唤援军，自身攻击援军阻挡的敌人时攻击力提升至150%
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.0

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 战术家：攻击援军阻挡的敌人150%，默认为最优输出环境
        return calculate_physical_damage(self.final_base_atk * 1.5, enemy.current_def)

class Spreadshooter(Operator):
    """
    职业：散射手
    特性：攻击范围内的所有敌人，对自己前方一横排的敌人攻击力提升至150%
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.3

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 散射手：正前方一横排150%，默认为最优输出环境
        return calculate_physical_damage(self.final_base_atk * 1.5, enemy.current_def)

class Pusher(Operator):
    """
    职业：推击手
    特性：同时攻击阻挡的所有敌人 可以放置于远程位
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.2

class Juggernaut(Operator):
    """
    职业：不屈者
    特性：无法被友方角色治疗
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

class DecelBinder(Operator):
    """
    职业：凝滞师
    特性：攻击造成法术伤害，并对敌人造成短暂的停顿
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.9

class PrimalCaster(Operator):
    """
    职业：本源术师
    特性：攻击造成法术伤害，可以造成元素伤害
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

class Hunter(Operator):
    """
    职业：猎手
    特性：攻击时需要消耗子弹且攻击力提升至120%，不攻击时会缓慢地装填子弹（最多8发）
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 猎手：攻击力提升至120%
        # 假定伤害为物理（如果为法术，子类需覆写）
        return calculate_physical_damage(self.final_base_atk * 1.2, enemy.current_def)

class Centurion(Operator):
    """
    职业：强攻手
    特性：同时攻击阻挡的所有敌人
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.2

class BlastCaster(Operator):
    """
    职业：轰击术师
    特性：攻击造成超远距离的群体法术伤害
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.9

class Artificer(Operator):
    """
    职业：工匠
    特性：能够阻挡两个敌人，使用<支援装置>协助作战
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.5

class Charger(Operator):
    """
    职业：冲锋手
    特性：击杀敌人后获得1点部署费用，撤退时返还初始部署费用
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.0

class Duelist(Operator):
    """
    职业：决战者
    特性：只有阻挡敌人时才能够回复技力
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.6

class ChainCaster(Operator):
    """
    职业：链术师
    特性：攻击造成法术伤害，且会在4个敌人间跳跃，每次跳跃伤害降低15%并造成短暂停顿(0.5s)
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.3

class Earthshaker(Operator):
    """
    职业：撼地者
    特性：攻击使目标周围的其他敌人受到相当于攻击力50%的群体物理伤害
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.8

class Loopshooter(Operator):
    """
    职业：回环射手
    特性：持有回旋投射物时才能够攻击（投射物需要时间回收）
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.0

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 回环射手：攻击间隔根据距离变化，出伤本身系数不变
        return super().calculate_normal_hit(enemy, target_count)

class Besieger(Operator):
    """
    职业：攻城手
    特性：优先攻击重量最重的敌人
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.4

class MechAccordCaster(Operator):
    """
    职业：驭械术师
    特性：操作浮游单元造成法术伤害，单元攻击同一敌人伤害提升（最高造成干员110%攻击力的伤害）
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.3

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 驭械术师：浮游单元最高110%。为了简化DPS计算平均值，取常态（本体100% + 单元满层110% = 210%）
        return calculate_arts_damage(self.final_base_atk * 2.1, enemy.current_res)

class StandardBearer(Operator):
    """
    职业：执旗手
    特性：技能发动期间阻挡数变为0
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 1.3

class Fortress(Operator):
    """
    职业：要塞
    特性：不阻挡敌人时优先远程群体物理攻击
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.attack_interval = 2.8

# --- 干员代码 ---
from backend.function.logic.professions import Besieger
from backend.function.logic.formulas import calculate_physical_damage

class Uss4早露(Besieger):
    """
    干员：早露
    """
    def __init__(self, data: dict):
        super().__init__(data)
        
        # 获取信赖属性并加到基础面板上
        self.trust_atk = self.raw_data.get("confidence_atk", 0)
        self.final_base_atk = self.base_atk + self.trust_atk
        
        self.apply_talents()
        
    def apply_talents(self):
        # 天赋 1：深入骨髓 (攻击重量较重（重量等级大于等于3）的敌人时，无视其防御力的60%)
        self.talent_ignore_def_ratio = 0.6
        self.talent_weight_threshold = 3 # 重量等级阈值
        
        # 天赋 2：学生楷模 (编入队伍时，所有【乌萨斯学生自治团】干员攻击力+8%)
        # 此天赋为光环效果，影响其他【乌萨斯学生自治团】干员，不直接提高早露自身的伤害。
        # 根据规则“只要天赋对提高伤害有帮助，均纳入考虑！”，此天赋不直接提高早露自身伤害，故在此处不作处理。
        
    def _calc_hit(self, atk_val: float, enemy) -> float:
        """
        计算单次命中时的期望物理伤害（考虑深入骨髓天赋的无视防御条件）
        """
        # 检查敌人重量等级是否满足天赋条件
        if hasattr(enemy, 'weight_level') and enemy.weight_level >= self.talent_weight_threshold:
            return calculate_physical_damage(atk_val, enemy.current_def, def_ignore_ratio=self.talent_ignore_def_ratio)
        else:
            return calculate_physical_damage(atk_val, enemy.current_def, def_ignore_ratio=0.0)

    def calculate_normal_hit(self, enemy, target_count: int = 1) -> float:
        # 普攻直接调用内部的 _calc_hit 方法，处理天赋的条件无视防御
        # Besieger父类没有特殊的calculate_normal_hit逻辑，因此直接实现早露的普攻逻辑是正确的。
        return self._calc_hit(self.final_base_atk, enemy)

    def calculate_skill_damage(self, enemy, skill_index: int, target_count: int = 1) -> dict:
        # 获取实际攻击间隔，用于计算技能期间的普攻次数和DPS
        actual_atk_interval = self.attack_interval * 100 / self.attack_speed
        
        if skill_index == 0:
            # 技能 1 (攻击力强化·γ型)：攻击力+100%，持续30秒
            skill_duration = 30
            skill_atk_multiplier = 1 + 1.00 # 攻击力+100%
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 技能持续期间能打出的普攻次数
            hits_during_skill = skill_duration / actual_atk_interval
            
            # 计算单次强化普攻的伤害
            single_hit_damage = self._calc_hit(enhanced_atk, enemy)
            
            # 总伤害 = 普攻次数 * 单次强化普攻伤害
            total_damage = hits_during_skill * single_hit_damage
            
            # DPS = 单次强化普攻伤害 / 实际攻击间隔
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 1:
            # 技能 2 (分裂射击)：攻击力+90%，可以额外攻击一个敌人，持续60秒
            # "可以额外攻击一个敌人" 属于群体攻击描述，根据规则，严禁在代码中乘以任何目标数。
            skill_duration = 60
            skill_atk_multiplier = 1 + 0.90 # 攻击力+90%
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # 技能持续期间能打出的普攻次数
            hits_during_skill = skill_duration / actual_atk_interval
            
            # 计算单次强化普攻的伤害
            single_hit_damage = self._calc_hit(enhanced_atk, enemy)
            
            # 总伤害 = 普攻次数 * 单次强化普攻伤害
            total_damage = hits_during_skill * single_hit_damage
            
            # DPS = 单次强化普攻伤害 / 实际攻击间隔
            dps = single_hit_damage / actual_atk_interval
            
            return {"total_damage": total_damage, "dps": dps}
            
        elif skill_index == 2:
            # 技能 3 (雪崩击)：攻击力+25%，立即向至多4个重量最重的敌人发射束缚叉枪；
            # 技能持续时间内所有目标受到束缚效果，每秒受到一次攻击，持续8秒
            skill_duration = 8
            skill_atk_multiplier = 1 + 0.25 # 攻击力+25%
            
            # 计算强化后的攻击力
            enhanced_atk = self.final_base_atk * skill_atk_multiplier
            
            # "立即向至多4个重量最重的敌人发射束缚叉枪" 视为技能触发效果，不单独计算伤害。
            # 伤害来源是 "每秒受到一次攻击"。
            
            # 技能持续期间的攻击次数 (每秒一次攻击，持续8秒，即攻击8次)
            hits_during_skill = skill_duration 
            
            # 计算单次攻击的伤害（使用强化后的攻击力）
            single_hit_damage = self._calc_hit(enhanced_atk, enemy)
            
            # 总伤害 = 攻击次数 * 单次攻击伤害
            total_damage = hits_during_skill * single_hit_damage
            
            # DPS = 单次攻击伤害 / 1.0 (因为是每秒一次攻击，攻击间隔为1秒)
            dps = single_hit_damage / 1.0
            
            return {"total_damage": total_damage, "dps": dps}
            
        # 如果技能索引不匹配，调用基类方法
        return super().calculate_skill_damage(enemy, skill_index, target_count)
